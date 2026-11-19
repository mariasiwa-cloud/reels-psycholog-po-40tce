"""Wspólne narzędzia do filmów TikTok SENS (@senswroclaw).

Format: 1080x1920, 30 fps. Strefa bezpieczna TikToka: tekst tylko w SAFE (x 80-940, y 200-1360) —
na dole jest opis i nazwa konta, po prawej przyciski (serce, komentarze, udostępnij).
Fonty: ../../narzedzia/fonts (uruchom raz ../../narzedzia/pobierz_fonty.sh).
"""
import math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SR = 1080, 1920, 30, 44100
SAFE = (80, 200, 940, 1360)
CX = 510  # środek treści lekko w lewo (przyciski TikToka po prawej)

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "..", "narzedzia", "fonts") + "/"
ASSETS = os.path.join(HERE, "..", "assets") + "/"

# kolory SENS
LAV, LAVD, INK, ACC, GREEN, YEL = (150, 120, 156), (129, 89, 131), (30, 52, 59), (108, 84, 214), (0, 84, 71), (254, 217, 14)
BG, WHITE, NIGHT = (247, 242, 248), (255, 255, 255), (20, 38, 44)
LAVL = (222, 206, 226)  # jasna lawenda na ciemnym tle

XB, B, M, CV = "Poppins-ExtraBold.ttf", "Poppins-Bold.ttf", "Poppins-Medium.ttf", "Caveat[wght].ttf"
_FC = {}


def font(name, size):
    k = (name, size)
    if k not in _FC:
        f = ImageFont.truetype(FONTS + name, size)
        if name.startswith("Caveat"):
            f.set_variation_by_axes([700])
        _FC[k] = f
    return _FC[k]


def asset(name, width=None):
    im = Image.open(ASSETS + name).convert("RGBA")
    if width:
        im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    return im


def text_sprite(lines, fnt, color, gap=1.18, align="center", pad=24):
    """lines: lista linii; linia = str albo lista (tekst, kolor)."""
    norm = [[(l, color)] if isinstance(l, str) else l for l in lines]
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * gap)
    widths = [sum(fnt.getlength(t) for t, _ in l) for l in norm]
    w = int(max(widths)) + pad * 2
    h = lh * len(norm) + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(norm):
        x = pad + ((w - 2 * pad - widths[i]) / 2 if align == "center" else 0)
        for t, c in l:
            d.text((x, pad + i * lh), t, font=fnt, fill=c)
            x += fnt.getlength(t)
    return im


def fit_font(lines, name, size, maxw):
    while max(font(name, size).getlength(l if isinstance(l, str) else "".join(t for t, _ in l)) for l in lines) > maxw:
        size -= 2
    return font(name, size)


def card_sprite(w, h, r=48, fill=WHITE, shadow=(60, 40, 70, 60)):
    m = 70
    im = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((m, m + 16, m + w, m + h + 16), r, fill=shadow)
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(26)))
    ImageDraw.Draw(im).rounded_rectangle((m, m, m + w, m + h), r, fill=fill if len(fill) == 4 else fill + (255,))
    return im, m


def pill(text, fnt, fg=WHITE, bgc=LAVD, padx=50, h=None):
    tx = text_sprite([text], fnt, fg, pad=0)
    h = h or int(tx.height * 1.9)
    im = Image.new("RGBA", (tx.width + 2 * padx, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, h - 1), h // 2, fill=bgc + (255,) if len(bgc) == 3 else bgc)
    im.alpha_composite(tx, (padx, (h - tx.height) // 2 - 2))
    return im


def paste(base, spr, cx, cy, a=1.0):
    if a <= 0.004:
        return
    if a < 0.996:
        spr = spr.copy()
        spr.putalpha(spr.getchannel("A").point(lambda v: int(v * a)))
    base.alpha_composite(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)))


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ramp(t, t0, dur):
    return ease((t - t0) / dur)


def win(t, t0, t1, fin=0.4, fout=0.35):
    """widoczność elementu między t0 i t1 (z wejściem i wyjściem)."""
    return ramp(t, t0, fin) * (1 - ramp(t, t1 - fout, fout))


# ---------- tła ----------
def _blobs(base, spots, blur):
    im = Image.new("RGB", (W + 240, H + 240), base)
    d = ImageDraw.Draw(im)
    for (x, y, r, c) in spots:
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(blur))


LIGHT = _blobs(BG, [(180, 320, 520, (232, 220, 236)), (1150, 900, 600, (238, 228, 242)),
                    (300, 1900, 640, (228, 214, 233)), (1100, 2050, 380, (243, 236, 226))], 170)
DARK = _blobs(NIGHT, [(200, 300, 520, (34, 60, 68)), (1100, 1000, 640, (40, 48, 70)),
                      (300, 1900, 600, (26, 50, 56))], 180)


