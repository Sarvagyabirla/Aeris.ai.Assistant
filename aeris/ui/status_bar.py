import customtkinter as ctk

class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.status_label = ctk.CTkLabel(
            self, 
            text="● OFFLINE", 
            text_color="gray", 
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        self.provider_label = ctk.CTkLabel(
            self,
            text="",
            text_color="gray",
            font=("Arial", 12)
        )
        self.provider_label.pack(side="right", padx=10, pady=5)

    def set_online(self, provider_info: str):
        self.status_label.configure(text="● ONLINE", text_color="#2ecc71")
        self.provider_label.configure(text=provider_info)
        
    def set_offline(self, reason: str = ""):
        self.status_label.configure(text="● OFFLINE", text_color="#e74c3c")
        if reason:
            self.provider_label.configure(text=reason)
