#!/usr/bin/env python3
"""Hydration heartbeat local state manager."""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data.json"


def emit(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def load_state() -> dict[str, Any]:
    if not DATA_PATH.exists():
        raise SystemExit("data.json 不存在")
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any]) -> None:
    DATA_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def profile(state: dict[str, Any]) -> dict[str, Any]:
    return state["profile"]


def tzinfo(state: dict[str, Any]):
    tz_name = profile(state).get("timezone", "Asia/Shanghai")
    if ZoneInfo is None:
        return None
    return ZoneInfo(tz_name)


def now_local(state: dict[str, Any], override: str | None = None) -> datetime:
    if override:
        dt = datetime.fromisoformat(override)
        return dt if dt.tzinfo else dt.replace(tzinfo=tzinfo(state))
    return datetime.now(tzinfo(state))


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def fmt_ts(value: datetime | None) -> str | None:
    return value.isoformat(timespec="seconds") if value else None


def ensure_daily(state: dict[str, Any], now: datetime) -> None:
    daily = state["daily"]
    today = now.date().isoformat()
    stored_date = daily.get("date")
    if stored_date == today:
        return
    if stored_date:
        archive = {
            "date": stored_date,
            "total_ml": daily.get("today_total_ml", 0),
            "events_count": len(daily.get("events", [])),
            "last_drink_at": daily.get("last_drink_at"),
        }
        history = state.setdefault("history", [])
        history = [item for item in history if item.get("date") != stored_date]
        history.append(archive)
        history.sort(key=lambda item: item["date"])
        state["history"] = history[-30:]
    goal_ml = daily.get("goal_ml") or profile(state).get("goal_ml", 2000)
    state["daily"] = {
        "date": today,
        "today_total_ml": 0,
        "goal_ml": goal_ml,
        "last_drink_at": None,
        "last_prompt_at": None,
        "last_prompt_kind": None,
        "defer_until": None,
        "cooldown_until": None,
        "standalone_prompts_today": 0,
        "contextual_prompts_today": 0,
        "events": [],
    }


def in_silent_hours(state: dict[str, Any], now: datetime) -> bool:
    hours = profile(state).get("silent_hours", {})
    start = hours.get("start", "23:00")
    end = hours.get("end", "09:00")
    start_h, start_m = map(int, start.split(":"))
    end_h, end_m = map(int, end.split(":"))
    current_minutes = now.hour * 60 + now.minute
    start_minutes = start_h * 60 + start_m
    end_minutes = end_h * 60 + end_m
    if start_minutes < end_minutes:
        return start_minutes <= current_minutes < end_minutes
    return current_minutes >= start_minutes or current_minutes < end_minutes


