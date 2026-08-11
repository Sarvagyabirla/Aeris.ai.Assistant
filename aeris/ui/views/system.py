import customtkinter as ctk
from aeris.ui.state import ui_state

class SystemView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        ctk.CTkLabel(self, text="SYSTEM METRICS", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 30))
        
        self.cpu_bar = self._create_metric("CPU Usage", "0%")
        self.ram_bar = self._create_metric("RAM Usage", "0%")
        self.disk_bar = self._create_metric("Disk Usage", "0%")
        self.battery_bar = self._create_metric("Battery", "100%")
        
        ui_state.subscribe(self._update_metrics)
        
    def _create_metric(self, name, default_text):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=40, pady=10)
        
        label = ctk.CTkLabel(frame, text=name, font=ctk.CTkFont(weight="bold"), width=100, anchor="w")
        label.pack(side="left", padx=20, pady=20)
        
        progress = ctk.CTkProgressBar(frame, height=20)
        progress.pack(side="left", fill="x", expand=True, padx=20)
        progress.set(0)
        
        val_label = ctk.CTkLabel(frame, text=default_text, width=60)
        val_label.pack(side="right", padx=20)
        
        return {"progress": progress, "label": val_label}
        
    def _update_metrics(self):
        self.after(0, self._update_metrics_sync)
        
    def _update_metrics_sync(self):
        m = ui_state.system_metrics
        
        self.cpu_bar["progress"].set(m["cpu"] / 100.0)
        self.cpu_bar["label"].configure(text=f"{m['cpu']:.1f}%")
        
        self.ram_bar["progress"].set(m["ram"] / 100.0)
        self.ram_bar["label"].configure(text=f"{m['ram']:.1f}%")
        
        self.disk_bar["progress"].set(m["disk"] / 100.0)
        self.disk_bar["label"].configure(text=f"{m['disk']:.1f}%")
        
        self.battery_bar["progress"].set(m["battery"] / 100.0)
        self.battery_bar["label"].configure(text=f"{m['battery']:.1f}%")
