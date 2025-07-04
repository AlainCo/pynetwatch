
import threading
from threading import Thread
import urllib3
from model import Config, Device, NetworkReport
from business import DeviceMonitor

# manage all device monitoring threads


class NetworkMonitor:
    def __init__(self, devices: list[Device], config: Config):
        self.config = config
        self.device_monitors = [DeviceMonitor(
            device) for device in devices if not device.is_disabled]
        urllib3.disable_warnings()

    def start(self):
        self.monitors_threads: list[Thread] = [
            threading.Thread(
                target=monitor.run_monitor,
                args=(self.config,),
                daemon=True)
            for monitor in self.device_monitors
        ]
        for thread in self.monitors_threads:
            thread.start()

    def get_report(self):
        report = NetworkReport()
        report.devices_up = [
            monitor.report for monitor in self.device_monitors if monitor.report.current_status is True]
        report.devices_down = [
            monitor.report for monitor in self.device_monitors if monitor.report.current_status is False]
        report.devices_unknown = [
            monitor.report for monitor in self.device_monitors if monitor.report.current_status is None]
        report.devices_down_important = [
            monitor.report for monitor in self.device_monitors
            if monitor.report.current_status is False and monitor.device.is_important]
        return report
