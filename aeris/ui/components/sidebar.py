import customtkinter as ctk
from aeris.ui.state import ui_state

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, nav_callback, **kwargs):
        super().__init__(master, corner_radius=0, **kwargs)
        self.nav_callback = nav_callback
        
        # Logo / Title
        self.logo_label = ctk.CTkLabel(self, text="AERIS CORE", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=(20, 10), padx=20)
        
        # Status Indicator
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(pady=(0, 20), padx=20)
        
        self.status_dot = ctk.CTkLabel(self.status_frame, text="●", text_color="gray", font=("Arial", 18))
        self.status_dot.pack(side="left", padx=(0, 5))
        
        self.status_text = ctk.CTkLabel(self.status_frame, text="OFFLINE", font=ctk.CTkFont(size=12))
        self.status_text.pack(side="left")

        # Navigation Buttons
        self._buttons = []
        
        self.btn_chat = ctk.CTkButton(self, text="Chat & Feed", anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=lambda: self._on_nav("chat"))
        self.btn_chat.pack(pady=5, padx=20, fill="x")
        self._buttons.append(("chat", self.btn_chat))
        
        self.btn_system = ctk.CTkButton(self, text="System Monitor", anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=lambda: self._on_nav("system"))
        self.btn_system.pack(pady=5, padx=20, fill="x")
        self._buttons.append(("system", self.btn_system))

        self.btn_tasks = ctk.CTkButton(self, text="Task Center", anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=lambda: self._on_nav("tasks"))
        self.btn_tasks.pack(pady=5, padx=20, fill="x")
        self._buttons.append(("tasks", self.btn_tasks))

        self.btn_security = ctk.CTkButton(self, text="Security", anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=lambda: self._on_nav("security"))
        self.btn_security.pack(pady=5, padx=20, fill="x")
        self._buttons.append(("security", self.btn_security))
        
        # Spacer
        ctk.CTkLabel(self, text="").pack(expand=True)
        
        # Mini metrics at bottom
        self.cpu_label = ctk.CTkLabel(self, text="CPU: 0%", font=ctk.CTkFont(size=10), text_color="gray")
        self.cpu_label.pack(pady=(5,0))
        self.ram_label = ctk.CTkLabel(self, text="RAM: 0%", font=ctk.CTkFont(size=10), text_color="gray")
        self.ram_label.pack(pady=(0,10))
        
        # Subscribe to state updates
        ui_state.subscribe(self._update_ui)
        self._on_nav("chat") # Default selection
        
    def _on_nav(self, view_name):
        # Update button colors
        for name, btn in self._buttons:
            if name == view_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
        self.nav_callback(view_name)
        
    def _update_ui(self):
        # We must schedule this on the main thread if it's called from another thread
        # CustomTkinter after() is thread safe in newer versions, but we should be careful.
        # Ideally, we call _update_ui_sync via after(0)
        self.after(0, self._update_ui_sync)
        
    def _update_ui_sync(self):
        # Update Status
        status_colors = {
            "OFFLINE": "gray",
            "IDLE": "#2ecc71",       # Green
            "THINKING": "#3498db",   # Blue
            "EXECUTING": "#f1c40f",  # Yellow
            "WAITING_FOR_PERMISSION": "#e67e22", # Orange
            "SUCCESS": "#2ecc71",
            "ERROR": "#e74c3c"       # Red
        }
        color = status_colors.get(ui_state.core_status, "gray")
        self.status_dot.configure(text_color=color)
        self.status_text.configure(text=ui_state.core_status)
        
        # Update mini metrics
        self.cpu_label.configure(text=f"CPU: {ui_state.system_metrics['cpu']:.1f}%")
        self.ram_label.configure(text=f"RAM: {ui_state.system_metrics['ram']:.1f}%")
