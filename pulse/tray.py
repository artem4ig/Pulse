from .constants import APP_NAME


def _make_icon():
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((4, 4, 60, 60), fill="#5865F2")
    draw.ellipse((22, 22, 42, 42), fill="white")
    return img


class Tray:
    """Іконка в треї. Колбеки викликаються з іншого потоку."""

    def __init__(self, on_show, on_quit):
        import pystray

        menu = pystray.Menu(
            pystray.MenuItem("Відкрити", lambda *_: on_show(), default=True),
            pystray.MenuItem("Вийти", lambda *_: on_quit()),
        )
        self._icon = pystray.Icon(APP_NAME, _make_icon(), APP_NAME, menu)

    def start(self):
        self._icon.run_detached()

    def stop(self):
        try:
            self._icon.stop()
        except Exception:
            pass
