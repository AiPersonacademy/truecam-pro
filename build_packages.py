#!/usr/bin/env python3
"""
TrueCam Pro — Multi-Store Packaging Engine
Packages production-ready archives for:
  1. Chrome Web Store (dist/truecam-pro-chrome.zip)
  2. Microsoft Edge Add-ons (dist/truecam-pro-edge.zip)
  3. Firefox Add-ons / AMO (dist/truecam-pro-firefox.zip)
"""

import os
import shutil
import zipfile
import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
DIST_DIR = ROOT_DIR / "dist"
STAGING_DIR = DIST_DIR / "staging"

EXTENSION_NAME = "TrueCam Pro — Hardware Webcam Mirror & Flip"
VERSION = "1.0.0"
DESCRIPTION = (
    "Mirrors the actual outgoing video stream sent over WebRTC so Google Meet, "
    "Zoom, Teams, and Discord participants see your mirrored camera feed."
)

ICONS_LIST = ["icon16.png", "icon32.png", "icon48.png", "icon128.png", "icon512.png"]


def read_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def copy_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def build_chrome(target_dir: Path):
    print("  -> Staging Chrome Web Store package...")
    target_dir.mkdir(parents=True, exist_ok=True)

    # Manifest V3 (Chrome 111+ for native world: MAIN)
    manifest = {
        "manifest_version": 3,
        "name": EXTENSION_NAME,
        "version": VERSION,
        "description": DESCRIPTION,
        "minimum_chrome_version": "111",
        "permissions": ["storage"],
        "host_permissions": ["<all_urls>"],
        "action": {
            "default_popup": "popup/popup.html",
            "default_title": "TrueCam Pro Settings",
            "default_icon": {
                "16": "icons/icon16.png",
                "32": "icons/icon32.png",
                "48": "icons/icon48.png",
                "128": "icons/icon128.png"
            }
        },
        "icons": {
            "16": "icons/icon16.png",
            "32": "icons/icon32.png",
            "48": "icons/icon48.png",
            "128": "icons/icon128.png"
        },
        "content_scripts": [
            {
                "matches": ["<all_urls>"],
                "js": ["isolated-bridge.js"],
                "run_at": "document_start",
                "all_frames": True,
                "match_about_blank": True
            },
            {
                "matches": ["<all_urls>"],
                "js": ["main-injector.js"],
                "run_at": "document_start",
                "world": "MAIN",
                "all_frames": True,
                "match_about_blank": True
            }
        ]
    }
    write_file(target_dir / "manifest.json", json.dumps(manifest, indent=2))

    # Core scripts
    copy_file(ROOT_DIR / "main-injector.js", target_dir / "main-injector.js")
    copy_file(ROOT_DIR / "isolated-bridge.js", target_dir / "isolated-bridge.js")

    # Popup
    copy_file(ROOT_DIR / "popup" / "popup.css", target_dir / "popup" / "popup.css")
    copy_file(ROOT_DIR / "popup" / "popup.js", target_dir / "popup" / "popup.js")
    popup_html = read_file(ROOT_DIR / "popup" / "popup.html")
    popup_html = popup_html.replace(
        'https://chrome.google.com/webstore',
        'https://chromewebstore.google.com/detail/truecam-pro'
    )
    write_file(target_dir / "popup" / "popup.html", popup_html)

    # Icons
    for icon in ICONS_LIST:
        copy_file(ROOT_DIR / "icons" / icon, target_dir / "icons" / icon)

    # Diagnostic lab
    copy_file(ROOT_DIR / "test" / "test.html", target_dir / "test" / "test.html")
    copy_file(ROOT_DIR / "test" / "test.js", target_dir / "test" / "test.js")


