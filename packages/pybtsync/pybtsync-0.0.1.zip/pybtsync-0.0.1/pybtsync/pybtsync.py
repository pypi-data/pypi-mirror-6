# -*- coding: utf-8 -*-

'''
Created on Nov 19, 2013

@author: Mac
'''

import json
import platform
import tempfile
import os
import random
import string
import uuid
import subprocess
import io
import tarfile

import requests
try:
    import pydevd
except:
    pass


class BTSync_process():
    def __init__(self, api_key=None,
                 btsync_exec_folder=None, btsync_app=None, 
                 address='127.0.0.1', port=None, login=None, password=None):
        if api_key is None:
            api_key = os.environ['PYBTSYNC_APIKEY']
        if btsync_exec_folder is None:
            self.btsync_exec_folder = tempfile.mkdtemp()
        if btsync_app is None:
                if btsync_exec_folder is None:
                    btsync_app = self.download_btsync(self.btsync_exec_folder)
                else:
                    self.btsync_exec_folder = btsync_exec_folder
                    btsync_app = self.download_btsync(btsync_exec_folder)
        
        [btsync_conf_file,
         address, port, login, password] = self.write_conf_file(self.btsync_exec_folder,
                                                                address, port, login, password, api_key)
        self.__address = address
        self.__port = port
        self.__login = login
        self.__password = password
        
        self.start_process(btsync_app, btsync_conf_file)

    def BTSync(self):
        return BTSync(self.__address, self.__port, self.__login, self.__password)

    def __del__(self): #probably remove this
        self.clean_up()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.clean_up()
        
    
    @classmethod  #TODO: This will not work if config file has comments   
    def use_conf_file(cls, btsync_conf_file,
                      btsync_app=None, btsync_exec_folder=None):
        with open(btsync_conf_file, 'r') as btsync_conf:
            content = btsync_conf.read()
        content_json = ''.join(content.split('\n'))
        content_dict = json.loads(content_json) #TODO: use the attribute trick
        return cls(content_dict['webui']['api_key'],
                   btsync_app=btsync_app,
                   address=content_dict['webui']['address'],
                   port=content_dict['webui']['port'],
                   login=content_dict['webui']['login'],
                   password=content_dict['webui']['password'])

    def clean_up(self):
        if self.btsync_process.poll() is None:
            self.btsync_process.kill()
        #TODO: clean temporary folder

    def download_btsync(self, btsync_dir):
        platform_data = {'Windows' : 
                                    {'download_URL' : 'http://download-lb.utorrent.com/endpoint/btsync/os/windows/track/stable',
                                     'file_name' : 'BTSync.exe'},
                         'Linux' :
                                    {'download_URL' : 'http://download-lb.utorrent.com/endpoint/btsync/os/linux-x64/track/stable',
                                     'file_name' : 'btsync'}
                         }
        self._platform_data = platform_data
        try:
            download_url = platform_data[platform.system()]['download_URL']
            file_name = platform_data[platform.system()]['file_name']
        except:
            raise(NotImplementedError)
        
        response = requests.get(download_url)
        if not response.status_code == requests.codes.ok:  # @UndefinedVariable
            response.raise_for_status()
        
        btsync_name = os.path.join(btsync_dir, file_name)
        if platform.system() == 'Windows':
            with open(btsync_name,'wb') as btsync:
                btsync.write(response.content)
        else:
            tar_gz = io.BytesIO()
            tar_gz.write(response.content)
            tar_gz.seek(0)
            with tarfile.open(mode='r:gz', fileobj=tar_gz) as btsync:
                btsync.extractall(btsync_dir)
            
        return btsync_name 

    def write_conf_file(self, btsync_dir, address, port, login, password, api_key):
        btsyn_conf_file_content = string.Template("""{
        "storage_path" : "$btsync_dir",
        "use_gui" : false,
        "webui" : {
            "listen" : "$address:$port",
            "login" : "$login",
            "password" : "$password",
            "api_key" : "$api_key"
        }
        }""")
        if port is None:
            port = str(random.randrange(10000, 65000 ,1)) #http://www.bittorrent.com/help/manual/appendixa0204
        if login is None:
            login = uuid.uuid4()
        if password is None:
            password = uuid.uuid4()
       
        btsync_dir_for_btsync = btsync_dir.replace("\\","//")
        
        btsync_conf_file = os.path.join(btsync_dir, 'sync.conf')
        with open(btsync_conf_file,'wb') as btsync_conf:
            btsync_conf.write( btsyn_conf_file_content.substitute( btsync_dir=btsync_dir_for_btsync,
                                                                   address=address,
                                                                   port=port,
                                                                   login=login,
                                                                   password=password,
                                                                   api_key=api_key ).encode('utf-8'))
        return btsync_conf_file, address, port, login, password
    
    def start_process(self, btsync_app, btsync_conf_file):
        if platform.system() == 'Windows': 
            self.btsync_process = subprocess.Popen([btsync_app, '/config', btsync_conf_file])
        else:
            self.btsync_process = subprocess.Popen([btsync_app, '--config', btsync_conf_file])
        #TODO: put some check if it started correctly

