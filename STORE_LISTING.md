# TrueCam Pro — Multi-Store Publishing Guide & Packages

Everything you need to publish **TrueCam Pro** to the **Google Chrome Web Store**, **Microsoft Edge Add-ons**, and **Mozilla Firefox Add-ons (AMO)**.

---

## 📦 Ready-to-Upload Distribution Packages

The production packages in `dist/` are pre-compiled, lint-verified, and stripped of all development artifacts:

| Marketplace | Target Zip Package | Engine / Spec | Key Architectural Details |
| :--- | :--- | :--- | :--- |
| **Google Chrome Web Store** | `dist/truecam-pro-chrome.zip` | Chromium MV3 (Chrome 111+) | Native `"world": "MAIN"`, `storage.local`, clean manifest |
| **Microsoft Edge Add-ons** | `dist/truecam-pro-edge.zip` | Chromium MV3 | Microsoft Partner Center compliant, Edge store rating link |
| **Mozilla Firefox Add-ons** | `dist/truecam-pro-firefox.zip` | Gecko MV3 (Firefox 109+) | `browser_specific_settings.gecko`, DOM `<script>` injection fallback, `web_accessible_resources`, zero `"world": "MAIN"` warnings |

To re-build or re-verify all packages at any time, run:
```bash
python build_packages.py
```

---

## 1. Store Metadata (Unified Across All Stores)

- **Extension Name:** `TrueCam Pro — Hardware Webcam Mirror & Flip`
- **Short Name:** `TrueCam Pro`
- **Summary / Tagline (Under 132 characters):**
  > Mirror, flip, and rotate your outgoing webcam stream on Google Meet, Zoom, and Teams so remote callers see text and gestures naturally.
- **Category:** Productivity / Workflow & Planning (Edge: Productivity; Firefox: Photos & Media / Appearance)
- **Language:** English
- **Pricing:** Free (With community donation links)

---

## 2. Detailed Store Description (Copy & Paste)

```markdown
Say goodbye to backwards handwriting, unreadable whiteboard notes, and inverted ceiling cameras.

TrueCam Pro is a lightweight, zero-latency WebRTC hardware stream transformer that mirrors and corrects your camera stream at the data level before it reaches Google Meet, Zoom, Microsoft Teams, or Discord.

Unlike superficial CSS flip extensions that only change your local screen, TrueCam Pro transforms the actual outgoing video stream so ALL meeting participants and call recordings see your video properly oriented.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ KEY FEATURES & WHY TRUEDCAM PRO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🪞 Hardware-Level WebRTC Video Mirroring
Flips the camera data stream directly inside the browser's WebRTC engine. What you see is guaranteed to be what all remote participants, teachers, and meeting recorders see.

📖 Whiteboard, Book & Document Reading Mode (Backwards Text Fix)
Solve the classic video conferencing headache: holding up notes, handwritten sketches, physical books, or index cards to your camera. Text is instantly rendered left-to-right, crisp, and 100% readable to everyone on the call.

🙃 Ceiling Mount & Boom Arm Inversion (180° Flip)
Using an overhead document camera, tripod rig, or inverted ceiling webcam? Invert vertically with a single tap to instantly orient your video right-side up.

📐 4-Way Angle Rotation (0°, 90°, 180°, 270°)
Essential for portrait monitors, mobile webcams, vertical live streaming, and side-mounted setups.

⚡ Ultra-Low Latency (<1ms), No Heavy Virtual Drivers
Unlike OBS Studio, ManyCam, or virtual webcam desktop drivers, TrueCam Pro requires NO desktop software, NO driver installations, and consumes near-zero CPU/GPU overhead.

🔒 100% Private, Local & Secure
Operates 100% client-side. Your camera stream is processed strictly in your browser's memory and NEVER leaves your device. No cloud processing, zero analytics, zero data logging.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 COMPATIBLE WEBRTC PLATFORMS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Google Meet (meet.google.com)
• Zoom Web Client (zoom.us)
• Microsoft Teams Web (teams.microsoft.com)
• Discord Web (discord.com)
• Slack Huddles
• Blackboard, Canvas, and online classroom portals
• Any browser-based WebRTC video conferencing application

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 SEARCH KEYWORDS & TAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
google meet mirror camera, flip webcam google meet, zoom camera reversed fix, mirror video call, flip webcam horizontal, inverted webcam fix, ceiling mount camera flip, unmirror webcam, flip webcam text readable, webrtc camera mirror, webcam mirror chrome extension, reading mode webcam, whiteboard text flipped fix.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☕ SUPPORT INDEPENDENT DEVELOPMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TrueCam Pro is completely free, tracker-free, and independently developed. If it saves you time in meetings, classes, or presentations, you can support development:
• Buy Me a Coffee: https://buymeacoffee.com/ab2005
• PayPal: https://paypal.me/boukhrisaymane
• USDT (TRON / TRC-20 Network): TNWXzQRWcBhs3yutz7XMhu4UpN1xkHDwWW
```

