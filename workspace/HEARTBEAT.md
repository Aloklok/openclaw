# HEARTBEAT TASKS

每次心跳触发时，必须按顺序执行以下检查：

1. **喝水提醒 (Hydro Heartbeat)**: 
   - 运行：`python skills/hydro-heartbeat/scripts/manage.py check --context standalone`
   - 如果 `should_prompt` 为 `true`：
     - 请根据 `suggested_prompt` 或自己组织一段幽默、自然（不带说教感）的中文提醒发送给用户。
     - 发送成功后，必须运行：`python skills/hydro-heartbeat/scripts/manage.py mark-prompt --kind standalone` 以记录本次提醒。
   - 如果 `should_prompt` 为 `false`：继续后续任务。

2. **静默判定**:
   - 如果以上任务都没有产生需要发给用户的信息，请务必保持绝对静默，不要输出任何文字回复，直接调用 `heartbeat_respond(status='ok')` 工具来结束本次任务。