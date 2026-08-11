import customtkinter as ctk
from aeris.tools.security import kill_switch
from aeris.config.settings import settings

class SecurityView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        ctk.CTkLabel(self, text="SECURITY CENTER", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 20))
        
        # Kill Switch
        self.kill_frame = ctk.CTkFrame(self, fg_color="#331111")
        self.kill_frame.pack(fill="x", padx=40, pady=10)
        
        self.kill_label = ctk.CTkLabel(self.kill_frame, text="GLOBAL KILL SWITCH", font=ctk.CTkFont(size=18, weight="bold"), text_color="red")
        self.kill_label.pack(pady=10)
        
        is_active = kill_switch.is_active
        btn_text = "DEACTIVATE" if is_active else "ACTIVATE"
        btn_color = "gray" if is_active else "red"
        
        self.kill_btn = ctk.CTkButton(self.kill_frame, text=btn_text, fg_color=btn_color, hover_color="#aa0000", font=ctk.CTkFont(weight="bold"), command=self._toggle_kill)
        self.kill_btn.pack(pady=(0, 20))
        
        # Dry Run
        self.dry_frame = ctk.CTkFrame(self)
        self.dry_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(self.dry_frame, text="Dry Run Mode (Simulation Only)", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=20, pady=20)
        self.dry_label = ctk.CTkLabel(self.dry_frame, text="ON" if settings.dry_run else "OFF", text_color="orange" if settings.dry_run else "gray", font=ctk.CTkFont(weight="bold"))
        self.dry_label.pack(side="right", padx=20)
        
        # Note on permissions
        ctk.CTkLabel(self, text="NOTE: Tools with SENSITIVE permissions will block execution\nand prompt you for approval in the Chat view.", text_color="gray").pack(pady=30)
        
    def _toggle_kill(self):
        kill_switch.toggle()
        if kill_switch.is_active:
            self.kill_btn.configure(text="DEACTIVATE", fg_color="gray")
        else:
            self.kill_btn.configure(text="ACTIVATE", fg_color="red")
