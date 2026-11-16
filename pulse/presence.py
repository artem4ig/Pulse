import threading
import time

from .constants import STALE_AFTER

SOURCE_LABELS = {"ytmusic": "YouTube Music", "youtube": "YouTube"}


def _clip(text, limit=128):
    text = (text or "").strip()
    if not text:
        return None
    text = text[:limit]
    return text if len(text) >= 2 else text + " "


def _num(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return number if number == number and number != float("inf") else 0.0


class PresenceManager(threading.Thread):
    """Тримає з'єднання з Discord і виставляє потрібну активність."""

    def __init__(self, config):
        super().__init__(daemon=True)
        self.cfg = config
        self._lock = threading.Lock()
        self._halt = threading.Event()

        self._media = None
        self._media_ts = 0.0
        self.custom_started = time.time()

        self._rpc = None
        self._rpc_id = None
        self._next_connect = 0.0
        self._sent_key = None
        self._sent_start = None
        self._last_send = 0.0

        self.connected = False
        self.error = ""
        self.view = None

    # ---------- публічний API ----------

    def push_media(self, raw):
        source = raw.get("source")
        if source not in SOURCE_LABELS:
            return
        now = time.time()
        position = _num(raw.get("position"))
        media = {
            "source": source,
            "title": str(raw.get("title", ""))[:256],
            "artist": str(raw.get("artist", ""))[:256],
            "album": str(raw.get("album", ""))[:256],
            "cover": str(raw.get("cover", ""))[:512],
            "url": str(raw.get("url", ""))[:512],
            "playing": bool(raw.get("playing")),
            "duration": _num(raw.get("duration")),
            "start": int(now - position),
        }
        with self._lock:
            # якщо позиція не змінилась суттєво — лишаємо старий start,
            # щоб не смикати Discord через похибки
            old = self._media
            if (
                old
                and old["title"] == media["title"]
                and old["source"] == source
                and abs(old["start"] - media["start"]) <= 3
            ):
                media["start"] = old["start"]
            self._media = media
            self._media_ts = now

    def reset_custom_timer(self):
        self.custom_started = time.time()

    def status(self):
        with self._lock:
            return {"connected": self.connected, "error": self.error, "view": self.view}

    def stop(self):
        self._halt.set()

    # ---------- основний цикл ----------

    def run(self):
        while not self._halt.is_set():
            try:
                self._tick()
            except Exception:
                self._drop()
                self._next_connect = time.time() + 3
            self._halt.wait(1)
        self._drop(clear=True)

    def _tick(self):
        cid = self.cfg.effective_client_id()
        payload, view = self._desired()
        with self._lock:
            self.view = view

        if not cid:
            self._drop()
            self.error = ""
            return

        if self._rpc is not None and cid != self._rpc_id:
            self._drop()
        if self._rpc is None and not self._connect(cid):
            return

        if payload is None:
            if self._sent_key is not None:
                self._rpc.clear()
                self._sent_key = None
                self._sent_start = None
            return

        key = (
            tuple(sorted((k, str(v)) for k, v in payload.items() if k not in ("start", "end"))),
            payload.get("end", 0) - payload.get("start", 0),
        )
        start = payload.get("start")
        drift = (
            start is not None
            and self._sent_start is not None
            and abs(start - self._sent_start) > 4
        )
        if key == self._sent_key and not drift:
            return
        if time.time() - self._last_send < 2:
            return

        self._send(payload)
        self._sent_key, self._sent_start, self._last_send = key, start, time.time()

    # ---------- що показувати ----------

    def _desired(self):
        data = self.cfg.data
        if data["mode"] == "custom":
            return self._custom()

        media = self._fresh_media()
        if media:
            return self._media_payload(media)

        if data["idle_fallback"]:
            return self._custom()
        return None, None

    def _fresh_media(self):
        with self._lock:
            media, ts = self._media, self._media_ts
        if not media or not media["playing"]:
            return None
        if time.time() - ts > STALE_AFTER:
            return None
        if not self.cfg.data["sources"].get(media["source"], False):
            return None
        return media

    def _media_payload(self, media):
        music = media["source"] == "ytmusic"
        payload = {
            "type": "LISTENING" if music else "WATCHING",
            "details": _clip(media["title"]),
            "state": _clip(media["artist"]),
            "large_text": _clip(media["album"] or SOURCE_LABELS[media["source"]]),
            "start": media["start"],
        }
        if media["duration"] > 0:
            payload["end"] = int(media["start"] + media["duration"])
        if media["cover"].startswith("http"):
            payload["large_image"] = media["cover"]
        if media["url"].startswith("http"):
            payload["buttons"] = [
                {
                    "label": "Слухати в YouTube Music" if music else "Дивитись на YouTube",
                    "url": media["url"],
                }
            ]
        view = {
            "kind": "media",
            "source": SOURCE_LABELS[media["source"]],
            "title": media["title"],
            "subtitle": media["artist"],
        }
        return payload, view

    def _custom(self):
        c = self.cfg.data["custom"]
        details, state = _clip(c["details"]), _clip(c["state"])
        if not details and not state:
            return None, None

        payload = {"type": c["type"], "details": details, "state": state}

        image = c["large_image"].strip()
        if image.startswith("http"):
            payload["large_image"] = image
            payload["large_text"] = _clip(c["large_text"])

        label, url = _clip(c["button_label"], 32), c["button_url"].strip()
        if label and url.startswith("http"):
            payload["buttons"] = [{"label": label, "url": url}]

        if c["timer"]:
            payload["start"] = int(self.custom_started)

        view = {
            "kind": "custom",
            "source": "Свій статус",
            "title": c["details"].strip() or c["state"].strip(),
            "subtitle": c["state"].strip() if c["details"].strip() else "",
        }
        return payload, view

    # ---------- Discord ----------

    def _connect(self, cid):
        if time.time() < self._next_connect:
            return False
        from pypresence import Presence

        rpc = None
        try:
            rpc = Presence(cid)
            rpc.connect()
        except Exception as exc:
            self.error = type(exc).__name__
            self._next_connect = time.time() + 5
            try:
                if rpc is not None:
                    rpc.close()
            except Exception:
                pass
            return False

        self._rpc, self._rpc_id = rpc, cid
        self.connected = True
        self.error = ""
        self._sent_key = None
        self._sent_start = None
        return True

    def _send(self, payload):
        from pypresence import ActivityType

        kwargs = {k: v for k, v in payload.items() if v not in (None, "", [])}
        kwargs["activity_type"] = getattr(ActivityType, kwargs.pop("type"))
        self._rpc.update(**kwargs)

    def _drop(self, clear=False):
        rpc, self._rpc = self._rpc, None
        self.connected = False
        self._sent_key = None
        self._sent_start = None
        if rpc is None:
            return
        try:
            if clear:
                rpc.clear()
        except Exception:
            pass
        try:
            rpc.close()
        except Exception:
            pass