def build_edge(target_dir: Path):
    print("  -> Staging Microsoft Edge Add-ons package...")
    target_dir.mkdir(parents=True, exist_ok=True)

    # Manifest V3 (Chromium MV3 compliant for Microsoft Partner Center)
    manifest = {
        "manifest_version": 3,
        "name": EXTENSION_NAME,
        "version": VERSION,
        "description": DESCRIPTION,
        "permissions": ["storage"],
        "host_permissions": ["<all_urls>"],
        "action": {
            "default_popup": "popup/popup.html",
            "default_title": "TrueCam Pro Settings",
            "default_icon": {
                "16": "icons/icon16.png",
                "32": "icons/icon32.png",
                "48": "icons/icon48.png",
                "128": "icons/icon128.png"
            }
        },
        "icons": {
            "16": "icons/icon16.png",
            "32": "icons/icon32.png",
            "48": "icons/icon48.png",
            "128": "icons/icon128.png"
        },
        "content_scripts": [
            {
                "matches": ["<all_urls>"],
                "js": ["isolated-bridge.js"],
                "run_at": "document_start",
                "all_frames": True,
                "match_about_blank": True
            },
            {
                "matches": ["<all_urls>"],
                "js": ["main-injector.js"],
                "run_at": "document_start",
                "world": "MAIN",
                "all_frames": True,
                "match_about_blank": True
            }
        ]
    }
    write_file(target_dir / "manifest.json", json.dumps(manifest, indent=2))

    # Core scripts
    copy_file(ROOT_DIR / "main-injector.js", target_dir / "main-injector.js")
    copy_file(ROOT_DIR / "isolated-bridge.js", target_dir / "isolated-bridge.js")

    # Popup
    copy_file(ROOT_DIR / "popup" / "popup.css", target_dir / "popup" / "popup.css")
    copy_file(ROOT_DIR / "popup" / "popup.js", target_dir / "popup" / "popup.js")
    popup_html = read_file(ROOT_DIR / "popup" / "popup.html")
    popup_html = popup_html.replace(
        'https://chrome.google.com/webstore',
        'https://microsoftedge.microsoft.com/addons/detail/truecam-pro'
    )
    write_file(target_dir / "popup" / "popup.html", popup_html)

    # Icons
    for icon in ICONS_LIST:
        copy_file(ROOT_DIR / "icons" / icon, target_dir / "icons" / icon)

    # Diagnostic lab
    copy_file(ROOT_DIR / "test" / "test.html", target_dir / "test" / "test.html")
    copy_file(ROOT_DIR / "test" / "test.js", target_dir / "test" / "test.js")


