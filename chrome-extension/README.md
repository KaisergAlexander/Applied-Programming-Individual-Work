# Chrome Extension: Dashboard New Tab

A Chrome extension that replaces the new-tab page with a personal dashboard in the style of [Momentum](https://momentumdash.com/): a full-screen photo, a big clock, a greeting, your focus for the day, a to-do list, the weather and a daily quote. It is built from scratch with plain HTML, CSS and JavaScript (Manifest V3, no frameworks, no build step).

## Features
- **Clock and greeting**: 24h or 12h clock, "Good morning / afternoon / evening, *name*". Click your name to change it.
- **Daily focus**: type your main goal for today, tick it off when done. It resets automatically on the next day.
- **To-do list**: add, check off and delete tasks. The button shows how many are still open.
- **Weather**: current temperature and weather icon for your location from [Open-Meteo](https://open-meteo.com/) (no API key). Celsius or Fahrenheit. If you deny the location permission, the widget is simply hidden.
- **Daily quote**: one bundled quote per day, so it works offline.
- **Background**: a new photo every day (from picsum.photos), a "New photo" button, or a plain gradient. Without internet it falls back to the gradient.
- **Settings** (gear icon, bottom left): clock format, temperature unit, background.
- Everything you enter is stored locally in your browser with `chrome.storage.local`. Nothing is sent to any server of mine.

## Installation (no store needed)
1. Download or clone this repository.
2. Open Chrome and go to `chrome://extensions`.
3. Turn on **Developer mode** (top right).
4. Click **Load unpacked** and select this folder (the one containing `manifest.json`).
5. Open a new tab. The dashboard appears. Allow the location request if you want the weather.

To update after changing the code: click the reload icon on the extension's card in `chrome://extensions`, then open a new tab.

## Project structure
| File | Purpose |
|---|---|
| `manifest.json` | Extension configuration (Manifest V3): overrides the new tab, permissions `storage` and `geolocation`, access to `api.open-meteo.com` only |
| `newtab.html` | Page layout |
| `style.css` | Styling (full-screen background, overlay, responsive text sizes) |
| `script.js` | Logic: clock, greeting, focus, to-do, weather, background, settings, storage |
| `quotes.js` | The bundled list of quotes |
| `icons/` | Extension icons (16, 48, 128 px) |

## How it works
- `chrome_url_overrides.newtab` in the manifest tells Chrome to open `newtab.html` instead of the default new tab.
- State (name, focus, todos, settings) lives in `chrome.storage.local`. The weather response is cached for 30 minutes to avoid repeated requests.
- User text is always inserted with `textContent`, never as HTML.
- The weather needs the browser's geolocation: coordinates are sent only to Open-Meteo to fetch the forecast.

## Troubleshooting
- **No weather shown**: location permission was denied or you are offline. Reset it via the lock icon next to the address bar.
- **No photo, only a gradient**: you are offline or picsum.photos is unreachable.
- **Page does not change after editing code**: reload the extension in `chrome://extensions`.
