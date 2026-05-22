#!/usr/bin/env python3
"""Integration between OpenClaw heartbeat and hydro-heartbeat."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def check_and_prompt_hydration():
    """Check hydration status and send prompt if needed."""
    try:
        # Check hydro-heartbeat status
        result = subprocess.run([
            'python3', 'hydro-heartbeat/scripts/manage.py', 'check', '--context', 'standalone'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        if result.returncode != 0:
            print(f"Hydro-heartbeat check failed: {result.stderr}")
            return False
            
        status = json.loads(result.stdout)
        
        if status.get('should_prompt', False):
            # Send hydration reminder
            prompt_text = status.get('suggested_prompt', '该喝水了！')
            total_ml = status.get('today_total_ml', 0)
            goal_ml = status.get('goal_ml', 1500)
            remaining_ml = status.get('remaining_ml', 1500)
            
            message = f"💧 {prompt_text}\n\n今日已饮水: {total_ml}ml / {goal_ml}ml\n还需饮水: {remaining_ml}ml"
            
            # Send message via OpenClaw
            send_result = subprocess.run([
                'openclaw', 'message', 'send', 
                '--target', 'o9cq80y6elATkZb3OAurZezVak0Q@im.wechat'
            ], input=message, text=True, capture_output=True)
            
            if send_result.returncode == 0:
                print(f"Hydration reminder sent successfully at {datetime.now()}")
                return True
            else:
                print(f"Failed to send message: {send_result.stderr}")
                return False
        else:
            print(f"No hydration prompt needed at {datetime.now()}")
            return False
            
    except Exception as e:
        print(f"Error in hydration check: {e}")
        return False

if __name__ == '__main__':
    check_and_prompt_hydration()