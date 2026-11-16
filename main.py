import tkinter as tk
from tkinter import messagebox

from pulse.config import Config
from pulse.constants import APP_NAME
from pulse.presence import PresenceManager
from pulse.server import start_server


def main():
    cfg = Config()
    manager = PresenceManager(cfg)

    try:
        httpd = start_server(manager)
    except OSError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(APP_NAME, f"{APP_NAME} вже запущено (порт зайнятий).")
        return

    manager.start()

    def shutdown():
        manager.stop()
        manager.join(timeout=3)
        httpd.shutdown()

    from pulse.ui import App

    App(cfg, manager, shutdown).mainloop()


if __name__ == "__main__":
    main()
