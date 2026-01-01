from model import Config, Device
from business import LogManager, NetworkMonitor
from ui import NetworkMonitorApp, SpeechMonitor


# main
if __name__ == "__main__":
    # load config
    config = Config.load()
    # configure log
    log_manager = LogManager(config)
    log_manager.configure()
    # load devices
    devices = Device.load(config)
    if not devices:
        print(
            f"[{time.strftime('%Y/%m/%d %H:%M:%S')}] No device loaded. Check file: {config.devices_file}")
        exit(1)
    Device.save(devices, config)
    # start network monitoring
    network_monitor = NetworkMonitor(devices, config)
    network_monitor.start()
    # start voice thread
    speech_monitor = SpeechMonitor(network_monitor, config)
    speech_monitor.start()
    # Start GUI
    app = NetworkMonitorApp(network_monitor, log_manager, config)
    app.mainloop()
