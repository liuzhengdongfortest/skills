# Stop Hook 续航闸门

当老板希望 Codex、Claude Code、OpenCode 在“准备停止”前再看一眼项目约束时，用这个模式。它服务路径 E 的持续推进：让项目用 `.ai/ff.yaml` 声明一个最终检查 prompt，Agent 到 stop 点时如果开关打开，就把 prompt 注回去继续执行。

## 项目开关

在项目根或任意父目录放：

```yaml
# .ai/ff.yaml
enabled: true
prompt: |
  Run final verification before stopping.
  If anything fails, fix it before reporting done.
```

规则：

- 不存在 `.ai/ff.yaml` 或 `.ai/ff.yml`：正常停止。
- `enabled: false`：正常停止。
- `enabled: true` 且 `prompt` 非空：Stop 时继续。
- 默认只续一次，避免无限循环；确实需要每次 stop 都触发时加 `repeat: true`。

开关别名：`enabled`、`enable`、`active`、`on`、`switch`、`开关`。prompt 别名：`prompt`、`reason`、`message`、`提示`。

## 三家差异

- Codex：原生 `Stop` hook，返回 `{"decision":"block","reason":"..."}` 阻止停止。需要 `[features] codex_hooks = true`。
- Claude Code：原生 `Stop` hook，返回同样的 `decision:block` JSON。
- OpenCode：没有原生 Stop block 协议。用插件监听 `session.idle`，再调用 `client.session.prompt(...)` 追加 prompt，效果是“停下后立刻续一轮”。

## 技能素材

- `assets/stop-hooks/ff-stop-hook.mjs`：Codex/Claude/OpenCode 共用判断器。
- `assets/stop-hooks/opencode-ff-stop-gate.js`：OpenCode 插件。
- `assets/stop-hooks/ff.yaml`：项目 `.ai/ff.yaml` 模板。
- `tools/install-ff-stop-hooks.mjs`：安装器，把素材写入用户目录并合并三家配置。

安装：

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

## 使用判断

这个 hook 是最后一道闸门，不是任务系统本体。适合放“最终验证、修失败、更新 task/plan、不要只汇报状态”的要求；不适合放大段需求、阶段计划或具体进度快照。路径 E 的长期状态仍然必须来自 `.boss/requirements/`、`.boss/architecture/`、`.boss/plans/` 和 `.boss/tasks/`。
