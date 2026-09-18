import asyncio
import http.server
import json
import socketserver
import threading
import time
from playwright.async_api import async_playwright

PORT = 9876

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
        context = await browser.new_context(
            permissions=["camera", "microphone"]
        )
        page = await context.new_page()
        await page.goto(f"http://localhost:{PORT}/webcam-mirror-extension/test/spec_probe.html")

        # Run comprehensive in-browser probe script
        probe_script = """
        async () => {
            const results = {};

            function serializeDesc(desc) {
                if (!desc) return null;
                return {
                    configurable: desc.configurable,
                    enumerable: desc.enumerable,
                    writable: desc.writable,
                    hasValue: typeof desc.value !== 'undefined',
                    valueType: typeof desc.value,
                    hasGetter: typeof desc.get === 'function',
                    hasSetter: typeof desc.set === 'function'
                };
            }

            // --- SECTION 1: W3C Media Capture & Streams ---
            results.gum_prototype_chain = {
                navigator_has_mediaDevices: 'mediaDevices' in navigator,
                navigator_own_mediaDevices: Object.prototype.hasOwnProperty.call(navigator, 'mediaDevices'),
                Navigator_proto_mediaDevices_desc: serializeDesc(Object.getOwnPropertyDescriptor(Navigator.prototype, 'mediaDevices')),
                MediaDevices_proto_gum_desc: serializeDesc(Object.getOwnPropertyDescriptor(MediaDevices.prototype, 'getUserMedia')),
                MediaDevices_proto_enum_desc: serializeDesc(Object.getOwnPropertyDescriptor(MediaDevices.prototype, 'enumerateDevices')),
                gum_native_toString: MediaDevices.prototype.getUserMedia.toString(),
                gum_native_name: MediaDevices.prototype.getUserMedia.name,
                gum_native_length: MediaDevices.prototype.getUserMedia.length,
            };

            // Test getUserMedia parameter validation
            results.gum_parameter_validation = {};
            try {
                await navigator.mediaDevices.getUserMedia();
                results.gum_parameter_validation.no_args = { status: 'resolved' };
            } catch (e) {
                results.gum_parameter_validation.no_args = { status: 'rejected', name: e.name, message: e.message, type: e.constructor.name };
            }

            try {
                await navigator.mediaDevices.getUserMedia({});
                results.gum_parameter_validation.empty_obj = { status: 'resolved' };
            } catch (e) {
                results.gum_parameter_validation.empty_obj = { status: 'rejected', name: e.name, message: e.message, type: e.constructor.name };
            }

            try {
                await navigator.mediaDevices.getUserMedia({ video: false, audio: false });
                results.gum_parameter_validation.false_false = { status: 'resolved' };
            } catch (e) {
                results.gum_parameter_validation.false_false = { status: 'rejected', name: e.name, message: e.message, type: e.constructor.name };
            }

            try {
                await navigator.mediaDevices.getUserMedia({ video: { width: { min: 999999, exact: 999999 } } });
                results.gum_parameter_validation.overconstrained_width = { status: 'resolved' };
            } catch (e) {
                results.gum_parameter_validation.overconstrained_width = {
                    status: 'rejected',
                    name: e.name,
                    message: e.message,
                    type: e.constructor.name,
                    constraint: e.constraint
                };
            }

            try {
                await navigator.mediaDevices.getUserMedia({ video: { deviceId: { exact: "definitely-fake-device-id-999" } } });
                results.gum_parameter_validation.invalid_exact_device = { status: 'resolved' };
            } catch (e) {
                results.gum_parameter_validation.invalid_exact_device = {
                    status: 'rejected',
                    name: e.name,
                    message: e.message,
                    type: e.constructor.name,
                    constraint: e.constraint
                };
            }

            // Test successful stream & track properties
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                results.stream_properties = {
                    id: stream.id,
                    active: stream.active,
                    constructor: stream.constructor.name,
                    track_count: stream.getTracks().length,
                    video_track_count: stream.getVideoTracks().length,
                    audio_track_count: stream.getAudioTracks().length
                };

                const videoTrack = stream.getVideoTracks()[0];
                results.native_video_track = {
                    id: videoTrack.id,
                    kind: videoTrack.kind,
                    label: videoTrack.label,
                    enabled: videoTrack.enabled,
                    muted: videoTrack.muted,
                    readyState: videoTrack.readyState,
                    settings: videoTrack.getSettings ? videoTrack.getSettings() : null,
                    capabilities: videoTrack.getCapabilities ? videoTrack.getCapabilities() : null,
                    constraints: videoTrack.getConstraints ? videoTrack.getConstraints() : null
                };

                // Test track.clone()
                const clonedTrack = videoTrack.clone();
                results.track_clone = {
                    original_id: videoTrack.id,
                    cloned_id: clonedTrack.id,
                    is_distinct_id: videoTrack.id !== clonedTrack.id,
                    cloned_enabled: clonedTrack.enabled,
                    cloned_readyState: clonedTrack.readyState,
                    cloned_settings: clonedTrack.getSettings()
                };
                clonedTrack.stop();

                // Test track.stop()
                videoTrack.stop();
                results.track_after_stop = {
                    readyState: videoTrack.readyState,
                    enabled: videoTrack.enabled
                };

                stream.getTracks().forEach(t => t.stop());
            } catch (e) {
                results.native_stream_error = { name: e.name, message: e.message };
            }

            // Test Canvas captureStream
            const canvas = document.createElement('canvas');
            canvas.width = 640;
            canvas.height = 480;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = 'red';
            ctx.fillRect(0, 0, 640, 480);

            const canvasStream = canvas.captureStream(30);
            const canvasTrack = canvasStream.getVideoTracks()[0];
            results.canvas_stream = {
                stream_constructor: canvasStream.constructor.name,
                track_constructor: canvasTrack.constructor.name,
                track_is_MediaStreamTrack: canvasTrack instanceof MediaStreamTrack,
                track_proto: Object.getPrototypeOf(canvasTrack).constructor.name,
                has_canvas_property: 'canvas' in canvasTrack,
                canvas_property_ref_equal: canvasTrack.canvas === canvas,
                has_requestFrame: typeof canvasTrack.requestFrame === 'function',
                settings: canvasTrack.getSettings ? canvasTrack.getSettings() : null,
                capabilities: canvasTrack.getCapabilities ? canvasTrack.getCapabilities() : null,
                constraints: canvasTrack.getConstraints ? canvasTrack.getConstraints() : null,
                label: canvasTrack.label,
                id: canvasTrack.id
            };
            canvasTrack.stop();

            // --- SECTION 2: Device Enumeration & Identity Mocking ---
            const devices = await navigator.mediaDevices.enumerateDevices();
            results.device_enumeration = {
                count: devices.length,
                kinds: devices.map(d => d.kind),
                first_device: devices.length > 0 ? {
                    deviceId: devices[0].deviceId,
                    groupId: devices[0].groupId,
                    kind: devices[0].kind,
                    label: devices[0].label,
                    constructor: devices[0].constructor.name,
                    hasToJSON: typeof devices[0].toJSON === 'function',
                    toJSON_res: devices[0].toJSON()
                } : null
            };

            // Test MediaDeviceInfo constructor behavior
            try {
                new MediaDeviceInfo();
                results.media_device_info_constructor = { status: 'allowed' };
            } catch (e) {
                results.media_device_info_constructor = { status: 'rejected', name: e.name, message: e.message };
            }

            // Test mock device inheritance
            const mockDev = {
                deviceId: 'mock-123',
                groupId: 'group-123',
                kind: 'videoinput',
                label: 'Mock Camera',
                toJSON: function() { return { deviceId: this.deviceId, groupId: this.groupId, kind: this.kind, label: this.label }; }
            };
            Object.setPrototypeOf(mockDev, MediaDeviceInfo.prototype);
            results.mock_device_instanceof = mockDev instanceof MediaDeviceInfo;

            // --- SECTION 3: JavaScript Metaprogramming & Prototype Invariants ---
            results.prototype_descriptors = {
                'MediaDevices.prototype.getUserMedia': serializeDesc(Object.getOwnPropertyDescriptor(MediaDevices.prototype, 'getUserMedia')),
                'MediaDevices.prototype.enumerateDevices': serializeDesc(Object.getOwnPropertyDescriptor(MediaDevices.prototype, 'enumerateDevices')),
                'Navigator.prototype.mediaDevices': serializeDesc(Object.getOwnPropertyDescriptor(Navigator.prototype, 'mediaDevices')),
                'HTMLIFrameElement.prototype.contentWindow': serializeDesc(Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow')),
                'HTMLIFrameElement.prototype.contentDocument': serializeDesc(Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentDocument')),
                'Document.prototype.createElement': serializeDesc(Object.getOwnPropertyDescriptor(Document.prototype, 'createElement')),
                'Node.prototype.appendChild': serializeDesc(Object.getOwnPropertyDescriptor(Node.prototype, 'appendChild')),
                'Node.prototype.insertBefore': serializeDesc(Object.getOwnPropertyDescriptor(Node.prototype, 'insertBefore')),
                'Node.prototype.replaceChild': serializeDesc(Object.getOwnPropertyDescriptor(Node.prototype, 'replaceChild')),
                'Element.prototype.attachShadow': serializeDesc(Object.getOwnPropertyDescriptor(Element.prototype, 'attachShadow'))
            };

            // Test Function.prototype.toString spoofing
            const fakeFn = function getUserMedia() {};
            const origToString = Function.prototype.toString;
            // Native function toString representation:
            results.native_function_tostring = origToString.call(MediaDevices.prototype.getUserMedia);

            // Test iframe synchronous creation behavior
            const unattachedIframe = document.createElement('iframe');
            results.iframe_lifecycle = {
                unattached_contentWindow: unattachedIframe.contentWindow === null ? 'null' : typeof unattachedIframe.contentWindow,
                unattached_contentDocument: unattachedIframe.contentDocument === null ? 'null' : typeof unattachedIframe.contentDocument
            };

            document.body.appendChild(unattachedIframe);
            results.iframe_lifecycle.attached_contentWindow = typeof unattachedIframe.contentWindow;
            results.iframe_lifecycle.attached_contentDocument = typeof unattachedIframe.contentDocument;
            results.iframe_lifecycle.is_separate_realm = unattachedIframe.contentWindow.MediaDevices.prototype !== MediaDevices.prototype;
            results.iframe_lifecycle.is_separate_MediaDevices_instance = unattachedIframe.contentWindow.navigator.mediaDevices !== navigator.mediaDevices;
            results.iframe_lifecycle.is_separate_Window = unattachedIframe.contentWindow.Window !== window.Window;
            unattachedIframe.remove();

            return results;
        }
        """

        output = await page.evaluate(probe_script)
        await browser.close()
        return output

if __name__ == "__main__":
    results = asyncio.run(run_probe())
    with open(r"c:\Users\pc\Master AI2brands Saas\webcam-mirror-extension\test\webrtc_spec_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("PROBE_SUCCESS")
