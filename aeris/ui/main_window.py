import asyncio
from threading import Thread
import customtkinter as ctk

from aeris.core.application import AerisCore
from aeris.ui.state import ui_state
from aeris.ui.monitor import SystemMonitor
from aeris.ui.components.sidebar import Sidebar
from aeris.ui.views.chat import ChatView
from aeris.ui.views.system import SystemView
from aeris.ui.views.tasks import TaskView
from aeris.ui.views.security import SecurityView

class MainWindow(ctk.CTk):
    def __init__(self, core: AerisCore):
        super().__init__()
        self.core = core
        
        # UI Setup
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title("AERIS COMMAND CENTER")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        # Grid config: Sidebar (col 0, fixed), Main (col 1, expandable)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Views Container
        self.views = {}
        self.current_view = None
        
        # Main content frame
        self.main_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Initialize views
        self._init_views()
        
        # Sidebar
        self.sidebar = Sidebar(self, nav_callback=self.show_view)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self._start_monitor()
        
    def _start_monitor(self):
        self.monitor_loop = asyncio.new_event_loop()
        self.monitor = SystemMonitor(self.monitor_loop)
        
        def run_loop():
            asyncio.set_event_loop(self.monitor_loop)
            self.monitor.start()
            self.monitor_loop.run_forever()
            
        self.monitor_thread = Thread(target=run_loop, daemon=True)
        self.monitor_thread.start()
        
    def _init_views(self):
        self.views["chat"] = ChatView(self.main_container, on_send_callback=self._process_chat_async)
        self.views["system"] = SystemView(self.main_container)
        self.views["tasks"] = TaskView(self.main_container)
        self.views["security"] = SecurityView(self.main_container)
        
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")
            
    def show_view(self, view_name: str):
        if view_name in self.views:
            self.views[view_name].tkraise()
            self.current_view = view_name
            
    def _process_chat_async(self, text: str):
        Thread(target=self._run_core_task, args=(text,), daemon=True).start()
        
    def _run_core_task(self, text: str):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(self.core.process_user_message(text))
            if response:
                self.views["chat"].add_message("assistant", response)
        except Exception as e:
            self.views["chat"].add_message("system", f"Internal Error: {e}")
        finally:
            loop.close()
            
    def destroy(self):
        if hasattr(self, 'monitor'):
            self.monitor.stop()
            self.monitor_loop.call_soon_threadsafe(self.monitor_loop.stop)
        super().destroy()
