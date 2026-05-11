# 工具

`tools/` 只保留当前技能需要的确定性辅助工具。详细背景放在对应 reference，入口文档只保留怎么用。

## install-stop-hooks.mjs

把 `.ai/continuous.yaml` 持续工作模式安装到 Codex、Claude Code、OpenCode。安装细节见 [`../references/stop-hooks-installation.md`](../references/stop-hooks-installation.md)；执行规程见 [`../guides/continuous-work.md`](../guides/continuous-work.md)，规程入口动作（大抬头）见 [`../guides/lookup-beats.md`](../guides/lookup-beats.md)，实际 prompt 写法见 [`../references/stop-hooks.md`](../references/stop-hooks.md)。

```bash
node tools/install-stop-hooks.mjs
```

安装器会保守合并现有配置，不会清空已有 hooks。项目级开关模板见 [`../assets/stop-hooks/continuous.yaml`](../assets/stop-hooks/continuous.yaml)。
