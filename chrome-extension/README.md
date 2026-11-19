# Chrome Extension: Dashboard New Tab

A Chrome extension that replaces the new-tab page with a personal dashboard in the style of [Momentum](https://momentumdash.com/): a full-screen photo, a big clock, a greeting, your focus for the day, a to-do list, the weather and a daily quote. It is built from scratch with plain HTML, CSS and JavaScript (Manifest V3, no frameworks, no build step).

## Purpose
This is my version of the Momentum Dash browser extension. It replaces Chrome's empty new-tab page with a dashboard that shows the time, a greeting, one focus for the day, a to-do list, the weather and a quote.

## Data collection
- **Weather:** from the free [Open-Meteo](https://open-meteo.com/) API, no key. It uses the browser's location only if the user allows it.
- **Background photo:** a new image each day from picsum.photos.
- **Quotes:** a short list of well-known quotes bundled in `quotes.js`, so it works offline.
- **User input:** name, focus, to-do tasks and settings that the user types.

## Data persistence
Name, focus, tasks and settings are stored in the browser with `chrome.storage.local`, and the weather answer is cached for 30 minutes. Nothing is sent to a server of mine. This is enough because the data is small and personal; an account system would add complexity without benefit.

## User interaction
After installing, every new tab shows the dashboard. Click the name to change it, type a focus and tick it off, add and delete tasks, and use the gear icon for clock format, temperature unit and background.

## Setup
See "Installation (no store needed)" below. No keys or configuration are needed.

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

## Learning
I learned how a browser extension is put together: a `manifest.json` that tells Chrome which page to open and which permissions are needed, plus ordinary HTML, CSS and JavaScript. I also learned to ask for as little as possible: the extension only has `storage` and `geolocation` permission and may only contact `api.open-meteo.com`. Inserting user text with `textContent` instead of as HTML was a practical lesson in basic security.

**A challenge:** the weather depends on the location permission, and users can say no or be offline. I made the weather widget and the photo fail quietly (the widget hides, the background falls back to a gradient) so the page never looks broken.

## Limitations and assistance
- **Not very original:** I stayed close to the Momentum idea. I am not a big fan of this kind of product, and to-do lists and daily goals on every new tab can feel stressful to me. I never decided what I would personally want to see when I open Chrome, so I did not build a distinctive concept. A clearer idea would have been a better project.
- **Only local:** it is installed manually (developer mode) and not published in the Chrome Web Store. Data stays in one browser and does not sync between devices.
- **Photos are random:** picsum.photos gives random images with no choice of theme.
- **AI assistance:** built with Claude Code (Anthropic). I defined the features, loaded the extension in Chrome and tested it (including the weather); Claude Code wrote most of the code. Sources used: the Chrome extension (Manifest V3) documentation, the Open-Meteo documentation, and Momentum as the visual inspiration.