def build_firefox(target_dir: Path):
    print("  -> Staging Firefox Add-ons (AMO) package...")
    target_dir.mkdir(parents=True, exist_ok=True)

    # Manifest V3 (Gecko MV3 compliant: browser_specific_settings, web_accessible_resources, NO world: MAIN)
    manifest = {
        "manifest_version": 3,
        "name": EXTENSION_NAME,
        "version": VERSION,
        "description": DESCRIPTION,
        "browser_specific_settings": {
            "gecko": {
                "id": "truecam-pro@aipersonacademy.com",
                "strict_min_version": "109.0",
                "data_collection_permissions": {
                    "required": ["none"]
                }
            }
        },
        "permissions": ["storage"],
        "host_permissions": ["<all_urls>"],
        "action": {
            "default_popup": "popup/popup.html",
            "default_title": "TrueCam Pro Settings",
            "default_icon": {
                "16": "icons/icon16.png",
                "32": "icons/icon32.png",
                "48": "icons/icon48.png",
                "128": "icons/icon128.png"
            }
        },
        "icons": {
            "16": "icons/icon16.png",
            "32": "icons/icon32.png",
            "48": "icons/icon48.png",
            "128": "icons/icon128.png"
        },
        "web_accessible_resources": [
            {
                "resources": ["main-injector.js"],
                "matches": ["<all_urls>"]
            }
        ],
        "content_scripts": [
            {
                "matches": ["<all_urls>"],
                "js": ["isolated-bridge.js"],
                "run_at": "document_start",
                "all_frames": True,
                "match_about_blank": True
            }
        ]
    }
    write_file(target_dir / "manifest.json", json.dumps(manifest, indent=2))

    # Core main-injector.js
    copy_file(ROOT_DIR / "main-injector.js", target_dir / "main-injector.js")

    # Firefox-tailored isolated-bridge.js with dynamic DOM script injection & cross-browser storage
    firefox_bridge_js = """/**
 * TrueCam Pro - Firefox Isolated World Bridge
 * In Firefox MV3, content_scripts do not support "world": "MAIN".
 * This bridge injects main-injector.js directly into the webpage DOM at document_start
 * and synchronizes user preferences between browser.storage and the page context.
 */
(function () {
  'use strict';

  // 1. DYNAMIC MAIN-WORLD INJECTION FOR FIREFOX MV3
  function injectMainScript() {
    try {
      const getURL = (typeof browser !== 'undefined' && browser.runtime?.getURL)
        ? browser.runtime.getURL.bind(browser.runtime)
        : (typeof chrome !== 'undefined' && chrome.runtime?.getURL ? chrome.runtime.getURL.bind(chrome.runtime) : null);

      if (!getURL) return;

      const scriptUrl = getURL('main-injector.js');
      const script = document.createElement('script');
      script.src = scriptUrl;
      script.async = false;

      const target = document.head || document.documentElement;
      if (target) {
        target.appendChild(script);
        script.remove();
      } else {
        document.addEventListener('DOMContentLoaded', () => {
          const docTarget = document.head || document.documentElement;
          if (docTarget) {
            docTarget.appendChild(script);
            script.remove();
          }
        }, { once: true });
      }
    } catch (err) {
      console.warn('[TrueCam Bridge] Firefox injection error:', err);
    }
  }

  injectMainScript();

  // 2. CONFIGURATION SYNC
  const DEFAULT_CONFIG = {
    mirrorEnabled: true,
    flipHorizontal: true,
    flipVertical: false,
    rotation: 0
  };

  const storageApi = (typeof browser !== 'undefined' && browser.storage)
    ? browser.storage
    : (typeof chrome !== 'undefined' && chrome.storage ? chrome.storage : null);

  function broadcastConfig(config) {
    try {
      window.sessionStorage.setItem('__TRUECAM_CONFIG__', JSON.stringify(config));
    } catch (e) {}
    window.postMessage(
      {
        source: 'TRUECAM_EXTENSION',
        type: 'TRUECAM_CONFIG_UPDATE',
        config: config
      },
      '*'
    );
  }

  function loadAndBroadcast() {
    if (!storageApi || !storageApi.local) return;
    try {
      storageApi.local.get(
        ['mirrorEnabled', 'flipHorizontal', 'flipVertical', 'rotation'],
        (result) => {
          const err = (typeof chrome !== 'undefined' && chrome.runtime?.lastError);
          if (err) {
            console.warn('[TrueCam Bridge] Storage read error:', err);
            return;
          }
          const res = result || {};
          const config = {
            mirrorEnabled: res.mirrorEnabled !== undefined ? res.mirrorEnabled : DEFAULT_CONFIG.mirrorEnabled,
            flipHorizontal: res.flipHorizontal !== undefined ? res.flipHorizontal : DEFAULT_CONFIG.flipHorizontal,
            flipVertical: res.flipVertical !== undefined ? res.flipVertical : DEFAULT_CONFIG.flipVertical,
            rotation: res.rotation !== undefined ? res.rotation : DEFAULT_CONFIG.rotation
          };
          broadcastConfig(config);
        }
      );
    } catch (e) {
      console.warn('[TrueCam Bridge] Context error:', e);
    }
  }

  if (storageApi && storageApi.onChanged) {
    storageApi.onChanged.addListener((changes, areaName) => {
      if (areaName === 'local') {
        loadAndBroadcast();
      }
    });
  }

  window.addEventListener('message', (event) => {
    if (event.source !== window || !event.data) return;
    if (event.data.source === 'TRUECAM_MAIN' && event.data.type === 'TRUECAM_REQUEST_CONFIG') {
      loadAndBroadcast();
    }
  });

  loadAndBroadcast();
})();
"""
    write_file(target_dir / "isolated-bridge.js", firefox_bridge_js)

    # Popup
    copy_file(ROOT_DIR / "popup" / "popup.css", target_dir / "popup" / "popup.css")
    copy_file(ROOT_DIR / "popup" / "popup.js", target_dir / "popup" / "popup.js")
    popup_html = read_file(ROOT_DIR / "popup" / "popup.html")
    popup_html = popup_html.replace(
        'https://chrome.google.com/webstore',
        'https://addons.mozilla.org/en-US/firefox/addon/truecam-pro/'
    )
    write_file(target_dir / "popup" / "popup.html", popup_html)

    # Icons
    for icon in ICONS_LIST:
        copy_file(ROOT_DIR / "icons" / icon, target_dir / "icons" / icon)

    # Diagnostic lab
    copy_file(ROOT_DIR / "test" / "test.html", target_dir / "test" / "test.html")
    copy_file(ROOT_DIR / "test" / "test.js", target_dir / "test" / "test.js")


def create_zip(source_dir: Path, zip_path: Path):
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in sorted(files):
                file_path = Path(root) / file
                arcname = file_path.relative_to(source_dir).as_posix()
                zipf.write(file_path, arcname)


