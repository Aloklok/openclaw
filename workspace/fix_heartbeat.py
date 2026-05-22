#!/usr/bin/env python3
"""
修复 Heartbeat 的消息发送功能
"""

import json
import subprocess
import sys
from pathlib import Path

def run_hydro_check():
    """运行 hydro-heartbeat 检查"""
    try:
        result = subprocess.run(
            ["python3", "skills/hydro-heartbeat/scripts/manage.py", "check", "--context", "standalone"],
            capture_output=True,
            text=True,
            cwd="/home/node/.openclaw/workspace"
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error running hydro check: {e}")
        return None

def send_message(content):
    """发送消息到微信"""
    try:
        # 使用 OpenClaw 的 message 工具发送消息
        import os
        os.system(f'cd /home/node/.openclaw/workspace && python3 -c "'
                  f'import sys; '
                  f'sys.path.append(\".openclaw\"); '
                  f'from openclaw.tools.message import message; '
                  f'message.send(\"openclaw-weixin\", \"o9cq80y6elATkZb3OAurZezVak0Q@im.wechat\", \"{content}\")"')
    except Exception as e:
        print(f"Error sending message: {e}")

def mark_prompt():
    """记录提醒"""
    try:
        subprocess.run(
            ["python3", "skills/hydro-heartbeat/scripts/manage.py", "mark-prompt", "--kind", "standalone"],
            cwd="/home/node/.openclaw/workspace"
        )
    except Exception as e:
        print(f"Error marking prompt: {e}")

def main():
    """主函数"""
    # 运行检查
    result = run_hydro_check()
    if not result:
        return
    
    # 检查是否需要提醒
    if result.get("should_prompt", False):
        suggested_prompt = result.get("suggested_prompt")
        if suggested_prompt:
            print(f"发送喝水提醒: {suggested_prompt}")
            send_message(suggested_prompt)
            mark_prompt()
        else:
            print("需要提醒但没有建议文案")
    else:
        print("不需要提醒")

if __name__ == "__main__":
    main()