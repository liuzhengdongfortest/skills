#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const TRUE_VALUES = new Set(["1", "true", "yes", "on", "y", "enabled", "enable"]);
const FALSE_VALUES = new Set(["0", "false", "no", "off", "n", "disabled", "disable"]);
const ENABLE_KEYS = ["enabled", "enable", "active", "on", "switch", "开关"];
const PROMPT_KEYS = ["prompt", "reason", "message", "提示"];
const REPEAT_KEYS = ["repeat", "reentry", "allow_reentry"];
const REPEAT_COUNT_KEYS = [
  "repeat_count",
  "repeat_times",
  "repeat_limit",
  "max_repeats",
  "max_repeat",
  "times",
  "count",
  "次数",
  "重复次数",
];
const STATE_TTL_MS = 24 * 60 * 60 * 1000;

function readStdin() {
  return new Promise((resolve) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => {
      data += chunk;
    });
    process.stdin.on("end", () => resolve(data));
    process.stdin.on("error", () => resolve(data));
  });
}

function parseJson(input) {
  if (!input.trim()) return {};
  try {
    return JSON.parse(input);
  } catch {
    return {};
  }
}

function stripInlineComment(value) {
  let quote = null;
  for (let i = 0; i < value.length; i += 1) {
    const ch = value[i];
    if ((ch === '"' || ch === "'") && value[i - 1] !== "\\") {
      quote = quote === ch ? null : quote || ch;
    }
    if (ch === "#" && quote === null) return value.slice(0, i).trimEnd();
  }
  return value.trimEnd();
}

function unquote(value) {
  const trimmed = stripInlineComment(value).trim();
  if (trimmed.length >= 2) {
    const first = trimmed[0];
    const last = trimmed[trimmed.length - 1];
    if ((first === '"' && last === '"') || (first === "'" && last === "'")) {
      return trimmed.slice(1, -1);
    }
  }
  return trimmed;
}

function indentation(line) {
  const match = line.match(/^ */);
  return match ? match[0].length : 0;
}

function parseScalar(value) {
  const text = unquote(value);
  const normalized = text.toLowerCase();
  if (TRUE_VALUES.has(normalized)) return true;
  if (FALSE_VALUES.has(normalized)) return false;
  return text;
}

function parseTopLevelYaml(source) {
  const result = {};
  const lines = source.replace(/^\uFEFF/, "").split(/\r?\n/);

  for (let i = 0; i < lines.length; i += 1) {
    const raw = lines[i];
    if (!raw.trim() || raw.trimStart().startsWith("#")) continue;
    if (indentation(raw) !== 0) continue;

    const match = raw.match(/^([A-Za-z0-9_\-\u4e00-\u9fff]+)\s*:\s*(.*)$/);
    if (!match) continue;

    const key = match[1].trim();
    const value = match[2].trimEnd();

    if (value === "|" || value === ">") {
      const block = [];
      const folded = value === ">";
      const baseIndent = indentation(raw);
      let blockIndent = null;

      while (i + 1 < lines.length) {
        const next = lines[i + 1];
        if (!next.trim()) {
          block.push("");
          i += 1;
          continue;
        }

        const nextIndent = indentation(next);
        if (nextIndent <= baseIndent) break;
        blockIndent ??= nextIndent;
        block.push(next.slice(Math.min(blockIndent, next.length)));
        i += 1;
      }

      result[key] = folded ? block.join(" ").replace(/\s+/g, " ").trim() : block.join("\n").trimEnd();
      continue;
    }

    result[key] = parseScalar(value);
  }

  return result;
}

function findConfig(startDir) {
  let current = path.resolve(startDir || process.cwd());
  const seen = new Set();

  while (!seen.has(current)) {
    seen.add(current);
    for (const name of ["ff.yaml", "ff.yml"]) {
      const candidate = path.join(current, ".ai", name);
      if (fs.existsSync(candidate)) return candidate;
    }

    const parent = path.dirname(current);
    if (parent === current) return null;
    current = parent;
  }

  return null;
}

function boolValue(value) {
  if (typeof value === "boolean") return value;
  if (typeof value === "number") return value !== 0;
  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase();
    if (TRUE_VALUES.has(normalized)) return true;
    if (FALSE_VALUES.has(normalized)) return false;
  }
  return false;
}

