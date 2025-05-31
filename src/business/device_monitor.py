import requests
import random
import time
from icmplib import ping as icmp_ping # type: ignore
from pathlib import Path
from model import Device,Config,DeviceReport
import paramiko
import re

#Device surveillance component
class DeviceMonitor:
    def __init__(self, device: Device):
        self.report=DeviceReport(device)
        self.device=device
        self.previous_status=None

    def check_ping(self):
        if self.device.ip is None:
            return False
        try:
            result = icmp_ping(self.device.ip, count=self.device.ping_count, timeout=self.device.ping_timeout, privileged=False)
            return result.packets_received > 0
        except Exception as e:
            if self.previous_status is not False:
                    print(f"PING for '{self.device.name}' : exception {e}")
            return False

    def check_url(self):
        if self.device.url is None:
            return False
        i=0
        while i<self.device.http_retry:
            try:
                response = requests.get(url=self.device.url, timeout=self.device.http_timeout, verify=False,)
                return response.status_code <500
            except requests.exceptions.RequestException as e:
                if self.previous_status is not False:
                    print(f"HTTP for '{self.device.name}' : exception {e}")
                i += 1
        else:
            return False
    
    def check_ssh(self):
        if self.device.ssh_host is None or self.device.ssh_user is None or self.device.ssh_command is None or self.device.ssh_key_file is None:
            return False
        i=0
        while i<self.device.ssh_retry:
            client=None
            stdin, stdout, stderr=(None,None,None)
            try:
                if self.device.ssh_key_folder:
                    ssh_key_folder_path=Path(self.device.ssh_key_folder)
                else:
                    ssh_key_folder_path=self.device.config_folder
                if self.device.ssh_key_file:
                    ssh_key_file_path=Path(ssh_key_folder_path,self.device.ssh_key_file )
                else:
                    ssh_key_file_path=None
                client = paramiko.SSHClient()
                # automatically add host key. use with precaution.
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                if self.device.ssh_obsolete:
                    disabled_algorithms={
                        'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512'],
                        'keys': ['rsa-sha2-256', 'rsa-sha2-512'],
                        'kex': ['diffie-hellman-group-exchange-sha256'],
                        'ciphers': ['aes256-ctr', 'aes256-cbc']
                    }
                else:
                    disabled_algorithms=None
                client.connect(
                    hostname=self.device.ssh_host,
                    username=self.device.ssh_user,
                    key_filename =str(ssh_key_file_path),
                    passphrase=self.device.ssh_key_password,
                    gss_auth=False,
                    gss_kex=False,
                    compress=True,
                    allow_agent=self.device.ssh_allow_agent,
                    password=self.device.ssh_user_password,
                    disabled_algorithms=disabled_algorithms,
                    timeout=self.device.ssh_timeout
                )
                stdin, stdout, stderr = client.exec_command(self.device.ssh_command)
    
                stdout_text=stdout.read().decode()
                stderr_text=stderr.read().decode()
                text=f"{stdout_text}\n{stderr_text}"
                for pattern in self.device.ssh_pattern_required:
                    try:
                        regex = re.compile(pattern,flags=0)
                        if not regex.search(text):
                            return False
                    except re.error:
                        if self.previous_status is not False:
                            print(f"SSH for '{self.device.name}' : invalid required regex '{pattern}' Ignored")
                for pattern in self.device.ssh_pattern_forbiden:
                    try:
                        regex = re.compile(pattern,flags=0)
                        if regex.search(text):
                            return False
                    except re.error:
                        if self.previous_status is not False:
                            print(f"SSH for '{self.device.name}' : invalid forbidden regex '{pattern}' Ignored")
                return True
            except Exception as e:
                if self.previous_status is not False:
                    print(f"SSH for '{self.device.name}' : exception {e}")
                i += 1
            finally:
                try:
                    if stdin is not None:
                        stdin.close()
                    if stdout is not None:
                        stdout.close()
                    if stderr is not None:
                        stderr.close()
                    if client is not None:
                        client.close()
                except Exception as e:
                    if self.previous_status is not False:
                        print(f"SSH closing for '{self.device.name}' : exception {e}")
        else:
            return False
    def check_mount(self):
        if self.device.mount_folder is None:
            return False
        try:
            mount_folder_path=Path(self.device.mount_folder)
            result = mount_folder_path.is_dir(follow_symlinks=True)
            if result and self.device.mount_test_file:
                mount_test_file_path=Path(mount_folder_path,self.device.mount_test_file)
                stream=None
                try:
                    if self.device.mount_test_write:
                        stream=mount_test_file_path.open(mode="w")
                        stream.flush()
                    else:
                        stream=mount_test_file_path.open(mode="r")
                        stream.read(1)
                finally:
                    if stream:
                        stream.close()
                result=True
            return result
        except Exception as e:
            if self.previous_status is not False:
                    print(f"MOUNT for '{self.device.name}' : exception {e}")
            return False

    
    def run_monitor(self,config:Config):
        #offset starting time to avoid bursts
        self.report.current_status=None
        start_delay=random.uniform(0.0,self.device.interval/5)
        time.sleep(start_delay)
        while True:
            start_time:float = time.time()
        
            self.previous_status = self.report.current_status
            ok:bool = True
            if self.device.mount_folder:
                ok = self.check_mount()
            if ok and self.device.ssh_host:
                ok = self.check_ssh()
            if ok and self.device.ip:
                ok = self.check_ping()
            if ok and self.device.url:
                ok = self.check_url()
            self.report.current_status = ok
            
            # detect state change
            if self.previous_status is None or self.previous_status != ok:
                if ok:
                    downtime_duration = time.time() - self.report.downtime_start if self.report.downtime_start else 0
                    if downtime_duration>0:
                        print(f"[{time.strftime('%Y/%m/%d %H:%M:%S')}] {self.device.name} {config.log_message_reconnected} ({config.log_message_unreachable_for} {downtime_duration:.1f}s)")
                    else:
                        print(f"[{time.strftime('%Y/%m/%d %H:%M:%S')}] {self.device.name} {config.log_message_reachable}")
                    self.report.downtime_start = None
                else:
                    self.report.downtime_start = time.time()
                    print(f"[{time.strftime('%Y/%m/%d %H:%M:%S')}] {self.device.name} {config.log_message_unreachable}")
            
            elapsed = time.time() - start_time
            interval_effective=self.device.interval/self.device.accelerate
            if self.device.ssh_host:
                interval_effective*=self.device.ssh_decelerate
            if self.device.ssh_host and not self.report.current_status:
                interval_effective/=self.device.ssh_failed_accelerate
            if not self.report.current_status:
                interval_effective/=self.device.failed_accelerate
            time.sleep(max(0.0, interval_effective - elapsed))
