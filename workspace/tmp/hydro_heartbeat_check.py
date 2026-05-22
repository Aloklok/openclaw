#!/usr/bin/env python3
"""Hydro heartbeat checker that runs periodically."""

import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

def check_hydration():
    """Check hydration and send reminder if needed."""
    try:
        # Check hydro-heartbeat status
        result = subprocess.run([
            'python3', 'skills/hydro-heartbeat/scripts/manage.py', 'check', '--context', 'standalone'
        ], capture_output=True, text=True, cwd=Path.home() / '.openclaw' / 'workspace')
        
        if result.returncode != 0:
            print(f"Hydro-heartbeat check failed: {result.stderr}")
            return False
            
        status = json.loads(result.stdout)
        
        if status.get('should_prompt', False):
            prompt_text = status.get('suggested_prompt', '该喝水了！')
            total_ml = status.get('today_total_ml', 0)
            goal_ml = status.get('goal_ml', 1500)
            remaining_ml = status.get('remaining_ml', 1500)
            
            message = f"💧 {prompt_text}\n\n今日已饮水: {total_ml}ml / {goal_ml}ml\n还需饮水: {remaining_ml}ml"
            
            # Send message using message tool
            try:
                subprocess.run([
                    'openclaw', 'message', 'send', 
                    '--target', 'o9cq80y6elATkZb3OAurZezVak0Q@im.wechat'
                ], input=message, text=True, capture_output=True, timeout=30)
                
                print(f"Hydration reminder sent at {datetime.now()}")
                
                # Mark prompt as sent
                subprocess.run([
                    'python3', 'skills/hydro-heartbeat/scripts/manage.py', 'mark-prompt', '--kind', 'standalone'
                ], cwd=Path.home() / '.openclaw' / 'workspace', capture_output=True)
                
                return True
            except Exception as e:
                print(f"Failed to send message: {e}")
                return False
        else:
            print(f"No hydration prompt needed at {datetime.now()}")
            return False
            
    except Exception as e:
        print(f"Error in hydration check: {e}")
        return False

if __name__ == '__main__':
    print(f"Starting hydro heartbeat check at {datetime.now()}")
    check_hydration()