import asyncio
import http.server
import json
import socketserver
import threading
from playwright.async_api import async_playwright

PORT = 9880

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def start_server():
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), QuietHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd

async def run_probe():
    start_server()
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream"
            ]
        )
        context = await browser.new_context(permissions=["camera", "microphone"])
        page = await context.new_page()
        await page.goto(f"http://localhost:{PORT}/webcam-mirror-extension/test/spec_probe.html")

        probe_js = """
        async () => {
            const results = {};

            // ==========================================
            // 1. DEDICATED WORKER SCOPE INSPECTION
            // ==========================================
            const dedicatedWorkerCode = `
                self.onmessage = async (e) => {
                    const res = {};
                    res.scope = 'DedicatedWorkerGlobalScope';
                    res.selfType = self.constructor.name;
                    res.hasNavigator = typeof navigator !== 'undefined';
                    res.navigatorType = navigator ? navigator.constructor.name : null;
                    res.hasMediaDevices = !!(navigator && navigator.mediaDevices);
                    res.mediaDevicesType = (navigator && navigator.mediaDevices) ? navigator.mediaDevices.constructor.name : typeof (navigator && navigator.mediaDevices);
                    res.hasGetUserMedia = !!(navigator && navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
                    
                    // WebCodecs
                    res.hasVideoEncoder = typeof VideoEncoder !== 'undefined';
                    res.hasVideoDecoder = typeof VideoDecoder !== 'undefined';
                    res.hasVideoFrame = typeof VideoFrame !== 'undefined';
                    res.hasEncodedVideoChunk = typeof EncodedVideoChunk !== 'undefined';
                    res.hasImageDecoder = typeof ImageDecoder !== 'undefined';
                    
                    // Insertable Streams (Breakout Box)
                    res.hasMediaStreamTrackProcessor = typeof MediaStreamTrackProcessor !== 'undefined';
                    res.hasMediaStreamTrackGenerator = typeof MediaStreamTrackGenerator !== 'undefined';

                    // Canvas & Rendering
                    res.hasOffscreenCanvas = typeof OffscreenCanvas !== 'undefined';
                    if (res.hasOffscreenCanvas) {
                        const oc = new OffscreenCanvas(256, 256);
                        res.offscreenCanvasHasCaptureStream = typeof oc.captureStream !== 'undefined';
                        res.offscreenCanvasHasConvertToBlob = typeof oc.convertToBlob !== 'undefined';
                        res.offscreenCanvasHasTransferToImageBitmap = typeof oc.transferToImageBitmap !== 'undefined';
                    }

                    // WebRTC PeerConnection in worker
                    res.hasRTCPeerConnection = typeof RTCPeerConnection !== 'undefined';
                    res.hasRTCRtpScriptTransform = typeof RTCRtpScriptTransform !== 'undefined';

                    self.postMessage(res);
                };
            `;
            const dedicatedBlob = new Blob([dedicatedWorkerCode], { type: 'application/javascript' });
            const dedicatedWorker = new Worker(URL.createObjectURL(dedicatedBlob));
            const dedicatedPromise = new Promise(resolve => {
                dedicatedWorker.onmessage = (e) => resolve(e.data);
            });
            dedicatedWorker.postMessage('ping');
            results.dedicatedWorker = await dedicatedPromise;

            // ==========================================
            // 2. SHARED WORKER SCOPE INSPECTION
            // ==========================================
            try {
                const sharedWorkerCode = `
                    self.onconnect = (e) => {
                        const port = e.ports[0];
                        const res = {};
                        res.scope = 'SharedWorkerGlobalScope';
                        res.selfType = self.constructor.name;
                        res.hasNavigator = typeof navigator !== 'undefined';
                        res.navigatorType = navigator ? navigator.constructor.name : null;
                        res.hasMediaDevices = !!(navigator && navigator.mediaDevices);
                        res.hasVideoEncoder = typeof VideoEncoder !== 'undefined';
                        res.hasVideoFrame = typeof VideoFrame !== 'undefined';
                        res.hasMediaStreamTrackProcessor = typeof MediaStreamTrackProcessor !== 'undefined';
                        res.hasMediaStreamTrackGenerator = typeof MediaStreamTrackGenerator !== 'undefined';
                        res.hasOffscreenCanvas = typeof OffscreenCanvas !== 'undefined';
                        res.hasRTCPeerConnection = typeof RTCPeerConnection !== 'undefined';
                        port.postMessage(res);
                    };
                `;
                const sharedBlob = new Blob([sharedWorkerCode], { type: 'application/javascript' });
                const sharedWorker = new SharedWorker(URL.createObjectURL(sharedBlob));
                const sharedPromise = new Promise(resolve => {
                    sharedWorker.port.onmessage = (e) => resolve(e.data);
                });
                sharedWorker.port.start();
                results.sharedWorker = await Promise.race([
                    sharedPromise,
                    new Promise(r => setTimeout(() => r({ error: 'timeout' }), 1500))
                ]);
            } catch (err) {
                results.sharedWorker = { error: err.name + ': ' + err.message };
            }

            // ==========================================
            // 3. AUDIO WORKLET GLOBAL SCOPE
            // ==========================================
            try {
                const audioCtx = new AudioContext();
                const workletCode = `
                    class ScopeProbeProcessor extends AudioWorkletProcessor {
                        constructor() {
                            super();
                            const res = {};
                            res.scope = 'AudioWorkletGlobalScope';
                            res.selfType = self.constructor.name;
                            res.hasNavigator = typeof navigator !== 'undefined';
                            res.hasMediaDevices = typeof navigator !== 'undefined' && !!navigator.mediaDevices;
                            res.hasVideoFrame = typeof VideoFrame !== 'undefined';
                            res.hasMediaStreamTrackProcessor = typeof MediaStreamTrackProcessor !== 'undefined';
                            this.port.postMessage(res);
                        }
                        process() { return false; }
                    }
                    registerProcessor('scope-probe', ScopeProbeProcessor);
                `;
                const workletBlob = new Blob([workletCode], { type: 'application/javascript' });
                await audioCtx.audioWorklet.addModule(URL.createObjectURL(workletBlob));
                const probeNode = new AudioWorkletNode(audioCtx, 'scope-probe');
                const workletPromise = new Promise(resolve => {
                    probeNode.port.onmessage = (e) => resolve(e.data);
                });
                results.audioWorklet = await Promise.race([
                    workletPromise,
                    new Promise(r => setTimeout(() => r({ error: 'timeout' }), 1500))
                ]);
                await audioCtx.close();
            } catch (err) {
                results.audioWorklet = { error: err.name + ': ' + err.message };
            }

            // ==========================================
            // 4. WINDOW SCOPE BASELINE
            // ==========================================
            results.window = {
                scope: 'Window',
                selfType: window.constructor.name,
                hasNavigator: typeof navigator !== 'undefined',
                navigatorType: navigator.constructor.name,
                hasMediaDevices: !!navigator.mediaDevices,
                mediaDevicesType: navigator.mediaDevices.constructor.name,
                hasGetUserMedia: typeof navigator.mediaDevices.getUserMedia === 'function',
                hasVideoEncoder: typeof VideoEncoder !== 'undefined',
                hasVideoFrame: typeof VideoFrame !== 'undefined',
                hasMediaStreamTrackProcessor: typeof MediaStreamTrackProcessor !== 'undefined',
                hasMediaStreamTrackGenerator: typeof MediaStreamTrackGenerator !== 'undefined',
                hasOffscreenCanvas: typeof OffscreenCanvas !== 'undefined',
                hasRTCPeerConnection: typeof RTCPeerConnection !== 'undefined',
                hasRTCRtpScriptTransform: typeof RTCRtpScriptTransform !== 'undefined'
            };

            // ==========================================
            // 5. NATIVE SLOT FIDELITY & V8 INTERNAL FIELDS
            // ==========================================
            const pc = new RTCPeerConnection();

            // Test 5A: Pure Duck-typed object
            const duckTrack = {
                id: 'mock-duck-track-1',
                kind: 'video',
                label: 'Mock Camera',
                enabled: true,
                muted: false,
                readyState: 'live',
                stop: () => {},
                clone: () => duckTrack,
                getSettings: () => ({ width: 1280, height: 720, frameRate: 30 }),
                getCapabilities: () => ({}),
                applyConstraints: async () => {}
            };
            try {
                pc.addTrack(duckTrack);
                results.duckTrack_addTrack = 'SUCCESS';
            } catch (e) {
                results.duckTrack_addTrack = { error: e.name, message: e.message };
            }

            // Test 5B: Object.create(MediaStreamTrack.prototype)
            const protoTrack = Object.create(MediaStreamTrack.prototype);
            for (const key of Object.keys(duckTrack)) {
                Object.defineProperty(protoTrack, key, { value: duckTrack[key], writable: true, configurable: true });
            }
            try {
                pc.addTrack(protoTrack);
                results.protoTrack_addTrack = 'SUCCESS';
            } catch (e) {
                results.protoTrack_addTrack = { error: e.name, message: e.message };
            }

            // Test 5C: Calling native MediaStreamTrack.prototype methods on duckTrack
            try {
                MediaStreamTrack.prototype.getSettings.call(duckTrack);
                results.duckTrack_nativeMethodCall = 'SUCCESS';
            } catch (e) {
                results.duckTrack_nativeMethodCall = { error: e.name, message: e.message };
            }

            // Test 5D: MediaStream constructor with duckTrack
            try {
                const s = new MediaStream([duckTrack]);
                results.duckTrack_mediaStreamConstructor = 'SUCCESS';
            } catch (e) {
                results.duckTrack_mediaStreamConstructor = { error: e.name, message: e.message };
            }

            // Test 5E: MediaStreamTrackProcessor with duckTrack
            if (window.MediaStreamTrackProcessor) {
                try {
                    new MediaStreamTrackProcessor({ track: duckTrack });
                    results.duckTrack_trackProcessor = 'SUCCESS';
                } catch (e) {
                    results.duckTrack_trackProcessor = { error: e.name, message: e.message };
                }
            }

            // Test 5F: Native Canvas captureStream track
            const canvas = document.createElement('canvas');
            canvas.width = 640;
            canvas.height = 480;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#00ff00';
            ctx.fillRect(0, 0, 640, 480);

            const canvasStream = canvas.captureStream(30);
            const canvasTrack = canvasStream.getVideoTracks()[0];

            results.canvasTrack_instanceCheck = {
                isInstanceOfMediaStreamTrack: canvasTrack instanceof MediaStreamTrack,
                constructorName: canvasTrack.constructor.name,
                protoName: Object.getPrototypeOf(canvasTrack).constructor.name,
                hasId: typeof canvasTrack.id === 'string',
                kind: canvasTrack.kind,
                readyState: canvasTrack.readyState
            };

            // Test 5G: pc.addTrack with Canvas track
            try {
                const sender = pc.addTrack(canvasTrack, canvasStream);
                results.canvasTrack_addTrack = {
                    status: 'SUCCESS',
                    senderTrackId: sender.track ? sender.track.id : null,
                    dtmfAvailable: !!sender.dtmf
                };
            } catch (e) {
                results.canvasTrack_addTrack = { error: e.name, message: e.message };
            }

            // Test 5H: MediaStreamTrackProcessor with Canvas track
            if (window.MediaStreamTrackProcessor) {
                try {
                    const processor = new MediaStreamTrackProcessor({ track: canvasTrack });
                    results.canvasTrack_trackProcessor = {
                        status: 'SUCCESS',
                        readableType: processor.readable.constructor.name,
                        locked: processor.readable.locked
                    };
                } catch (e) {
                    results.canvasTrack_trackProcessor = { error: e.name, message: e.message };
                }
            }

            // Test 5I: MediaStreamTrackGenerator (Breakout Box)
            if (window.MediaStreamTrackGenerator) {
                try {
                    const generator = new MediaStreamTrackGenerator({ kind: 'video' });
                    results.generator_instance = {
                        status: 'SUCCESS',
                        isInstanceOfMediaStreamTrack: generator instanceof MediaStreamTrack,
                        kind: generator.kind,
                        writableType: generator.writable.constructor.name
                    };
                    const senderGen = pc.addTrack(generator);
                    results.generator_addTrack = {
                        status: 'SUCCESS',
                        senderTrackId: senderGen.track ? senderGen.track.id : null
                    };
                } catch (e) {
                    results.generator_instance = { error: e.name, message: e.message };
                }
            }

            // ==========================================
            // 6. PIPING VIDEOFRAME ACROSS WORKER THREAD
            // ==========================================
            try {
                if (window.MediaStreamTrackProcessor && window.MediaStreamTrackGenerator) {
                    const processor = new MediaStreamTrackProcessor({ track: canvasTrack });
                    const generator = new MediaStreamTrackGenerator({ kind: 'video' });

                    const pipelineWorkerCode = `
                        self.onmessage = async (e) => {
                            const { readable, writable } = e.data;
                            const reader = readable.getReader();
                            const writer = writable.getWriter();

                            let framesProcessed = 0;
                            while (framesProcessed < 3) {
                                const { value: frame, done } = await reader.read();
                                if (done) break;
                                
                                // Frame manipulation in worker
                                const ts = frame.timestamp;
                                const width = frame.displayWidth;
                                const height = frame.displayHeight;

                                // Pass-through / forward
                                await writer.write(frame);
                                framesProcessed++;
                            }
                            self.postMessage({ status: 'SUCCESS', framesProcessed });
                        };
                    `;
                    const pWorker = new Worker(URL.createObjectURL(new Blob([pipelineWorkerCode], { type: 'application/javascript' })));
                    
                    const pipelinePromise = new Promise(resolve => {
                        pWorker.onmessage = (e) => resolve(e.data);
                    });

                    // Kick paint to generate frames
                    const drawInterval = setInterval(() => {
                        ctx.fillStyle = ctx.fillStyle === '#00ff00' ? '#ff0000' : '#00ff00';
                        ctx.fillRect(0, 0, 640, 480);
                    }, 33);

                    pWorker.postMessage({
                        readable: processor.readable,
                        writable: generator.writable
                    }, [processor.readable, generator.writable]);

                    results.workerPipeline = await Promise.race([
                        pipelinePromise,
                        new Promise(r => setTimeout(() => r({ error: 'timeout after 2500ms' }), 2500))
                    ]);
                    clearInterval(drawInterval);
                }
            } catch (err) {
                results.workerPipeline = { error: err.name + ': ' + err.message };
            }

            return results;
        }
        """

        res = await page.evaluate(probe_js)
        print(json.dumps(res, indent=2))
        with open("c:/Users/pc/Master AI2brands Saas/webcam-mirror-extension/test/worker_probe_results.json", "w") as f:
            json.dump(res, f, indent=2)

if __name__ == "__main__":
    asyncio.run(run_probe())
