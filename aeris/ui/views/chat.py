import customtkinter as ctk
from aeris.ui.state import ui_state

class ChatView(ctk.CTkFrame):
    def __init__(self, master, on_send_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_send_callback = on_send_callback
        
        # Grid layout: Chat on left (weight 3), Activity Feed on right (weight 1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Chat Area ---
        self.chat_container = ctk.CTkFrame(self, fg_color="transparent")
        self.chat_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.chat_container.grid_rowconfigure(0, weight=1)
        self.chat_container.grid_columnconfigure(0, weight=1)
        
        self.chat_scroll = ctk.CTkScrollableFrame(self.chat_container)
        self.chat_scroll.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        self.input_frame = ctk.CTkFrame(self.chat_container, height=50)
        self.input_frame.grid(row=1, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        self.input_field = ctk.CTkEntry(self.input_frame, placeholder_text="Enter command...", font=("Arial", 14))
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(10, 10), pady=10)
        self.input_field.bind("<Return>", lambda e: self._send_message())
        
        self.send_btn = ctk.CTkButton(self.input_frame, text="SEND", width=60, command=self._send_message)
        self.send_btn.grid(row=0, column=1, padx=(0, 10), pady=10)
        
        # --- Activity Feed Area ---
        self.feed_container = ctk.CTkFrame(self)
        self.feed_container.grid(row=0, column=1, sticky="nsew")
        self.feed_container.grid_rowconfigure(1, weight=1)
        self.feed_container.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.feed_container, text="ACTIVITY FEED", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=10)
        
        self.feed_text = ctk.CTkTextbox(self.feed_container, state="disabled", wrap="word", font=("Courier", 10))
        self.feed_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        ui_state.subscribe(self._update_feed)
        
    def _send_message(self):
        text = self.input_field.get().strip()
        if text:
            self.add_message("user", text)
            self.input_field.delete(0, ctk.END)
            self.input_field.configure(state="disabled")
            self.send_btn.configure(state="disabled")
            self.on_send_callback(text)
            
    def add_message(self, role: str, content: str):
        self.after(0, self._add_message_sync, role, content)
        
    def _add_message_sync(self, role: str, content: str):
        # Enable input if assistant replied
        if role in ["assistant", "system"]:
            self.input_field.configure(state="normal")
            self.send_btn.configure(state="normal")
            self.input_field.focus_set()
            
        bg_color = ("#D1E8FF", "#1E3A8A") if role == "user" else ("#E5E7EB", "#374151")
        if role == "system": bg_color = ("#FFD1D1", "#7F1D1D")
        
        anchor = "e" if role == "user" else "w"
        
        msg_frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        msg_frame.pack(fill="x", pady=5, padx=10, anchor=anchor)
        
        name_label = ctk.CTkLabel(msg_frame, text=role.capitalize(), font=("Arial", 10, "bold"), text_color="gray")
        name_label.pack(anchor=anchor, pady=(0, 2))
        
        bubble = ctk.CTkFrame(msg_frame, fg_color=bg_color, corner_radius=10)
        bubble.pack(anchor=anchor)
        
        text_label = ctk.CTkLabel(bubble, text=content, text_color=("black", "white"), font=("Arial", 14), justify="left", wraplength=400)
        text_label.pack(padx=15, pady=10)
        
        self.after(100, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))
        
    def _update_feed(self):
        self.after(0, self._update_feed_sync)
        
    def _update_feed_sync(self):
        self.feed_text.configure(state="normal")
        self.feed_text.delete("0.0", "end")
        feed_content = "\n".join(ui_state.ai_activity_feed)
        self.feed_text.insert("end", feed_content)
        self.feed_text.see("end")
        self.feed_text.configure(state="disabled")
