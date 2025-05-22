
from typing import Any
import queue
import os
import sys
import time
import tkinter as tk
from tkinter import ttk
from model import Config
from business import NetworkMonitor,LogManager

#gestionnaire de l'icone de l'application
class IconManager:
    def __init__(self,app:tk.Tk):
        self.app=app
        self.current_icon = ""
        self.current_icon_handle=None
        self.icons = {
            "ok": self._get_icon_path("ok.ico"),
            "warn": self._get_icon_path("warn.ico"),
            "alert": self._get_icon_path("alert.ico"),
            "wait": self._get_icon_path("wait.ico"),
        }
        
    def _get_icon_path(self, filename:str):
        """Gère le chemin des ressources pour PyInstaller"""
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, "icons", filename) # type: ignore
        return os.path.join("icons", filename)

    def change_icon(self, icon_name:str):
        """Change l'icône de la fenêtre et de la barre des tâches"""
        if icon_name not in self.icons:
            return
        if self.current_icon == icon_name:
            return
        icon_path = self.icons[icon_name]
        # Pour Windows
        if sys.platform == "win32":
            import win32gui
            import win32con
            try:
                hwnd = win32gui.GetParent(self.app.winfo_id())
                if not hwnd:
                    return
                if self.current_icon_handle:
                    win32gui.DestroyIcon(self.current_icon_handle) #type: ignore
                # Charger la nouvelle icône
                self.current_icon_handle = win32gui.LoadImage(
                    0, icon_path, win32con.IMAGE_ICON, 0, 0, 
                    win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                )
                # Mise à jour des deux tailles d'icônes
                for icon_type in [win32con.ICON_SMALL, win32con.ICON_BIG]:
                    win32gui.SendMessage(
                        hwnd,
                        win32con.WM_SETICON,
                        icon_type,
                        self.current_icon_handle # type: ignore
                    )
                self.current_icon = icon_name
            except Exception as e:
                print(f"Erreur dans change_icon: {e}")

# application graphique de surveilance
class NetworkMonitorApp(tk.Tk):
    def __init__(self, network_monitor:NetworkMonitor, log_manager:LogManager, config:Config,*args:Any, **kwargs:Any):
        super().__init__(*args, **kwargs)
        self.icon_manager=IconManager(self)
        self.log_manager=log_manager
        self.network_monitor = network_monitor
        # Configuration de l'interface
        self.title("Network Monitor")
        self.status_label = ttk.Label(self, text="Initialisation", foreground="green")
        self.status_label.pack(side=tk.TOP)
        self.tree = ttk.Treeview(self, columns=('Status', 'Downtime'), show='headings')
        self.tree.heading('Status', text='Statut')
        self.tree.heading('Downtime', text='Indisponible depuis')
        self.tree.pack(fill=tk.BOTH, expand=True)
        # zone de logs
        self.log_frame = ttk.Frame(self)
        self.log_text = tk.Text(self.log_frame, height=10, state='disabled',width=40)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        # Bouton pour escamoter
        self.toggle_btn = ttk.Button(
            self,
            text="▲ Afficher les logs ▼",
            command=self.toggle_logs
        )
        self.toggle_btn.pack(fill=tk.X,side=tk.BOTTOM)
        self.log_visible = False
        self.log_frame.pack_forget()
        self.update_interval=1000
        self.update_display()
    
    def toggle_logs(self):
        if self.log_visible:
            self.log_frame.pack_forget()
            self.toggle_btn.config(text="▲ Afficher les logs ▼")
        else:
            self.log_frame.pack(fill=tk.BOTH, expand=True)
            self.toggle_btn.config(text="▲ Masquer les logs ▼")
        self.log_visible = not self.log_visible        
    
    def process_log_queue(self):
        """Vide la queue de logs dans le widget (thread principal)"""
        while True:
            try:
                msg = self.log_manager.log_queue.get_nowait()
                self.log_text.configure(state='normal')
                self.log_text.insert('end', msg + '\n')
                self.log_text.see('end')
                self.log_text.configure(state='disabled')
            except queue.Empty:
                break
    
    def update_display(self):
        self.tree.delete(*self.tree.get_children())
        network_report=self.network_monitor.get_report()
        any_down = network_report.devices_down
        important_down=network_report.devices_down_important
        any_unknown=network_report.devices_unknown
        for r in network_report.devices_down:
            downtime = time.strftime("%H:%M:%S", time.localtime(r.downtime_start)) if r.downtime_start else "N/A"
            self.tree.insert('', 'end', values=(r.device.name, downtime))
        if important_down:
            self.status_label.config(text="Problèmes graves détectés", foreground="red",font=('Helvetica', 18, 'bold'))
            self.icon_manager.change_icon('alert')
        else:
            if any_down:
                self.status_label.config(text="Problèmes détectés", foreground="orange",font=('Helvetica', 15, 'bold'))
                self.icon_manager.change_icon('warn')
            else:
                self.status_label.config(text="Tout est joignable", foreground="green",font=('Helvetica', 10, 'normal'))
                if any_unknown:
                    self.icon_manager.change_icon('wait')
                else:
                    self.icon_manager.change_icon('ok')
        self.process_log_queue()
        self.after(self.update_interval, self.update_display)

