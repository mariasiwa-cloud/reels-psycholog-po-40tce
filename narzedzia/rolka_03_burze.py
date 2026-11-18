import os
import sys, os, math, random, subprocess, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from base import (W, H, FPS, LAV, LAVD, INK, GREEN, WHITE, BGIM, XB, B, M, CV,
                  font, text_sprite, card_sprite, paste, ease, ramp)
from scipy.signal import butter, lfilter, fftconvolve

TOTAL = 33.0
SPR = {}
YEL = (254, 217, 14)


def make_storm():
    bw, bh = W + 240, H + 240
    im = Image.new("RGB", (bw, bh), (34, 48, 58))
    d = ImageDraw.Draw(im)
    for (x, y, r, c) in [(200, 300, 600, (70, 62, 92)), (1150, 700, 620, (44, 70, 78)),
                         (350, 1800, 700, (78, 60, 92)), (1050, 2100, 420, (48, 64, 74))]:
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(180))


STORM = make_storm()


def bg(gt):
    ox = 120 + 100 * math.sin(gt * 0.11)
    oy = 120 + 100 * math.cos(gt * 0.09)
    box = (int(ox), int(oy), int(ox) + W, int(oy) + H)
    p = ramp(gt, 11.8, 2.5)
    s = STORM.crop(box)
    im = s if p <= 0 else Image.blend(s, BGIM.crop(box), p)
    return im.convert("RGBA")


def cloud(w, h, col):
    im = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    o = 40
    for (cx, cy, r) in [(0.22, 0.62, 0.30), (0.42, 0.42, 0.38), (0.66, 0.48, 0.33), (0.82, 0.66, 0.24), (0.5, 0.7, 0.3)]:
        d.ellipse((o + (cx - r * 0.75) * w, o + (cy - r) * h, o + (cx + r * 0.75) * w, o + (cy + r) * h), fill=col + (255,))
    d.rounded_rectangle((o + 0.1 * w, o + 0.55 * h, o + 0.92 * w, o + 0.92 * h), int(0.18 * h), fill=col + (255,))
    sh = im.filter(ImageFilter.GaussianBlur(3))
    return sh


def chip(text, fg=WHITE, bgc=(255, 255, 255, 40), size=36, fnt=M):
    tx = text_sprite([text], font(fnt, size), fg, pad=0)
    w, h = tx.width + 48, tx.height + 26
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=bgc, outline=(255, 255, 255, 120), width=2)
    im.alpha_composite(tx, (24, 13 - 4))
    return im


