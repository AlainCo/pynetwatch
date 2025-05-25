import requests
import random
import time
from icmplib import ping as icmp_ping # type: ignore
from model import Device,Config,DeviceReport
import paramiko
import re

#Device surveillance component
class DeviceMonitor:
    def __init__(self, device: Device):
        self.report=DeviceReport(device)
        self.device=device

    def check_ping(self):
        if self.device.ip is None:
            return False
        try:
            result = icmp_ping(self.device.ip, count=self.device.ping_count, timeout=self.device.ping_timeout, privileged=False)
            return result.packets_received > 0
        except Exception:
            return False

    def check_url(self):
        if self.device.url is None:
            return False
        i=0
        while i<self.device.http_retry:
            try:
                response = requests.get(url=self.device.url, timeout=self.device.http_timeout, verify=False,)
                return response.status_code <500
            except requests.exceptions.RequestException:
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
                    key_filename =self.device.ssh_key_file,
                    passphrase=self.device.ssh_key_password,
                    gss_auth=False,
                    gss_kex=False,
                    compress=True,
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
                        print(f"Ignored: invalid regex : {pattern}")
                for pattern in self.device.ssh_pattern_forbiden:
                    try:
                        regex = re.compile(pattern,flags=0)
                        if regex.search(text):
                            return False
                    except re.error:
                        print(f"Ignored: invalid regex : {pattern}")
                return True
            except Exception:
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
                except Exception:
                    pass
        else:
            return False
    
    def run_monitor(self,config:Config):
        #offset starting time to avoid bursts
        start_delay=random.uniform(0.0,self.device.interval/5)
        time.sleep(start_delay)
        while True:
            start_time:float = time.time()
        
            previous_status = self.report.current_status
            ok:bool = False
            if self.device.ssh_host:
                ok = self.check_ssh()
            if self.device.ip:
                ok = self.check_ping()
            if not ok and self.device.url:
                ok = self.check_url()
            self.report.current_status = ok
            
            # detect state change
            if previous_status is None or previous_status != ok:
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
