#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const TRUE_VALUES = new Set(["1", "true", "yes", "on", "y", "enabled", "enable"]);
const FALSE_VALUES = new Set(["0", "false", "no", "off", "n", "disabled", "disable"]);
const CONFIG_FILES = ["continuous.yaml", "continuous.yml"];
const STATE_TTL_MS = 24 * 60 * 60 * 1000;

const KEYS = {
  enable: ["enabled", "enable", "active", "on", "switch", "开关"],
  prompt: ["prompt", "reason", "message", "提示"],
  repeat: ["repeat", "reentry", "allow_reentry"],
  count: [
    "repeat_count",
    "repeat_times",
    "repeat_limit",
    "max_repeats",
    "max_repeat",
    "times",
    "count",
    "次数",
    "重复次数",
  ],
  session: [
    "session_id",
    "sessionID",
    "sessionId",
    "conversation_id",
    "conversationID",
    "transcript_path",
    "transcriptPath",
  ],
  cli_enable: {
    codex: ["codex", "codex_enabled", "codex_enable"],
    claude: ["claude", "claude_enabled", "claude_enable"],
    opencode: ["opencode", "opencode_enabled", "opencode_enable"],
  },
};

const hasOwn = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
const indentation = (line) => line.length - line.trimStart().length;
const stateFilePath = () => process.env.STOP_HOOK_STATE || path.join(os.homedir(), ".ai-hooks", "stop-state.json");

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
  try {
    return input.trim() ? JSON.parse(input) : {};
  } catch {
    return {};
  }
}

function stripInlineComment(value) {
  let quote = null;
  for (let i = 0; i < value.length; i += 1) {
    const char = value[i];
    if ((char === '"' || char === "'") && value[i - 1] !== "\\") {
      quote = quote === char ? null : quote || char;
    }
    if (char === "#" && quote === null) return value.slice(0, i).trimEnd();
  }
  return value.trimEnd();
}

function unquote(value) {
  const text = stripInlineComment(value).trim();
  const first = text[0];
  const last = text[text.length - 1];
  if (text.length >= 2 && ((first === '"' && last === '"') || (first === "'" && last === "'"))) {
    return text.slice(1, -1);
  }
  return text;
}

function asBool(value) {
  if (typeof value === "boolean") return value;
  if (typeof value === "number") return value !== 0;
  if (typeof value !== "string") return false;

  const normalized = value.trim().toLowerCase();
  if (TRUE_VALUES.has(normalized)) return true;
  if (FALSE_VALUES.has(normalized)) return false;
  return false;
}

function asInt(value) {
  if (typeof value === "number" && Number.isFinite(value)) return Math.trunc(value);
  if (typeof value !== "string" || !/^-?\d+$/.test(value.trim())) return null;
  return Number.parseInt(value.trim(), 10);
}

function parseScalar(value) {
  const text = unquote(value);
  const normalized = text.toLowerCase();
  if (TRUE_VALUES.has(normalized)) return true;
  if (FALSE_VALUES.has(normalized)) return false;
  return text;
}

function readBlock(lines, index, marker, baseIndent) {
  const block = [];
  let blockIndent = null;
  let i = index + 1;

  for (; i < lines.length; i += 1) {
    const line = lines[i];
    if (!line.trim()) {
      block.push("");
      continue;
    }

    const level = indentation(line);
    if (level <= baseIndent) break;
    blockIndent ??= level;
    block.push(line.slice(Math.min(blockIndent, line.length)));
  }

  return {
    nextIndex: i - 1,
    value: marker === ">" ? block.join(" ").replace(/\s+/g, " ").trim() : block.join("\n").trimEnd(),
  };
}

function parseTopLevelYaml(source) {
  const result = {};
  const lines = source.replace(/^\uFEFF/, "").split(/\r?\n/);

  for (let i = 0; i < lines.length; i += 1) {
    const raw = lines[i];
    if (!raw.trim() || raw.trimStart().startsWith("#") || indentation(raw) !== 0) continue;

    const match = raw.match(/^([A-Za-z0-9_\-\u4e00-\u9fff]+)\s*:\s*(.*)$/);
    if (!match) continue;

    const [, key, rawValue] = match;
    const value = rawValue.trimEnd();
    if (value === "|" || value === ">") {
      const block = readBlock(lines, i, value, indentation(raw));
      result[key.trim()] = block.value;
      i = block.nextIndex;
    } else {
      result[key.trim()] = parseScalar(value);
    }
  }

  return result;
}

