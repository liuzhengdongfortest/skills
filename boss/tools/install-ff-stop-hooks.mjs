#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const toolPath = fileURLToPath(import.meta.url);
const skillRoot = path.resolve(path.dirname(toolPath), "..");
const assetsDir = path.join(skillRoot, "assets", "stop-hooks");
const home = os.homedir();

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function readJson(file, fallback) {
  if (!fs.existsSync(file)) return fallback;
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function copyAsset(name, destination) {
  ensureDir(path.dirname(destination));
  fs.copyFileSync(path.join(assetsDir, name), destination);
}

function commandFor(scriptPath) {
  return `node "${scriptPath.split(path.sep).join("/")}"`;
}

function ensureHookCommand(settings, eventName, command, extra = {}) {
  settings.hooks ??= {};
  settings.hooks[eventName] ??= [];

  const entries = settings.hooks[eventName];
  for (const entry of entries) {
    for (const hook of entry.hooks ?? []) {
      if (hook.type === "command" && hook.command === command) return false;
    }
  }

  entries.push({
    hooks: [
      {
        type: "command",
        command,
        timeout: 30,
        ...extra,
      },
    ],
  });
  return true;
}

function ensureCodexFeature(configPath) {
  ensureDir(path.dirname(configPath));
  let text = fs.existsSync(configPath) ? fs.readFileSync(configPath, "utf8") : "";

  if (/^\s*\[features\]\s*$/m.test(text)) {
    const lines = text.split(/\r?\n/);
    let inFeatures = false;
    let found = false;

    for (let i = 0; i < lines.length; i += 1) {
      const line = lines[i];
      if (/^\s*\[.+\]\s*$/.test(line)) inFeatures = /^\s*\[features\]\s*$/.test(line);
      if (inFeatures && /^\s*codex_hooks\s*=/.test(line)) {
        lines[i] = "codex_hooks = true";
        found = true;
      }
      if (inFeatures && i + 1 < lines.length && /^\s*\[.+\]\s*$/.test(lines[i + 1]) && !found) {
        lines.splice(i + 1, 0, "codex_hooks = true");
        found = true;
        break;
      }
    }

    if (!found) lines.push("codex_hooks = true");
    text = lines.join("\n");
  } else {
    text = `${text.trimEnd()}\n\n[features]\ncodex_hooks = true\n`;
  }

  fs.writeFileSync(configPath, text.endsWith("\n") ? text : `${text}\n`, "utf8");
}

const hookScript = path.join(home, ".ai-hooks", "ff-stop-hook.mjs");
copyAsset("ff-stop-hook.mjs", hookScript);

const command = commandFor(hookScript);

const codexHooksPath = path.join(home, ".codex", "hooks.json");
const codexHooks = readJson(codexHooksPath, { hooks: {} });
ensureHookCommand(codexHooks, "Stop", command, { statusMessage: "Checking 牛马模式" });
writeJson(codexHooksPath, codexHooks);
ensureCodexFeature(path.join(home, ".codex", "config.toml"));

const claudeSettingsPath = path.join(home, ".claude", "settings.json");
const claudeSettings = readJson(claudeSettingsPath, {});
ensureHookCommand(claudeSettings, "Stop", command);
writeJson(claudeSettingsPath, claudeSettings);

const opencodePluginPath = path.join(home, ".config", "opencode", "plugins", "ff-stop-gate.js");
copyAsset("opencode-ff-stop-gate.js", opencodePluginPath);

const opencodeConfigPath = path.join(home, ".config", "opencode", "opencode.json");
const opencodeConfig = readJson(opencodeConfigPath, {
  $schema: "https://opencode.ai/config.json",
});
opencodeConfig.plugin ??= [];

const pluginUrl = pathToFileURL(opencodePluginPath).href;
if (!opencodeConfig.plugin.includes(pluginUrl)) opencodeConfig.plugin.push(pluginUrl);
writeJson(opencodeConfigPath, opencodeConfig);

console.log("Installed 牛马模式 for Codex, Claude Code, and OpenCode.");
console.log(`Hook runner: ${hookScript}`);
