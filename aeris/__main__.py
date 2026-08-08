import asyncio
import customtkinter as ctk

from aeris.core.application import AerisCore
from aeris.ui.main_window import MainWindow
from aeris.logging.logger import log

def main():
    try:
        log.info("Starting Aeris application...")
        
        # Configure CustomTkinter appearance
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Initialize Core
        core = AerisCore()
        
        # Run core initialization synchronously for startup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        is_online = loop.run_until_complete(core.initialize())
        
        # Initialize UI
        app = MainWindow(core)
        app.update_status()
        
        if is_online:
            app.chat_view.add_message("system", "Aeris Core Online. How can I help you?")
        else:
            app.chat_view.add_message("system", "Aeris Core Started (OFFLINE). Check API configuration.")
            
        log.info("Aeris UI launched.")
        app.mainloop()
        
        log.info("Aeris application shutdown.")
    except Exception as e:
        log.error(f"Fatal error during application startup: {e}")
        print(f"Aeris encountered a fatal error and could not start: {e}")

if __name__ == "__main__":
    main()