def bg(img, gt):
    ox = 120 + 100 * math.sin(gt * 0.11)
    oy = 120 + 100 * math.cos(gt * 0.09)
    return img.crop((int(ox), int(oy), int(ox) + W, int(oy) + H)).convert("RGBA")


# ---------- render ----------
def render(frame_fn, total, out_mp4, music_wav):
    """frame_fn(t) -> PIL RGBA; zapisuje film z muzyką, głośność -14 LUFS."""
    silent = out_mp4 + ".silent.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    for n in range(int(round(total * FPS))):
        p.stdin.write(frame_fn(n / FPS).convert("RGB").tobytes())
    p.stdin.close()
    assert p.wait() == 0
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", music_wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                    "-shortest", "-movflags", "+faststart", out_mp4], check=True)
    os.remove(silent)


def sheet(frame_fn, times, path):
    ims = [frame_fn(t).convert("RGB").resize((360, 640)) for t in times]
    g = Image.new("RGB", (370 * len(ims), 650), (90, 90, 90))
    for i, im in enumerate(ims):
        g.paste(im, (5 + 370 * i, 5))
        d = ImageDraw.Draw(g)
        x0, y0, x1, y1 = [v / 3 for v in SAFE]
        d.rectangle((5 + 370 * i + x0, 5 + y0, 5 + 370 * i + x1, 5 + y1), outline=(255, 0, 0))
    g.save(path, quality=85)


# ---------- muzyka (oryginalna, syntetyczna) ----------
def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


class Mix:
    def __init__(self, total, seed=7):
        self.n = int(total * SR)
        self.total = total
        self.bus = {}
        self.rng = np.random.default_rng(seed)

    def add(self, bus, t0, sig, gain=1.0):
        a = self.bus.setdefault(bus, np.zeros(self.n))
        i0 = int(t0 * SR)
        if i0 >= self.n or i0 < 0:
            return
        L = min(len(sig), self.n - i0)
        a[i0:i0 + L] += gain * sig[:L]

    # instrumenty
    def kick(self):
        L = int(0.4 * SR); t = np.arange(L) / SR
        f = 48 + 110 * np.exp(-t * 32)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8) * np.clip(t / 0.002, 0, 1)

    def _flt(self, x, lo=None, hi=None):
        X = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR)
        if lo: X[fr < lo] = 0
        if hi: X[fr > hi] = 0
        return np.fft.irfft(X, len(x))

    def clap(self):
        L = int(0.25 * SR); t = np.arange(L) / SR
        env = sum(np.where(t >= o, np.exp(-(t - o) * (55 if o < 0.02 else 14)), 0) for o in (0, 0.011, 0.022))
        return self._flt(self.rng.standard_normal(L), 900, 3200) * env * 1.4

    def hat(self, open_=False):
        L = int((0.18 if open_ else 0.045) * SR); t = np.arange(L) / SR
        return self._flt(self.rng.standard_normal(L), 7000) * np.exp(-t * (18 if open_ else 95))

    def pluck(self, m, dur=0.4, bright=6, decay=6):
        L = int(dur * SR); t = np.arange(L) / SR; f = mtof(m)
        s = sum(np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (decay + 4 * k)) for k in range(1, bright + 1))
        return s * np.clip(t / 0.003, 0, 1)

    def keys(self, m, dur):
        L = int(dur * SR); t = np.arange(L) / SR; f = mtof(m)
        s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)
        return s * np.exp(-t * 2.2) * np.clip(t / 0.005, 0, 1)

    def bass(self, m, dur):
        L = int(dur * SR); t = np.arange(L) / SR; f = mtof(m)
        s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
        return s * np.clip(t / 0.004, 0, 1) * np.clip((dur - t) / 0.03, 0, 1)

    def blip(self, m=84):
        return self.pluck(m, 0.18, 3, 14)

    def tick(self):
        L = int(0.03 * SR); t = np.arange(L) / SR
        return self._flt(self.rng.standard_normal(L), 2500, 9000) * np.exp(-t * 160)

    def riser(self, dur):
        L = int(dur * SR); t = np.arange(L) / SR
        return self._flt(self.rng.standard_normal(L), 1200) * (t / dur) ** 2.2

    def save(self, path, gains=None):
        gains = gains or {}
        out = sum(gains.get(k, 1.0) * v for k, v in self.bus.items())
        t = np.arange(self.n) / SR
        out *= np.clip(t / 0.05, 0, 1) * np.clip((self.total - t) / 1.2, 0, 1)
        out = np.tanh(out / (np.max(np.abs(out)) + 1e-9) * 1.4) * 0.7
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((out * 32767).astype(np.int16).tobytes())
