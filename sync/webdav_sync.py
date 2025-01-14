from webdav3.client import Client
import json
import os
import time
from datetime import datetime
import logging
from PyQt6.QtCore import QObject

class WebDAVSync(QObject):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.options = {
            'webdav_hostname': '',
            'webdav_login': '',
            'webdav_password': '',
            'disable_check': True
        }
        self.client = None
        self.sync_interval = 300
        self.last_sync_time = 0
        self.logger = self._setup_logger()
        self.connected = False
        self.config_file = 'webdav_config.json'
        
    def connect(self, url, username, password):
        """Initialize WebDAV connection"""
        try:
            self.options.update({
                'webdav_hostname': url,
                'webdav_login': username,
                'webdav_password': password
            })
            self.client = Client(self.options)
            if self.client.check('/'):
                self.connected = True
                self._save_config()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            return False
            
    def _save_config(self):
        """Save WebDAV configuration to file"""
        config = {
            'url': self.options['webdav_hostname'],
            'username': self.options['webdav_login'],
            'password': self.options['webdav_password']
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
            
    def load_config(self):
        """Load WebDAV configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return self.connect(
                        config['url'],
                        config['username'],
                        config['password']
                    )
            return False
        except Exception as e:
            self.logger.error(f"Config load failed: {str(e)}")
            return False
    
    def _setup_logger(self):
        """配置日志记录器"""
        logger = logging.getLogger('webdav_sync')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('webdav_sync.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def sync_to_cloud(self, local_file):
        """将本地数据同步到WebDAV服务器"""
        try:
            if os.path.exists(local_file):
                remote_path = f'/tasks/{os.path.basename(local_file)}'
                self.client.upload_sync(remote_path=remote_path, local_path=local_file)
                self.logger.info(f"成功上传文件: {local_file}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"上传失败: {str(e)}")
            return False
    
    def sync_from_cloud(self, remote_file, local_file):
        """从WebDAV服务器同步数据到本地"""
        try:
            remote_path = f'/tasks/{remote_file}'
            if self.client.check(remote_path):
                self.client.download_sync(remote_path=remote_path, local_path=local_file)
                self.logger.info(f"成功下载文件: {remote_file}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"下载失败: {str(e)}")
            return False
    
    def auto_sync(self, local_file):
        """自动同步任务"""
        current_time = time.time()
        if current_time - self.last_sync_time > self.sync_interval:
            self.last_sync_time = current_time
            if self.sync_to_cloud(local_file):
                self.logger.info("自动同步成功")
            else:
                self.logger.warning("自动同步失败")
    
    def resolve_conflict(self, local_file, remote_file):
        """解决同步冲突"""
        try:
            # 获取本地和远程文件的修改时间
            local_mtime = os.path.getmtime(local_file)
            remote_info = self.client.info(f'/tasks/{remote_file}')
            remote_mtime = remote_info['modified']
            
            # 比较修改时间，保留最新版本
            if local_mtime > remote_mtime:
                return self.sync_to_cloud(local_file)
            else:
                return self.sync_from_cloud(remote_file, local_file)
        except Exception as e:
            self.logger.error(f"冲突解决失败: {str(e)}")
            return False
            
    def sync_tasks(self):
        """同步任务数据"""
        if not self.connected:
            self.logger.warning("未连接WebDAV服务器")
            return False
            
        try:
            # 导出本地任务数据
            local_tasks = self.db.export_tasks()
            temp_file = 'tasks_export.json'
            with open(temp_file, 'w') as f:
                json.dump(local_tasks, f)
                
            # 同步到云端
            if not self.sync_to_cloud(temp_file):
                return False
                
            # 检查远程是否有更新
            remote_file = 'tasks.json'
            if self.client.check(f'/tasks/{remote_file}'):
                remote_info = self.client.info(f'/tasks/{remote_file}')
                remote_mtime = remote_info['modified']
                local_mtime = os.path.getmtime(temp_file)
                
                if remote_mtime > local_mtime:
                    # 下载远程更新
                    if not self.sync_from_cloud(remote_file, temp_file):
                        return False
                        
                    # 导入远程任务数据
                    with open(temp_file, 'r') as f:
                        remote_tasks = json.load(f)
                    self.db.import_tasks(remote_tasks)
                    
            os.remove(temp_file)
            return True
            
        except Exception as e:
            self.logger.error(f"任务同步失败: {str(e)}")
            return False
            
    def start_periodic_sync(self):
        """启动定期同步"""
        if not self.connected:
            return False
            
        def sync_loop():
            while True:
                self.sync_tasks()
                time.sleep(self.sync_interval)
                
        import threading
        sync_thread = threading.Thread(target=sync_loop, daemon=True)
        sync_thread.start()
        return True
