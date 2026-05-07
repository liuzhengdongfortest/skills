#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const TRUE_VALUES = new Set(["1", "true", "yes", "on", "y", "enabled", "enable"]);
const FALSE_VALUES = new Set(["0", "false", "no", "off", "n", "disabled", "disable"]);
const ENABLE_KEYS = ["enabled", "enable", "active", "on", "switch", "开关"];
const PROMPT_KEYS = ["prompt", "reason", "message", "提示"];

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

function firstPresent(record, keys) {
  for (const key of keys) {
    if (Object.prototype.hasOwnProperty.call(record, key)) return record[key];
  }
  return undefined;
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
  const repeat = boolValue(parsed.repeat ?? parsed.reentry ?? parsed.allow_reentry);
  const stopHookActive = input.stop_hook_active === true || input.stop_hook_active === "true";

  if (!enabled || !prompt) return { action: "allow", file };
  if (stopHookActive && !repeat) return { action: "allow", file, alreadyActive: true };

  return { action: "continue", prompt, file, repeat };
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