def minutes_since(value: datetime | None, now: datetime) -> int | None:
    if value is None:
        return None
    return max(int((now - value).total_seconds() // 60), 0)


@dataclass
class CheckResult:
    should_prompt: bool
    reason: str
    mode: str
    suggested_prompt: str | None


def progress_percent(today_total: int, goal_ml: int) -> int:
    if goal_ml <= 0:
        return 0
    return int((today_total / goal_ml) * 100)


def classify_stage(
    state: dict[str, Any],
    context: str,
    now: datetime,
    gap: int | None,
) -> tuple[str, str]:
    daily = state["daily"]
    prof = profile(state)
    today_total = daily.get("today_total_ml", 0)
    goal_ml = daily.get("goal_ml") or prof.get("goal_ml", 2000)
    remaining = max(goal_ml - today_total, 0)
    percent = progress_percent(today_total, goal_ml)
    last_prompt_at = parse_ts(daily.get("last_prompt_at"))
    minutes_since_prompt = minutes_since(last_prompt_at, now)
    threshold = prof.get("drink_gap_minutes", 90) if context == "contextual" else prof.get("standalone_gap_minutes", 150)
    cup_ml = prof.get("cup_ml", 250)

    if today_total <= 0:
        if now.hour >= 11:
            return "behind_schedule", "no_record_after_11"
        return "first_cup", "day_not_started"
    if remaining <= cup_ml and now.hour >= 18:
        return "wrap_up", "close_to_goal"
    if minutes_since_prompt is not None and gap is not None and gap >= threshold + 45 and minutes_since_prompt >= prof.get("prompt_cooldown_minutes", 120):
        return "resume", "back_after_gap"
    if percent < 25 and now.hour >= 14:
        return "behind_schedule", "progress_lagging"
    return "in_progress", "gap_over_threshold"


def stage_prompt_pool(stage: str, context: str) -> list[str]:
    if context == "contextual":
        return [
            "顺便问一句，你刚刚有补水吗？",
            "学习这会儿也别忘了喝口水，要不要我顺手帮你记一下？",
            "对了，休息的时候可以一起补点水。你要是喝了我就记上。",
            "这一轮结束顺带确认下，你刚刚喝水了吗？",
            "我顺手关心一句：刚刚这段时间有补水吗？",
            "别的都先不展开，只插一句：这会儿有喝水的话我帮你记一下。",
        ]
    anchor_pools = {
        "first_cup": [
            "给今天开个张，第一口水下肚，整个人都醒了。",
            "睡醒先润一下，比咖啡更能叫醒你的灵魂。",
            "还没打算变身仙人掌吧？先喝一杯垫垫底。",
            "晨起第一杯，喝完感觉每个细胞都在舒展。",
            "新的一天，先去跟水杯打个招呼。",
        ],
        "behind_schedule": [
            "再不喝水，下午直接送博物馆当木乃伊。",
            "进度条还是 0，再不补水，大脑要宕机了。",
            "哪怕是为了证明你不是一株仙人掌，也该去跟水杯打个招呼了。",
            "最难的一步是拿起杯子。只要杯子到了嘴边，剩下的其实也就那么回事。",
            "别等身体发信号，主动出击才够酷。现在补一口，你会发现接下来的路走得轻快多了。",
        ],
        "in_progress": [
            "这会儿是不是忙得还没顾上喝水？深圳这天气燥得嘴唇都要抗议了。",
            "进度不错，说明你还没把自己忘了。再顺手补一口，今天的状态就稳了。",
            "再喝一杯水，你就是今天最会关照自己的那个。",
            "看来你还没忙丢，顺手补一口水，效率翻倍。",
        ],
        "wrap_up": [
            "下午好，最后这几口喝完就圆满了，省得晚上口渴还得爬起来找水。",
            "今天的进度还不错。最后这杯干了，给今天画个漂亮的句号。",
            "提前存点水额度，晚上睡觉才踏实。",
            "喝完这杯水就全勤收工。",
        ],
        "resume": [
            "刚才那是忙到隐身了？回来就好，现在续上一口就行，原地复活。",
            "忘了就忘了，别有压力。给水杯一个表现的机会。",
        ],
    }
    creative_pools = {
        "first_cup": [
            "先让水杯今天别失业，喝一口，整个人上线会快很多。",
            "这会儿先补点水，脑子和嗓子都能少受点委屈。",
        ],
        "behind_schedule": [
            "今天这补水进度有点想装死了，再不拉它一把，下午真容易蔫。",
            "水杯都快等成望夫石了，你去碰它一下，今天还能救回来。",
            "距离上次喝水好像过去很久了，进度条还是一动不动哦。",
            "系统检测到你这会儿极度缺水，如果再不喝，我的算法都要替你报警了。",
        ],
        "in_progress": [
            "你今天其实没掉线，再补一口，状态会更像个正常运转的人类。",
            "这会儿补点水很值，脑子不卡顿，人也没那么干巴。",
            "就差一点点，顺手拿起杯子，打乱一下久坐的僵硬节奏吧。",
        ],
        "wrap_up": [
            "今天已经走到收官段了，顺手补这一口，晚上会舒服很多。",
            "尾巴已经不长了，这杯补完，今天这局就能体面收工。",
            "马上大功告成，喝完就可以骄傲地给自己打个勾了。",
        ],
        "resume": [
            "中间掉了一拍没事，现在把这口接上，节奏就又回来了。",
            "刚刚那段算临时失联，现在人回来了，水也顺手续上。",
            "失踪人口回归，第一件事当然是先喝口水压压惊。",
        ],
    }
    return anchor_pools[stage] + creative_pools[stage]


def progress_context(state: dict[str, Any], stage: str, now: datetime, gap: int | None) -> str:
    daily = state["daily"]
    prof = profile(state)
    today_total = daily.get("today_total_ml", 0)
    goal_ml = daily.get("goal_ml") or prof.get("goal_ml", 2000)
    remaining = max(goal_ml - today_total, 0)
    percent = progress_percent(today_total, goal_ml)
    options = [""]
    if stage == "behind_schedule":
        options += [
            f"已经 {now.hour}:{now.minute:02d} 了。",
            f"你现在才喝到 {today_total}ml。" if today_total > 0 else "",
        ]
    elif stage == "in_progress":
        options += [
            f"你现在大概有 {today_total}ml 打底了。",
            f"离今天的量还差 {remaining}ml 左右。",
            f"今天大概走到 {percent}% 了。",
        ]
    elif stage == "wrap_up":
        options += [
            f"离收工大概还差 {remaining}ml。",
            f"这会儿已经 {now.hour}:{now.minute:02d} 了。",
        ]
    elif stage == "resume":
        options += [
            f"你现在有 {today_total}ml 在身上了。",
            f"离上次喝水已经差不多 {gap} 分钟了。" if gap is not None else "",
        ]
    else:
        options += [
            f"现在这个点喝一口正合适。",
        ]
    options = [item for item in options if item]
    return options[(today_total + now.hour + remaining) % len(options)]


def choose_prompt(state: dict[str, Any], context: str, stage: str, now: datetime, gap: int | None) -> str:
    pool = stage_prompt_pool(stage, context)
    base = random.choice(pool)
    if context == "contextual":
        return base
    suffix = progress_context(state, stage, now, gap)
    return f"{base} {suffix}".strip() if suffix else base


def choose_log_reply(state: dict[str, Any], amount: int) -> str:
    daily = state["daily"]
    total = daily.get("today_total_ml", 0)
    cup_ml = profile(state).get("cup_ml", 250)
    if amount <= 0:
        return "记上了。"
    if amount < cup_ml:
        pool = [
            "收到，先润一口也算数。",
            "记上了，水杯刚刚完成了一次有效出勤。",
            "好，这一口没白喝。",
        ]
    elif amount <= cup_ml:
        pool = [
            "好，这杯记上了，今天算是稳稳续了一格。",
            "收到，这杯水已经替你签到。",
            "记好了，这一杯下去状态会顺一点。",
        ]
    else:
        pool = [
            "这波补水很可以，已经帮你记上了。",
            "收到，这一大口算有效回血，已经记上。",
            "记好了，这杯下去水杯今天算干了件正事。",
        ]
    return random.choice(pool)

def calculate_dynamic_cooldown(state: dict[str, Any], now: datetime, action: str = "prompt") -> int:
    daily = state["daily"]
    prof = profile(state)
    today_total = daily.get("today_total_ml", 0)
    goal_ml = daily.get("goal_ml") or prof.get("goal_ml", 2000)
    
    hours = prof.get("silent_hours", {})
    end_silent = hours.get("end", "09:00")
    end_h, end_m = map(int, end_silent.split(":"))
    wake_hour = end_h + (end_m / 60)
    
    current_hour = now.hour + (now.minute / 60)
    if current_hour < wake_hour:
        current_hour += 24
    
    active_elapsed = max(current_hour - wake_hour, 0.1)
    expected_percent = min(active_elapsed / 14.0, 1.0)
    actual_percent = today_total / goal_ml if goal_ml > 0 else 0
    
    lag_percent = expected_percent - actual_percent
    
    if action == "prompt":
        last_drink_at = parse_ts(daily.get("last_drink_at"))
        gap = minutes_since(last_drink_at, now) if last_drink_at else 999
        if lag_percent > 0.3 or gap > 120:
            return 30
        elif lag_percent > 0.1:
            return 60
        else:
            return 120
    else:
        if lag_percent > 0.2:
            return 60
        return 90


def run_check(state: dict[str, Any], now: datetime, context: str) -> dict[str, Any]:
    ensure_daily(state, now)
    daily = state["daily"]
    prof = profile(state)
    if in_silent_hours(state, now):
        result = CheckResult(False, "silent_hours", "none", None)
    else:
        defer_until = parse_ts(daily.get("defer_until"))
        cooldown_until = parse_ts(daily.get("cooldown_until"))
        last_drink_at = parse_ts(daily.get("last_drink_at"))
        standalone_count = daily.get("standalone_prompts_today", 0)
        if context == "contextual":
            threshold = prof.get("drink_gap_minutes", 90)
        else:
            today_total = daily.get("today_total_ml", 0)
            goal_ml = daily.get("goal_ml") or prof.get("goal_ml", 2000)
            if goal_ml > 0 and (today_total / goal_ml) < 0.3 and now.hour >= 14:
                threshold = 60
            else:
                threshold = prof.get("standalone_gap_minutes", 90)
        if defer_until and now < defer_until:
            result = CheckResult(False, "deferred", "none", None)
        elif cooldown_until and now < cooldown_until:
            result = CheckResult(False, "cooldown", "none", None)
        elif context == "standalone" and standalone_count >= prof.get("standalone_prompt_limit", 5):
            result = CheckResult(False, "standalone_limit", "none", None)
        else:
            gap = minutes_since(last_drink_at, now)
            if gap is None:
                stage, reason = classify_stage(state, context, now, gap)
                result = CheckResult(True, reason, context, choose_prompt(state, context, stage, now, gap))
            elif gap < threshold:
                result = CheckResult(False, "recently_drank", "none", None)
            else:
                stage, reason = classify_stage(state, context, now, gap)
                result = CheckResult(True, reason, context, choose_prompt(state, context, stage, now, gap))
    payload = {
        "should_prompt": result.should_prompt,
        "mode": result.mode,
        "reason": result.reason,
        "suggested_prompt": result.suggested_prompt,
        "today_total_ml": daily.get("today_total_ml", 0),
        "goal_ml": daily.get("goal_ml") or prof.get("goal_ml", 2000),
        "remaining_ml": max((daily.get("goal_ml") or prof.get("goal_ml", 2000)) - daily.get("today_total_ml", 0), 0),
        "minutes_since_last_drink": minutes_since(parse_ts(daily.get("last_drink_at")), now),
        "standalone_prompts_today": daily.get("standalone_prompts_today", 0),
        "contextual_prompts_today": daily.get("contextual_prompts_today", 0),
        "defer_until": daily.get("defer_until"),
        "cooldown_until": daily.get("cooldown_until"),
        "last_drink_at": daily.get("last_drink_at"),
    }
    save_state(state)
    return payload


def cmd_check(args: argparse.Namespace) -> int:
    state = load_state()
    now = now_local(state, args.now)
    payload = run_check(state, now, args.context)
    return emit(payload)


def cmd_log(args: argparse.Namespace) -> int:
    state = load_state()
    now = now_local(state, args.now)
    ensure_daily(state, now)
    daily = state["daily"]
    prof = profile(state)
    amount = args.amount if args.amount is not None else prof.get("cup_ml", 250)
    amount = max(int(amount), 0)
    daily["today_total_ml"] = daily.get("today_total_ml", 0) + amount
    daily["last_drink_at"] = fmt_ts(now)
    daily["defer_until"] = None
    daily["cooldown_until"] = fmt_ts(now + timedelta(minutes=calculate_dynamic_cooldown(state, now, "drink")))
    daily.setdefault("events", []).append(
        {
            "time": fmt_ts(now),
            "amount_ml": amount,
            "source": args.source,
        }
    )
    save_state(state)
    return emit(
        {
            "ok": True,
            "logged_ml": amount,
            "suggested_reply": choose_log_reply(state, amount),
        }
    )


def cmd_defer(args: argparse.Namespace) -> int:
    state = load_state()
    now = now_local(state, args.now)
    ensure_daily(state, now)
    minutes = int(args.minutes or profile(state).get("default_defer_minutes", 25))
    until = now + timedelta(minutes=minutes)
    daily = state["daily"]
    daily["defer_until"] = fmt_ts(until)
    save_state(state)
    return emit({"ok": True, "defer_until": daily["defer_until"], "minutes": minutes})


def cmd_mark_prompt(args: argparse.Namespace) -> int:
    state = load_state()
    now = now_local(state, args.now)
    ensure_daily(state, now)
    daily = state["daily"]
    prof = profile(state)
    kind = args.kind
    daily["last_prompt_at"] = fmt_ts(now)
    daily["last_prompt_kind"] = kind
    daily["cooldown_until"] = fmt_ts(now + timedelta(minutes=calculate_dynamic_cooldown(state, now, "prompt")))
    if kind == "standalone":
        daily["standalone_prompts_today"] = daily.get("standalone_prompts_today", 0) + 1
    else:
        daily["contextual_prompts_today"] = daily.get("contextual_prompts_today", 0) + 1
    save_state(state)
    return emit(
        {
            "ok": True,
            "kind": kind,
            "last_prompt_at": daily["last_prompt_at"],
            "cooldown_until": daily["cooldown_until"],
            "standalone_prompts_today": daily.get("standalone_prompts_today", 0),
            "contextual_prompts_today": daily.get("contextual_prompts_today", 0),
        }
    )


def cmd_today(args: argparse.Namespace) -> int:
    state = load_state()
    now = now_local(state, args.now)
    ensure_daily(state, now)
    daily = state["daily"]
    prof = profile(state)
    return emit(
        {
            "date": daily["date"],
            "today_total_ml": daily.get("today_total_ml", 0),
            "goal_ml": daily.get("goal_ml") or prof.get("goal_ml", 2000),
            "remaining_ml": max((daily.get("goal_ml") or prof.get("goal_ml", 2000)) - daily.get("today_total_ml", 0), 0),
            "last_drink_at": daily.get("last_drink_at"),
            "events_count": len(daily.get("events", [])),
            "standalone_prompts_today": daily.get("standalone_prompts_today", 0),
            "contextual_prompts_today": daily.get("contextual_prompts_today", 0),
        }
    )


def cmd_week(args: argparse.Namespace) -> int:
    state = load_state()
    now = now_local(state, args.now)
    ensure_daily(state, now)
    rows = list(state.get("history", []))
    rows = [row for row in rows if row.get("date")] + [
        {
            "date": state["daily"]["date"],
            "total_ml": state["daily"].get("today_total_ml", 0),
            "events_count": len(state["daily"].get("events", [])),
            "last_drink_at": state["daily"].get("last_drink_at"),
        }
    ]
    rows.sort(key=lambda item: item["date"])
    rows = rows[-7:]
    total = sum(int(item.get("total_ml", 0)) for item in rows)
    average = int(total / len(rows)) if rows else 0
    return emit({"days": rows, "weekly_total_ml": total, "daily_average_ml": average})


def cmd_status(args: argparse.Namespace) -> int:
    state = load_state()
    now = now_local(state, args.now)
    ensure_daily(state, now)
    daily = state["daily"]
    payload = {
        "profile": state["profile"],
        "daily": daily,
        "minutes_since_last_drink": minutes_since(parse_ts(daily.get("last_drink_at")), now),
        "minutes_since_last_prompt": minutes_since(parse_ts(daily.get("last_prompt_at")), now),
    }
    save_state(state)
    return emit(payload)


def cmd_set_goal(args: argparse.Namespace) -> int:
    state = load_state()
    now = now_local(state, args.now)
    ensure_daily(state, now)
    amount = max(int(args.amount), 0)
    state["profile"]["goal_ml"] = amount
    state["daily"]["goal_ml"] = amount
    save_state(state)
    return emit({"ok": True, "goal_ml": amount})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hydration heartbeat local manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check")
    p.add_argument("--context", choices=("standalone", "contextual"), default="standalone")
    p.add_argument("--now")
    p.set_defaults(handler=cmd_check)

    p = sub.add_parser("log")
    p.add_argument("amount", nargs="?", type=int)
    p.add_argument("--source", default="user")
    p.add_argument("--now")
    p.set_defaults(handler=cmd_log)

    p = sub.add_parser("defer")
    p.add_argument("minutes", nargs="?", type=int)
    p.add_argument("--now")
    p.set_defaults(handler=cmd_defer)

    p = sub.add_parser("mark-prompt")
    p.add_argument("--kind", choices=("standalone", "contextual"), default="standalone")
    p.add_argument("--now")
    p.set_defaults(handler=cmd_mark_prompt)

    p = sub.add_parser("today")
    p.add_argument("--now")
    p.set_defaults(handler=cmd_today)

    p = sub.add_parser("week")
    p.add_argument("--now")
    p.set_defaults(handler=cmd_week)

    p = sub.add_parser("status")
    p.add_argument("--now")
    p.set_defaults(handler=cmd_status)

    p = sub.add_parser("set-goal")
    p.add_argument("amount", type=int)
    p.add_argument("--now")
    p.set_defaults(handler=cmd_set_goal)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
