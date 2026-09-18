/**
 * TrueCam Mirror - Isolated World Bridge
 * Bridges chrome.storage.local settings to the webpage's MAIN world.
 */
(function () {
  'use strict';

  const DEFAULT_CONFIG = {
    mirrorEnabled: true,
    flipHorizontal: true,
    flipVertical: false,
    rotation: 0
  };

  // Broadcast settings to the MAIN world
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

  // Load current configuration from chrome storage
  function loadAndBroadcast() {
    try {
      chrome.storage.local.get(
        ['mirrorEnabled', 'flipHorizontal', 'flipVertical', 'rotation'],
        (result) => {
          if (chrome.runtime.lastError) {
            console.warn('[TrueCam Bridge] Storage read error:', chrome.runtime.lastError);
            return;
          }
          const config = {
            mirrorEnabled: result.mirrorEnabled !== undefined ? result.mirrorEnabled : DEFAULT_CONFIG.mirrorEnabled,
            flipHorizontal: result.flipHorizontal !== undefined ? result.flipHorizontal : DEFAULT_CONFIG.flipHorizontal,
            flipVertical: result.flipVertical !== undefined ? result.flipVertical : DEFAULT_CONFIG.flipVertical,
            rotation: result.rotation !== undefined ? result.rotation : DEFAULT_CONFIG.rotation
          };
          broadcastConfig(config);
        }
      );
    } catch (e) {
      console.warn('[TrueCam Bridge] Context error:', e);
    }
  }

  // Listen for storage changes when user changes toggles in popup
  chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName === 'local') {
      loadAndBroadcast();
    }
  });

  // Listen for initial config requests from main-injector
  window.addEventListener('message', (event) => {
    if (event.source !== window || !event.data) return;
    if (event.data.source === 'TRUECAM_MAIN' && event.data.type === 'TRUECAM_REQUEST_CONFIG') {
      loadAndBroadcast();
    }
  });

  // Initial load
  loadAndBroadcast();
})();
