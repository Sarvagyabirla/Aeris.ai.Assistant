import psutil
import time
import asyncio
from threading import Thread
from aeris.core.events import event_manager, Events

class SystemMonitor:
    def __init__(self, loop):
        self.running = False
        self.thread = None
        self.loop = loop

    def start(self):
        if not self.running:
            self.running = True
            self.thread = Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def _monitor_loop(self):
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                
                battery = 100
                if hasattr(psutil, "sensors_battery"):
                    bat = psutil.sensors_battery()
                    if bat:
                        battery = bat.percent
                        
                # Emit async event from a sync thread
                asyncio.run_coroutine_threadsafe(
                    event_manager.emit(
                        Events.SYSTEM_METRICS_UPDATED, 
                        cpu=cpu, 
                        ram=ram, 
                        disk=disk, 
                        battery=battery
                    ),
                    self.loop
                )
            except Exception as e:
                pass
            time.sleep(2.0)