function findConfig(startDir) {
  for (let current = path.resolve(startDir || process.cwd()); ; current = path.dirname(current)) {
    for (const name of CONFIG_FILES) {
      const file = path.join(current, ".ai", name);
      if (fs.existsSync(file)) return file;
    }

    const parent = path.dirname(current);
    if (parent === current) return null;
  }
}

function pick(record, keys) {
  for (const key of keys) {
    if (hasOwn(record, key)) return record[key];
  }
  return undefined;
}

function repeatLimit(config) {
  const explicitCount = asInt(pick(config, KEYS.count));
  if (explicitCount !== null) return Math.max(0, explicitCount);

  const repeat = pick(config, KEYS.repeat);
  const repeatCount = asInt(repeat);
  if (repeatCount !== null) return Math.max(0, repeatCount);
  return asBool(repeat) ? Infinity : 1;
}

function sessionIdentity(input) {
  return pick(input, KEYS.session);
}

function fileStamp(file) {
  try {
    return String(Math.trunc(fs.statSync(file).mtimeMs));
  } catch {
    return "";
  }
}

function stateKey(input, file) {
  const session = sessionIdentity(input);
  if (!session) return null;

  return crypto
    .createHash("sha256")
    .update(`${file}\0${fileStamp(file)}\0${session}`)
    .digest("hex");
}

function readState() {
  try {
    const state = JSON.parse(fs.readFileSync(stateFilePath(), "utf8"));
    state.entries ??= {};
    return state;
  } catch {
    return { entries: {} };
  }
}

function writeState(state) {
  const file = stateFilePath();
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(state, null, 2)}\n`, "utf8");
}

function pruneState(state, now = Date.now()) {
  for (const [key, entry] of Object.entries(state.entries)) {
    if (!entry?.updatedAt || now - entry.updatedAt > STATE_TTL_MS) delete state.entries[key];
  }
}

function continueCount(input, file, maxContinues) {
  if (maxContinues === Infinity) return { action: "continue", repeat: true };
  if (maxContinues <= 0) return { action: "allow", maxContinues, limitReached: true };

  const key = stateKey(input, file);
  if (!key) {
    const alreadyActive = input.stop_hook_active === true || input.stop_hook_active === "true";
    return alreadyActive
      ? { action: "allow", maxContinues, alreadyActive: true }
      : { action: "continue", maxContinues, count: 1, remaining: maxContinues - 1 };
  }

  const now = Date.now();
  const state = readState();
  pruneState(state, now);

  const current = state.entries[key]?.count ?? 0;
  if (current >= maxContinues) {
    writeState(state);
    return { action: "allow", maxContinues, count: current, limitReached: true };
  }

  const count = current + 1;
  state.entries[key] = { count, file, updatedAt: now };
  writeState(state);
  return { action: "continue", maxContinues, count, remaining: maxContinues - count };
}

function detectCli() {
  if (process.argv.includes("--codex")) return "codex";
  if (process.argv.includes("--claude")) return "claude";
  if (process.argv.includes("--opencode")) return "opencode";
  return null;
}

function isEnabled(config, cli) {
  if (cli && KEYS.cli_enable[cli]) {
    const perCli = pick(config, KEYS.cli_enable[cli]);
    if (perCli !== undefined) return asBool(perCli);
  }
  return asBool(pick(config, KEYS.enable));
}

function evaluate(input, cli) {
  const cwd = input.cwd || input.project_dir || input.directory || process.cwd();
  const file = findConfig(cwd);
  if (!file) return { action: "allow", file: null };

  let config;
  try {
    config = parseTopLevelYaml(fs.readFileSync(file, "utf8"));
  } catch {
    return { action: "allow", file };
  }

  const prompt = String(pick(config, KEYS.prompt) ?? "").trim();
  if (!isEnabled(config, cli) || !prompt) return { action: "allow", file };

  return {
    ...continueCount(input, file, repeatLimit(config)),
    prompt,
    file,
  };
}

const input = parseJson(await readStdin());
const cli = detectCli();
const result = evaluate(input, cli);

if (process.argv.includes("--opencode")) {
  process.stdout.write(JSON.stringify(result));
} else if (result.action === "continue") {
  process.stdout.write(JSON.stringify({ decision: "block", reason: result.prompt }));
}
