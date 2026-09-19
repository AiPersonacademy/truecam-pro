import asyncio
from playwright.async_api import async_playwright
import os

TEMPLATES = {
    "step1_download_zip.png": """
    <div class="card">
        <div class="card-header">
            <span class="step-badge">STEP 1</span>
            <h2>Download & Extract the Extension</h2>
        </div>
        <div class="visual-container">
            <!-- Simulated GitHub Bar -->
            <div class="github-bar">
                <div class="repo-info">
                    <span class="repo-owner">AiPersonacademy</span> / <span class="repo-name">truecam-pro</span>
                </div>
                <div class="btn-code active">
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path d="M4.72 3.22a.75.75 0 0 1 1.06 1.06L2.06 8l3.72 3.72a.75.75 0 1 1-1.06 1.06L.47 8.53a.75.75 0 0 1 0-1.06l4.25-4.25zm6.56 0a.75.75 0 0 1 1.06 0l4.25 4.25a.75.75 0 0 1 0 1.06l-4.25 4.25a.75.75 0 0 1-1.06-1.06L13.94 8l-3.72-3.72a.75.75 0 0 1 0-1.06z"/></svg>
                    <span>&lt;&gt; Code</span>
                    <span class="arrow-down">▼</span>
                </div>
            </div>

            <!-- Dropdown Menu -->
            <div class="github-dropdown">
                <div class="dropdown-item">
                    <span>Clone HTTPS</span>
                </div>
                <div class="dropdown-item">
                    <span>Open with GitHub Desktop</span>
                </div>
                <div class="dropdown-separator"></div>
                <div class="dropdown-item highlight">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M2.75 14A1.75 1.75 0 0 1 1 12.25v-2.5a.75.75 0 0 1 1.5 0v2.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25v-2.5a.75.75 0 0 1 1.5 0v2.5A1.75 1.75 0 0 1 13.25 14Z"/><path d="M7.25 7.689V2a.75.75 0 0 1 1.5 0v5.689l1.97-1.969a.749.749 0 1 1 1.06 1.06l-3.25 3.25a.749.749 0 0 1-1.06 0L4.22 6.78a.749.749 0 1 1 1.06-1.06l1.97 1.969Z"/></svg>
                    <strong>Download ZIP</strong>
                    <span class="callout-pill">Click Here</span>
                </div>
            </div>

            <!-- Extract Tip Callout -->
            <div class="callout-box">
                <span class="callout-icon">📁</span>
                <div class="callout-text">
                    <strong>Next: Right-click the downloaded .zip file &rarr; "Extract All..."</strong>
                    <p>Unzip the files to a normal folder on your computer (e.g. in your Downloads or Desktop).</p>
                </div>
            </div>
        </div>
    </div>
    """,

    "step2_open_chrome_extensions.png": """
    <div class="card">
        <div class="card-header">
            <span class="step-badge">STEP 2</span>
            <h2>Open Extensions in Google Chrome</h2>
        </div>
        <div class="visual-container">
            <!-- Simulated Chrome Browser Address Bar -->
            <div class="browser-chrome">
                <div class="browser-nav">
                    <span class="nav-btn">&larr;</span>
                    <span class="nav-btn">&rarr;</span>
                    <span class="nav-btn">&#x21bb;</span>
                </div>
                <div class="address-bar-highlight">
                    <span class="lock-icon">&#128274;</span>
                    <span class="url-text">chrome://extensions</span>
                    <span class="enter-badge">&crarr; Press Enter</span>
                </div>
            </div>

            <!-- Alternative Menu Way -->
            <div class="alt-method-card">
                <span class="alt-tag">OR ALTERNATIVE WAY</span>
                <p>Click the <strong>3 dots menu (&vellip;)</strong> in the top right of Chrome &rarr; <strong>Extensions</strong> &rarr; <strong>Manage extensions</strong>.</p>
            </div>
        </div>
    </div>
    """,

    "step3_enable_developer_mode.png": """
    <div class="card">
        <div class="card-header">
            <span class="step-badge">STEP 3</span>
            <h2>Turn ON "Developer mode"</h2>
        </div>
        <div class="visual-container">
            <div class="extensions-topbar">
                <div class="ext-title-group">
                    <span class="hamburger">&equiv;</span>
                    <span class="ext-heading">Extensions</span>
                </div>
                <div class="devmode-group-highlight">
                    <span class="devmode-label">Developer mode</span>
                    <div class="toggle-switch active">
                        <span class="toggle-thumb"></span>
                    </div>
                    <div class="callout-pointer">
                        <span class="pointer-arrow">&rarr;</span>
                        <span class="pointer-text">SWITCH THIS TO ON</span>
                    </div>
                </div>
            </div>

            <div class="tip-banner">
                <span class="tip-icon">&#128161;</span>
                <p>Turning on Developer Mode unlocks the <strong>"Load unpacked"</strong> button shown in the next step.</p>
            </div>
        </div>
    </div>
    """,

    "step4_click_load_unpacked.png": """
    <div class="card">
        <div class="card-header">
            <span class="step-badge">STEP 4</span>
            <h2>Click "Load unpacked" & Select Folder</h2>
        </div>
        <div class="visual-container">
            <div class="button-bar-sim">
                <div class="btn-load-unpacked highlight">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg>
                    <strong>Load unpacked</strong>
                    <div class="click-indicator">👆 Click Here</div>
                </div>
                <div class="btn-secondary-sim">Pack extension</div>
                <div class="btn-secondary-sim">Update</div>
            </div>

            <!-- Simulated Folder Picker -->
            <div class="folder-picker-sim">
                <div class="picker-header">Select Extension Directory</div>
                <div class="folder-row selected">
                    <span class="folder-icon">📁</span>
                    <span class="folder-name">webcam-mirror-extension</span>
                    <span class="check-badge">✓ Selected</span>
                </div>
                <div class="picker-footer">
                    <button class="btn-select-folder">Select Folder</button>
                </div>
            </div>
        </div>
    </div>
    """,

    "step5_pin_and_use.png": """
    <div class="card">
        <div class="card-header">
            <span class="step-badge">STEP 5</span>
            <h2>Pin to Toolbar & Open Meeting!</h2>
        </div>
        <div class="visual-container step5-grid">
            <!-- Toolbar Pin simulation -->
            <div class="step5-col">
                <span class="col-title">1. Pin TrueCam to Toolbar</span>
                <div class="puzzle-menu-sim">
                    <div class="puzzle-row">
                        <span class="puzzle-icon">🧩</span>
                        <span>Click Extensions Puzzle</span>
                    </div>
                    <div class="puzzle-subrow selected">
                        <img src="../icons/icon48.png" width="18" height="18" style="border-radius:4px;">
                        <strong>TrueCam Pro</strong>
                        <span class="pin-active">📌 Pinned</span>
                    </div>
                </div>
            </div>

            <!-- Live Meeting simulation -->
            <div class="step5-col">
                <span class="col-title">2. Ready in Google Meet & Zoom</span>
                <div class="meeting-box-sim">
                    <div class="meeting-header">
                        <span class="green-dot">●</span>
                        <span>Google Meet (Stream Mirrored 🪞)</span>
                    </div>
                    <div class="preview-mini-feed">
                        <div class="readability-badge">✓ Text Reads Correctly (ABC 123)</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
}

CSS = """
:root {
    --bg-page: #0b0f19;
    --bg-card: #131b2e;
    --bg-elevated: #1e293b;
    --border: rgba(255, 255, 255, 0.12);
    --accent: #2563eb;
    --accent-light: #3b82f6;
    --success: #10b981;
    --text-primary: #f8fafc;
    --text-muted: #94a3b8;
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; font-family: var(--font); }
body {
    background-color: var(--bg-page);
    color: var(--text-primary);
    width: 820px;
    height: 440px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.card {
    width: 100%;
    height: 100%;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 12px;
}

.step-badge {
    background: var(--accent);
    color: #fff;
    font-size: 11px;
    font-weight: 800;
    padding: 4px 10px;
    border-radius: 20px;
    letter-spacing: 0.8px;
}

.card-header h2 {
    font-size: 20px;
    font-weight: 700;
    color: #fff;
}

.visual-container {
    flex: 1;
    background: #090d16;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    gap: 16px;
}

/* Step 1 */
.github-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #161b22;
    border: 1px solid #30363d;
    padding: 10px 16px;
    border-radius: 8px;
}
.repo-owner { color: #58a6ff; font-weight: 500; }
.repo-name { color: #fff; font-weight: 700; }
.btn-code {
    background: #238636;
    color: #fff;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
}
.github-dropdown {
    align-self: flex-end;
    width: 280px;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.6);
    overflow: hidden;
    margin-top: -8px;
}
.dropdown-item {
    padding: 10px 14px;
    font-size: 13px;
    color: #c9d1d9;
    display: flex;
    align-items: center;
    gap: 8px;
}
.dropdown-separator { height: 1px; background: #30363d; }
.dropdown-item.highlight {
    background: rgba(35, 134, 54, 0.15);
    border: 2px solid #2ea043;
    border-radius: 6px;
    margin: 4px;
    color: #fff;
    justify-content: space-between;
}
.callout-pill {
    background: #238636;
    color: #fff;
    font-size: 10.5px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 12px;
}
.callout-box {
    background: rgba(59, 130, 246, 0.1);
    border: 1px dashed rgba(59, 130, 246, 0.4);
    border-radius: 8px;
    padding: 12px 14px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.callout-icon { font-size: 24px; }
.callout-text strong { color: #60a5fa; font-size: 13px; display: block; }
.callout-text p { color: var(--text-muted); font-size: 11.5px; margin-top: 2px; }

/* Step 2 */
.browser-chrome {
    background: #202124;
    border: 1px solid #3c4043;
    border-radius: 10px;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.browser-nav { display: flex; gap: 10px; color: #9aa0a6; font-size: 16px; }
.address-bar-highlight {
    flex: 1;
    background: #303134;
    border: 2px solid #8ab4f8;
    border-radius: 20px;
    padding: 8px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 0 12px rgba(138, 180, 248, 0.3);
}
.url-text { font-size: 15px; font-weight: 600; color: #fff; font-family: ui-monospace, monospace; }
.enter-badge { background: #8ab4f8; color: #202124; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 6px; }
.alt-method-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 12.5px;
    color: var(--text-muted);
}
.alt-tag { font-size: 9.5px; font-weight: 800; color: #94a3b8; display: block; margin-bottom: 4px; }

/* Step 3 */
.extensions-topbar {
    background: #202124;
    border: 1px solid #3c4043;
    border-radius: 10px;
    padding: 14px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.ext-title-group { display: flex; align-items: center; gap: 12px; }
.hamburger { font-size: 20px; color: #9aa0a6; }
.ext-heading { font-size: 18px; font-weight: 600; color: #fff; }
.devmode-group-highlight {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(138, 180, 248, 0.12);
    border: 2px solid #8ab4f8;
    padding: 6px 14px;
    border-radius: 30px;
    position: relative;
    box-shadow: 0 0 14px rgba(138, 180, 248, 0.3);
}
.devmode-label { font-size: 13px; font-weight: 600; color: #fff; }
.toggle-switch.active {
    width: 38px; height: 20px; background: #8ab4f8; border-radius: 20px; position: relative;
}
.toggle-thumb {
    width: 16px; height: 16px; background: #202124; border-radius: 50%; position: absolute; top: 2px; right: 2px;
}
.callout-pointer {
    position: absolute;
    bottom: -32px;
    right: 10px;
    display: flex;
    align-items: center;
    gap: 4px;
    color: #8ab4f8;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.5px;
}
.tip-banner {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 8px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 12px;
    color: #a7f3d0;
    margin-top: 14px;
}

/* Step 4 */
.button-bar-sim { display: flex; gap: 10px; }
.btn-load-unpacked {
    background: #1a73e8;
    color: #fff;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 8px;
    position: relative;
}
.btn-load-unpacked.highlight {
    box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.4), 0 0 16px rgba(26, 115, 232, 0.5);
}
.click-indicator {
    position: absolute;
    top: -28px;
    left: 20px;
    background: #f59e0b;
    color: #000;
    font-size: 10px;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 12px;
}
.btn-secondary-sim {
    background: #282a2d;
    border: 1px solid #3c4043;
    color: #9aa0a6;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
}
.folder-picker-sim {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.picker-header { font-size: 12px; font-weight: 600; color: #8b949e; }
.folder-row.selected {
    background: rgba(37, 99, 235, 0.2);
    border: 1px solid #3b82f6;
    border-radius: 6px;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.folder-name { font-size: 13px; font-weight: 700; color: #fff; flex: 1; }
.check-badge { color: #34d399; font-size: 12px; font-weight: 700; }
.picker-footer { display: flex; justify-content: flex-end; }
.btn-select-folder {
    background: #2563eb; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600;
}

/* Step 5 */
.step5-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.step5-col { display: flex; flex-direction: column; gap: 8px; }
.col-title { font-size: 12px; font-weight: 700; color: #94a3b8; }
.puzzle-menu-sim {
    background: #1e293b;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.puzzle-row { font-size: 12px; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
.puzzle-subrow.selected {
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid #3b82f6;
    border-radius: 6px;
    padding: 6px 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 12.5px;
    color: #fff;
}
.pin-active { color: #38bdf8; font-weight: 700; font-size: 11px; }
.meeting-box-sim {
    background: #000;
    border: 1px solid #334155;
    border-radius: 8px;
    overflow: hidden;
    height: 125px;
    display: flex;
    flex-direction: column;
}
.meeting-header {
    background: #1e293b;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: 600;
    color: #94a3b8;
    display: flex;
    align-items: center;
    gap: 6px;
}
.green-dot { color: #10b981; }
.preview-mini-feed {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #090d16, #131b2e);
}
.readability-badge {
    background: rgba(16, 185, 129, 0.2);
    border: 1px solid #10b981;
    color: #34d399;
    font-size: 11px;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 20px;
}
"""

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 820, "height": 440}, device_scale_factor=2)
        
        os.makedirs("docs/guide", exist_ok=True)
        
        for filename, html_content in TEMPLATES.items():
            full_html = f"<!DOCTYPE html><html><head><style>{CSS}</style></head><body>{html_content}</body></html>"
            await page.set_content(full_html)
            await page.wait_for_timeout(200)
            out_path = os.path.join("docs/guide", filename)
            await page.screenshot(path=out_path)
            print(f"RENDERED: {out_path}")
            
        await browser.close()
        print("ALL_STEP_SCREENSHOTS_RENDERED_SUCCESSFULLY")

if __name__ == "__main__":
    asyncio.run(main())
