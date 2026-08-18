import asyncio
import customtkinter as ctk

from aeris.core.application import AerisCore
from aeris.ui.main_window import MainWindow
from aeris.app_logger.logger import log


def main():
    log.info("Starting Aeris application...")

    # Configure CustomTkinter appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Initialize Core
    core = AerisCore()

    # Run async initialization in a temporary loop, then discard it.
    # The UI creates its own separate loops for background tasks.
    init_loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(init_loop)
        is_online = init_loop.run_until_complete(core.initialize())
    except Exception as e:
        log.error(f"Fatal error during core initialization: {e}")
        print(f"Aeris failed to initialize: {e}")
        init_loop.close()
        return
    finally:
        # Always close the init loop; UI manages its own loops via threads.
        if not init_loop.is_closed():
            init_loop.close()
        asyncio.set_event_loop(None)

    # Initialize and run UI
    try:
        app = MainWindow(core)
        app.update_status()

        if is_online:
            app.chat_view.add_message(
                "system", "Aeris Core Online. How can I help you?"
            )
        else:
            app.chat_view.add_message(
                "system",
                "Aeris Core Started (OFFLINE). "
                "Check your AERIS_API_KEY in .env configuration.",
            )

        log.info("Aeris UI launched.")
        app.mainloop()
        log.info("Aeris application shutdown complete.")
    except Exception as e:
        log.error(f"Fatal error in UI: {e}")
        print(f"Aeris encountered a fatal UI error: {e}")


if __name__ == "__main__":
    main()