class BTSync():
    def __init__(self, address, port, login, password):
        self._address = address
        self._port = port
        self._login = login
        self._password = password
        self.preferences = BTSync_preferences(address, port, login, password)

    @property        
    def folders(self):
        return self._request_function('get_folders')
        
    def add_folder(self, folder_path, secret=None, selective_sync=0):
        arguments = 'dir=' + folder_path
        if secret is not None:
            arguments = arguments + '&secret=' + secret
        if selective_sync != 0:
            arguments = arguments + '&selective_sync=' + str(selective_sync)
        return self._request_function('add_folder', arguments = arguments)
        
    def remove_folder(self, secret):
        arguments = 'secret=' + secret
        return self._request_function('remove_folder', arguments = arguments)
        
    def get_files(self, secret, path=None):
        arguments = 'secret=' + secret
        if path is not None:
            arguments = arguments + '&path=' + path
        return self._request_function('get_files', arguments = arguments)
    
    def set_file_prefs(self, secret, path, download): #relative path
        arguments = 'secret=' + secret
        arguments = arguments + '&path=' + path
        arguments = arguments + '&download=' + str(download)
        return self._request_function('set_file_prefs', arguments = arguments)
        
    def get_folder_peers(self, secret):
        arguments = 'secret=' + secret
        return self._request_function('get_folder_peers', arguments = arguments)

    def get_secrets(self, secret=None): #encryption enables always
        if secret is not None:
            arguments = '&secret=' + secret
        else:
            arguments = ''
        arguments = 'type=encryption' + arguments
        return self._request_function('get_secrets', arguments = arguments)
        
    def get_folder_prefs(self, secret):
        arguments = 'secret=' + secret
        return self._request_function('get_folder_prefs', arguments = arguments)
    
    def set_folder_prefs(self, secret, param, value):
        arguments = 'secret=' + secret
        arguments = arguments + '&' + param + '=' + str(value)
        return self._request_function('set_folder_prefs', arguments = arguments)
    
    def get_folder_hosts(self, secret):
        arguments = 'secret=' + secret
        return self._request_function('get_folder_hosts', arguments = arguments)
    
    def set_folder_hosts(self, secret, hosts):
        arguments = 'secret=' + secret
        arguments = arguments + '&hosts=' + ",".join(hosts)
        return self._request_function('set_folder_hosts', arguments = arguments)
    
        
    @property
    def os(self):
        return self._request_function('get_os', key='os')

    @property
    def version(self):
        return self._request_function('get_version', key='version')

    @property
    def download_speed(self):
        return self._request_function('get_speed', key='download')    

    @property
    def upload_speed(self):
        return self._request_function('get_speed', key='upload')

    def shutdown(self):
        return self._request_function('shutdown', key='error')

    def _request_function(self, method_name, arguments='', key=None):
        URL = 'http://' + self._address + ':' + self._port +'/api?method=' + method_name + '&' + arguments
        request = requests.get(URL, auth=(self._login, self._password))
        request_data = eval(request.text)
        if key is not None:
            return request_data[key]
        return request_data

class BTSync_preferences():
    def __init__(self, address, port, login, password):
        self._address = address
        self._port = port
        self._login = login
        self._password = password
        
    def __getattr__(self, name):
        return self._request_function('set_prefs', key=name)
    
    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            self._request_function('set_prefs', arguments = name + '=' + str(value))

    def __repr__(self):
        return json.dumps(self._request_function('set_prefs'), indent=4, sort_keys=True)

    def __dir__(self): #dirty magic to make auto-complete work
        if False:
            self.device_name = None
            self.disk_low_priority = None
            self.download_limit = None
            self.folder_rescan_interval = None
            self.lan_encrypt_data = None
            self.lan_use_tcp = None
            self.lang = None
            self.listening_port = None
            self.max_file_size_diff_for_patching = None
            self.max_file_size_for_versioning = None
            self.rate_limit_local_peers = None
            self.send_buf_size = None
            self.sync_max_time_diff = None
            self.sync_trash_ttl = None
            self.upload_limit = None
            self.use_upnp = None
            self.recv_buf_size = None
        res = dir(type(self)) + list(self.__dict__.keys())
        res.extend(self._request_function('set_prefs').keys())
        return res
        
    def _request_function(self, method_name, arguments='', key=None):
        URL = 'http://' + self._address + ':' + self._port +'/api?method=' + method_name + '&' + arguments
        request = requests.get(URL, auth=(self._login, self._password))
        request_data = eval(request.text)
        if key is not None:
            return request_data[key]
        return request_data
