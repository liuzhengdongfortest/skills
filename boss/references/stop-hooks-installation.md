# 牛马模式安装手册

本文件只讲 Codex、Claude Code、OpenCode 的 stop hook 安装和实现细节。

停止前执行规程见 [`../guides/ff-execution.md`](../guides/ff-execution.md)，实际 prompt 写法见 [`stop-hooks.md`](stop-hooks.md)。不要把安装细节当作执行指令。

## 底层实现

牛马模式底层实现是 stop hook：

- Codex：原生 `Stop` hook，返回 `{"decision":"block","reason":"..."}` 阻止停止。需要 `[features] codex_hooks = true`。
- Claude Code：原生 `Stop` hook，返回同样的 `decision:block` JSON。
- OpenCode：没有原生 Stop block 协议。用插件监听 `message.part.updated` 中的 `step-finish(reason=stop)`，并兼容监听 `session.idle`，再调用 `client.session.prompt(...)` 追加 prompt。

## 项目开关

在项目根或任意父目录放：

```yaml
# .ai/ff.yaml
enabled: true
repeat: 10
prompt: |
  Run final verification before stopping.
  If anything fails, fix it before reporting done.
```

规则：

- 不存在 `.ai/ff.yaml` 或 `.ai/ff.yml`：正常停止。
- `enabled: false`：正常停止。
- `enabled: true` 且 `prompt` 非空：Stop 时继续。
- 默认只续一次，避免无限循环。
- `repeat: 10`：最多连续续 10 次，第 11 次 stop 允许停止。
- `repeat: true`：每次 stop 都触发，适合明确要无限续的场景。

开关别名：`enabled`、`enable`、`active`、`on`、`switch`、`开关`。

prompt 别名：`prompt`、`reason`、`message`、`提示`。

重复次数字段别名：`repeat_count`、`repeat_times`、`repeat_limit`、`max_repeats`、`max_repeat`、`times`、`count`、`次数`、`重复次数`。独立字段优先于 `repeat`。

计数按 session 和 `.ai/ff.yaml` 文件版本隔离，状态保存在 `~/.ai-hooks/ff-stop-state.json`，一天后自动清理。

## 技能素材

- `assets/stop-hooks/ff-stop-hook.mjs`：Codex/Claude/OpenCode 共用判断器。
- `assets/stop-hooks/opencode-ff-stop-gate.js`：OpenCode 插件。
- `assets/stop-hooks/ff.yaml`：项目 `.ai/ff.yaml` 模板。
- `tools/install-ff-stop-hooks.mjs`：安装器，把素材写入用户目录并合并三家配置。

## 安装

```bash
node tools/install-ff-stop-hooks.mjs
```

安装器会写入：

- `~/.ai-hooks/ff-stop-hook.mjs`
- `~/.codex/hooks.json`
- `~/.codex/config.toml`
- `~/.claude/settings.json`
- `~/.config/opencode/plugins/ff-stop-gate.js`
- `~/.config/opencode/opencode.json`
