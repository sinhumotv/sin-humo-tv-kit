#!/usr/bin/env python3
"""Genera fondo.jpg (papel beige con cuadrícula, ruido suave y viñeta), una sola vez."""
import os
import numpy as np
from PIL import Image, ImageDraw
W, H, s = 1080, 1920, 1.5
img = Image.new("RGB", (W, H), (0xf6, 0xeb, 0xd0)); d = ImageDraw.Draw(img)
for x in np.arange(0, W, 40 * s): d.line([(x, 0), (x, H)], fill=(0xe4, 0xd3, 0xa8), width=2)
for y in np.arange(0, H, 40 * s): d.line([(0, y), (W, y)], fill=(0xe4, 0xd3, 0xa8), width=2)
a = np.asarray(img).astype(np.float32)
n = np.random.default_rng(7).normal(0, 1, (H // 3, W // 3)); n = np.kron(n, np.ones((3, 3)))[:H, :W]
a += n[..., None] * 4.5
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
v = np.clip((r - 0.55) / 0.6, 0, 1) ** 1.6
a = a * (1 - 0.16 * v[..., None]) + np.array([90, 60, 30]) * 0.16 * v[..., None]
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fondo.jpg"), quality=92)
