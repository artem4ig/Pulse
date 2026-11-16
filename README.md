# Pulse

**English** · [Українська](#українська)

Pulse is a small desktop app that shows what you're listening to or watching on **YouTube Music** and **YouTube** in your Discord profile. You can also set your own custom status with a title, description, image, button and timer.

It uses only the official Discord Rich Presence API. No Discord token, no account access, nothing leaves your computer.

## Features

- **YouTube Music** → "Listening to" with track, artist, cover art, progress bar and an "open track" button
- **YouTube** → "Watching" with video title, channel, thumbnail and a "watch" button
- **Custom status** → activity type (Playing / Listening / Watching / Competing), title, description, image by URL, button, timer
- **Auto mode or custom mode**, with an optional fallback: show your custom status when nothing is playing
- Per-source toggles (turn YouTube or YouTube Music off separately)
- Minimal dark interface, tray icon, autostart with Windows, start minimized
- Status disappears automatically on pause or when the tab is closed
- Single-instance protection and automatic reconnect if Discord is restarted

## How it works

```
Browser tab ──► Extension ──► Pulse (127.0.0.1:48200) ──► Discord Rich Presence
```

1. A content script in the browser extension reads the current track or video from the page (title, artist, cover, position, duration) every 3 seconds.
2. The extension's background worker sends it to Pulse over a local HTTP request to `127.0.0.1`.
3. Pulse decides what to show (auto or custom status) and sends it to the Discord desktop client through its local IPC pipe.
4. If no data arrives for 12 seconds, or the media is paused, the status is cleared.

## Tech stack

| Part | Technology |
|---|---|
| Language | Python 3.9+ |
| GUI | [customtkinter](https://github.com/TomSchimansky/CustomTkinter) (on top of tkinter) |
| Discord | [pypresence](https://github.com/qwertyquerty/pypresence) (Rich Presence over local IPC) |
| Tray icon | [pystray](https://github.com/moses-palmer/pystray) + [Pillow](https://python-pillow.org/) |
| Local receiver | `http.server` (`ThreadingHTTPServer`) from the standard library |
| Config | JSON file in `%APPDATA%\Pulse` |
| Autostart | `winreg` (Windows registry, `HKCU\...\Run`) |
| Browser extension | JavaScript, Chrome Extension Manifest V3, [Media Session API](https://developer.mozilla.org/docs/Web/API/Media_Session_API) |
| Packaging | [PyInstaller](https://pyinstaller.org/) |

## Requirements

- Windows (macOS and Linux should work for the status itself, but autostart is Windows-only and untested elsewhere)
- Python 3.9 or newer (not needed if you use the built `.exe`)
- Discord **desktop** client running on the same machine (the web version is not supported)
- A Chromium-based browser: Chrome, Edge, Brave, Opera, Vivaldi
- In Discord: *User Settings → Activity Privacy → Share your detected activity with others* must be on

## Installation

### 1. Create a Discord application

1. Go to <https://discord.com/developers/applications> and click **New Application**.
2. Give it a name. **This name is shown in your status**, for example "Listening to *YouTube Music*".
3. Copy the **Application ID** from the *General Information* page.

### 2. Run Pulse

```bash
git clone https://github.com/<your-name>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
python main.py
```

Open the **Settings** tab and paste your Application ID.

### 3. Install the browser extension

1. Open `chrome://extensions` (or `edge://extensions`).
2. Enable **Developer mode**.
3. Click **Load unpacked** and select the `extension` folder.
4. Reload any open YouTube / YouTube Music tabs.

Start playing something. The status should show up in Discord within a few seconds.

## Usage

**Home**: shows what is currently being broadcast, the Discord connection state, source toggles and the mode switch (Auto / Custom).

**Custom status**: fill in the fields and press *Apply*. Switch the mode to *Custom* on the Home tab to show it. Notes:

- *Image* must be a direct link (`https://...`) to a picture.
- *Button* needs both a text and a link starting with `http`.
- Discord does not show your own buttons to you, only to other people.

**Settings**: Application ID, autostart, start minimized, close to tray, shortcut to the extension folder.

## Build a standalone .exe

```bat
build.bat
```

The result appears in `dist/`: `Pulse.exe` and the `extension` folder. Keep them side by side, the app opens the extension folder from there.

## Configuration

Settings are stored in `%APPDATA%\Pulse\config.json` (on other systems `~/.config/Pulse/config.json`). You can edit it manually while the app is closed.

If you publish your own build and want users to skip the "create an application" step, set your Application ID in `APP_ID` inside `pulse/constants.py`.

The local port (`48200`) is defined in two places: `pulse/constants.py` and `extension/background.js`. Change both if the port is taken.

## Troubleshooting

| Problem | What to check |
|---|---|
| "Invalid Application ID" | Use the **Application ID** (digits only), not the public key, secret or a bot token |
| "Discord is not running" | Open the desktop Discord client; the browser version does not work |
| Connected but no status | Reload the YouTube tab after installing the extension; check *Activity Privacy* in Discord; make sure the track is actually playing, not paused |
| "Already running" on start | Pulse is already open (check the tray) or another program uses port 48200 |
| No cover image | Some images are not accepted by Discord; the status works without it |

## Project structure

```
main.py              entry point
requirements.txt
build.bat            .exe build script
pulse/
  presence.py        Discord connection and status logic
  server.py          local HTTP receiver for the extension
  ui.py              interface (customtkinter)
  tray.py            tray icon (pystray)
  config.py          settings storage
  autostart.py       Windows autostart
  constants.py       app name, port, built-in Application ID
extension/
  manifest.json      Manifest V3
  content.js         reads track/video info from the page
  background.js      forwards data to the local app
```

## Privacy

Pulse runs entirely on your machine. The extension talks only to `127.0.0.1`. The only data sent outside is the status itself, which goes to Discord through the official Rich Presence API. Nothing is collected or stored remotely.

## Contributing

Issues and pull requests are welcome. For larger changes please open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE)

---

<a name="українська"></a>

# Pulse

[English](#pulse) · **Українська**

Pulse це невелика програма для ПК, яка показує у вашому профілі Discord, що ви слухаєте або дивитесь на **YouTube Music** і **YouTube**. Також можна поставити власний статус із заголовком, описом, картинкою, кнопкою та таймером.

Використовується лише офіційний Discord Rich Presence API. Жодних токенів і доступу до акаунта, і нічого не виходить за межі вашого комп'ютера.

## Можливості

- **YouTube Music** → «Слухає»: трек, виконавець, обкладинка, смужка прогресу та кнопка «Слухати»
- **YouTube** → «Дивиться»: назва відео, канал, мініатюра та кнопка «Дивитись»
- **Власний статус** → тип активності (Грає / Слухає / Дивиться / Змагається), заголовок, опис, картинка за посиланням, кнопка, таймер
- **Автоматичний або власний режим**, а також опція показувати власний статус, коли нічого не грає
- Окремі перемикачі для кожного джерела (YouTube і YouTube Music вмикаються незалежно)
- Мінімалістичний темний інтерфейс, іконка в треї, автозапуск з Windows, запуск згорнутою
- Статус сам зникає при паузі або закритті вкладки
- Захист від другого запуску та автоматичне перепідключення, якщо Discord перезапустили

## Як це працює

```
Вкладка браузера ──► Розширення ──► Pulse (127.0.0.1:48200) ──► Discord Rich Presence
```

1. Скрипт розширення кожні 3 секунди зчитує зі сторінки поточний трек або відео (назву, виконавця, обкладинку, позицію, тривалість).
2. Фоновий скрипт розширення надсилає це в Pulse локальним HTTP-запитом на `127.0.0.1`.
3. Pulse вирішує, що показувати (автоматичний чи власний статус), і передає це в десктопний Discord через локальний IPC.
4. Якщо дані не надходять 12 секунд або відео на паузі, статус прибирається.

## Технології

| Частина | Технологія |
|---|---|
| Мова | Python 3.9+ |
| Інтерфейс | [customtkinter](https://github.com/TomSchimansky/CustomTkinter) (надбудова над tkinter) |
| Discord | [pypresence](https://github.com/qwertyquerty/pypresence) (Rich Presence через локальний IPC) |
| Іконка в треї | [pystray](https://github.com/moses-palmer/pystray) + [Pillow](https://python-pillow.org/) |
| Локальний приймач | `http.server` (`ThreadingHTTPServer`) зі стандартної бібліотеки |
| Налаштування | JSON-файл у `%APPDATA%\Pulse` |
| Автозапуск | `winreg` (реєстр Windows, `HKCU\...\Run`) |
| Розширення | JavaScript, Chrome Extension Manifest V3, [Media Session API](https://developer.mozilla.org/docs/Web/API/Media_Session_API) |
| Збірка | [PyInstaller](https://pyinstaller.org/) |

## Вимоги

- Windows (сам статус має працювати і на macOS та Linux, але автозапуск лише для Windows, а на інших системах не перевірялось)
- Python 3.9 або новіший (не потрібен, якщо використовуєте готовий `.exe`)
- **Десктопний** Discord, запущений на цьому ж ПК (веб-версія не підтримується)
- Браузер на Chromium: Chrome, Edge, Brave, Opera, Vivaldi
- У Discord: *Налаштування → Приватність активності → Ділитися виявленою активністю* має бути увімкнено

## Встановлення

### 1. Створіть програму в Discord

1. Відкрийте <https://discord.com/developers/applications> і натисніть **New Application**.
2. Дайте їй назву. **Саме ця назва показується у вашому статусі**, наприклад «Слухає *YouTube Music*».
3. На сторінці *General Information* скопіюйте **Application ID**.

### 2. Запустіть Pulse

```bash
git clone https://github.com/<your-name>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
python main.py
```

Відкрийте вкладку **Налаштування** і вставте Application ID.

### 3. Встановіть розширення для браузера

1. Відкрийте `chrome://extensions` (або `edge://extensions`).
2. Увімкніть **Режим розробника**.
3. Натисніть **Завантажити розпаковане** і виберіть папку `extension`.
4. Перезавантажте відкриті вкладки YouTube / YouTube Music.

Увімкніть щось, і за кілька секунд статус з'явиться в Discord.

## Використання

**Головна**: що зараз транслюється, стан підключення до Discord, перемикачі джерел і режим (Автоматично / Свій статус).

**Свій статус**: заповніть поля й натисніть *Застосувати*. Щоб він показувався, на вкладці «Головна» оберіть режим *Свій статус*. Нотатки:

- *Зображення* має бути прямим посиланням (`https://...`) на картинку.
- Для *кнопки* потрібні і текст, і посилання, що починається з `http`.
- Discord не показує вам ваші ж кнопки, їх бачать лише інші люди.

**Налаштування**: Application ID, автозапуск, запуск згорнутою, закриття в трей, швидкий перехід до папки розширення.

## Збірка окремого .exe

```bat
build.bat
```

Результат з'явиться в `dist/`: `Pulse.exe` і папка `extension`. Тримайте їх поруч, бо програма відкриває папку розширення звідти.

## Конфігурація

Налаштування зберігаються в `%APPDATA%\Pulse\config.json` (на інших системах `~/.config/Pulse/config.json`). Файл можна редагувати вручну, поки програма закрита.

Якщо публікуєте власну збірку й хочете, щоб користувачі не створювали програму в Discord, впишіть свій Application ID в `APP_ID` у файлі `pulse/constants.py`.

Порт локального сервера (`48200`) задано у двох місцях: `pulse/constants.py` і `extension/background.js`. Якщо порт зайнятий, змініть в обох.

## Часті проблеми

| Проблема | Що перевірити |
|---|---|
| «Невірний Application ID» | Потрібен саме **Application ID** (лише цифри), а не публічний ключ, секрет чи токен бота |
| «Discord не запущено» | Відкрийте десктопний Discord, у браузерній версії не працює |
| Підключено, але статусу немає | Перезавантажте вкладку YouTube після встановлення розширення; перевірте «Приватність активності» в Discord; переконайтесь, що трек справді грає, а не на паузі |
| «Вже запущено» при старті | Pulse уже відкритий (перевірте трей) або порт 48200 зайнятий іншою програмою |
| Немає обкладинки | Discord приймає не всі зображення, а статус працює і без неї |

## Структура проєкту

```
main.py              точка входу
requirements.txt
build.bat            скрипт збірки .exe
pulse/
  presence.py        з'єднання з Discord і логіка статусу
  server.py          локальний HTTP-приймач для розширення
  ui.py              інтерфейс (customtkinter)
  tray.py            іконка в треї (pystray)
  config.py          збереження налаштувань
  autostart.py       автозапуск Windows
  constants.py       назва, порт, вбудований Application ID
extension/
  manifest.json      Manifest V3
  content.js         зчитує дані про трек/відео зі сторінки
  background.js      передає дані в локальну програму
```

## Приватність

Pulse повністю працює на вашому ПК. Розширення звертається лише до `127.0.0.1`. Назовні йде тільки сам статус: він передається в Discord через офіційний Rich Presence API. Нічого не збирається і не зберігається віддалено.

## Участь у розробці

Issues і pull request'и вітаються. Для великих змін спершу створіть issue, щоб обговорити, що саме хочете змінити.

## Ліцензія

[MIT](LICENSE)
