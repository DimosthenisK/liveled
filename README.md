# LiveLED

A Pico app and a browser app that share one BLE session. The Pico advertises. The page paints an 8×8 matrix and sends those colors to the LEDs.

## Pico

`liveled-pico/main.py` imports `ble`, `onboard_led`, and `ws2812b`. On startup it clears the matrix and advertises as `LiveLED`. The onboard LED turns on while a central is connected and turns off when that connection ends. Incoming packets fill 64 colors. The last packet unpacks them and lights the matrix.

From `liveled-pico`. This attaches the shared Pico into WSL, then installs and runs:

```bash
./run.sh
```

That installs `ble` at `v0.2.0` from `github:DimosthenisK/pico-lib`, copies the local `ble`, `ws2812b`, and `onboard_led` modules onto the board, copies `main.py` to the board, then runs it. The data pin is GP16.

A packet is `offset` as a little-endian uint16, `length`, `flags`, then `length` bytes. Bit 0 of `flags` marks the last packet. Bit 1 means the payload is the raw 192-byte color buffer. Otherwise the payload is run-length encoded and unpacks to those 192 bytes. Each LED is red, green, blue. The page sends the bottom row first, and each row right to left, so the canvas matches the panel. Each write carries at most 16 payload bytes. The Pico treats that write as a whole packet.

## PWA

Local development, from `liveled-pwa`:

```bash
python3 dev.py
```

Open `http://127.0.0.1:8082` in Chrome or Edge. Web Bluetooth does not run over plain HTTP except on localhost. Connect, pick a color and a brightness, then draw. Brightness scales the colors sent to the LEDs. The canvas keeps the colors you painted. Each change starts a transfer. If a transfer is already running, later changes wait and the latest matrix is sent when the radio is free. A 250ms poll sends anything still waiting.

## CapRover

The repository root has `captain-definition`. It builds `liveled-pwa/Dockerfile`, which serves the page with nginx on port 80. CapRover terminates HTTPS in front of that port.

Create an app named `liveled`. Leave the container HTTP port at 80. Enable HTTPS, then force HTTPS. Web Bluetooth runs in Chrome or Edge only on that `https://` address, on a device that is next to the Pico.

In the app's Deployment tab, set the repository to `github.com/DimosthenisK/liveled`, branch `main`, and your GitHub username. For a public repository the password can be any non-empty text. Save, copy the webhook CapRover shows, and add it to the GitHub repository: Settings, Webhooks, content type `application/json`, push events only. The next push to `main` builds and deploys the page.
