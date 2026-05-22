#!/usr/bin/env python3
"""
测试 Heartbeat 消息发送功能
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

def mark_prompt():
    """记录提醒"""
    try:
        subprocess.run(
            ["python3", "skills/hydro-heartbeat/scripts/manage.py", "mark-prompt", "--kind", "standalone"],
            cwd="/home/node/.openclaw/workspace"
        )
        print("已记录提醒")
    except Exception as e:
        print(f"Error marking prompt: {e}")

def main():
    """主函数 - 模拟 Heartbeat 执行流程"""
    print("开始 Heartbeat 检查...")
    
    # 运行检查
    result = run_hydro_check()
    if not result:
        print("检查失败")
        return
    
    print(f"检查结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 检查是否需要提醒
    if result.get("should_prompt", False):
        suggested_prompt = result.get("suggested_prompt")
        if suggested_prompt:
            print(f"\n📢 检测到需要提醒: {suggested_prompt}")
            print("\n🔄 现在应该发送消息到微信...")
            
            # 这里应该是 Heartbeat 发送消息的逻辑
            # 但由于我们在测试环境，先打印出来
            print(f"📱 应该发送的消息: {suggested_prompt}")
            
            # 记录提醒
            mark_prompt()
            print("✅ 测试完成：Heartbeat 检测到需要提醒并生成了文案")
        else:
            print("❌ 需要提醒但没有建议文案")
    else:
        print("ℹ️ 不需要提醒")

if __name__ == "__main__":
    main()