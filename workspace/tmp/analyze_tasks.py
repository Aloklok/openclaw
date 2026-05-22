#!/usr/bin/env python3
import json
from datetime import datetime, timedelta
import sys

def analyze_tasks():
    # Load tasks data
    with open('/tmp/all_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tasks = data.get('tasks', [])
    current_time = datetime.now()
    
    # Find overdue tasks
    overdue_tasks = []
    upcoming_tasks = []
    
    for task in tasks:
        if task.get('status') != 0:  # Skip completed tasks
            continue
            
        due_date_str = task.get('dueDate')
        if not due_date_str:
            continue
            
        # Parse due date
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            # Convert to local timezone for comparison
            due_date = due_date.replace(tzinfo=None)
        except:
            continue
            
        task_info = {
            'id': task.get('id'),
            'title': task.get('title', 'Untitled'),
            'dueDate': due_date_str,
            'priority': task.get('priority', 0),
            'projectId': task.get('projectId'),
            'tags': task.get('tags', []),
            'days_overdue': (current_time - due_date).days if due_date < current_time else 0
        }
        
        if due_date < current_time:
            overdue_tasks.append(task_info)
        else:
            upcoming_tasks.append(task_info)
    
    # Sort overdue tasks by how overdue they are
    overdue_tasks.sort(key=lambda x: x['days_overdue'], reverse=True)
    
    # Sort upcoming tasks by due date
    upcoming_tasks.sort(key=lambda x: x['dueDate'])
    
    print(f"分析结果:")
    print(f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"过期任务数量: {len(overdue_tasks)}")
    print(f"未过期任务数量: {len(upcoming_tasks)}")
    print()
    
    if overdue_tasks:
        print("📅 过期任务列表:")
        for task in overdue_tasks:
            print(f"  - {task['title']} (过期 {task['days_overdue']} 天, 优先级: {task['priority']})")
        print()
    
    return overdue_tasks, upcoming_tasks

if __name__ == '__main__':
    analyze_tasks()