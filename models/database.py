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
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_sync_time TEXT,
            sync_status TEXT DEFAULT 'pending',
            sync_version INTEGER DEFAULT 0
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
            sync_version INTEGER DEFAULT 0,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        )
        ''')
        
        # 创建同步日志表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            sync_time TEXT DEFAULT CURRENT_TIMESTAMP,
            sync_status TEXT,
            sync_message TEXT,
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

    def delete_task(self, task_id):
        """删除任务"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 先删除子任务
            cursor.execute('DELETE FROM subtasks WHERE task_id = ?', (task_id,))
            # 再删除主任务
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"删除任务错误: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def update_task_progress(self, task_id, progress):
        """更新任务进度"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE tasks SET progress = ? WHERE id = ?
            ''', (progress, task_id))
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"更新进度错误: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def update_task(self, task_data):
        """更新任务信息"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE tasks 
            SET name = ?, priority = ?, deadline = ?
            WHERE id = ?
            ''', (task_data["name"], task_data["priority"], 
                  task_data["deadline"], task_data["id"]))
            
            conn.commit()
            print(f"成功更新任务: {task_data['name']}")
            
        except sqlite3.Error as e:
            print(f"更新任务错误: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def get_task_statistics(self):
        """获取任务统计数据"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取各种统计数据
            stats = {
                'total': cursor.execute('SELECT COUNT(*) FROM tasks').fetchone()[0],
                'completed': cursor.execute('SELECT COUNT(*) FROM tasks WHERE progress = 100').fetchone()[0],
                'in_progress': cursor.execute('SELECT COUNT(*) FROM tasks WHERE progress > 0 AND progress < 100').fetchone()[0],
                'pending': cursor.execute('SELECT COUNT(*) FROM tasks WHERE progress = 0').fetchone()[0],
                'synced': cursor.execute('SELECT COUNT(*) FROM tasks WHERE sync_status = "synced"').fetchone()[0],
                'pending_sync': cursor.execute('SELECT COUNT(*) FROM tasks WHERE sync_status = "pending"').fetchone()[0],
                'sync_errors': cursor.execute('SELECT COUNT(*) FROM sync_logs WHERE sync_status = "error"').fetchone()[0]
            }
            
            return stats
        finally:
            if conn:
                conn.close()

    def update_sync_status(self, task_id, status, message=None):
        """更新任务同步状态"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 更新任务同步状态
            cursor.execute('''
            UPDATE tasks 
            SET sync_status = ?, last_sync_time = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (status, task_id))
            
            # 记录同步日志
            if message:
                cursor.execute('''
                INSERT INTO sync_logs (task_id, sync_status, sync_message)
                VALUES (?, ?, ?)
                ''', (task_id, status, message))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新同步状态错误: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    def get_unsynced_tasks(self):
        """获取所有未同步的任务"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM tasks 
            WHERE sync_status = 'pending' 
            ORDER BY created_at DESC
            ''')
            tasks = cursor.fetchall()
            return tasks
        except sqlite3.Error as e:
            print(f"获取未同步任务错误: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()

    def increment_sync_version(self, task_id):
        """增加任务同步版本号"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE tasks 
            SET sync_version = sync_version + 1 
            WHERE id = ?
            ''', (task_id,))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"增加同步版本号错误: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()
