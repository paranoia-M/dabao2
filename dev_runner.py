# dev_runner.py
import sys, time, subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

MAIN_APP_SCRIPT = 'main.py'
WATCH_PATH = '.'

class AppReloader(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.process = None
        self.start_app()

    def start_app(self):
        if self.process:
            print("-------------------------------------------------")
            print("检测到代码变动，正在重启应用...")
            self.process.terminate()
            self.process.wait()
        
        self.process = subprocess.Popen([sys.executable, MAIN_APP_SCRIPT])
        print(f"应用已启动 (PID: {self.process.pid})...")
        print("-------------------------------------------------")

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            self.start_app()

if __name__ == "__main__":
    print(">>> 启动开发模式：代码热重载已激活 <<<")
    event_handler = AppReloader()
    observer = Observer(); observer.schedule(event_handler, WATCH_PATH, recursive=True); observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process: event_handler.process.terminate(); event_handler.process.wait()
        print("\n>>> 开发模式已退出 <<<")
    observer.join()