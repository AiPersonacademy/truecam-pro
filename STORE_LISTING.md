# TrueCam Pro — Chrome Web Store Publishing Package

Everything you need to publish **TrueCam Pro** to the Chrome Web Store and start receiving user donations.

---

## 1. Store Metadata

- **Extension Name:** `TrueCam Pro — Hardware Webcam Mirror & Flip`
- **Short Name:** `TrueCam Pro`
- **Summary (Under 132 characters):**
  > Mirror, flip, and rotate your outgoing webcam stream on Google Meet, Zoom, and Teams so remote callers see text and gestures naturally.
- **Category:** Productivity / Workflow & Planning
- **Language:** English

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

## 3. Chrome Web Store Review Justification (Mandatory)

When submitting to the Chrome Web Store developer dashboard, Google requires a written justification for permissions:

- **Single Purpose Description:**
  > Provides hardware-level stream mirroring, inversion, and rotation for WebRTC camera inputs across video conferencing websites.
- **Permission Justification (`storage`):**
  > Used exclusively to save user orientation preferences (horizontal flip, vertical invert, rotation angle) locally on their device so settings persist across browser sessions.
- **Host Permission Justification (`<all_urls>`):**
  > Required to inject the WebRTC stream transformer across video calling platforms (Google Meet, Zoom, Teams, Discord, and proprietary enterprise conference portals) requested by the user.

---

## 4. Privacy Policy (Mandatory Template)

Host this on GitHub Pages, Notion, or a free static page:

```markdown
# Privacy Policy for TrueCam Pro
Last updated: September 2026

TrueCam Pro ("the Extension") is committed to protecting your privacy.

1. Information Collection and Use
TrueCam Pro does not collect, transmit, store, or sell any personal data, video feeds, audio recordings, or browsing history.

2. Camera and Media Stream Access
The Extension operates exclusively on the client-side within your browser. Video frames processed by the Extension are modified in local memory for the purpose of mirroring or rotating your outgoing webcam stream. No video or audio data is ever transmitted to external servers.

3. Local Storage
The Extension uses Chrome's `storage.local` API solely to remember your preferred orientation settings (such as mirror toggle and rotation angle) on your local device.

4. Third-Party Services
The Extension does not integrate any third-party tracking, analytics, or advertising SDKs.

Contact:
For questions or support, please reach out via the official Chrome Web Store support tab.
```

---

## 5. Visual Store Assets Included

The extension directory already includes your generated store assets:
1. **App Icons:** `icons/icon16.png`, `icons/icon48.png`, `icons/icon128.png`
2. **Promotional Marquee Banner (1280x800):** `icons/promo_banner_1280x800.jpg`
3. **Popup Interface Screenshot:** `popup_preview.png`
