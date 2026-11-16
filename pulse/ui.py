import os
import sys
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from . import autostart
from .config import BASE_DIR
from .constants import APP_ID, APP_NAME

BG = "#0e0f14"
CARD = "#171922"
FIELD = "#20232f"
ACCENT = "#5865F2"
ACCENT_HOVER = "#4752c4"
TEXT = "#eceef5"
DIM = "#8b90a5"
GREEN = "#3ba55d"
RED = "#ed4245"
ORANGE = "#faa61a"

PAGES = ["Головна", "Свій статус", "Налаштування"]
ACTIVITY_TYPES = {
    "Грає": "PLAYING",
    "Слухає": "LISTENING",
    "Дивиться": "WATCHING",
    "Змагається": "COMPETING",
}
ERRORS = {
    "InvalidID": "Невірний Application ID",
    "DiscordNotFound": "Discord не запущено",
    "DiscordError": "Discord не відповідає",
}


class App(ctk.CTk):
    def __init__(self, cfg, manager, on_shutdown):
        ctk.set_appearance_mode("dark")
        super().__init__(fg_color=BG)
        self.cfg = cfg
        self.manager = manager
        self._on_shutdown = on_shutdown
        self._pending = None
        self._last_view = object()
        self._last_conn = None

        self.title(APP_NAME)
        self.geometry("460x680")
        self.resizable(False, False)

        self.tray = self._make_tray()

        self._build_header()
        self.nav = ctk.CTkSegmentedButton(
            self,
            values=PAGES,
            command=self.show_page,
            fg_color=CARD,
            selected_color=ACCENT,
            selected_hover_color=ACCENT_HOVER,
            unselected_color=CARD,
            unselected_hover_color=FIELD,
            text_color=TEXT,
            height=36,
            corner_radius=10,
        )
        self.nav.pack(fill="x", padx=20, pady=(0, 12))
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.pages = {
            "Головна": self._build_home(),
            "Свій статус": self._build_custom(),
            "Налаштування": self._build_settings(),
        }
        self.nav.set(PAGES[0])
        self.show_page(PAGES[0])

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        if self.tray:
            self.tray.start()
            if cfg.data["start_minimized"]:
                self.withdraw()
        self.after(500, self.refresh)

    # ---------- каркас ----------

    def _make_tray(self):
        try:
            from .tray import Tray

            return Tray(lambda: self._set_pending("show"), lambda: self._set_pending("quit"))
        except Exception:
            return None

    def _set_pending(self, action):
        self._pending = action

    def _build_header(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(18, 12))
        ctk.CTkLabel(
            bar, text=APP_NAME, text_color=TEXT, font=ctk.CTkFont("Segoe UI", 24, "bold")
        ).pack(side="left")
        self.dot = ctk.CTkLabel(bar, text="●", text_color=RED, font=ctk.CTkFont(size=14))
        self.dot.pack(side="right")

    def _card(self, parent, title=None):
        frame = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14)
        frame.pack(fill="x", pady=(0, 12))
        if title:
            ctk.CTkLabel(
                frame, text=title, text_color=DIM, font=ctk.CTkFont("Segoe UI", 12)
            ).pack(anchor="w", padx=16, pady=(12, 4))
        return frame

    def show_page(self, name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[name].pack(fill="both", expand=True)

    # ---------- головна ----------

    def _build_home(self):
        page = ctk.CTkFrame(self.container, fg_color="transparent")

        now = self._card(page, "Зараз у статусі")
        self.src_label = ctk.CTkLabel(
            now, text="", text_color=ACCENT, font=ctk.CTkFont("Segoe UI", 12, "bold")
        )
        self.title_label = ctk.CTkLabel(
            now,
            text="Нічого не транслюється",
            text_color=TEXT,
            font=ctk.CTkFont("Segoe UI", 16, "bold"),
            wraplength=380,
            justify="left",
        )
        self.sub_label = ctk.CTkLabel(
            now,
            text="Увімкніть музику чи відео на YouTube",
            text_color=DIM,
            font=ctk.CTkFont("Segoe UI", 13),
            wraplength=380,
            justify="left",
        )
        self.src_label.pack(anchor="w", padx=16)
        self.title_label.pack(anchor="w", padx=16, pady=(2, 0))
        self.sub_label.pack(anchor="w", padx=16, pady=(2, 14))

        conn = self._card(page, "Discord")
        self.conn_label = ctk.CTkLabel(
            conn, text="", text_color=TEXT, font=ctk.CTkFont("Segoe UI", 13)
        )
        self.conn_label.pack(anchor="w", padx=16, pady=(0, 14))

        sources = self._card(page, "Джерела")
        self.src_vars = {}
        for key, label in (("ytmusic", "YouTube Music"), ("youtube", "YouTube")):
            var = ctk.BooleanVar(value=self.cfg.data["sources"][key])
            self.src_vars[key] = var
            ctk.CTkSwitch(
                sources,
                text=label,
                variable=var,
                command=lambda k=key: self._toggle_source(k),
                progress_color=ACCENT,
                text_color=TEXT,
            ).pack(anchor="w", padx=16, pady=(2, 10))

        mode = self._card(page, "Режим")
        self.mode_btn = ctk.CTkSegmentedButton(
            mode,
            values=["Автоматично", "Свій статус"],
            command=self._set_mode,
            fg_color=FIELD,
            selected_color=ACCENT,
            selected_hover_color=ACCENT_HOVER,
            unselected_color=FIELD,
            unselected_hover_color=BG,
            text_color=TEXT,
        )
        self.mode_btn.set("Свій статус" if self.cfg.data["mode"] == "custom" else "Автоматично")
        self.mode_btn.pack(fill="x", padx=16, pady=(0, 10))
        self.fallback_var = ctk.BooleanVar(value=self.cfg.data["idle_fallback"])
        ctk.CTkCheckBox(
            mode,
            text="Показувати свій статус, коли нічого не грає",
            variable=self.fallback_var,
            command=self._toggle_fallback,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=DIM,
            font=ctk.CTkFont("Segoe UI", 12),
        ).pack(anchor="w", padx=16, pady=(0, 14))
        return page

    def _toggle_source(self, key):
        self.cfg.data["sources"][key] = bool(self.src_vars[key].get())
        self.cfg.save()

    def _set_mode(self, value):
        self.cfg.data["mode"] = "custom" if value == "Свій статус" else "auto"
        if self.cfg.data["mode"] == "custom":
            self.manager.reset_custom_timer()
        self.cfg.save()

    def _toggle_fallback(self):
        self.cfg.data["idle_fallback"] = bool(self.fallback_var.get())
        self.cfg.save()

    # ---------- свій статус ----------

    def _build_custom(self):
        page = ctk.CTkScrollableFrame(
            self.container, fg_color=CARD, corner_radius=14, scrollbar_button_color=FIELD
        )
        c = self.cfg.data["custom"]

        ctk.CTkLabel(page, text="Тип активності", text_color=DIM, font=ctk.CTkFont(size=12)).pack(
            anchor="w", padx=8, pady=(6, 0)
        )
        current = next((k for k, v in ACTIVITY_TYPES.items() if v == c["type"]), "Грає")
        self.type_menu = ctk.CTkOptionMenu(
            page,
            values=list(ACTIVITY_TYPES),
            fg_color=FIELD,
            button_color=FIELD,
            button_hover_color=BG,
            dropdown_fg_color=FIELD,
            text_color=TEXT,
            height=34,
        )
        self.type_menu.set(current)
        self.type_menu.pack(fill="x", padx=8, pady=(2, 0))

        self.fields = {}
        for label, key, hint in (
            ("Заголовок", "details", "Наприклад: Кодю проєкт"),
            ("Опис", "state", "Наприклад: Python + Discord"),
            ("Зображення (посилання)", "large_image", "https://…/image.png"),
            ("Підпис до зображення", "large_text", ""),
            ("Кнопка: текст", "button_label", "Відкрити GitHub"),
            ("Кнопка: посилання", "button_url", "https://github.com/…"),
        ):
            ctk.CTkLabel(page, text=label, text_color=DIM, font=ctk.CTkFont(size=12)).pack(
                anchor="w", padx=8, pady=(10, 0)
            )
            entry = ctk.CTkEntry(
                page, placeholder_text=hint, fg_color=FIELD, border_width=0, height=34
            )
            entry.pack(fill="x", padx=8, pady=(2, 0))
            if c[key]:
                entry.insert(0, c[key])
            self.fields[key] = entry

        self.timer_var = ctk.BooleanVar(value=c["timer"])
        ctk.CTkCheckBox(
            page,
            text="Показувати таймер",
            variable=self.timer_var,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=TEXT,
        ).pack(anchor="w", padx=8, pady=(14, 0))

        self.saved_label = ctk.CTkLabel(page, text="", text_color=GREEN, font=ctk.CTkFont(size=12))
        ctk.CTkButton(
            page,
            text="Застосувати",
            command=self._save_custom,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            height=38,
            corner_radius=10,
        ).pack(fill="x", padx=8, pady=(14, 0))
        self.saved_label.pack(pady=(6, 8))
        return page

    def _save_custom(self):
        c = self.cfg.data["custom"]
        c["type"] = ACTIVITY_TYPES[self.type_menu.get()]
        for key, entry in self.fields.items():
            c[key] = entry.get().strip()
        c["timer"] = bool(self.timer_var.get())
        self.cfg.save()
        self.manager.reset_custom_timer()
        self.saved_label.configure(text="Збережено")
        self.after(2000, lambda: self.saved_label.configure(text=""))

    # ---------- налаштування ----------

    def _build_settings(self):
        page = ctk.CTkFrame(self.container, fg_color="transparent")

        app = self._card(page, "Discord Application ID")
        hint = (
            "Необов'язково — у програми вже є вбудований ID."
            if APP_ID
            else "Створіть програму на discord.com/developers/applications.\n"
            "Її назва буде видна в статусі."
        )
        ctk.CTkLabel(
            app, text=hint, text_color=DIM, font=ctk.CTkFont(size=12), justify="left"
        ).pack(anchor="w", padx=16)
        row = ctk.CTkFrame(app, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(8, 14))
        self.id_entry = ctk.CTkEntry(
            row, placeholder_text="Application ID", fg_color=FIELD, border_width=0, height=34
        )
        self.id_entry.pack(side="left", fill="x", expand=True)
        if self.cfg.data["client_id"]:
            self.id_entry.insert(0, self.cfg.data["client_id"])
        ctk.CTkButton(
            row,
            text="Зберегти",
            width=90,
            height=34,
            command=self._save_id,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
        ).pack(side="left", padx=(8, 0))

        general = self._card(page, "Загальні")
        self.opt_vars = {}
        options = [
            ("close_to_tray", "Згортати в трей при закритті"),
            ("start_minimized", "Запускати згорнутою"),
        ]
        if autostart.supported():
            options.insert(0, ("autostart", "Запускати разом з Windows"))
        for key, label in options:
            var = ctk.BooleanVar(value=self.cfg.data[key])
            self.opt_vars[key] = var
            ctk.CTkSwitch(
                general,
                text=label,
                variable=var,
                command=lambda k=key: self._toggle_option(k),
                progress_color=ACCENT,
                text_color=TEXT,
            ).pack(anchor="w", padx=16, pady=(2, 10))

        ext = self._card(page, "Розширення для браузера")
        ctk.CTkLabel(
            ext,
            text="Потрібне, щоб програма бачила, що грає на YouTube.\n"
            "Встановіть його через chrome://extensions → «Завантажити розпаковане».",
            text_color=DIM,
            font=ctk.CTkFont(size=12),
            justify="left",
        ).pack(anchor="w", padx=16)
        ctk.CTkButton(
            ext,
            text="Відкрити папку розширення",
            command=self._open_extension,
            fg_color=FIELD,
            hover_color=BG,
            height=34,
        ).pack(fill="x", padx=16, pady=(8, 14))
        return page

    def _save_id(self):
        value = self.id_entry.get().strip()
        if value and not value.isdigit():
            messagebox.showerror(APP_NAME, "Application ID — це лише цифри.")
            return
        self.cfg.data["client_id"] = value
        self.cfg.save()

    def _toggle_option(self, key):
        value = bool(self.opt_vars[key].get())
        self.cfg.data[key] = value
        self.cfg.save()
        if key == "autostart":
            try:
                autostart.set_enabled(value)
            except OSError:
                messagebox.showerror(APP_NAME, "Не вдалося змінити автозапуск.")

    def _open_extension(self):
        folder = BASE_DIR / "extension"
        if not folder.exists():
            messagebox.showinfo(APP_NAME, f"Папку не знайдено:\n{folder}")
            return
        if sys.platform == "win32":
            os.startfile(folder)
        else:
            import webbrowser

            webbrowser.open(folder.as_uri())

    # ---------- життєвий цикл ----------

    def refresh(self):
        if self._pending == "show":
            self._pending = None
            self.deiconify()
            self.lift()
            self.focus_force()
        elif self._pending == "quit":
            self.quit_app()
            return

        st = self.manager.status()
        if not self.cfg.effective_client_id():
            conn = (ORANGE, "Вкажіть Application ID в налаштуваннях")
        elif st["connected"]:
            conn = (GREEN, "Підключено до Discord")
        else:
            conn = (RED, ERRORS.get(st["error"], "Очікую на Discord…"))
        if conn != self._last_conn:
            self._last_conn = conn
            self.dot.configure(text_color=conn[0])
            self.conn_label.configure(text=conn[1])

        view = st["view"]
        marker = tuple(view.values()) if view else None
        if marker != self._last_view:
            self._last_view = marker
            if view:
                self.src_label.configure(text=view["source"].upper())
                self.title_label.configure(text=view["title"] or "—")
                self.sub_label.configure(text=view["subtitle"])
            else:
                self.src_label.configure(text="")
                self.title_label.configure(text="Нічого не транслюється")
                self.sub_label.configure(text="Увімкніть музику чи відео на YouTube")

        self.after(500, self.refresh)

    def on_close(self):
        if self.cfg.data["close_to_tray"] and self.tray:
            self.withdraw()
        else:
            self.quit_app()

    def quit_app(self):
        self._on_shutdown()
        if self.tray:
            self.tray.stop()
        self.destroy()
