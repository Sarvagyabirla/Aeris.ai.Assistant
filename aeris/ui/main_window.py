import asyncio
import customtkinter as ctk
from threading import Thread

from aeris.core.application import AerisCore
from aeris.ui.status_bar import StatusBar
from aeris.ui.chat_view import ChatView

class MainWindow(ctk.CTk):
    def __init__(self, core: AerisCore):
        super().__init__()
        self.core = core
        
        self.title("Aeris Assistant")
        self.geometry("800x600")
        self.minsize(400, 500)
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Status Bar
        self.status_bar = StatusBar(self, height=30, fg_color=("gray85", "gray15"))
        self.status_bar.grid(row=0, column=0, sticky="ew")
        
        # Chat View
        self.chat_view = ChatView(self)
        self.chat_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=(10, 0))
        
        # Input Frame
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        self.input_field = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Type your message...",
            font=("Arial", 14)
        )
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_field.bind("<Return>", lambda e: self._on_send())
        
        self.send_button = ctk.CTkButton(
            self.input_frame, 
            text="➤ Send", 
            width=80,
            command=self._on_send
        )
        self.send_button.grid(row=0, column=1)

    def update_status(self):
        if self.core.is_online:
            self.status_bar.set_online(self.core.provider.get_model_information())
        else:
            self.status_bar.set_offline("Provider unreachable")

    def _on_send(self):
        text = self.input_field.get().strip()
        if not text:
            return
            
        # Clear input field
        self.input_field.delete(0, ctk.END)
        
        # Disable input while processing
        self.input_field.configure(state="disabled")
        self.send_button.configure(state="disabled")
        
        # Add to UI immediately
        self.chat_view.add_message("user", text)
        
        # Process asynchronously in a separate thread so UI doesn't freeze
        Thread(target=self._run_async_process, args=(text,), daemon=True).start()

    def _run_async_process(self, text: str):
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the core process
        try:
            response = loop.run_until_complete(self.core.process_user_message(text))
            # Schedule UI update on main thread
            self.after(0, lambda: self._on_response_received(response))
        except Exception as e:
            self.after(0, lambda: self._on_response_error(str(e)))
        finally:
            loop.close()

    def _on_response_received(self, response: str):
        self.chat_view.add_message("assistant", response)
        self._re_enable_input()

    def _on_response_error(self, error: str):
        self.chat_view.add_message("system", f"Internal Error: {error}")
        self._re_enable_input()

    def _re_enable_input(self):
        self.input_field.configure(state="normal")
        self.send_button.configure(state="normal")
        self.input_field.focus_set()
