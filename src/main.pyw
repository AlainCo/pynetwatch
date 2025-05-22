from model import Config,Device
from business import LogManager,NetworkMonitor
from ui import NetworkMonitorApp,SpeechMonitor


# main
if __name__ == "__main__":
    config=Config.load()
    log_manager=LogManager(config)
    log_manager.configure()
    # Charger les périphériques depuis le fichier JSON
    devices = Device.load(config)
    if not devices:
        print(f"Aucun périphérique chargé. Vérifiez le fichier {config.devices_file}")
        exit(1)
    #lancer la surveillance
    network_monitor=NetworkMonitor(devices,config)
    network_monitor.start()
    #lancer le rapport audio de surveillance
    speech_monitor=SpeechMonitor(network_monitor, config)
    speech_monitor.start()
    # Lancer l'interface graphique
    app = NetworkMonitorApp(network_monitor, log_manager, config)
    app.mainloop()