def verify_zip(zip_path: Path, expected_manifest_checks: dict):
    print(f"\n[Verification] Checking {zip_path.name} ({zip_path.stat().st_size:,} bytes)...")
    with zipfile.ZipFile(zip_path, "r") as zipf:
        file_list = sorted(zipf.namelist())
        print(f"  Files contained ({len(file_list)} total):")
        for f in file_list:
            info = zipf.getinfo(f)
            print(f"    - {f:<30} ({info.file_size:>6} bytes -> {info.compress_size:>6} compressed)")

        # Verify no forbidden development files
        forbidden = [".git", ".py", ".md", ".jsonl", ".png.bak", "popup_preview.png"]
        for f in file_list:
            for bad in forbidden:
                if bad == ".json":
                    continue
                if f.endswith(bad) or bad in f.split("/"):
                    raise ValueError(f"Forbidden file in production zip: {f}")

        # Check required files
        required = [
            "manifest.json",
            "main-injector.js",
            "isolated-bridge.js",
            "popup/popup.html",
            "popup/popup.css",
            "popup/popup.js",
            "icons/icon16.png",
            "icons/icon48.png",
            "icons/icon128.png",
            "test/test.html",
            "test/test.js"
        ]
        for req in required:
            if req not in file_list:
                raise ValueError(f"Missing required file in zip: {req}")

        # Validate manifest JSON
        manifest_data = json.loads(zipf.read("manifest.json").decode("utf-8"))
        for k, expected_v in expected_manifest_checks.items():
            actual_v = manifest_data.get(k)
            if actual_v != expected_v:
                raise ValueError(f"Manifest mismatch for key '{k}': expected {expected_v}, got {actual_v}")

    print(f"  [PASS] {zip_path.name} passed all production integrity checks.")


def main():
    print("==================================================")
    print(" TrueCam Pro - Multi-Store Distribution Builder   ")
    print("==================================================")

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Build staging dirs
    chrome_stage = STAGING_DIR / "chrome"
    edge_stage = STAGING_DIR / "edge"
    firefox_stage = STAGING_DIR / "firefox"

    build_chrome(chrome_stage)
    build_edge(edge_stage)
    build_firefox(firefox_stage)

    # 2. Package Zips
    chrome_zip = DIST_DIR / "truecam-pro-chrome.zip"
    edge_zip = DIST_DIR / "truecam-pro-edge.zip"
    firefox_zip = DIST_DIR / "truecam-pro-firefox.zip"
    source_zip = DIST_DIR / "truecam-pro-source.zip"

    print("\n[Archiving]")
    print(f"  Writing {chrome_zip.name}...")
    create_zip(chrome_stage, chrome_zip)

    print(f"  Writing {edge_zip.name}...")
    create_zip(edge_stage, edge_zip)

    print(f"  Writing {firefox_zip.name}...")
    create_zip(firefox_stage, firefox_zip)

    print(f"  Writing {source_zip.name} (for reviewer inspection)...")
    source_files = [
        "BUILD.md",
        "README.md",
        "STORE_LISTING.md",
        "build_packages.py",
        "manifest.json",
        "isolated-bridge.js",
        "main-injector.js",
        "popup/popup.html",
        "popup/popup.css",
        "popup/popup.js",
        "icons/icon16.png",
        "icons/icon32.png",
        "icons/icon48.png",
        "icons/icon128.png",
        "icons/icon512.png",
        "icons/icon.svg",
        "icons/promo_banner_1280x800.jpg",
        "test/test.html",
        "test/test.js"
    ]
    with zipfile.ZipFile(source_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for rel in source_files:
            p = ROOT_DIR / rel
            if p.exists():
                zipf.write(p, rel)

    # 3. Clean up staging artifacts so dist contains only clean packages
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)

    # 4. Verify
    verify_zip(chrome_zip, {
        "manifest_version": 3,
        "name": EXTENSION_NAME,
        "minimum_chrome_version": "111"
    })
    verify_zip(edge_zip, {
        "manifest_version": 3,
        "name": EXTENSION_NAME
    })
    verify_zip(firefox_zip, {
        "manifest_version": 3,
        "name": EXTENSION_NAME,
        "browser_specific_settings": {
            "gecko": {
                "id": "truecam-pro@aipersonacademy.com",
                "strict_min_version": "109.0",
                "data_collection_permissions": {
                    "required": ["none"]
                }
            }
        }
    })

    print("\n==================================================")
    print(" ALL 3 STORE PACKAGES CREATED SUCCESSFULLY!")
    print(f" 1. Chrome:  {chrome_zip}")
    print(f" 2. Edge:    {edge_zip}")
    print(f" 3. Firefox: {firefox_zip}")
    print("==================================================")


if __name__ == "__main__":
    main()
