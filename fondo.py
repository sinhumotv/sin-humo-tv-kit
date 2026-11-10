#!/usr/bin/env python3
"""Genera fondo.jpg (papel beige con cuadrícula, ruido suave y viñeta), una sola vez."""
import os
import numpy as np
from PIL import Image, ImageDraw
import sys
HOR = len(sys.argv) > 1 and sys.argv[1] == "h"
CLASICO = not (len(sys.argv) > 1 and sys.argv[1] in ("m", "mh"))
if CLASICO:
    W, H, s = (1920, 1080, 1.5) if HOR else (1080, 1920, 1.5)
    img = Image.new("RGB", (W, H), (0xf6, 0xeb, 0xd0)); d = ImageDraw.Draw(img)
    for x in np.arange(0, W, 40 * s): d.line([(x, 0), (x, H)], fill=(0xe4, 0xd3, 0xa8), width=2)
    for y in np.arange(0, H, 40 * s): d.line([(0, y), (W, y)], fill=(0xe4, 0xd3, 0xa8), width=2)
    a = np.asarray(img).astype(np.float32)
    n = np.random.default_rng(7).normal(0, 1, (H // 3, W // 3)); n = np.kron(n, np.ones((3, 3)))[:H, :W]
    a += n[..., None] * 4.5
    yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = np.clip((r - 0.55) / 0.6, 0, 1) ** 1.6
    a = a * (1 - 0.16 * v[..., None]) + np.array([90, 60, 30]) * 0.16 * v[..., None]
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fondo_h.jpg" if HOR else "fondo.jpg"), quality=92)

def moderno(hor):
    """v30 · Fondo del aspecto moderno: degradado oscuro (tinta → morado), dos brillos suaves (naranja y turquesa),
    trama de puntos muy fina y viñeta."""
    W, H = (1920, 1080) if hor else (1080, 1920)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u, v = xx / W, yy / H
    g = (u * (0.35 if hor else 0.25) + v * (0.65 if hor else 0.75))[..., None]
    a = np.array([0x14, 0x11, 0x1d]) * (1 - g) + np.array([0x2b, 0x1f, 0x3d]) * g
    def brillo(cx, cy, r, color, f):
        d = np.sqrt(((xx - cx * W) / (r * max(W, H))) ** 2 + ((yy - cy * H) / (r * max(W, H))) ** 2)
        return np.clip(1 - d, 0, 1)[..., None] ** 2.2 * np.array(color) * f
    a = a + brillo(0.05, 0.98, 0.55, (0xf0, 0x7d, 0x2a), 0.34) + brillo(1.0, 0.02, 0.5, (0x2a, 0xa6, 0xa0), 0.26) + brillo(0.5, 0.45, 0.6, (0x6b, 0x4f, 0xa3), 0.12)
    paso = 36
    puntos = ((xx % paso < 3) & (yy % paso < 3))[..., None]
    a = a + puntos * 14
    n = np.random.default_rng(7).normal(0, 1, (H // 2 + 1, W // 2 + 1)); n = np.kron(n, np.ones((2, 2)))[:H, :W]
    a += n[..., None] * 2.2
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    a = a * (1 - 0.35 * np.clip((r - 0.6) / 0.7, 0, 1) ** 1.5)[..., None]
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fondo_mh.jpg" if hor else "fondo_m.jpg"), quality=93)


if len(sys.argv) > 1 and sys.argv[1] in ("m", "mh"):
    moderno(sys.argv[1] == "mh")
