/**
 * TrueCam Pro - Minimalist Native Controller
 */
document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const masterToggle = document.getElementById('masterToggle');
  const horizontalToggle = document.getElementById('horizontalToggle');
  const verticalToggle = document.getElementById('verticalToggle');
  const activeDot = document.getElementById('activeDot');
  const contextText = document.getElementById('contextText');
  const contextDot = document.getElementById('contextDot');

  // Preview elements
  const btnTogglePreview = document.getElementById('btnTogglePreview');
  const previewVideo = document.getElementById('previewVideo');
  const standbyScreen = document.getElementById('standbyScreen');
  const hudLayer = document.getElementById('hudLayer');
  const hudMetrics = document.getElementById('hudMetrics');
  const hudTransform = document.getElementById('hudTransform');

  // Presets & Rotation
  const presetMirror = document.getElementById('presetMirror');
  const presetWhiteboard = document.getElementById('presetWhiteboard');
  const presetCeiling = document.getElementById('presetCeiling');
  const segments = document.querySelectorAll('#rotationGroup .segment');

  // Support
  const btnCopyUsdt = document.getElementById('btnCopyUsdt');
  const usdtInfo = document.getElementById('usdtInfo');
  const usdtAddressText = document.getElementById('usdtAddressText');
  const openTestLab = document.getElementById('openTestLab');
  const toast = document.getElementById('toast');

  let activeStream = null;

  // 1. Detect Active Context
  try {
    if (chrome.tabs && chrome.tabs.query) {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs && tabs[0] && tabs[0].url) {
          const url = tabs[0].url.toLowerCase();
          if (url.includes('meet.google.com')) {
            contextText.textContent = 'Google Meet Active';
            contextDot.style.backgroundColor = '#10b981';
          } else if (url.includes('zoom.us')) {
            contextText.textContent = 'Zoom Web Active';
            contextDot.style.backgroundColor = '#3b82f6';
          } else if (url.includes('teams.microsoft.com') || url.includes('teams.live.com')) {
            contextText.textContent = 'Microsoft Teams Active';
            contextDot.style.backgroundColor = '#8b5cf6';
          } else if (url.includes('discord.com')) {
            contextText.textContent = 'Discord Active';
            contextDot.style.backgroundColor = '#6366f1';
          } else if (url.includes('webcamtests.com')) {
            contextText.textContent = 'Webcam Test Lab Active';
            contextDot.style.backgroundColor = '#10b981';
          }
        }
      });
    }
  } catch (e) {}

  // 2. Load and Apply Settings
  chrome.storage.local.get(['mirrorEnabled', 'flipHorizontal', 'flipVertical', 'rotation'], (res) => {
    masterToggle.checked = res.mirrorEnabled !== undefined ? res.mirrorEnabled : true;
    horizontalToggle.checked = res.flipHorizontal !== undefined ? res.flipHorizontal : true;
    verticalToggle.checked = res.flipVertical !== undefined ? res.flipVertical : false;
    const rot = res.rotation !== undefined ? res.rotation : 0;

    syncSegments(rot);
    updateUI();
  });

  function getSelectedRotation() {
    const active = document.querySelector('#rotationGroup .segment.active');
    return active ? parseInt(active.getAttribute('data-deg'), 10) : 0;
  }

  function syncSegments(deg) {
    segments.forEach((seg) => {
      if (parseInt(seg.getAttribute('data-deg'), 10) === deg) {
        seg.classList.add('active');
      } else {
        seg.classList.remove('active');
      }
    });
  }

  function updateUI() {
    const isMaster = masterToggle.checked;
    const isH = horizontalToggle.checked;
    const isV = verticalToggle.checked;
    const rot = getSelectedRotation();

    // Dot indicator
    if (isMaster) {
      activeDot.className = 'status-indicator live';
    } else {
      activeDot.className = 'status-indicator';
    }

    // Presets Highlight
    [presetMirror, presetWhiteboard, presetCeiling].forEach((p) => p.classList.remove('active'));
    if (isMaster && rot === 0) {
      if (isH && !isV) presetMirror.classList.add('active');
      else if (!isH && !isV) presetWhiteboard.classList.add('active');
      else if (isH && isV) presetCeiling.classList.add('active');
    }

    // HUD transform text
    if (!isMaster) {
      hudTransform.textContent = 'Original Feed';
      hudTransform.className = 'hud-tag';
    } else if (isH && isV) {
      hudTransform.textContent = `Inverted (H+V) ${rot ? rot + '°' : ''}`;
      hudTransform.className = 'hud-tag highlight';
    } else if (isH) {
      hudTransform.textContent = `Mirrored ${rot ? rot + '°' : ''}`;
      hudTransform.className = 'hud-tag highlight';
    } else if (isV) {
      hudTransform.textContent = `Vertical Flip ${rot ? rot + '°' : ''}`;
      hudTransform.className = 'hud-tag highlight';
    } else {
      hudTransform.textContent = `Natural / Text ${rot ? rot + '°' : ''}`;
      hudTransform.className = 'hud-tag';
    }

    applyPreviewTransform();
  }

  function saveConfig() {
    const config = {
      mirrorEnabled: masterToggle.checked,
      flipHorizontal: horizontalToggle.checked,
      flipVertical: verticalToggle.checked,
      rotation: getSelectedRotation()
    };
    chrome.storage.local.set(config, () => {
      updateUI();
    });
  }

  masterToggle.addEventListener('change', saveConfig);
  horizontalToggle.addEventListener('change', saveConfig);
  verticalToggle.addEventListener('change', saveConfig);

  // Preset Clicks
  presetMirror.addEventListener('click', () => {
    masterToggle.checked = true;
    horizontalToggle.checked = true;
    verticalToggle.checked = false;
    syncSegments(0);
    saveConfig();
  });

  presetWhiteboard.addEventListener('click', () => {
    masterToggle.checked = true;
    horizontalToggle.checked = false;
    verticalToggle.checked = false;
    syncSegments(0);
    saveConfig();
  });

  presetCeiling.addEventListener('click', () => {
    masterToggle.checked = true;
    horizontalToggle.checked = true;
    verticalToggle.checked = true;
    syncSegments(0);
    saveConfig();
  });

  // Rotation Segments
  segments.forEach((seg) => {
    seg.addEventListener('click', () => {
      syncSegments(parseInt(seg.getAttribute('data-deg'), 10));
      saveConfig();
    });
  });

  // 3. Video Preview
  function applyPreviewTransform() {
    if (!previewVideo) return;
    const isMaster = masterToggle.checked;
    const rot = getSelectedRotation();
    const scaleX = isMaster && horizontalToggle.checked ? -1 : 1;
    const scaleY = isMaster && verticalToggle.checked ? -1 : 1;
    previewVideo.style.transform = `rotate(${rot}deg) scale(${scaleX}, ${scaleY})`;
  }

  btnTogglePreview.addEventListener('click', async () => {
    if (activeStream) {
      stopPreview();
      return;
    }

    try {
      btnTogglePreview.textContent = 'Connecting...';
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false
      });

      activeStream = stream;
      previewVideo.srcObject = stream;
      previewVideo.style.display = 'block';
      standbyScreen.style.display = 'none';
      hudLayer.style.display = 'flex';

      btnTogglePreview.textContent = 'Turn off preview';
      applyPreviewTransform();

      const track = stream.getVideoTracks()[0];
      previewVideo.onloadedmetadata = () => {
        const s = track.getSettings ? track.getSettings() : {};
        const w = s.width || previewVideo.videoWidth;
        const h = s.height || previewVideo.videoHeight;
        const fps = s.frameRate ? Math.round(s.frameRate) : 30;
        hudMetrics.textContent = `${w}×${h} • ${fps}fps`;
      };
    } catch (e) {
      stopPreview();
      chrome.tabs.create({ url: chrome.runtime.getURL('test/test.html?autostart=1') });
    }
  });

  function stopPreview() {
    if (activeStream) {
      activeStream.getTracks().forEach((t) => {
        try { t.stop(); } catch (err) {}
      });
      activeStream = null;
    }
    if (previewVideo) {
      previewVideo.srcObject = null;
      previewVideo.style.display = 'none';
    }
    standbyScreen.style.display = 'flex';
    hudLayer.style.display = 'none';
    btnTogglePreview.textContent = 'Turn on preview';
  }

  ['unload', 'beforeunload', 'pagehide', 'blur'].forEach((evt) => {
    window.addEventListener(evt, stopPreview);
  });

  // 4. Support & Copy
  function showToast(text) {
    toast.textContent = text;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2000);
  }

  btnCopyUsdt.addEventListener('click', () => {
    const isHidden = usdtInfo.style.display === 'none';
    usdtInfo.style.display = isHidden ? 'flex' : 'none';

    const addr = usdtAddressText.textContent.trim();
    navigator.clipboard.writeText(addr).then(() => {
      showToast('USDT Address copied');
    }).catch(() => {
      showToast('Copied address');
    });
  });

  usdtInfo.addEventListener('click', () => {
    const addr = usdtAddressText.textContent.trim();
    navigator.clipboard.writeText(addr).then(() => {
      showToast('USDT Address copied');
    });
  });

  openTestLab.addEventListener('click', () => {
    stopPreview();
    chrome.tabs.create({ url: chrome.runtime.getURL('test/test.html') });
  });
});
