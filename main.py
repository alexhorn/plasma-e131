import time
import rp2
import network
import plasma
from config import *
from colorsys import hsv_to_rgb
from e131 import E131Server

rp2.country(COUNTRY)

nic = network.WLAN(network.STA_IF)
nic.config(pm=network.WLAN.PM_NONE)
if not nic.active():
    nic.active(True)
if not nic.isconnected():
    nic.connect(SSID, PSK)

led_strip = plasma.WS2812(NUM_LEDS, 0, 0, plasma.plasma_stick.DAT, color_order=plasma.COLOR_ORDER_RGB, rgbw=RGBW)
led_strip.start(FPS)

print('Connecting ...')

def set_color(r, g, b, w=0):
    r = int(r * POWER_LIMIT)
    g = int(g * POWER_LIMIT)
    b = int(b * POWER_LIMIT)
    w = int(w * POWER_LIMIT)
    led_strip.set_rgb(0, r, g, b, w)

hue = 0.0
while not nic.isconnected():
    r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
    set_color(r * 255, g * 255, b * 255)
    time.sleep(0.01)
    hue = (hue + 0.001) % 1.0
    if nic.status() == network.STAT_WRONG_PASSWORD:
        print('Wrong password')
    elif nic.status() == network.STAT_NO_AP_FOUND:
        print('No AP found')
    elif nic.status() == network.STAT_CONNECT_FAIL:
        print('Connection failed')

print('Connected!')

server = E131Server()
server.bind('0.0.0.0', 5568)

while nic.isconnected():
    dmx = server.recv()
    if dmx is not None:
        r = dmx[0]
        g = dmx[1]
        b = dmx[2]
        w = dmx[3]
        print(f'R: {r}, G: {g}, B: {b}, W: {w}')
        set_color(r, g, b, w)
