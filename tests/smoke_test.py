import asyncio
import sys
import customtkinter as ctk

from aeris.core.application import AerisCore
from aeris.ui.main_window import MainWindow

def test_startup():
    print("Initializing Core...")
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    core = AerisCore()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # We use a mock provider to avoid hitting the actual API during tests
    class MockProvider:
        async def send_message(self, request): return None
        async def stream_message(self, request): pass
        async def validate_connection(self): return True
        def get_model_information(self): return "MockModel"
    
    core.provider = MockProvider()
    
    # Initialize Core
    is_online = loop.run_until_complete(core.initialize())
    
    print("Initializing UI...")
    app = MainWindow(core)
    app.update_status()
    
    # Auto-destroy after 1 second
    app.after(1000, app.destroy)
    
    print("Entering Mainloop...")
    app.mainloop()
    
    print("Smoke test passed successfully!")

if __name__ == "__main__":
    test_startup()
