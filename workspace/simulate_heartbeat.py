#!/usr/bin/env python3
"""
模拟 Heartbeat 执行，包含消息发送功能
"""

import json
import subprocess
import sys
import os

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
    """使用 message 工具发送消息到微信"""
    try:
        # 使用 OpenClaw 的 message 工具
        cmd = f"""
import sys
sys.path.append('/app')
from openclaw.tools.message import message
message.send("openclaw-weixin", "o9cq80y6elATkZb3OAurZezVak0Q@im.wechat", "{content}")
"""
        result = subprocess.run(
            ["python3", "-c", cmd],
            capture_output=True,
            text=True,
            cwd="/home/node/.openclaw/workspace"
        )
        if result.returncode == 0:
            print(f"✅ 消息发送成功: {content}")
        else:
            print(f"❌ 消息发送失败: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 消息发送异常: {e}")
        return False

def mark_prompt():
    """记录提醒"""
    try:
        subprocess.run(
            ["python3", "skills/hydro-heartbeat/scripts/manage.py", "mark-prompt", "--kind", "standalone"],
            cwd="/home/node/.openclaw/workspace"
        )
        print("✅ 已记录提醒")
    except Exception as e:
        print(f"❌ 记录提醒失败: {e}")

def main():
    """主函数 - 模拟 Heartbeat 执行流程"""
    print("🔄 开始模拟 Heartbeat 执行...")
    
    # 读取 HEARTBEAT.md
    try:
        with open("/home/node/.openclaw/workspace/HEARTBEAT.md", "r", encoding="utf-8") as f:
            heartbeat_content = f.read()
        print("📖 已读取 HEARTBEAT.md")
    except Exception as e:
        print(f"❌ 读取 HEARTBEAT.md 失败: {e}")
        return
    
    # 运行 hydro-heartbeat 检查
    result = run_hydro_check()
    if not result:
        print("❌ hydro-heartbeat 检查失败")
        return
    
    print(f"📊 检查结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 检查是否需要提醒
    if result.get("should_prompt", False):
        suggested_prompt = result.get("suggested_prompt")
        if suggested_prompt:
            print(f"\n📢 检测到需要提醒: {suggested_prompt}")
            
            # 发送消息到微信
            print("📱 正在发送消息到微信...")
            send_message(suggested_prompt)
            
            # 记录提醒
            mark_prompt()
            
            print("✅ Heartbeat 执行完成：已发送提醒并记录")
        else:
            print("❌ 需要提醒但没有建议文案")
    else:
        print("ℹ️ 不需要提醒，输出 HEARTBEAT_OK")
        print("HEARTBEAT_OK")

if __name__ == "__main__":
    main()