def house():
    im = Image.new("RGBA", (420, 380), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (214, 190, 220, 255)
    d.line([(30, 170), (210, 30), (390, 170)], fill=c, width=14, joint="curve")
    d.rectangle((70, 165, 350, 360), outline=c, width=14)
    d.rectangle((180, 250, 240, 360), outline=c, width=10)
    for x in (100, 270):
        d.rectangle((x, 205, x + 50, 250), outline=c, width=8)
    return im


def bolt():
    im = Image.new("RGBA", (220, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(120, 0), (40, 250), (110, 250), (60, 520), (200, 200), (120, 200), (170, 0)]
    d.polygon(pts, fill=YEL + (255,))
    g = im.filter(ImageFilter.GaussianBlur(14))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(g); out.alpha_composite(g); out.alpha_composite(im)
    return out


def quote_card(num, quote_lines, sub):
    cw = 960
    q = text_sprite(quote_lines, font(B, 54), INK, align="left", gap=1.18, pad=0)
    s = text_sprite([sub], font(M, 38), LAVD, align="left", pad=0)
    ch = q.height + s.height + 130
    card, m = card_sprite(cw, ch)
    n = text_sprite([str(num)], font(XB, 170), LAV, pad=0)
    card.alpha_composite(n, (m + 50, m + 30))
    card.alpha_composite(q, (m + 200, m + 55))
    card.alpha_composite(s, (m + 200, m + 55 + q.height + 26))
    return card


def prep():
    SPR["tv"] = chip("PROGNOZA POGODY · TWÓJ DOM", WHITE, (129, 89, 131, 255), 34, B)
    SPR["h1"] = text_sprite(["Ty w perimenopauzie."], font(XB, 86), WHITE)
    SPR["h2"] = text_sprite(["Ona w dojrzewaniu."], font(XB, 86), (214, 190, 220))
    SPR["h3"] = text_sprite(["Dwie burze hormonalne", "pod jednym dachem"], font(CV, 92), (236, 228, 242), gap=1.0)
    SPR["cl"] = cloud(470, 250, (96, 84, 116))
    SPR["cr"] = cloud(470, 250, (70, 96, 104))
    SPR["fl"] = text_sprite(["Front:", "perimenopauza"], font(B, 44), WHITE, gap=1.05)
    SPR["fr"] = text_sprite(["Front:", "dojrzewanie"], font(B, 44), WHITE, gap=1.05)
    SPR["chl"] = [chip(t) for t in ["drażliwość", "zmęczenie", "mniej cierpliwości"]]
    SPR["chr"] = [chip(t) for t in ["trzaśnięte drzwi", "„Nic nie rozumiesz!”", "huśtawki nastroju"]]
    SPR["house"] = house()
    SPR["bolt"] = bolt()
    l = text_sprite([[("Prognoza: ", LAVD), ("przelotne kłótnie", INK)], [("przy kolacji. Możliwe", INK)],
                     [("trzaśnięcia drzwiami.", INK)]], font(XB, 60), INK, gap=1.12, pad=10)
    cw = max(860, l.width + 90)
    c, m = card_sprite(cw, l.height + 100)
    c.alpha_composite(l, (m + (cw - l.width) // 2, m + 50))
    SPR["fc"] = c
    SPR["t1"] = text_sprite(["3 zdania,"], font(XB, 130), INK)
    SPR["t2"] = text_sprite(["które nie dolewają oliwy"], font(B, 62), LAVD)
    SPR["q1"] = quote_card(1, ["„Widzę, że jesteś zła.", "Wrócimy do tego, gdy", "obie ochłoniemy.”"],
                           "Nazwij emocję, rozmowę odłóż na później.")
    SPR["q2"] = quote_card(2, ["„Nie musisz teraz", "nic mówić.", "Jestem obok.”"],
                           "Obecność bez przesłuchania i kazań.")
    SPR["q3"] = quote_card(3, ["„Mam dziś gorszy dzień.", "To nie przez ciebie.”"],
                           "Twoje emocje też mają nazwę.")
    l = text_sprite([[("Obie zmieniacie się", INK)], [("naraz.", LAVD)]], font(XB, 76), INK, gap=1.1, pad=10)
    l2 = text_sprite(["To nie znaczy, że coś", "jest z wami nie tak."], font(M, 50), INK, gap=1.2, pad=0)
    cw = 900
    c, m = card_sprite(cw, l.height + l2.height + 140)
    c.alpha_composite(l, (m + (cw - l.width) // 2, m + 50))
    c.alpha_composite(l2, (m + (cw - l2.width) // 2, m + 70 + l.height))
    SPR["norm"] = c
    sun = Image.new("RGBA", (1400, 1400), (0, 0, 0, 0))
    ImageDraw.Draw(sun).ellipse((350, 350, 1050, 1050), fill=(255, 226, 170, 170))
    SPR["sun"] = sun.filter(ImageFilter.GaussianBlur(150))
    # end card
    SPR["e0"] = text_sprite(["KONSULTACJE DLA RODZICÓW · SENS"], font(M, 38), LAVD)
    SPR["e1"] = text_sprite(["Spokojniej", "w domu"], font(XB, 128), INK, gap=1.05)
    SPR["e2"] = text_sprite(["dla rodziców nastolatków", "ul. Dyrekcyjna 37/47, Wrocław"], font(M, 48), INK)
    tx = text_sprite([[("Umów ", WHITE), ("bezpłatną", YEL), (" rozmowę (15 min)", WHITE)]], font(B, 48), WHITE)
    btn = Image.new("RGBA", (tx.width + 90, 140), (0, 0, 0, 0))
    ImageDraw.Draw(btn).rounded_rectangle((0, 0, btn.width - 1, 139), 70, fill=LAVD + (255,))
    btn.alpha_composite(tx, (45, (140 - tx.height) // 2))
    SPR["btn"] = btn
    SPR["e3"] = text_sprite(["„Każda emocja ma sens.”"], font(CV, 84), LAVD)
    SPR["e4"] = text_sprite(["senswroclaw.pl · @senswroclaw"], font(B, 44), INK)
    SPR["e5"] = text_sprite(["dr Maria Siwa — psycholożka i psychodietetyczka,",
                             "psychoterapeutka CBT w trakcie szkolenia"], font(M, 32), INK)


random.seed(5)
DROPS = [(random.uniform(-200, 200), random.uniform(0, 1), random.uniform(0.6, 1.0)) for _ in range(26)]


def rain(im, cx, cy, t, a):
    if a <= 0:
        return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for dx, ph, sp in DROPS:
        y = cy + 90 + ((t * 520 * sp + ph * 400) % 400)
        x = cx + dx + (y - cy) * 0.12
        d.line((x, y, x + 6, y + 34), fill=(200, 210, 230, int(150 * a)), width=4)
    im.alpha_composite(lay)


def frame(t):
    im = bg(t)
    storm = 1 - ramp(t, 11.8, 1.2)
    # sun behind house after the drop
    sp = ramp(t, 12.0, 4.0)
    if sp > 0 and t < 28.2:
        paste(im, SPR["sun"], W / 2, 1500 - 140 * sp, sp * (1 - ramp(t, 27.8, 0.4)))
    # house (whole story, until end card)
    ha = 1 - ramp(t, 27.8, 0.4)
    hy = 1330 + (1 - ramp(t, 3.3, 0.6)) * 120 if t > 3 else None
    if hy is not None:
        paste(im, SPR["house"], W / 2, hy, ramp(t, 3.3, 0.6) * ha)
    # TV label
    paste(im, SPR["tv"], W / 2, 300, (1 - ramp(t, 11.6, 0.4)))
    # hook 0-3.4 (visible from frame 0)
    hk = 1 - ramp(t, 3.2, 0.35)
    paste(im, SPR["h1"], W / 2, 700, hk)
    a2 = 1.0
    paste(im, SPR["h2"], W / 2, 830, a2 * hk)
    a3 = ramp(t, 1.4, 0.45)
    paste(im, SPR["h3"], W / 2, 1080 + 20 * (1 - a3), a3 * hk)
    # clouds
    mv = ease((t - 8.4) / 1.3) if t > 8.4 else 0.0
    shake = 6 * math.sin(t * 40) * (1 if 9.7 < t < 10.4 else 0)
    if t > 3.5:
        k = ramp(t, 3.6, 0.8)
        x = -300 + (300 + 300) * k + 130 * mv
        paste(im, SPR["cl"], x + shake, 560, storm)
        rain(im, x, 560, t, storm * k)
    if t > 5.9:
        k = ramp(t, 6.0, 0.8)
        x = W + 300 - (300 + 300) * k - 130 * mv
        paste(im, SPR["cr"], W - (W - x) - shake, 560, storm)
        rain(im, x, 560, t + 3, storm * k)
    # front labels + chips
    ca = 1 - ramp(t, 8.2, 0.3)
    paste(im, SPR["fl"], 300, 560, ramp(t, 4.2, 0.4) * ca)
    paste(im, SPR["fr"], 780, 560, ramp(t, 6.6, 0.4) * ca)
    for i, c in enumerate(SPR["chl"]):
        a = ramp(t, 4.6 + 0.4 * i, 0.3) * ca
        paste(im, c, 300, 790 + 82 * i, a)
    for i, c in enumerate(SPR["chr"]):
        a = ramp(t, 7.0 + 0.35 * i, 0.3) * ca
        paste(im, c, 780, 790 + 82 * i, a)
    # lightning
    if 9.7 < t < 10.5:
        f = 1 - (t - 9.7) / 0.8
        flash = Image.new("RGBA", (W, H), (255, 255, 255, int(180 * f * (1 if int(t * 20) % 2 == 0 else 0.4))))
        im.alpha_composite(flash)
        paste(im, SPR["bolt"], W / 2, 900, f)
    # forecast card
    fa = ramp(t, 10.0, 0.4) * (1 - ramp(t, 11.7, 0.3))
    paste(im, SPR["fc"], W / 2, 960 + 30 * (1 - ramp(t, 10.0, 0.4)), fa)
    # title
    ta = ramp(t, 12.2, 0.4) * (1 - ramp(t, 13.8, 0.3))
    paste(im, SPR["t1"], W / 2, 640 + 30 * (1 - ramp(t, 12.2, 0.4)), ta)
    paste(im, SPR["t2"], W / 2, 800, ramp(t, 12.5, 0.4) * (1 - ramp(t, 13.8, 0.3)))
    for key, t0, t1 in [("q1", 14.0, 17.5), ("q2", 17.5, 21.0), ("q3", 21.0, 24.5)]:
        a = ramp(t, t0, 0.4) * (1 - ramp(t, t1 - 0.3, 0.3))
        paste(im, SPR[key], W / 2, 720 + 40 * (1 - ramp(t, t0, 0.4)), a)
    na = ramp(t, 24.5, 0.45) * (1 - ramp(t, 27.7, 0.3))
    paste(im, SPR["norm"], W / 2, 780 + 30 * (1 - ramp(t, 24.5, 0.45)), na)
    if t >= 28.0:
        te = t - 28.0
        for k, y, t0 in [("e0", 420, 0.0), ("e1", 640, 0.1), ("e2", 900, 0.45), ("btn", 1110, 0.8),
                         ("e3", 1290, 1.2), ("e4", 1400, 1.4), ("e5", 1492, 1.5)]:
            a = ramp(te, t0, 0.5)
            paste(im, SPR[k], W / 2, y + 22 * (1 - a), a)
    return im


# ---------------- music ----------------
SR = 44100


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def music(path):
    n = int(TOTAL * SR)
    tt = np.arange(n) / SR
    mix = {k: np.zeros(n) for k in ["drums", "bass", "pad", "lead", "fx"]}
    rng = np.random.default_rng(11)

    def add(bus, t0, sig, gain=1.0):
        i0 = int(t0 * SR)
        if i0 >= n:
            return
        L = min(len(sig), n - i0)
        mix[bus][i0:i0 + L] += gain * sig[:L]

    def kick():
        L = int(0.45 * SR); t = np.arange(L) / SR
        f = 46 + 120 * np.exp(-t * 30)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * np.clip(t / 0.002, 0, 1)

    bp = butter(2, [900 / (SR / 2), 2800 / (SR / 2)], btype="band")
    hp = butter(2, 7000 / (SR / 2), btype="high")
    lp = butter(2, 160 / (SR / 2))

    def clap():
        L = int(0.3 * SR); t = np.arange(L) / SR
        env = np.zeros(L)
        for o in (0, 0.012, 0.024):
            m = t >= o
            env[m] += np.exp(-(t[m] - o) * (60 if o < 0.02 else 15))
        return lfilter(*bp, rng.standard_normal(L)) * env * 1.6

    def hat(open_=False):
        L = int((0.2 if open_ else 0.05) * SR); t = np.arange(L) / SR
        return lfilter(*hp, rng.standard_normal(L)) * np.exp(-t * (20 if open_ else 90))

    def saw(f, L, harm=8, detune=(0.0,)):
        t = np.arange(L) / SR
        s = np.zeros(L)
        for d in detune:
            ff = f * (1 + d)
            for k in range(1, harm + 1):
                if ff * k > 9000:
                    break
                s += np.sin(2 * np.pi * ff * k * t + k * d * 40) / k
        return s / len(detune)

    def pluck(m, dur=0.45, bright=7):
        L = int(dur * SR); t = np.arange(L) / SR
        f = mtof(m)
        s = np.zeros(L)
        for k in range(1, bright + 1):
            s += np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (6 + 5 * k))
        return s * np.clip(t / 0.003, 0, 1)

    def rumble(dur, gain):
        L = int(dur * SR); t = np.arange(L) / SR
        r = lfilter(*lp, rng.standard_normal(L)) * 6
        return r * np.clip(t / 0.05, 0, 1) * np.exp(-t * 1.6) * gain

    # ---- storm intro (0-12), A minor, steady pulse ----
    intro = [(0, [45, 57, 60, 64]), (2, [41, 57, 60, 65]), (4, [45, 57, 60, 64]), (6, [41, 57, 60, 65]),
             (8, [43, 55, 59, 62]), (10, [40, 56, 59, 64])]
    for i, (t0, ch) in enumerate(intro):
        L = int(2.0 * SR)
        env = np.clip(np.arange(L) / (0.08 * SR), 0, 1)
        for m in ch[1:]:
            add("pad", t0, saw(mtof(m), L, 5, (-0.005, 0.0, 0.006)) * env, 0.06)
        for e in range(4):
            tb = t0 + e * 0.5
            Lb = int(0.45 * SR)
            add("bass", tb, saw(mtof(ch[0] - 12), Lb, 4) * np.exp(-np.arange(Lb) / SR * 5), 0.4)
    for b in range(0, 24):
        add("drums", b * 0.5, hat(), 0.12)
        add("drums", b * 0.5 + 0.25, hat(), 0.18)
    for b in range(8, 22):  # kick from 4 s (clouds arrive)
        add("drums", b * 0.5, kick(), 0.7 if b % 2 == 0 else 0.45)
    for b in range(12, 22, 2):
        add("drums", b * 0.5 + 0.5, clap(), 0.25)
    # stingers for each front + chips
    for t0, base in [(3.6, 76), (6.0, 79)]:
        for j, m in enumerate([base, base + 3, base + 7]):
            add("lead", t0 + 0.5 + j * 0.4, pluck(m, 0.4, 5), 0.22)
    add("fx", 3.5, rumble(2.5, 0.5))
    add("fx", 5.9, rumble(2.5, 0.5))
    # riser 8.4-9.7
    L = int(1.3 * SR); t = np.arange(L) / SR
    nz = lfilter(*butter(2, 1500 / (SR / 2), btype="high"), rng.standard_normal(L))
    add("fx", 8.4, nz * (t / 1.3) ** 2, 0.5)
    # thunder at 9.7
    L = int(2.3 * SR); t = np.arange(L) / SR
    crack = rng.standard_normal(L) * np.exp(-t * 9)
    add("fx", 9.7, crack * 0.7 + rumble(2.3, 1.2)[:L] * 1.0, 0.9)
    # little pickup fill 11.0-12
    for j, m in enumerate([69, 72, 76, 79]):
        add("lead", 11.0 + j * 0.25, pluck(m, 0.3, 6), 0.2)

    # ---- sunny drop (12-33), C major: C G Am F ----
    prog = [(48, [64, 67, 72]), (43, [62, 67, 71]), (45, [64, 69, 72]), (41, [65, 69, 72])]
    kicks = []
    t0, bar = 12.0, 0
    while t0 < 31.9:
        root, ch = prog[bar % 4]
        calm = 24.5 <= t0 < 28.0
        L = int(2.0 * SR)
        for m in ch:
            add("pad", t0, saw(mtof(m), L, 7, (-0.006, 0.0, 0.007)), 0.08)
        for e in range(8):
            tb = t0 + e * 0.25
            Lb = int(0.22 * SR); tb_ = np.arange(Lb) / SR
            bs = saw(mtof(root - 12 + (12 if e in (3, 6) else 0)), Lb, 6) * np.exp(-tb_ * 9)
            add("bass", tb, bs, 0.0 if calm else (0.55 if e % 2 else 0.35))
        for b in range(4):
            tb = t0 + b * 0.5
            if not calm:
                add("drums", tb, kick(), 0.85); kicks.append(tb)
                if b % 2 == 1:
                    add("drums", tb, clap(), 0.45)
                add("drums", tb + 0.25, hat(True), 0.13)
            add("drums", tb + 0.125, hat(), 0.07)
            add("drums", tb + 0.375, hat(), 0.07)
        t0 += 2.0; bar += 1
    A = [76, None, 79, 76, 74, None, 72, None, 74, None, 76, 79, None, 81, 79, None]
    Bp = [84, None, 83, 79, None, 76, 79, None, 81, None, 79, 76, None, 74, 72, None]
    t0, ph = 12.0, 0
    while t0 < 31.5:
        seq = A if ph % 2 == 0 else Bp
        quiet = 24.5 <= t0 < 28.0
        for j, m in enumerate(seq):
            if m is not None and t0 + j * 0.25 < 31.6:
                add("lead", t0 + j * 0.25, pluck(m, 0.5, 8), 0.17 if quiet else 0.24)
                add("lead", t0 + j * 0.25, pluck(m + 12, 0.3, 3), 0.05)
        t0 += 4.0; ph += 1
    for m, d in [(72, 0), (76, 0.08), (79, 0.16), (84, 0.24)]:
        add("fx", 28.0 + d, pluck(m, 1.6, 4), 0.18)
    L = int(1.6 * SR)
    for m in [60, 64, 67, 72]:
        add("pad", 31.4, saw(mtof(m), L, 5, (-0.005, 0.005)) * np.exp(-np.arange(L) / SR * 2.2), 0.09)

    sc = np.ones(n)
    for k in kicks:
        i0 = int(k * SR); L = min(int(0.4 * SR), n - i0)
        sc[i0:i0 + L] = np.minimum(sc[i0:i0 + L], 1 - 0.6 * np.exp(-np.arange(L) / SR * 9))
    mix["pad"] *= sc
    mix["bass"][int(12 * SR):] *= sc[int(12 * SR):]
    mix["pad"][:int(12 * SR)] = lfilter(*butter(2, 2000 / (SR / 2)), mix["pad"][:int(12 * SR)])
    Lr = int(1.2 * SR)
    ir = rng.standard_normal(Lr) * np.exp(-np.arange(Lr) / SR * 4.0)
    ir /= np.sqrt(np.sum(ir ** 2))
    wet = fftconvolve(mix["lead"] + 0.5 * mix["fx"] + 0.4 * mix["pad"], ir)[:n] * 0.2
    out = sum(mix.values()) + wet
    out *= np.clip(tt / 0.05, 0, 1) * np.clip((TOTAL - tt) / 1.2, 0, 1)
    out = np.tanh(out / np.max(np.abs(out)) * 1.6) * 0.89
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


SEGS = [(0, 4), (4, 8), (8, 12), (12, 16), (16, 20), (20, 24), (24, 28), (28, 33)]


def render_seg(a, b, outdir):
    prep()
    tmp, final = f"{outdir}/seg_{a:02d}.tmp.mp4", f"{outdir}/seg_{a:02d}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for k in range(int(round((b - a) * FPS))):
        p.stdin.write(frame(a + k / FPS).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.rename(tmp, final)
    return os.path.basename(final)


if __name__ == "__main__":
    outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    if sys.argv[1] == "test":
        prep()
        ts = [float(x) for x in sys.argv[3].split(",")]
        ims = [frame(t).convert("RGB").resize((360, 640)) for t in ts]
        s = Image.new("RGB", (360 * len(ims), 640))
        for i, im in enumerate(ims):
            s.paste(im, (i * 360, 0))
        s.save(f"{outdir}/sheet.jpg", quality=85)
    elif sys.argv[1] == "music":
        music(f"{outdir}/music.wav")
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(2) as ex:
            files = list(ex.map(render_seg, [a for a, _ in SEGS], [b for _, b in SEGS], [outdir] * len(SEGS)))
        with open(f"{outdir}/list.txt", "w") as f:
            f.writelines(f"file '{x}'\n" for x in files)
