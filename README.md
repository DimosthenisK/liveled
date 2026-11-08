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

## Production (NixOS homeserver)

Push `main` builds `liveled-pwa/` via `.github/workflows/deploy.yml`, publishes `ghcr.io/dimosthenisk/liveled:main`, then hits `https://deploy.dimosthenis.dev/deploy/liveled`. The homeserver stack is a thin compose file that pulls that image (loopback `127.0.0.1:8085`).

| URL | Scope |
| --- | --- |
| https://liveled.dimosthenis.dev | Public (Cloudflare Tunnel) |
| https://liveled.afrino-macaroni.ts.net | Tailnet |

Repo secret required: `DEPLOY_WEBHOOK_TOKEN`. Guide: https://github.com/DimosthenisK/homeserver-directory

Web Bluetooth needs HTTPS (or localhost) in Chrome/Edge, on a device next to the Pico.

Local image: `docker build -t liveled-pwa liveled-pwa`.
