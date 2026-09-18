import asyncio
import http.server
import json
import socketserver
import threading
from playwright.async_api import async_playwright

PORT = 9877

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def start_server():
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), QuietHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd

async def run_invariants_test():
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

        eval_script = """
        async () => {
            const results = {};

            // 1. Test ToString and Prototype spoofing
            const nativeGUM = MediaDevices.prototype.getUserMedia;
            
            // Apply pristine stealth patch pattern
            const toStringMap = new WeakMap();
            const origToString = Function.prototype.toString;

            const stealthToString = function toString() {
                if (toStringMap.has(this)) {
                    return toStringMap.get(this);
                }
                return origToString.call(this);
            };

            // Spoof toString itself
            toStringMap.set(stealthToString, "function toString() { [native code] }");
            Object.defineProperty(Function.prototype, 'toString', {
                value: stealthToString,
                writable: true,
                configurable: true,
                enumerable: false
            });

            // Wrap getUserMedia
            const wrappedGUM = function getUserMedia(constraints) {
                return nativeGUM.call(this, constraints);
            };
            Object.defineProperty(wrappedGUM, 'name', { value: 'getUserMedia', configurable: true });
            Object.defineProperty(wrappedGUM, 'length', { value: 0, configurable: true });
            toStringMap.set(wrappedGUM, "function getUserMedia() { [native code] }");

            // Apply to prototype with exact native descriptors
            Object.defineProperty(MediaDevices.prototype, 'getUserMedia', {
                value: wrappedGUM,
                writable: true,
                enumerable: true,
                configurable: true
            });

            // Inspect wrapped function properties
            results.stealth_gum = {
                toString_call: wrappedGUM.toString(),
                Function_proto_toString_call: Function.prototype.toString.call(wrappedGUM),
                string_concat: "" + wrappedGUM,
                name: wrappedGUM.name,
                length: wrappedGUM.length,
                descriptor: Object.getOwnPropertyDescriptor(MediaDevices.prototype, 'getUserMedia'),
                toString_own_toString: Function.prototype.toString.toString()
            };

            // 2. Test iframe interception vectors
            let iframeInterceptionAttempts = {};

            // A) Test standard createElement + appendChild
            const ifr1 = document.createElement('iframe');
            document.body.appendChild(ifr1);
            iframeInterceptionAttempts.standard_append = {
                hasGUM: typeof ifr1.contentWindow.navigator.mediaDevices.getUserMedia === 'function',
                is_isolated_from_top_proto: ifr1.contentWindow.MediaDevices.prototype.getUserMedia !== MediaDevices.prototype.getUserMedia
            };
            ifr1.remove();

            // B) Test Shadow DOM appendChild
            const hostDiv = document.createElement('div');
            document.body.appendChild(hostDiv);
            const shadow = hostDiv.attachShadow({ mode: 'closed' });
            const ifr2 = document.createElement('iframe');
            shadow.appendChild(ifr2);
            iframeInterceptionAttempts.shadow_dom_append = {
                hasGUM: typeof ifr2.contentWindow.navigator.mediaDevices.getUserMedia === 'function',
                is_isolated_from_top_proto: ifr2.contentWindow.MediaDevices.prototype.getUserMedia !== MediaDevices.prototype.getUserMedia
            };
            hostDiv.remove();

            // C) Test insertBefore
            const ifr3 = document.createElement('iframe');
            document.body.insertBefore(ifr3, document.body.firstChild);
            iframeInterceptionAttempts.insert_before = {
                hasGUM: typeof ifr3.contentWindow.navigator.mediaDevices.getUserMedia === 'function',
                is_isolated_from_top_proto: ifr3.contentWindow.MediaDevices.prototype.getUserMedia !== MediaDevices.prototype.getUserMedia
            };
            ifr3.remove();

            // D) Test srcdoc iframe
            const ifr4 = document.createElement('iframe');
            ifr4.srcdoc = "<html><body><h1>srcdoc</h1></body></html>";
            document.body.appendChild(ifr4);
            iframeInterceptionAttempts.srcdoc = {
                hasGUM: typeof ifr4.contentWindow.navigator.mediaDevices.getUserMedia === 'function',
                is_isolated_from_top_proto: ifr4.contentWindow.MediaDevices.prototype.getUserMedia !== MediaDevices.prototype.getUserMedia
            };
            ifr4.remove();

            // E) Test iframe contentDocument.defaultView
            const ifr5 = document.createElement('iframe');
            document.body.appendChild(ifr5);
            iframeInterceptionAttempts.contentDocument_defaultView = {
                sameWindow: ifr5.contentDocument.defaultView === ifr5.contentWindow
            };
            ifr5.remove();

            // F) Test window.frames indexing
            const ifr6 = document.createElement('iframe');
            ifr6.name = "testFrame6";
            document.body.appendChild(ifr6);
            iframeInterceptionAttempts.window_frames = {
                by_index: window.frames[window.frames.length - 1] === ifr6.contentWindow,
                by_name: window.frames["testFrame6"] === ifr6.contentWindow
            };
            ifr6.remove();

            results.iframe_interception_attempts = iframeInterceptionAttempts;

            // 3. Test comprehensive patch hook on HTMLIFrameElement.prototype.contentWindow
            const origContentWindowDesc = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow');
            let patchedIframeCalls = 0;

            Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                get: function() {
                    const win = origContentWindowDesc.get.call(this);
                    if (win && !win.__MOCKED__) {
                        win.__MOCKED__ = true;
                        patchedIframeCalls++;
                        try {
                            if (win.MediaDevices && win.MediaDevices.prototype) {
                                win.MediaDevices.prototype.getUserMedia = wrappedGUM;
                            }
                            if (win.navigator && win.navigator.mediaDevices) {
                                win.navigator.mediaDevices.getUserMedia = wrappedGUM;
                            }
                        } catch(e) {}
                    }
                    return win;
                },
                enumerable: origContentWindowDesc.enumerable,
                configurable: origContentWindowDesc.configurable
            });

            // Test if patched contentWindow works
            const ifrTest = document.createElement('iframe');
            document.body.appendChild(ifrTest);
            const win = ifrTest.contentWindow;
            results.patched_contentWindow_test = {
                patchedCalls: patchedIframeCalls,
                iframe_received_mock_gum: win.navigator.mediaDevices.getUserMedia === wrappedGUM
            };
            ifrTest.remove();

            return results;
        };
        """

        output = await page.evaluate(eval_script)
        await browser.close()
        return output

if __name__ == "__main__":
    results = asyncio.run(run_invariants_test())
    with open(r"c:\Users\pc\Master AI2brands Saas\webcam-mirror-extension\test\invariants_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("INVARIANTS_SUCCESS")
