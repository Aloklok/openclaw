#!/usr/bin/env python3
"""Setup persistent hydro heartbeat monitoring."""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

def trigger_hydro_check():
    """Trigger hydro heartbeat check via system event."""
    try:
        # Create a system event that will trigger the agent
        result = subprocess.run([
            'openclaw', 'system', 'event', 
            '--mode', 'next-heartbeat',
            '--text', '检查喝水状态 - 运行: python3 tmp/hydro_heartbeat_check.py',
            '--timeout', '60000'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"Hydro check triggered at {datetime.now()}")
            return True
        else:
            print(f"Failed to trigger hydro check: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error triggering hydro check: {e}")
        return False

def main():
    """Main loop to trigger hydro check every 30 minutes."""
    print("Starting hydro heartbeat monitoring...")
    
    # Initial check
    trigger_hydro_check()
    
    # Schedule every 30 minutes
    while True:
        time.sleep(30 * 60)  # 30 minutes
        trigger_hydro_check()

if __name__ == '__main__':
    main()