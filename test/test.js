/**
 * TrueCam Mirror - Diagnostic Lab Logic
 */
document.addEventListener('DOMContentLoaded', () => {
  const btnStart = document.getElementById('btnStart');
  const btnStop = document.getElementById('btnStop');
  const btnSnapshot = document.getElementById('btnSnapshot');
  const liveVideo = document.getElementById('liveVideo');
  const emptyPrompt = document.getElementById('emptyPrompt');
  const statusBadge = document.getElementById('statusBadge');
  const diagInjected = document.getElementById('diagInjected');
  const diagConfig = document.getElementById('diagConfig');
  const diagDevice = document.getElementById('diagDevice');
  const diagResolution = document.getElementById('diagResolution');
  const diagFps = document.getElementById('diagFps');
  const diagAudio = document.getElementById('diagAudio');
  const audioFill = document.getElementById('audioFill');
  const meterDb = document.getElementById('meterDb');
  const snapshotCanvas = document.getElementById('snapshotCanvas');
  const snapshotNote = document.getElementById('snapshotNote');

  let currentStream = null;
  let audioContext = null;
  let analyser = null;
  let audioAnim = null;

  // Check injection status
  function checkInjection() {
    if (window.__TRUECAM_INJECTED__) {
      diagInjected.textContent = 'Active (world: MAIN)';
      diagInjected.style.color = '#34d399';
    } else {
      diagInjected.textContent = 'Active (Direct Engine)';
      diagInjected.style.color = '#34d399';
    }

    if (window.__TRUECAM_CONFIG__) {
      const c = window.__TRUECAM_CONFIG__;
      diagConfig.textContent = `Mirror: ${c.mirrorEnabled ? 'ON' : 'OFF'} (H:${c.flipHorizontal} V:${c.flipVertical})`;
    } else {
      diagConfig.textContent = 'Default';
    }
  }

  setInterval(checkInjection, 1000);
  checkInjection();

  btnStart.addEventListener('click', async () => {
    try {
      btnStart.disabled = true;
      btnStart.textContent = 'Requesting Camera...';

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1920, min: 1280 },
          height: { ideal: 1080, min: 720 },
          frameRate: { ideal: 30 }
        },
        audio: true
      });

      currentStream = stream;
      liveVideo.srcObject = stream;
      liveVideo.style.display = 'block';
      emptyPrompt.style.display = 'none';

      btnStart.style.display = 'none';
      btnStop.style.display = 'inline-block';
      btnSnapshot.style.display = 'inline-block';
      statusBadge.textContent = 'Stream Active & Running';
      statusBadge.className = 'badge-pill';

      // Read stream metadata
      const videoTrack = stream.getVideoTracks()[0];
      const audioTrack = stream.getAudioTracks()[0];

      diagDevice.textContent = videoTrack.label || 'Webcam';

      liveVideo.onloadedmetadata = () => {
        const settings = videoTrack.getSettings ? videoTrack.getSettings() : {};
        const w = settings.width || liveVideo.videoWidth;
        const h = settings.height || liveVideo.videoHeight;
        const fps = settings.frameRate ? Math.round(settings.frameRate) : 30;
        diagResolution.textContent = `${w} x ${h}px`;
        diagFps.textContent = `${fps} FPS`;
      };

      // Setup microphone analyzer
      if (audioTrack) {
        diagAudio.textContent = audioTrack.label || 'Connected';
        setupAudioMeter(stream);
      } else {
        diagAudio.textContent = 'No Audio Track';
      }
    } catch (err) {
      console.error(err);
      alert('Could not start stream: ' + err.message);
      btnStart.disabled = false;
      btnStart.textContent = 'Start Webcam Stream';
    }
  });

  function setupAudioMeter(stream) {
    try {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContext.createMediaStreamSource(stream);
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      function updateMeter() {
        if (!analyser) return;
        analyser.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const avg = sum / dataArray.length;
        const pct = Math.min(100, Math.round((avg / 128) * 100));
        audioFill.style.width = pct + '%';
        meterDb.textContent = pct + '%';
        audioAnim = requestAnimationFrame(updateMeter);
      }
      updateMeter();
    } catch (e) {
      console.warn('Audio meter error:', e);
    }
  }

  btnStop.addEventListener('click', stopStream);

  function stopStream() {
    if (currentStream) {
      currentStream.getTracks().forEach((t) => t.stop());
      currentStream = null;
    }
    if (audioContext) {
      audioContext.close();
      audioContext = null;
    }
    if (audioAnim) {
      cancelAnimationFrame(audioAnim);
      audioAnim = null;
    }

    liveVideo.srcObject = null;
    liveVideo.style.display = 'none';
    emptyPrompt.style.display = 'block';

    btnStart.disabled = false;
    btnStart.textContent = 'Start Webcam Stream';
    btnStart.style.display = 'inline-block';
    btnStop.style.display = 'none';
    btnSnapshot.style.display = 'none';

    statusBadge.textContent = 'Stream Inactive';
    statusBadge.className = 'badge-pill warning';
    diagResolution.textContent = '--';
    diagFps.textContent = '--';
    diagAudio.textContent = 'Inactive';
    audioFill.style.width = '0%';
    meterDb.textContent = '0%';
  }

  // Direct pixel test snapshot
  btnSnapshot.addEventListener('click', () => {
    if (!liveVideo || !liveVideo.videoWidth) return;

    snapshotCanvas.width = liveVideo.videoWidth;
    snapshotCanvas.height = liveVideo.videoHeight;
    const ctx = snapshotCanvas.getContext('2d');
    ctx.drawImage(liveVideo, 0, 0, snapshotCanvas.width, snapshotCanvas.height);

    snapshotCanvas.style.display = 'block';
    snapshotNote.style.display = 'block';
  });

  // Automatically trigger camera stream if opened with ?autostart=1
  if (new URLSearchParams(window.location.search).get('autostart') === '1') {
    setTimeout(() => {
      btnStart.click();
    }, 400);
  }
});
