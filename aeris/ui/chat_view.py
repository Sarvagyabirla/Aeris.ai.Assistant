import customtkinter as ctk
import datetime

class ChatView(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Configure layout to expand messages properly
        self.grid_columnconfigure(0, weight=1)
        self._messages = []

    def add_message(self, role: str, content: str):
        """Add a message bubble to the chat view."""
        # Determine styling based on role
        if role == "user":
            bg_color = ("#D1E8FF", "#1E3A8A")
            align = "e"
            anchor = "e"
            sticky = "e"
            text_color = ("black", "white")
        elif role == "assistant":
            bg_color = ("#E5E7EB", "#374151")
            align = "w"
            anchor = "w"
            sticky = "w"
            text_color = ("black", "white")
        else: # system or error
            bg_color = ("#FFD1D1", "#7F1D1D")
            align = "center"
            anchor = "center"
            sticky = ""
            text_color = ("black", "white")

        msg_frame = ctk.CTkFrame(self, fg_color="transparent")
        msg_frame.grid(row=len(self._messages), column=0, sticky=sticky, pady=5, padx=10)

        # Name label
        name = role.capitalize()
        name_label = ctk.CTkLabel(msg_frame, text=name, font=("Arial", 10, "bold"), text_color="gray")
        name_label.pack(anchor=anchor, pady=(0, 2))

        # Bubble
        bubble = ctk.CTkFrame(msg_frame, fg_color=bg_color, corner_radius=10)
        bubble.pack(anchor=anchor)

        text_label = ctk.CTkLabel(
            bubble, 
            text=content,
            text_color=text_color,
            font=("Arial", 14),
            justify=ctk.LEFT if role != "user" else ctk.RIGHT,
            wraplength=400 # Will dynamically wrap
        )
        text_label.pack(padx=15, pady=10)
        
        self._messages.append(msg_frame)
        
        # Scroll to bottom
        self.after(100, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        self._parent_canvas.yview_moveto(1.0)
