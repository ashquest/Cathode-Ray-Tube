# Cathode Ray Tube (CRT) 📺

> **Turn off, tune in, drop out.** A distraction-free, nostalgic TV experience powered by YouTube content.

`cathode-ray-tube` is a web application that reimagines watching internet video by bringing back the serendipity and constraints of traditional broadcast television. Select a channel, sit back, and watch what’s currently playing. No endless scrolling, no playbar scrubbing, and no speeding through content—just channel surfing like it's 1995.

---

## ⚡ Features

* **Authentic TV Experience:** Video playback runs strictly in real time. 
* **Zero Scrubbing Control:** Seek forward, seek backward, pause, and playback speed adjustments are intentionally disabled.
* **Channel Surfing:** Switch seamlessly between themed channels (e.g., Sci-Fi, Documentaries, Retro Cartoons, Music Videos).
* **Automated Program Guide:** Videos are dynamically curated from YouTube playlists and channels to form continuous broadcast schedules.
* **Retro Aesthetics:** Optional CRT screen effects (scanlines, screen flicker, static transitions on channel switch).

---

## 🛠️ How It Works

1. **Content Curation:** Categories and channels map to specific YouTube playlists or channel IDs configured in the app's settings.
2. **Pseudo-Live Sync:** Playback timestamps are calculated relative to an internal clock. When you switch to a channel, the video starts playing at the *exact point* it would be if it were broadcasting continuously in real time.
3. **Restricted Controls:** The standard YouTube player UI is masked and controlled strictly through custom TV-like interactions (Channel UP/DOWN, Power, Volume).

---

## 🎛️ Channel Configuration

Channels can be modified or added in `lists/list.json`. 


## ⚠️ Disclaimer

This project is not affiliated with, endorsed by, or sponsored by YouTube or Google LLC. All content is embedded using YouTube's standard embed APIs in accordance with their Terms of Service.
