(function initializeWebRTCMockEngine(rootWindow) {
  'use strict';

  if (rootWindow.__WEBRTC_MOCK_ENGINE_INITIALIZED__) return;
  rootWindow.__WEBRTC_MOCK_ENGINE_INITIALIZED__ = true;

  // 1. CAPTURE NATIVE PRIMITIVES IMMEDIATELY BEFORE ANY PROTOTYPE IS TOUCHED
  const nativeReflectApply = Reflect.apply;
  const nativeObjectDefineProperty = Object.defineProperty;
  const nativeGetOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
  const nativeToString = Function.prototype.toString;

  let originalGetUserMediaFn = null;
  let originalEnumerateDevicesFn = null;

  if (rootWindow.navigator && rootWindow.navigator.mediaDevices) {
    if (rootWindow.navigator.mediaDevices.getUserMedia) {
      originalGetUserMediaFn = rootWindow.navigator.mediaDevices.getUserMedia;
    }
    if (rootWindow.navigator.mediaDevices.enumerateDevices) {
      originalEnumerateDevicesFn = rootWindow.navigator.mediaDevices.enumerateDevices;
    }
  }
  if (rootWindow.MediaDevices && rootWindow.MediaDevices.prototype) {
    if (!originalGetUserMediaFn && rootWindow.MediaDevices.prototype.getUserMedia) {
      originalGetUserMediaFn = rootWindow.MediaDevices.prototype.getUserMedia;
    }
    if (!originalEnumerateDevicesFn && rootWindow.MediaDevices.prototype.enumerateDevices) {
      originalEnumerateDevicesFn = rootWindow.MediaDevices.prototype.enumerateDevices;
    }
  }

  const patchedRealms = new WeakSet();
  const hookedToStringMap = new WeakMap();

  // 2. STEALTH FUNCTION SPOOFER
  function makeNativeStealth(fn, name) {
    hookedToStringMap.set(fn, `function ${name}() { [native code] }`);
    try {
      nativeObjectDefineProperty(fn, 'name', { value: name, configurable: true });
      nativeObjectDefineProperty(fn, 'length', { value: 0, configurable: true });
    } catch (e) {}
    return fn;
  }

  try {
    const customToString = function toString() {
      if (hookedToStringMap.has(this)) return hookedToStringMap.get(this);
      return nativeReflectApply(nativeToString, this, arguments);
    };
    makeNativeStealth(customToString, 'toString');
    nativeObjectDefineProperty(Function.prototype, 'toString', {
      value: customToString, writable: true, enumerable: false, configurable: true
    });
  } catch (e) {}

  // 3. CONFIGURATION SYNC (Listens to popup changes)
  let currentConfig = {
    mirrorEnabled: true,
    flipHorizontal: true,
    flipVertical: false,
    rotation: 0
  };

  try {
    const cached = window.sessionStorage.getItem('__TRUECAM_CONFIG__');
    if (cached) {
      currentConfig = Object.assign(currentConfig, JSON.parse(cached));
    }
  } catch (e) {}

  window.addEventListener('message', (event) => {
    if (event.data && event.data.source === 'TRUECAM_EXTENSION' && event.data.type === 'TRUECAM_CONFIG_UPDATE') {
      if (event.data.config) {
        currentConfig = Object.assign({}, currentConfig, event.data.config);
      }
    }
  });

  // Request initial config
  try {
    window.postMessage({ source: 'TRUECAM_MAIN', type: 'TRUECAM_REQUEST_CONFIG' }, '*');
  } catch (e) {}

  // 4. STREAM TRANSFORMER (CANVAS FLIPPING & ROTATION ENGINE)
  const VIRTUAL_DEVICE_ID = 'truecam-virtual-device-id';
  const VIRTUAL_GROUP_ID = 'truecam-virtual-group-id';
  const VIRTUAL_LABEL = 'TrueCam Mirrored Camera';

  function transformStream(stream, constraints) {
    const originalVideoTrack = stream.getVideoTracks()[0];
    const originalAudioTracks = stream.getAudioTracks();
    if (!originalVideoTrack) return stream;

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d', { alpha: false });
    const video = document.createElement('video');
    video.autoplay = true;
    video.playsInline = true;
    video.muted = true;
    video.srcObject = new MediaStream([originalVideoTrack]);

    const s = originalVideoTrack.getSettings ? originalVideoTrack.getSettings() : {};
    let targetWidth = s.width || 1280;
    let targetHeight = s.height || 720;
    let targetFps = s.frameRate || 30;

    canvas.width = targetWidth;
    canvas.height = targetHeight;

    let isRunning = true;
    let animHandle;

    function draw() {
      if (!isRunning) return;
      const rot = currentConfig.rotation || 0;
      const is90or270 = (rot === 90 || rot === 270);

      const srcW = video.videoWidth || canvas.width;
      const srcH = video.videoHeight || canvas.height;
      const outW = is90or270 ? srcH : srcW;
      const outH = is90or270 ? srcW : srcH;

      if (canvas.width !== outW || canvas.height !== outH) {
        canvas.width = outW;
        canvas.height = outH;
      }

      ctx.save();
      // Center transform
      ctx.translate(canvas.width / 2, canvas.height / 2);

      if (rot !== 0) {
        ctx.rotate((rot * Math.PI) / 180);
      }

      let scaleX = 1;
      let scaleY = 1;
      if (currentConfig.mirrorEnabled) {
        if (currentConfig.flipHorizontal) scaleX = -1;
        if (currentConfig.flipVertical) scaleY = -1;
      }
      ctx.scale(scaleX, scaleY);

      if (video.readyState >= 2) {
        ctx.drawImage(video, -srcW / 2, -srcH / 2, srcW, srcH);
      } else {
        ctx.fillStyle = '#111827';
        ctx.fillRect(-srcW / 2, -srcH / 2, srcW, srcH);
      }
      ctx.restore();
    }

    function loop() {
      if (!isRunning) return;
      draw();
      animHandle = requestAnimationFrame(loop);
    }

    video.addEventListener('loadeddata', draw);
    video.addEventListener('timeupdate', draw);
    video.play().catch(() => {});
    draw();
    animHandle = requestAnimationFrame(loop);
    const timerHandle = setInterval(draw, 1000 / targetFps);

    const processedStream = canvas.captureStream(targetFps);
    const processedVideoTrack = processedStream.getVideoTracks()[0];

    // Maintain native label and settings
    nativeObjectDefineProperty(processedVideoTrack, 'label', {
      get: () => originalVideoTrack.label || VIRTUAL_LABEL,
      enumerable: true,
      configurable: true
    });

    const nativeStop = processedVideoTrack.stop.bind(processedVideoTrack);
    processedVideoTrack.stop = function stop() {
      isRunning = false;
      if (animHandle) cancelAnimationFrame(animHandle);
      if (timerHandle) clearInterval(timerHandle);
      video.pause();
      video.srcObject = null;
      originalVideoTrack.stop();
      nativeStop();
    };
    makeNativeStealth(processedVideoTrack.stop, 'stop');

    processedVideoTrack.getSettings = function getSettings() {
      const origSettings = originalVideoTrack.getSettings ? originalVideoTrack.getSettings() : {};
      return Object.assign({}, origSettings, {
        width: canvas.width,
        height: canvas.height,
        frameRate: targetFps
      });
    };
    makeNativeStealth(processedVideoTrack.getSettings, 'getSettings');

    processedVideoTrack.getCapabilities = function getCapabilities() {
      return originalVideoTrack.getCapabilities ? originalVideoTrack.getCapabilities() : {};
    };
    makeNativeStealth(processedVideoTrack.getCapabilities, 'getCapabilities');

    processedVideoTrack.getConstraints = function getConstraints() {
      return originalVideoTrack.getConstraints ? originalVideoTrack.getConstraints() : {};
    };
    makeNativeStealth(processedVideoTrack.getConstraints, 'getConstraints');

    processedVideoTrack.applyConstraints = async function applyConstraints(newConstraints) {
      if (originalVideoTrack.applyConstraints) {
        await originalVideoTrack.applyConstraints(newConstraints);
      }
    };
    makeNativeStealth(processedVideoTrack.applyConstraints, 'applyConstraints');

    const origClone = processedVideoTrack.clone.bind(processedVideoTrack);
    processedVideoTrack.clone = function clone() {
      const clonedTrack = origClone();
      nativeObjectDefineProperty(clonedTrack, 'label', {
        get: () => originalVideoTrack.label || VIRTUAL_LABEL,
        enumerable: true,
        configurable: true
      });
      clonedTrack.getSettings = processedVideoTrack.getSettings;
      clonedTrack.getCapabilities = processedVideoTrack.getCapabilities;
      clonedTrack.getConstraints = processedVideoTrack.getConstraints;
      clonedTrack.applyConstraints = processedVideoTrack.applyConstraints;
      const origClonedStop = clonedTrack.stop.bind(clonedTrack);
      clonedTrack.stop = function() {
        processedVideoTrack.stop();
        origClonedStop();
      };
      makeNativeStealth(clonedTrack.stop, 'stop');
      clonedTrack.clone = processedVideoTrack.clone;
      return clonedTrack;
    };
    makeNativeStealth(processedVideoTrack.clone, 'clone');

    originalVideoTrack.addEventListener('ended', () => processedVideoTrack.stop());
    return new MediaStream([processedVideoTrack, ...originalAudioTracks]);
  }

  // 5. CORE HOOKS FOR GETUSERMEDIA & ENUMERATEDEVICES
  const mockGetUserMedia = async function getUserMedia(constraints) {
    console.log('[TrueCam Mirror] getUserMedia called with constraints:', constraints);
    const origGUM = originalGetUserMediaFn;
    if (!origGUM) throw new Error("No native getUserMedia available");

    const targetThis = (this && typeof this.getUserMedia === 'function')
      ? this
      : (rootWindow.navigator && rootWindow.navigator.mediaDevices ? rootWindow.navigator.mediaDevices : rootWindow);

    let strippedConstraints = JSON.parse(JSON.stringify(constraints || {}));
    if (strippedConstraints.video && typeof strippedConstraints.video === 'object' && strippedConstraints.video.deviceId) {
      let reqId = strippedConstraints.video.deviceId;
      if (reqId === VIRTUAL_DEVICE_ID || (reqId.exact && reqId.exact === VIRTUAL_DEVICE_ID)) {
        delete strippedConstraints.video.deviceId;
      }
    }

    const stream = await nativeReflectApply(origGUM, targetThis, [strippedConstraints]);
    if (strippedConstraints && (strippedConstraints.video === true || typeof strippedConstraints.video === 'object')) {
      console.log('[TrueCam Mirror] Transforming video stream to apply mirror effects...');
      return transformStream(stream, strippedConstraints);
    }
    return stream;
  };
  makeNativeStealth(mockGetUserMedia, 'getUserMedia');

  const mockEnumerateDevices = async function enumerateDevices() {
    const origEnum = originalEnumerateDevicesFn;
    if (!origEnum) return [];

    const targetThis = (this && typeof this.enumerateDevices === 'function')
      ? this
      : (rootWindow.navigator && rootWindow.navigator.mediaDevices ? rootWindow.navigator.mediaDevices : rootWindow);

    const devices = await nativeReflectApply(origEnum, targetThis, []);
    
    // Check if a virtual device should be added
    if (devices.some((d) => d.kind === 'videoinput')) {
      const mockDevice = Object.create(typeof MediaDeviceInfo !== 'undefined' ? MediaDeviceInfo.prototype : Object.prototype);
      nativeObjectDefineProperty(mockDevice, 'deviceId', { value: VIRTUAL_DEVICE_ID, enumerable: true });
      nativeObjectDefineProperty(mockDevice, 'kind', { value: 'videoinput', enumerable: true });
      nativeObjectDefineProperty(mockDevice, 'label', { value: VIRTUAL_LABEL, enumerable: true });
      nativeObjectDefineProperty(mockDevice, 'groupId', { value: VIRTUAL_GROUP_ID, enumerable: true });
      nativeObjectDefineProperty(mockDevice, 'toJSON', {
        value: function toJSON() {
          return { deviceId: this.deviceId, kind: this.kind, label: this.label, groupId: this.groupId };
        }, enumerable: true
      });
      devices.unshift(mockDevice);
    }
    return devices;
  };
  makeNativeStealth(mockEnumerateDevices, 'enumerateDevices');

  // 6. MULTI-REALM HOOKING ENGINE
  function patchRealm(targetWin) {
    if (!targetWin || typeof targetWin !== 'object') return;
    if (patchedRealms.has(targetWin)) return;

    try {
      if (targetWin.MediaDevices && targetWin.MediaDevices.prototype) {
        nativeObjectDefineProperty(targetWin.MediaDevices.prototype, 'getUserMedia', {
          value: mockGetUserMedia, writable: true, enumerable: false, configurable: true
        });
        nativeObjectDefineProperty(targetWin.MediaDevices.prototype, 'enumerateDevices', {
          value: mockEnumerateDevices, writable: true, enumerable: false, configurable: true
        });
      }

      if (targetWin.navigator && targetWin.navigator.mediaDevices) {
        nativeObjectDefineProperty(targetWin.navigator.mediaDevices, 'getUserMedia', {
          value: mockGetUserMedia, writable: true, enumerable: true, configurable: true
        });
        nativeObjectDefineProperty(targetWin.navigator.mediaDevices, 'enumerateDevices', {
          value: mockEnumerateDevices, writable: true, enumerable: true, configurable: true
        });
      }

      if (targetWin.Navigator && targetWin.Navigator.prototype) {
        const origMediaDevicesDesc = nativeGetOwnPropertyDescriptor(targetWin.Navigator.prototype, 'mediaDevices');
        if (origMediaDevicesDesc && origMediaDevicesDesc.get) {
          const origGetter = origMediaDevicesDesc.get;
          const hookedGetter = function mediaDevices() {
            const md = nativeReflectApply(origGetter, this, []);
            if (md && md.getUserMedia !== mockGetUserMedia) {
              md.getUserMedia = mockGetUserMedia;
              md.enumerateDevices = mockEnumerateDevices;
            }
            return md;
          };
          makeNativeStealth(hookedGetter, 'get mediaDevices');
          nativeObjectDefineProperty(targetWin.Navigator.prototype, 'mediaDevices', {
            get: hookedGetter, set: origMediaDevicesDesc.set, enumerable: true, configurable: true
          });
        }
      }

      if (targetWin.navigator) {
        const legacyWrapper = function getUserMedia(constraints, success, error) {
          mockGetUserMedia(constraints).then(stream => success && success(stream)).catch(err => error && error(err));
        };
        makeNativeStealth(legacyWrapper, 'getUserMedia');
        try {
          targetWin.navigator.getUserMedia = legacyWrapper;
          targetWin.navigator.webkitGetUserMedia = legacyWrapper;
        } catch (e) {}
      }

      patchedRealms.add(targetWin);
      installDOMTraps(targetWin);
    } catch (e) {}
  }

  function scanNodeAndPatch(node) {
    if (!node || node.nodeType !== 1) return;
    if (node.tagName === 'IFRAME') {
      try { if (node.contentWindow) patchRealm(node.contentWindow); } catch (e) {}
    } else if (node.querySelectorAll) {
      try {
        const iframes = node.querySelectorAll('iframe');
        for (let i = 0; i < iframes.length; i++) {
          if (iframes[i].contentWindow) patchRealm(iframes[i].contentWindow);
        }
      } catch (e) {}
    }
  }

  function installDOMTraps(win) {
    if (!win || !win.HTMLIFrameElement) return;

    // Vector 1: contentWindow
    try {
      const origContentWindowDesc = nativeGetOwnPropertyDescriptor(win.HTMLIFrameElement.prototype, 'contentWindow');
      if (origContentWindowDesc && origContentWindowDesc.get) {
        const origGet = origContentWindowDesc.get;
        nativeObjectDefineProperty(win.HTMLIFrameElement.prototype, 'contentWindow', {
          get: function contentWindow() {
            const childWin = nativeReflectApply(origGet, this, []);
            if (childWin) patchRealm(childWin);
            return childWin;
          },
          set: origContentWindowDesc.set, enumerable: origContentWindowDesc.enumerable, configurable: true
        });
      }
    } catch (e) {}

    // Vector 2: contentDocument
    try {
      const origContentDocDesc = nativeGetOwnPropertyDescriptor(win.HTMLIFrameElement.prototype, 'contentDocument');
      if (origContentDocDesc && origContentDocDesc.get) {
        const origGet = origContentDocDesc.get;
        nativeObjectDefineProperty(win.HTMLIFrameElement.prototype, 'contentDocument', {
          get: function contentDocument() {
            const childDoc = nativeReflectApply(origGet, this, []);
            if (childDoc && childDoc.defaultView) patchRealm(childDoc.defaultView);
            return childDoc;
          },
          set: origContentDocDesc.set, enumerable: origContentDocDesc.enumerable, configurable: true
        });
      }
    } catch (e) {}

    // Vector 5: Node.prototype.appendChild / insertBefore
    try {
      const origAppendChild = win.Node.prototype.appendChild;
      const hookedAppendChild = function appendChild(child) {
        scanNodeAndPatch(child);
        return nativeReflectApply(origAppendChild, this, arguments);
      };
      makeNativeStealth(hookedAppendChild, 'appendChild');
      win.Node.prototype.appendChild = hookedAppendChild;

      const origInsertBefore = win.Node.prototype.insertBefore;
      const hookedInsertBefore = function insertBefore(child, ref) {
        scanNodeAndPatch(child);
        return nativeReflectApply(origInsertBefore, this, arguments);
      };
      makeNativeStealth(hookedInsertBefore, 'insertBefore');
      win.Node.prototype.insertBefore = hookedInsertBefore;
    } catch (e) {}
    
    // Vector 5b: Element.prototype.append
    try {
      const origAppend = win.Element.prototype.append;
      if (origAppend) {
        const hookedAppend = function append(...nodes) {
          for (let i = 0; i < nodes.length; i++) scanNodeAndPatch(nodes[i]);
          return nativeReflectApply(origAppend, this, arguments);
        };
        makeNativeStealth(hookedAppend, 'append');
        win.Element.prototype.append = hookedAppend;
      }
    } catch(e) {}
  }

  // 7. INITIALIZE ROOT REALM
  patchRealm(rootWindow);
  console.log('[TrueCam Mirror] WebRTC Mirror & Hardware Injection Engine Initialized.');

})(window);
