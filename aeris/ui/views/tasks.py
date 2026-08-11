import customtkinter as ctk
from aeris.ui.state import ui_state

class TaskView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        ctk.CTkLabel(self, text="TASK CENTER", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 30))
        
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(self.status_frame, text="Active Context:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        self.task_label = ctk.CTkLabel(self.status_frame, text="Ready", font=ctk.CTkFont(size=18), text_color="#3498db")
        self.task_label.pack(anchor="w", padx=20, pady=(0, 20))
        
        ui_state.subscribe(self._update_task)
        
    def _update_task(self):
        self.after(0, self._update_task_sync)
        
    def _update_task_sync(self):
        self.task_label.configure(text=ui_state.current_task)
