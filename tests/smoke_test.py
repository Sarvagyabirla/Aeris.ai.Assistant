"""
Smoke test for Aeris startup.

This test opens a real Tkinter window and is intended for MANUAL verification only.
It is excluded from automated pytest runs via the `manual` marker.

To run manually:
    python tests/smoke_test.py
"""
import asyncio
import sys


def test_startup():
    """
    Manual smoke test: verifies the full startup sequence.
    Skipped in automated test runs.
    """
    import pytest
    pytest.skip("Smoke test is manual-only (opens a real UI window).")


if __name__ == "__main__":
    # Manual execution path — actually opens the UI window for 2 seconds.
    import customtkinter as ctk
    from aeris.core.application import AerisCore
    from aeris.ui.main_window import MainWindow

    print("=== Aeris Smoke Test ===")
    print("Initializing Core...")
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    core = AerisCore()

    class MockProvider:
        async def send_message(self, request):
            return None
        async def stream_message(self, request):
            pass
        async def validate_connection(self):
            return True
        def get_model_information(self):
            return "MockModel"

    core.provider = MockProvider()

    init_loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(init_loop)
        is_online = init_loop.run_until_complete(core.initialize())
    finally:
        init_loop.close()
        asyncio.set_event_loop(None)

    print(f"Core initialized. Online: {is_online}")
    print("Initializing UI...")

    app = MainWindow(core)
    app.update_status()
    app.chat_view.add_message("system", "Smoke test: Aeris Core Online.")

    # Auto-destroy after 2 seconds so the test can complete unattended
    app.after(2000, app.destroy)

    print("Entering Mainloop (will auto-close in 2 seconds)...")
    app.mainloop()

    print("Smoke test PASSED successfully.")
