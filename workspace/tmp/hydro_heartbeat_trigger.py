#!/usr/bin/env python3
"""Create a persistent hydro heartbeat using OpenClaw system events."""

import subprocess
import json
from datetime import datetime

def create_hydro_heartbeat():
    """Create a system event that triggers hydro check."""
    
    # Create a system event that will be processed by the agent
    event_text = """💧 喝水心跳检查
    
请执行以下操作：
1. 检查hydro-heartbeat状态：python3 skills/hydro-heartbeat/scripts/manage.py check --context standalone
2. 如果需要提醒，发送微信消息
3. 完成后回复 NO_REPLY

这是自动心跳检查，每30分钟执行一次。"""
    
    try:
        result = subprocess.run([
            'openclaw', 'system', 'event',
            '--mode', 'next-heartbeat',
            '--text', event_text,
            '--timeout', '60000'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"Hydro heartbeat event created at {datetime.now()}")
            return True
        else:
            print(f"Failed to create hydro heartbeat: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error creating hydro heartbeat: {e}")
        return False

if __name__ == '__main__':
    print("Setting up hydro heartbeat monitoring...")
    success = create_hydro_heartbeat()
    
    if success:
        print("✅ Hydro heartbeat has been restored!")
        print("📱 You will now receive hydration reminders every 30 minutes during active hours")
        print("⏰ Reminders are paused during 23:00-08:00 silent hours")
    else:
        print("❌ Failed to setup hydro heartbeat")