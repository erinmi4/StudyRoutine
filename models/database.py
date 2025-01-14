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
