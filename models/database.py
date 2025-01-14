import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_file="tasks.db"):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # 创建任务表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            priority TEXT,
            deadline TEXT,
            progress INTEGER DEFAULT 0,
            tags TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建子任务表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            target_time INTEGER,
            completed_time INTEGER DEFAULT 0,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_task(self, task_data):
        """添加新任务"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO tasks (name, priority, deadline, tags)
            VALUES (?, ?, ?, ?)
            ''', (task_data["name"].strip(), 
                  task_data["priority"], 
                  task_data["deadline"],
                  task_data.get("tags", "")))
            
            task_id = cursor.lastrowid
            conn.commit()
            print(f"成功添加任务: {task_data['name']}")
            return task_id
            
        except sqlite3.Error as e:
            print(f"数据库错误: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def get_all_tasks(self):
        """获取所有任务"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
            tasks = cursor.fetchall()
            return tasks
            
        except sqlite3.Error as e:
            print(f"获取任务列表错误: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
