import requests
import random
import time
from icmplib import ping as icmp_ping # type: ignore
from model import Device,Config,DeviceReport
#composant de surveillance d'un device
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
        
    def run_monitor(self,config:Config):
        #décale les moment de démarrage pour éviter les rafales, au hasard dans 20% de l'intervalle
        start_delay=random.uniform(0.0,self.device.interval/5)
        time.sleep(start_delay)
        while True:
            start_time:float = time.time()
        
            previous_status = self.report.current_status
            # Vérification du statut
            ok:bool = False
            if self.device.ip:
                ok = self.check_ping()
            if not ok and self.device.url:
                ok = self.check_url()
            self.report.current_status = ok
            
            # Détection des changements d'état
            if previous_status is None or previous_status != ok:
                if ok:
                    downtime_duration = time.time() - self.report.downtime_start if self.report.downtime_start else 0
                    if downtime_duration>0:
                        print(f"[{time.strftime('%H:%M:%S')}] {self.device.name} reconnecté (indisponible pendant {downtime_duration:.1f}s)")
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] {self.device.name} connecté")
                    self.report.downtime_start = None
                else:
                    self.report.downtime_start = time.time()
                    print(f"[{time.strftime('%H:%M:%S')}] {self.device.name} injoignable")
            
            elapsed = time.time() - start_time
            interval_effective=self.device.interval/self.device.accelerate;
            if not self.report.current_status:
                interval_effective/=self.device.failed_accelerate
            time.sleep(max(0.0, interval_effective - elapsed))
