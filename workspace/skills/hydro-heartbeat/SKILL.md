---
name: hydro-heartbeat
description: 本地喝水状态机。用 JSON 记录饮水、延后、冷却和一周汇总；优先用于 Heartbeat 的低频柔性问询，不做死板定时轰炸。
---

# 技能背景

这是一个本地维护的喝水打卡技能。用户希望系统能像一个贴心的朋友一样，在检测到他可能忘记喝水时，自然地“顺嘴一提”，而不是像闹钟一样生硬地播报。

## 核心机制

- 依靠 `hydro-heartbeat/scripts/manage.py` 管理本地 JSON 状态（`data.json`）
- 本地记录当天的总量、上次喝水时间、冷却期
- 不联网
- 不读取其他应用数据
- 不从“任何来源”偷偷吸收健康信息

## 命令

- `python3 skills/hydro-heartbeat/scripts/manage.py check --context standalone`
  - 供 Heartbeat 使用。返回是否适合主动问一句。
- `python3 skills/hydro-heartbeat/scripts/manage.py log 250`
  - 记录喝水 250ml。
- `python3 skills/hydro-heartbeat/scripts/manage.py defer 25`
  - 用户说“等会儿/先忙”，延后 25 分钟。
- `python3 skills/hydro-heartbeat/scripts/manage.py mark-prompt --kind standalone`
  - 当你真的已经发出主动喝水问句后，立刻调用它记录本次打扰，避免后续复读。
- `python3 skills/hydro-heartbeat/scripts/manage.py today`
  - 查看今日累计、目标、最近一次喝水时间。
- `python3 skills/hydro-heartbeat/scripts/manage.py week`
  - 查看最近 7 天汇总。
- `python3 skills/hydro-heartbeat/scripts/manage.py status`
  - 查看今日完整状态。

## 风格基调

- 主动提醒的语气是：有趣、幽默、鼓励式
- 像一个嘴贫但真在关心人的朋友
- 会轻轻推一把，但不命令、不说教、不制造压力
- 鼓励必须贴着当前状态，不能悬空乱夸
- 目标是让用户更愿意立刻喝一口，而不是写出一段热闹文案

## 提醒阶段

- `first_cup`
  - 今天进度为 0，重点是“开张”
- `behind_schedule`
  - 比如 11 点后还没开张，或下午进度明显偏慢
- `in_progress`
  - 已经喝了一些，但隔了一阵子，适合顺势鼓励
- `wrap_up`
  - 晚些时候接近目标，只差一点，适合优雅收尾
- `resume`
  - 中间忙忘了或断了一阵，重点是“接回来就行”

## 核心语料

（注：系统现在在后台直接返回随机语料，请依据系统返回的 `suggested_prompt` 进行改写）

## 生成约束

- **核心执行路径：强制动态改写**：必须结合当前的喝水进度、落后程度和前文聊天语境，对 `suggested_prompt` 进行动态改写与润色。**严禁**原封不动地直接复制粘贴 `suggested_prompt`。务必让提示像人类朋友随口关心一样自然，绝不生硬死板。
- 允许轻微夸张、拟人、画面感和嘴贫式幽默
- 不允许羞辱、攻击、阴阳怪气或制造负罪感
- 每条提醒尽量简短，像聊天，不像公告

## 使用规则

- 主动问之前先跑 `check`
- 只有 `should_prompt=true` 时，才允许主动提喝水
- 如果真的发出了问句，必须紧接着运行 `mark-prompt`
- 用户主动说“刚喝了/喝了一杯/喝了 300ml”时，优先调用 `log`
- `log` 之后给用户的回复要短、有点风格，像顺手接一句，不要播报“今日总量 / 距离目标 / 下次提醒时间”
- `log` 之后不要再追加客服式收尾，例如“还有什么其他需要我帮你处理的吗？”
- 用户说“等会儿/先忙”时，调用 `defer`
- 问句要简短、自然、中文，不要说教，不要连续追问
- 如果 `check` 返回不该问，就保持安静

## 常见中文映射

- “喝了”“喝过了”“刚喝了”：
  - 默认记录一杯，运行 `python3 skills/hydro-heartbeat/scripts/manage.py log 250`
- “喝了一杯”：
  - 运行 `python3 skills/hydro-heartbeat/scripts/manage.py log 250`
- “半杯”“喝了半杯”：
  - 运行 `python3 skills/hydro-heartbeat/scripts/manage.py log 125`
- “一瓶”“喝了一瓶”：
  - 运行 `python3 skills/hydro-heartbeat/scripts/manage.py log 500`
- “喝了 300ml”“喝了 450 毫升”：
  - 按用户明确数值记录
- “先忙”“等会儿”“稍后提醒”“待会儿再说”：
  - 运行 `python3 skills/hydro-heartbeat/scripts/manage.py defer 25`
- “刚喝过了，不用提醒”：
  - 优先记录一杯，再停止追问
- 如果用户表达含糊，但明显是在确认“已经补水”：
  - 默认按 250ml 记一杯，不要为了几十毫升反复追问
- 如果用户明确说“没喝”“还没喝”：
  - 不记量，也不要立刻继续催；等下一次 `check` 再决定

## 对话风格

- 语气像陪跑，不像闹钟
- 可以顺口提醒，不要命令式
- 不要机械重复同一句模板
- 不要擅自设定严格医学目标