function intValue(value) {
  if (typeof value === "number" && Number.isFinite(value)) return Math.trunc(value);
  if (typeof value !== "string") return null;

  const normalized = value.trim();
  if (!/^-?\d+$/.test(normalized)) return null;
  return Number.parseInt(normalized, 10);
}

function firstPresent(record, keys) {
  for (const key of keys) {
    if (Object.prototype.hasOwnProperty.call(record, key)) return record[key];
  }
  return undefined;
}

function repeatLimit(parsed) {
  const count = intValue(firstPresent(parsed, REPEAT_COUNT_KEYS));
  if (count !== null) return Math.max(0, count);

  const repeat = firstPresent(parsed, REPEAT_KEYS);
  const repeatNumber = intValue(repeat);
  if (repeatNumber !== null) return Math.max(0, repeatNumber);
  if (boolValue(repeat)) return Infinity;
  return 1;
}

function stateFilePath() {
  return process.env.FF_STOP_HOOK_STATE || path.join(os.homedir(), ".ai-hooks", "ff-stop-state.json");
}

function readState() {
  try {
    return JSON.parse(fs.readFileSync(stateFilePath(), "utf8"));
  } catch {
    return { entries: {} };
  }
}

function writeState(state) {
  const file = stateFilePath();
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(state, null, 2)}\n`, "utf8");
}

function pruneState(state, now) {
  state.entries ??= {};
  for (const [key, entry] of Object.entries(state.entries)) {
    if (!entry || typeof entry.updatedAt !== "number" || now - entry.updatedAt > STATE_TTL_MS) {
      delete state.entries[key];
    }
  }
}

function sessionIdentity(input) {
  return (
    input.session_id ||
    input.sessionID ||
    input.sessionId ||
    input.conversation_id ||
    input.conversationID ||
    input.transcript_path ||
    input.transcriptPath ||
    null
  );
}

function stateKey(input, file) {
  const session = sessionIdentity(input);
  if (!session) return null;

  let fileStamp = "";
  try {
    fileStamp = String(Math.trunc(fs.statSync(file).mtimeMs));
  } catch {
    // The file path is already part of the key, so missing stat data can be tolerated.
  }

  return crypto
    .createHash("sha256")
    .update(`${file}\0${fileStamp}\0${session}`)
    .digest("hex");
}

function evaluateCount(input, file, maxContinues) {
  if (maxContinues === Infinity) return { action: "continue", repeat: true };
  if (maxContinues <= 0) return { action: "allow", file, maxContinues, limitReached: true };

  const key = stateKey(input, file);
  if (!key) {
    const stopHookActive = input.stop_hook_active === true || input.stop_hook_active === "true";
    if (stopHookActive) return { action: "allow", file, maxContinues, alreadyActive: true };
    return { action: "continue", maxContinues, count: 1, remaining: Math.max(0, maxContinues - 1) };
  }

  const now = Date.now();
  const state = readState();
  pruneState(state, now);

  const current = state.entries[key]?.count ?? 0;
  if (current >= maxContinues) {
    writeState(state);
    return { action: "allow", file, maxContinues, count: current, limitReached: true };
  }

  const count = current + 1;
  state.entries[key] = {
    count,
    file,
    updatedAt: now,
  };
  writeState(state);

  return {
    action: "continue",
    maxContinues,
    count,
    remaining: Math.max(0, maxContinues - count),
  };
}

function evaluate(input) {
  const cwd = input.cwd || input.project_dir || input.directory || process.cwd();
  const file = findConfig(cwd);
  if (!file) return { action: "allow", file: null };

  let parsed;
  try {
    parsed = parseTopLevelYaml(fs.readFileSync(file, "utf8"));
  } catch {
    return { action: "allow", file };
  }

  const enabled = boolValue(firstPresent(parsed, ENABLE_KEYS));
  const prompt = String(firstPresent(parsed, PROMPT_KEYS) ?? "").trim();
  const maxContinues = repeatLimit(parsed);

  if (!enabled || !prompt) return { action: "allow", file };

  return {
    ...evaluateCount(input, file, maxContinues),
    prompt,
    file,
  };
}

const input = parseJson(await readStdin());
const result = evaluate(input);

if (process.argv.includes("--opencode")) {
  process.stdout.write(JSON.stringify(result));
  process.exit(0);
}

if (result.action === "continue") {
  process.stdout.write(
    JSON.stringify({
      decision: "block",
      reason: result.prompt,
    }),
  );
}

process.exit(0);
