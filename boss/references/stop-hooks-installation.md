# 持续工作模式安装手册

本文件只讲 Codex、Claude Code、OpenCode 的 stop hook 安装和实现细节。

停止前执行规程见 [`../guides/continuous-work.md`](../guides/continuous-work.md)，规程入口动作（大抬头）见 [`../guides/lookup-beats.md`](../guides/lookup-beats.md)，实际 prompt 写法见 [`stop-hooks.md`](stop-hooks.md)。不要把安装细节当作执行指令。

## 底层实现

持续工作模式底层实现是 stop hook：

- Codex：原生 `Stop` hook，返回 `{"decision":"block","reason":"..."}` 阻止停止。需要 `--enable hooks` 或 `[features] hooks = true`。旧字段 `codex_hooks` 已废弃，会触发 deprecated 警告。
- Claude Code：原生 `Stop` hook，返回同样的 `decision:block` JSON。
- OpenCode：没有原生 Stop block 协议。用插件监听 `message.part.updated` 中的 `step-finish(reason=stop)`，并兼容监听 `session.idle`，再调用 `client.session.prompt(...)` 追加 prompt。

## 项目开关

在项目根或任意父目录放：

```yaml
# .ai/continuous.yaml
enabled: true
# 按 CLI 分别控制（可选，未设置时回退到 enabled）：
# codex: true
# claude: true
# opencode: true
repeat: 10
prompt: |
  Run final verification before stopping.
  If anything fails, fix it before reporting done.
```

规则：

- 不存在 `.ai/continuous.yaml` 或 `.ai/continuous.yml`：正常停止。
- `enabled: false`：所有 CLI 正常停止。
- `enabled: true` 且 `prompt` 非空：Stop 时继续。
- `codex` / `claude` / `opencode`：单独控制某个 CLI 的启停，优先级高于 `enabled`。未设置时回退到 `enabled` 的值。
  - 例如 `enabled: true` + `codex: false` → Codex 停止时不触发，Claude/OpenCode 正常触发。
- 默认只续一次，避免无限循环。
- `repeat: 10`：最多连续续 10 次，第 11 次 stop 允许停止。
- `repeat: true`：每次 stop 都触发，适合明确要无限续的场景。

开关别名：`enabled`、`enable`、`active`、`on`、`switch`、`开关`。

CLI 开关别名：`codex` / `codex_enabled` / `codex_enable`；`claude` / `claude_enabled` / `claude_enable`；`opencode` / `opencode_enabled` / `opencode_enable`。

prompt 别名：`prompt`、`reason`、`message`、`提示`。

重复次数字段别名：`repeat_count`、`repeat_times`、`repeat_limit`、`max_repeats`、`max_repeat`、`times`、`count`、`次数`、`重复次数`。独立字段优先于 `repeat`。

计数按 session 和 `.ai/continuous.yaml` 文件版本隔离，状态保存在 `~/.ai-hooks/stop-state.json`，一天后自动清理。

## 技能素材

- `assets/stop-hooks/stop-hook.mjs`：Codex/Claude/OpenCode 共用判断器。
- `assets/stop-hooks/opencode-stop-gate.js`：OpenCode 插件。
- `assets/stop-hooks/continuous.yaml`：项目 `.ai/continuous.yaml` 模板。
- `tools/install-stop-hooks.mjs`：安装器，把素材写入用户目录并合并三家配置。

## 安装

```bash
node tools/install-stop-hooks.mjs
```

安装器会写入：

- `~/.ai-hooks/stop-hook.mjs`
- `~/.codex/hooks.json`
- `~/.codex/config.toml`
- `~/.claude/settings.json`
- `~/.config/opencode/plugins/stop-gate.js`
- `~/.config/opencode/opencode.json`

## 从旧版本迁移（牛马模式 → 持续工作模式）

以前用 `.ai/ff.yaml` + `~/.ai-hooks/ff-stop-hook.mjs` 的项目，做这几步：

1. 项目内：`mv .ai/ff.yaml .ai/continuous.yaml`（已经用 `.ai/ff.yml` 的同理改 `.ai/continuous.yml`）。如果 yaml 内的 `prompt:` 字段里还写着"牛马模式执行规程"，改成"持续工作模式执行规程"，并在开头加一句 `Start with a 大抬头`。
2. 全局：重新跑 `node tools/install-stop-hooks.mjs`。它会写入新的 `~/.ai-hooks/stop-hook.mjs` 并更新三家 CLI 配置，指向新脚本。
3. 清理：旧的 `~/.ai-hooks/ff-stop-hook.mjs`、`~/.ai-hooks/ff-stop-state.json`、`~/.config/opencode/plugins/ff-stop-gate.js`、以及 Codex/Claude/OpenCode 配置里指向 `ff-stop-hook.mjs` 的 Stop hook 条目可以手动删除——新安装器只新增条目，不会自动清掉旧条目。