---

## 3. Store-Specific Submission Guides

### 🟢 A. Google Chrome Web Store
1. **Developer Portal:** [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
2. **Action:** Click **"New Item"** -> Upload `dist/truecam-pro-chrome.zip`.
3. **Store Listing Tab:**
   - Paste Description from Section 2 above.
   - Upload Icon: `icons/icon128.png`.
   - Upload Promotional Tile / Marquee: `icons/promo_banner_1280x800.jpg` (1280x800).
   - Upload Screenshots: `popup_preview.png` + `docs/guide/step5_pin_and_use.png`.
4. **Privacy Tab:**
   - **Single Purpose Description:**
     > Provides hardware-level stream mirroring, inversion, and rotation for WebRTC camera inputs across video conferencing websites.
   - **Permission Justification (`storage`):**
     > Used exclusively to save user orientation preferences (horizontal flip, vertical invert, rotation angle) locally on their device so settings persist across browser sessions.
   - **Host Permission Justification (`<all_urls>`):**
     > Required to inject the WebRTC stream transformer across video calling platforms (Google Meet, Zoom, Teams, Discord, and proprietary enterprise conference portals) requested by the user.
   - **Data Usage:** Select "This extension does not collect or transmit user data."
5. **Submit for Review.**

---

### 🔵 B. Microsoft Edge Add-ons
1. **Developer Portal:** [Microsoft Partner Center](https://partner.microsoft.com/en-us/dashboard/microsoftedge)
2. **Action:** Click **"Create new extension"** -> Upload `dist/truecam-pro-edge.zip`.
3. **Store Listing:**
   - Name: `TrueCam Pro — Hardware Webcam Mirror & Flip`
   - Description: Paste Description from Section 2.
   - Extension Icon: `icons/icon128.png` (or 300x300 promo).
   - Screenshots: `popup_preview.png` (1280x800 format).
4. **Certification Notes for Reviewer:**
   > TrueCam Pro is a client-side WebRTC camera mirror tool. It intercepts getUserMedia calls on video conferencing sites to apply horizontal and vertical flips requested by the user. All video processing occurs entirely in local memory with no external servers or data collection.
5. **Submit.**

---

### 🟠 C. Mozilla Firefox Add-ons (AMO)
1. **Developer Portal:** [Firefox Add-on Developer Hub](https://addons.mozilla.org/en-US/developers/addon/submit/upload-listed)
2. **Action:** Select **"On this site"** (Listed distribution) -> Upload `dist/truecam-pro-firefox.zip`.
3. **Automated Validation:**
   - The package is tailored for AMO:
     - `gecko.id`: `truecam-pro@aipersonacademy.com`
     - Uses `web_accessible_resources` + DOM script injection (avoids AMO's `"world" is not supported` rejection).
   - Passes automated AMO linter with 0 errors.
4. **Reviewer Notes:**
   > This add-on provides client-side stream flipping and rotation for WebRTC camera inputs. To intercept navigator.mediaDevices.getUserMedia before page scripts execute, main-injector.js is injected into the document root via isolated-bridge.js. No user data, audio, or video is collected or sent over the network.
5. **Submit for Signing and Review.**

---

## 4. Privacy Policy (Mandatory Template)

Host this on GitHub Pages, Notion, or your project site:

```markdown
# Privacy Policy for TrueCam Pro
Last updated: September 2026

TrueCam Pro ("the Extension") is committed to protecting your privacy.

1. Information Collection and Use
TrueCam Pro does not collect, transmit, store, or sell any personal data, video feeds, audio recordings, or browsing history.

2. Camera and Media Stream Access
The Extension operates exclusively on the client-side within your browser. Video frames processed by the Extension are modified in local memory for the purpose of mirroring or rotating your outgoing webcam stream. No video or audio data is ever transmitted to external servers.

3. Local Storage
The Extension uses your browser's local storage API solely to remember your preferred orientation settings (such as mirror toggle and rotation angle) on your local device.

4. Third-Party Services
The Extension does not integrate any third-party tracking, analytics, or advertising SDKs.

Contact:
For questions or support, please open an issue on the official GitHub repository:
https://github.com/AiPersonacademy/truecam-pro
```

---

## 5. Visual Store Assets Included

The extension directory includes all production store assets:
1. **App Icons:** `icons/icon16.png`, `icons/icon32.png`, `icons/icon48.png`, `icons/icon128.png`, `icons/icon512.png`
2. **Promotional Marquee Banner (1280x800):** `icons/promo_banner_1280x800.jpg`
3. **Popup Interface Screenshot:** `popup_preview.png`
4. **Step-by-step Visual Assets:** `docs/guide/step1_download_zip.png` through `step5_pin_and_use.png`
