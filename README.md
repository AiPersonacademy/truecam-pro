# TrueCam Pro 🪞

> **Hardware-Level WebRTC Webcam Stream Mirror, Flip & Rotation Extension**  
> *Engineered for Google Meet, Zoom Web, Microsoft Teams, Discord & Enterprise WebRTC Apps.*

![TrueCam Pro Banner](icons/promo_banner_1280x800.jpg)

<p align="center">
  <img src="https://img.shields.io/badge/Manifest-V3-blue?style=flat-square" alt="Manifest V3">
  <img src="https://img.shields.io/badge/WebRTC-Hardware--Level-emerald?style=flat-square&color=10b981" alt="Hardware Level">
  <img src="https://img.shields.io/badge/Latency-%3C1ms-blueviolet?style=flat-square" alt="Latency">
  <img src="https://img.shields.io/badge/Privacy-100%25%20Client--Side-green?style=flat-square" alt="Privacy">
  <a href="https://buymeacoffee.com/ab2005"><img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-FFDD00?style=flat-square&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"></a>
</p>

---

## 💡 The Problem TrueCam Solves

When you hold up notes, books, or write on a physical whiteboard during a Google Meet or Zoom call:
1. Most video conference tools **reverse or invert your video** to remote callers.
2. Naive browser extensions only apply a CSS `transform: scaleX(-1)` to your personal preview box on your screen — **callers still see backwards, unreadable text!**
3. Desktop virtual cameras (like OBS Studio or ManyCam) require heavy background software, virtual driver installations, and consume massive CPU/GPU resources.

**TrueCam Pro fixes this at the browser's hardware stream layer.**  
It intercepts `navigator.mediaDevices.getUserMedia` before video packets are encoded and transmitted. What you see is guaranteed to be what all remote attendees and recordings receive.

---

## 🖥️ Sleek Native Apple-Style Interface

<p align="center">
  <img src="popup_preview.png" alt="TrueCam Pro Interface" width="340">
</p>

- **Zinc Neutral Design**: Clean, distraction-free macOS / Raycast aesthetic.
- **1-Click Presets**:
  - `Natural Mirror`: Natural reflection for facial camera view.
  - `Whiteboard / Text`: Unmirrored raw view so handwritten notes and book pages are 100% legible to attendees.
  - `Ceiling Cam`: 180° vertical inversion for upside-down webcam boom arms.
- **4-Way Angle Rotation**: `0°`, `90°`, `180°`, `270°` for portrait screens and mobile rigs.
- **Live HUD Monitor**: Compact 16:9 preview viewport with real-time resolution and framerate tracking (`1080p • 30fps`).

---

## 🛠️ Step-by-Step Installation Guide

Follow these 4 simple steps to install TrueCam Pro in any Chromium browser (**Google Chrome, Brave, Microsoft Edge, Opera, Vivaldi**):

### Step 1: Download or Clone the Repository
Clone this repository to your computer:
```bash
git clone https://github.com/YOUR_USERNAME/truecam-pro.git
```
*(Or click **Code > Download ZIP** on GitHub and extract the folder to your PC).*

---

### Step 2: Open Extensions Management
1. In your browser's address bar, navigate to:
   ```text
   chrome://extensions
   ```
   *(For Microsoft Edge, go to `edge://extensions`)*.

---

### Step 3: Enable Developer Mode
In the **top-right corner** of the Extensions page, toggle the **Developer mode** switch to **ON**:

```
+-------------------------------------------------------------+
| Extensions                                [ Developer mode (•) ] |
+-------------------------------------------------------------+
```

---

### Step 4: Load the Unpacked Extension
1. In the **top-left corner**, click the **Load unpacked** button:
   ```
   [ Load unpacked ]  [ Pack extension ]  [ Update ]
   ```
2. In the folder picker dialog, select the `webcam-mirror-extension` folder.
3. **Done!** The TrueCam Pro icon will appear in your browser toolbar. Pin it to your toolbar for instant 1-click access.

---

## 🎥 How to Use in Meetings

1. **Open Google Meet, Zoom, or Teams** in your browser.
2. Click the **TrueCam icon** in your extensions toolbar.
3. Select your desired preset:
   - Click **Natural Mirror** for video meetings.
   - Click **Whiteboard / Text** when holding physical books or handwritten documents to the camera.
   - Click **Ceiling Cam** if your camera is mounted upside-down.
4. Turn on your webcam in the meeting — **your stream is instantly mirrored for all participants!**

---

## 🔬 Built-In Diagnostic Studio

TrueCam includes a standalone diagnostic lab to verify pixel stream manipulation without joining a real meeting:
1. Open the TrueCam popup.
2. Click **"Diagnostic Studio"** at the bottom.
3. Inspect real-time stream resolution, FPS counter, microphone audio levels, and capture instant pixel snapshots.

---

## 🔒 Security & Privacy Invariants

- **100% Client-Side**: Operates entirely in your browser's local memory.
- **Zero Cloud Processing**: Video and audio data are never uploaded to any remote server.
- **No Trackers or Analytics**: Zero third-party telemetry, zero cookies, zero data collection.

---

## ☕ Support Independent Development

TrueCam Pro is 100% free, tracker-free, and independently developed. If it saves you time in meetings, classes, or presentations, you can support development:

- **Buy Me a Coffee**: [buymeacoffee.com/ab2005](https://buymeacoffee.com/ab2005)
- **PayPal**: [paypal.me/boukhrisaymane](https://paypal.me/boukhrisaymane)
- **USDT (TRON Network / TRC-20)**:
  ```text
  TNWXzQRWcBhs3yutz7XMhu4UpN1xkHDwWW
  ```

---

## 📄 License
MIT License © 2026 Aymane Boukhris.
