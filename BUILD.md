# TrueCam Pro — Build & Reproduction Instructions

This document is provided for Mozilla Add-on (AMO) reviewers to verify and reproduce the extension build package.

---

## 1. Nature of the Source Code
TrueCam Pro is authored in **100% native vanilla JavaScript (ES6+), HTML5, and CSS3**:
- **NO Minification**: No minifiers (Terser, Uglify, esbuild minification) are used.
- **NO Bundlers**: No bundlers or transpilers (Webpack, Vite, Rollup, Babel) are used.
- **NO Obfuscation**: The source code is completely un-obfuscated and formatted for human readability.
- **NO Third-Party Runtime Dependencies**: Zero npm dependencies or external libraries.

The files inside the submitted package (`main-injector.js`, `isolated-bridge.js`, `popup/popup.js`) are the identical, human-written source files.

---

## 2. How to Reproduce the Build

### Prerequisites
- Python 3.8+ (standard library only, no external packages required)

### Reproduction Command
From the root of this source archive, run:
```bash
python build_packages.py
```

### Generated Artifacts
The build engine compiles and verifies three clean production packages inside the `dist/` folder:
- `dist/truecam-pro-firefox.zip` (Firefox AMO build with `data_collection_permissions` and Gecko MV3 settings)
- `dist/truecam-pro-chrome.zip` (Chrome Web Store build)
- `dist/truecam-pro-edge.zip` (Microsoft Edge build)

All files can be diffed directly against the uploaded package to confirm 1:1 parity.
