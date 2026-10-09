import bluetooth

from ble import Bluetooth
from onboard_led import OnboardLED
from ws2812b import WS2812B

# 8x8 matrix, three bytes per LED: red, green, blue.
# Rows arrive from the bottom, and each row right to left, so the canvas matches the panel.
WIDTH = 8
HEIGHT = 8
LEDS = WIDTH * HEIGHT
FRAME = LEDS * 3
DATA = 16

# Each BLE write is one packet:
#   offset uint16 little-endian, length uint8, flags uint8, then `length` bytes.
# flags bit 0 marks the last packet. Bit 1 means the payload is raw.
# Otherwise the payload is run-length encoded. A code is one control byte:
#   bit 7 set: repeat the next byte ((ctrl & 0x7f) + 1) times
#   bit 7 clear: copy the next ((ctrl & 0x7f) + 1) bytes
# A complete payload unpacks to exactly FRAME bytes.
_LAST = 1
_RAW = 2

leds = WS2812B(DATA)
led = OnboardLED()
radio = Bluetooth()
filled = 0
comp = bytearray(FRAME)
frame = bytearray(FRAME)


def _show():
    for index in range(LEDS):
        offset = index * 3
        leds.set(index, frame[offset], frame[offset + 1], frame[offset + 2])
    leds.show()


def _decode(n):
    i = 0
    o = 0
    while i < n:
        ctrl = comp[i]
        i += 1
        count = (ctrl & 0x7F) + 1
        if o + count > FRAME:
            return False
        if ctrl & 0x80:
            if i >= n:
                return False
            frame[o:o + count] = bytes((comp[i],)) * count
            i += 1
            o += count
        else:
            if i + count > n:
                return False
            frame[o:o + count] = comp[i:i + count]
            i += count
            o += count
    return o == FRAME


def _reject(data):
    print("bad frame", len(data), bytes(data[:8]))


def _apply(flags):
    if flags & _RAW:
        if filled != FRAME:
            print("bad frame raw", filled)
            return
        frame[:] = comp
    elif not _decode(filled):
        print("bad frame rle", filled)
        return
    try:
        _show()
    except Exception as err:
        print("draw", err)


def incoming(data):
    # One BLE write is one packet. A short write must not borrow bytes from
    # the next write, or every later frame stays misaligned.
    global filled
    if len(data) < 4:
        _reject(data)
        return
    offset = data[0] | (data[1] << 8)
    length = data[2]
    flags = data[3]
    if length == 0 or len(data) != 4 + length:
        _reject(data)
        return
    end = offset + length
    if offset > FRAME or end > FRAME:
        _reject(data)
        return
    if offset == 0:
        filled = 0
    if offset != filled:
        _reject(data)
        filled = 0
        return
    comp[offset:end] = data[4:]
    filled = end
    if flags & _LAST:
        _apply(flags)
        filled = 0


try:
    hw = bluetooth.BLE()
    hw.active(True)
    hw.config(mtu=256)
except Exception as err:
    print("mtu", err)

def connected(up):
    if up:
        led.on()
    else:
        led.off()


print("advertising as LiveLED")
radio.open(incoming, name="LiveLED", on_connect=connected)
