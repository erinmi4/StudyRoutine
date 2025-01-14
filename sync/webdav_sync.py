from webdav3.client import Client
import json
import os

class WebDAVSync:
    def __init__(self, webdav_url, username, password):
        self.options = {
            'webdav_hostname': webdav_url,
            'webdav_login': username,
            'webdav_password': password
        }
        self.client = Client(self.options)
    
    def sync_to_cloud(self, local_file):
        """将本地数据同步到WebDAV服务器"""
        if os.path.exists(local_file):
            remote_path = f'/tasks/{os.path.basename(local_file)}'
            self.client.upload_sync(remote_path=remote_path, local_path=local_file)
    
    def sync_from_cloud(self, remote_file, local_file):
        """从WebDAV服务器同步数据到本地"""
        remote_path = f'/tasks/{remote_file}'
        if self.client.check(remote_path):
            self.client.download_sync(remote_path=remote_path, local_path=local_file)
