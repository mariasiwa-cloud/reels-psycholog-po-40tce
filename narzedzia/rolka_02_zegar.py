import os
import sys, os, math, random, subprocess, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from base import (W, H, FPS, LAV, LAVD, INK, GREEN, WHITE, BGIM, XB, B, M, CV,
                  font, text_sprite, card_sprite, paste, ease, ramp)
from scipy.signal import butter, lfilter, fftconvolve

TOTAL = 33.0
CREAM = (250, 246, 240)

# ---------------- backgrounds: night -> dawn ----------------
def make_night():
    bw, bh = W + 240, H + 240
    im = Image.new("RGB", (bw, bh), (20, 36, 44))
    d = ImageDraw.Draw(im)
    for (x, y, r, c) in [(200, 300, 560, (52, 50, 84)), (1150, 800, 620, (30, 62, 70)),
                         (350, 1800, 700, (62, 46, 80)), (1050, 2100, 420, (36, 54, 66))]:
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(180))

NIGHT = make_night()
random.seed(7)
STARS = [(random.uniform(40, W - 40), random.uniform(120, 1300), random.uniform(2, 4.5), random.uniform(0, 6.3))
         for _ in range(70)]

def bg(gt):
    ox = 120 + 100 * math.sin(gt * 0.11)
    oy = 120 + 100 * math.cos(gt * 0.09)
    box = (int(ox), int(oy), int(ox) + W, int(oy) + H)
    p = ramp(gt, 12.0, 10.0)
    n = NIGHT.crop(box)
    im = n if p <= 0 else Image.blend(n, BGIM.crop(box), p)
    im = im.convert("RGBA")
    if p < 1:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for x, y, r, ph in STARS:
            a = int(255 * (1 - p) * (0.45 + 0.4 * math.sin(gt * 1.3 + ph)))
            d.ellipse((x - r, y - r, x + r, y + r), fill=(235, 225, 245, max(a, 0)))
        im.alpha_composite(lay)
    # rising sun (soft) at dawn
    s = ramp(gt, 19.0, 9.0)
    if s > 0:
        glow = SPR["sun"]
        paste(im, glow, W / 2, 1950 - 330 * s, 0.6 * s)
    return im


# ---------------- sprites ----------------
THOUGHTS = [
    (["Czy zamknęłam drzwi?"], (330, 650), -4),
    (["Ten mail do szefowej…"], (770, 760), 3),
    (["A jeśli to coś", "poważnego?"], (300, 880), 2),
    (["Rata za mieszkanie"], (790, 940), -3),
    (["Czemu ona tak", "trzasnęła drzwiami?"], (380, 1085), -2),
    (["Zostały mi", "4 godziny snu"], (810, 1110), 4),
    (["Co ja powiedziałam", "na zebraniu?"], (320, 1270), 3),
    (["Prezent dla mamy"], (790, 1285), -4),
    (["Pobudka o 6:30…"], (560, 560), 2),
    (["Czemu znowu nie śpię?"], (560, 1420), -1),
]
NB = (540, 1270)  # notebook centre
SPR = {}


def bubble(lines, rot):
    tx = text_sprite(lines, font(CV, 64), (244, 236, 248), gap=1.05, pad=0)
    w, h = tx.width + 70, tx.height + 46
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((10, 10, 10 + w, 10 + h), 34, fill=(38, 58, 68, 235),
                                         outline=LAV + (255,), width=3)
    im.alpha_composite(tx, (10 + 35, 10 + 20))
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)


def tip_card(num, title, sub):
    cw = 960
    tf = font(B, 64)
    sf_size = 44
    sub_lines = sub
    while max(font(M, sf_size).getlength(l) for l in sub_lines) > cw - 230 and sf_size > 34:
        sf_size -= 2
    t = text_sprite([title], tf, INK, align="left", pad=0)
    s = text_sprite(sub_lines, font(M, sf_size), INK, align="left", gap=1.22, pad=0)
    ch = t.height + s.height + 120
    card, m = card_sprite(cw, ch)
    n = text_sprite([str(num)], font(XB, 190), LAV, pad=0)
    card.alpha_composite(n, (m + 55, m + (ch - n.height) // 2 - 18))
    card.alpha_composite(t, (m + 215, m + 50))
    s2 = s.copy()
    card.alpha_composite(s2, (m + 215, m + 50 + t.height + 22))
    # lavender keyword underline
    ImageDraw.Draw(card).line((m + 215, m + 50 + t.height + 8, m + 215 + min(t.width, 420), m + 50 + t.height + 8),
                              fill=LAV + (255,), width=6)
    return card


def prep():
    for i, (lines, _, rot) in enumerate(THOUGHTS):
        SPR[f"b{i}"] = bubble(lines, rot)
    SPR["pre"] = text_sprite(["Budzisz się o"], font(M, 64), (236, 228, 242))
    SPR["post"] = text_sprite(["i myśli pędzą?"], font(B, 84), (236, 228, 242))
    big = font(XB, 300)
    SPR["d03"] = text_sprite(["03"], big, (214, 190, 220))
    SPR["d00"] = text_sprite(["00"], big, (214, 190, 220))
    SPR["dcol"] = text_sprite([":"], big, (214, 190, 220))
    SPR["ddash"] = text_sprite(["– –"], font(XB, 200), (214, 190, 220))
    for k in ["d03", "d00", "dcol", "ddash"]:  # soft glow
        g = SPR[k].filter(ImageFilter.GaussianBlur(18))
        g2 = Image.new("RGBA", g.size, (0, 0, 0, 0))
        g2.alpha_composite(g); g2.alpha_composite(g); g2.alpha_composite(SPR[k])
        SPR[k] = g2
    # line card (scene 3)
    l1 = text_sprite([[("Mózg o 3:00", INK)], [("nie rozwiązuje problemów.", LAVD)], [("Tylko je powiększa.", INK)]],
                     font(XB, 62), INK, gap=1.12, pad=10)
    cw = max(860, l1.width + 90)
    c, m = card_sprite(cw, l1.height + 100)
    c.alpha_composite(l1, (m + (cw - l1.width) // 2, m + 50))
    SPR["linecard"] = c
    # notebook
    nb = Image.new("RGBA", (600, 360), (0, 0, 0, 0))
    sh = Image.new("RGBA", nb.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 60, 560, 340), 28, fill=(40, 30, 60, 90))
    nb.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(nb)
    d.rounded_rectangle((40, 40, 560, 320), 28, fill=CREAM + (255,))
    d.rounded_rectangle((40, 40, 92, 320), 28, fill=LAV + (255,))
    d.rectangle((70, 40, 92, 320), fill=LAV + (255,))
    for y in range(150, 310, 44):
        d.line((120, y, 530, y), fill=(222, 210, 226, 255), width=3)
    h1 = text_sprite(["Myśli na jutro"], font(CV, 70), LAVD, pad=0)
    h2 = text_sprite(["godz. 17:00"], font(B, 40), INK, pad=0)
    nb.alpha_composite(h1, (122, 62))
    nb.alpha_composite(h2, (125, 165))
    SPR["nb"] = nb
    SPR["t1"] = tip_card(1, "Zapisz te myśli.", ["Umów się z nimi na jutro,", "np. na 17:00. Teraz jest noc."])
    SPR["t2"] = tip_card(2, "Nie patrz na zegarek.", ["Liczenie, ile snu zostało,", "tylko podkręca napięcie."])
    SPR["t3"] = tip_card(3, "Nie walcz ze snem.", ["Nie zasypiasz ok. 20 minut?", "Wstań na chwilę, przygaś światło,", "zrób coś spokojnego. Wróć, gdy", "poczujesz senność."])
    # doctor note
    nl = text_sprite([[("Budzenie się w nocy", INK)], [("to częsty objaw", INK)], [("perimenopauzy.", LAVD)]],
                     font(XB, 76), INK, gap=1.1, pad=10)
    c, m = card_sprite(900, nl.height + 110)
    c.alpha_composite(nl, (m + (900 - nl.width) // 2, m + 55))
    SPR["note"] = c
    tx = text_sprite(["Trwa to tygodniami? Porozmawiaj z lekarzem."], font(B, 40), WHITE, pad=0)
    pill = Image.new("RGBA", (tx.width + 80, 116), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill.width - 1, 115), 58, fill=GREEN + (255,))
    pill.alpha_composite(tx, (40, (116 - tx.height) // 2 - 4))
    SPR["pill"] = pill
    # lamp glow + sun
    for k, r, col in [("lamp", 260, (255, 214, 140)), ("sun", 420, (255, 232, 196))]:
        g = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((r, r, 3 * r, 3 * r), fill=col + (150,))
        SPR[k] = g.filter(ImageFilter.GaussianBlur(r * 0.45))
    # end card
    SPR["e0"] = text_sprite(["KURS W SENS · WROCŁAW"], font(M, 38), LAVD)
    SPR["e1"] = text_sprite(["Środek,", "nie koniec"], font(XB, 128), INK, gap=1.05)
    SPR["e2"] = text_sprite(["sen, lęk, mgła mózgowa i więcej", "start: czwartek 3 grudnia"], font(M, 50), INK)
    tx = text_sprite([[("Napisz ", WHITE), ("ŚRODEK", (254, 217, 14)), (" w wiadomości", WHITE)]], font(B, 52), WHITE)
    btn = Image.new("RGBA", (tx.width + 90, 140), (0, 0, 0, 0))
    ImageDraw.Draw(btn).rounded_rectangle((0, 0, btn.width - 1, 139), 70, fill=LAVD + (255,))
    btn.alpha_composite(tx, (45, (140 - tx.height) // 2))
    SPR["btn"] = btn
    SPR["e3"] = text_sprite(["„Każda emocja ma sens.”"], font(CV, 84), LAVD)
    SPR["e4"] = text_sprite(["senswroclaw.pl · @senswroclaw"], font(B, 44), INK)
    SPR["e5"] = text_sprite(["dr Maria Siwa — psycholożka i psychodietetyczka,",
                             "psychoterapeutka CBT w trakcie szkolenia"], font(M, 32), INK)


def scaled(spr, s):
    if abs(s - 1) < 0.01:
        return spr
    return spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BICUBIC)


def clock(im, cx, cy, s, a, gt, dashed=0.0):
    if a <= 0:
        return
    w03 = SPR["d03"].width * s
    col_on = 0.35 + 0.65 * (1 if (gt % 1.0) < 0.5 else 0)  # blinks on the beat (120 bpm)
    left = SPR["d03"]
    right = SPR["d00"]
    gap = 120 * s
    paste(im, scaled(left, s), cx - gap - w03 / 2 + 30 * s, cy, a * (1 - dashed))
    paste(im, scaled(right, s), cx + gap + w03 / 2 - 30 * s, cy, a * (1 - dashed))
    if dashed > 0:
        paste(im, scaled(SPR["ddash"], s), cx - gap - w03 / 2 + 30 * s, cy, a * dashed)
        paste(im, scaled(SPR["ddash"], s), cx + gap + w03 / 2 - 30 * s, cy, a * dashed)
    paste(im, scaled(SPR["dcol"], s), cx, cy - 20 * s, a * col_on)


# ---------------- frame function (one timeline) ----------------
def frame(t):
    im = bg(t)
    # --- clock & hook (0-12) ---
    if t < 12.2:
        k = ramp(t, 3.6, 0.7)
        cy = 930 + (420 - 930) * k
        s = 1.0 - 0.45 * k
        fade = 1 - ramp(t, 11.6, 0.5)
        clock(im, W / 2, cy, s, fade, t)
        hk = 1 - ramp(t, 3.4, 0.4)
        paste(im, SPR["pre"], W / 2, 640, hk)
        paste(im, SPR["post"], W / 2, 1200, hk)
    # --- thoughts (4-13.6) ---
    for i, (lines, (x, y), rot) in enumerate(THOUGHTS):
        t0 = 4.0 + 0.5 * i
        if t < t0:
            continue
        a = ramp(t, t0, 0.25)
        pop = 0.85 + 0.15 * ease((t - t0) / 0.3)
        dx = 10 * math.sin(t * 0.7 + i)
        dy = 8 * math.cos(t * 0.6 + i * 1.7)
        dim = 1 - 0.7 * ramp(t, 9.0, 0.4)
        f0 = 12.0 + 0.11 * i
        f = ramp(t, f0, 0.55)
        if f > 0:
            dim = 0.3 + 0.7 * f if f < 0.5 else 1 - (f - 0.5) * 2
            pop = 1 - 0.8 * f
            x2, y2 = x + (NB[0] - x) * f, y + (NB[1] - y) * f
        else:
            x2, y2 = x, y
        if dim > 0.01:
            paste(im, scaled(SPR[f"b{i}"], pop), x2 + dx * (1 - f), y2 + dy * (1 - f), a * dim)
    # line card 9-12
    lc = ramp(t, 9.1, 0.4) * (1 - ramp(t, 11.7, 0.3))
    paste(im, SPR["linecard"], W / 2, 980 + 30 * (1 - ramp(t, 9.1, 0.4)), lc)
    # notebook 11.8-16
    na = ramp(t, 11.7, 0.4) * (1 - ramp(t, 15.6, 0.4))
    if na > 0:
        bump = 1 + 0.03 * math.sin(max(0, t - 12) * 12) * (1 - ramp(t, 12.0, 1.6))
        paste(im, scaled(SPR["nb"], bump), NB[0], NB[1] + 40 * (1 - ramp(t, 11.7, 0.4)), na)
    # tip cards
    for key, t0, t1 in [("t1", 13.0, 16.0), ("t2", 16.0, 20.0), ("t3", 20.0, 24.0)]:
        a = ramp(t, t0, 0.4) * (1 - ramp(t, t1 - 0.3, 0.3))
        paste(im, SPR[key], W / 2, 640 + 40 * (1 - ramp(t, t0, 0.4)), a)
    # tip 2: clock hides its digits
    a2 = ramp(t, 16.3, 0.4) * (1 - ramp(t, 19.7, 0.3))
    if a2 > 0:
        clock(im, W / 2, 1190, 0.7, a2, t, dashed=ramp(t, 17.4, 0.6))
    # tip 3: warm lamp glow
    a3 = ramp(t, 20.3, 0.6) * (1 - ramp(t, 23.7, 0.3))
    paste(im, SPR["lamp"], W / 2, 1220, a3)
    # doctor note 24-28
    an = ramp(t, 24.0, 0.45) * (1 - ramp(t, 27.7, 0.3))
    paste(im, SPR["note"], W / 2, 860 + 30 * (1 - ramp(t, 24.0, 0.45)), an)
    ap = ramp(t, 24.8, 0.4) * (1 - ramp(t, 27.7, 0.3))
    paste(im, SPR["pill"], W / 2, 1180, ap)
    # end card 28-33
    if t >= 28.0:
        te = t - 28.0
        for k, y, t0 in [("e0", 420, 0.0), ("e1", 640, 0.1), ("e2", 900, 0.45), ("btn", 1110, 0.8),
                         ("e3", 1290, 1.2), ("e4", 1400, 1.4), ("e5", 1492, 1.5)]:
            a = ramp(te, t0, 0.5)
            paste(im, SPR[k], W / 2, y + 22 * (1 - a), a)
    return im


# ---------------- music: 120 bpm, tension at night, drop at 12 s ----------------
SR = 44100


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def music(path):
    n = int(TOTAL * SR)
    tt = np.arange(n) / SR
    mix = {k: np.zeros(n) for k in ["drums", "bass", "pad", "lead", "fx"]}
    rng = np.random.default_rng(3)

    def add(bus, t0, sig, gain=1.0):
        i0 = int(t0 * SR)
        if i0 >= n:
            return
        L = min(len(sig), n - i0)
        mix[bus][i0:i0 + L] += gain * sig[:L]

    def kick(gain=1.0):
        L = int(0.45 * SR); t = np.arange(L) / SR
        f = 48 + 110 * np.exp(-t * 32)
        ph = 2 * np.pi * np.cumsum(f) / SR
        return gain * np.sin(ph) * np.exp(-t * 7.5) * np.clip(t / 0.002, 0, 1)

    bp = butter(2, [900 / (SR / 2), 2600 / (SR / 2)], btype="band")
    hp = butter(2, 7000 / (SR / 2), btype="high")

    def clap():
        L = int(0.3 * SR); t = np.arange(L) / SR
        env = np.zeros(L)
        for o in (0, 0.011, 0.022):
            m = t >= o
            env[m] += np.exp(-(t[m] - o) * (60 if o < 0.02 else 16))
        return lfilter(*bp, rng.standard_normal(L)) * env * 1.6

    def hat(open_=False):
        L = int((0.18 if open_ else 0.05) * SR); t = np.arange(L) / SR
        return lfilter(*hp, rng.standard_normal(L)) * np.exp(-t * (22 if open_ else 90))

    def tick():
        L = int(0.06 * SR); t = np.arange(L) / SR
        return (np.sin(2 * np.pi * 1850 * t) + 0.5 * np.sin(2 * np.pi * 2770 * t)) * np.exp(-t * 90)

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

    # ---- intro / night (0-12) in D minor ----
    for b in range(24):  # beats 0..11.5
        add("fx", b * 0.5, tick(), 0.22 if b % 2 else 0.3)
    intro_ch = [(0, [50, 57, 62, 65]), (4, [50, 57, 62, 65]), (6, [46, 58, 62, 65]), (8, [43, 58, 62, 67]),
                (10, [45, 57, 61, 64])]
    for i, (t0, ch) in enumerate(intro_ch):
        t1 = intro_ch[i + 1][0] if i + 1 < len(intro_ch) else 11.85
        L = int((t1 - t0) * SR)
        env = np.clip(np.arange(L) / (0.3 * SR), 0, 1) * np.clip((L - np.arange(L)) / (0.05 * SR), 0, 1)
        harm = 3 if t0 < 8 else 5
        for m in ch[1:]:
            add("pad", t0, saw(mtof(m), L, harm, (-0.004, 0.0, 0.005)) * env, 0.06)
        add("bass", t0, np.sin(2 * np.pi * mtof(ch[0] - 12) * np.arange(L) / SR) * env, 0.2)
    for b in range(12, 24):  # 8th hats from 6 s
        for h in (0, 0.25):
            add("drums", b * 0.5 + h, hat(), 0.16 if h else 0.22)
    for b in range(16, 23):  # kick from 8 s
        add("drums", b * 0.5, kick(), 0.75 if b % 2 == 0 else 0.55)
    # thought pops: rising D-minor pentatonic blips, synced to the bubbles
    pent = [74, 77, 79, 81, 84, 86, 89, 91, 93, 96]
    for i, m in enumerate(pent):
        add("lead", 4.0 + 0.5 * i, pluck(m, 0.35, 5), 0.28)
    # riser 9.5-11.9
    L = int(2.4 * SR); t = np.arange(L) / SR
    nz = lfilter(*butter(2, 1500 / (SR / 2), btype="high"), rng.standard_normal(L))
    sweep = np.sin(2 * np.pi * np.cumsum(220 + 600 * (t / 2.4) ** 2) / SR)
    add("fx", 9.5, (0.5 * nz + 0.4 * sweep) * (t / 2.4) ** 2, 0.5)
    # whoosh as the thoughts fly into the notebook
    L = int(0.9 * SR); t = np.arange(L) / SR
    add("fx", 12.0, lfilter(*bp, rng.standard_normal(L)) * np.sin(np.pi * t / 0.9) ** 2, 0.35)

    # ---- drop / dawn (12-33) in F major: F C Dm Bb ----
    prog = [(53, [65, 69, 72]), (48, [64, 67, 72]), (50, [62, 65, 69]), (46, [62, 65, 70])]
    kicks = []
    t0 = 12.0
    bar = 0
    while t0 < 31.9:
        root, ch = prog[bar % 4]
        breakdown = 24.0 <= t0 < 28.0
        L = int(2.0 * SR)
        for m in ch:
            add("pad", t0, saw(mtof(m), L, 7, (-0.006, 0.0, 0.007)), 0.085)
        for e in range(8):  # offbeat-pumping bass in 8ths
            tb = t0 + e * 0.25
            Lb = int(0.22 * SR); tb_ = np.arange(Lb) / SR
            bs = saw(mtof(root - 12 + (12 if e % 4 == 3 else 0)), Lb, 6) * np.exp(-tb_ * 9)
            add("bass", tb, bs, 0.0 if breakdown else (0.55 if e % 2 else 0.35))
        for b in range(4):
            tb = t0 + b * 0.5
            if not breakdown:
                add("drums", tb, kick(), 0.85)
                kicks.append(tb)
                if b % 2 == 1:
                    add("drums", tb, clap(), 0.45)
                add("drums", tb + 0.25, hat(True), 0.14)
            add("drums", tb + 0.125, hat(), 0.07)
            add("drums", tb + 0.375, hat(), 0.07)
        t0 += 2.0
        bar += 1
    # catchy lead hook (two 2-bar phrases), 8th-note grid
    A = [81, None, 84, 81, None, 79, 77, None, 79, None, 76, 79, None, 81, 84, None]
    Bp = [86, None, 84, 81, None, 84, 81, None, 79, None, 77, 79, None, 81, 77, None]
    t0 = 12.0
    ph = 0
    while t0 < 31.5:
        seq = A if ph % 2 == 0 else Bp
        quiet = 24.0 <= t0 < 28.0
        for j, m in enumerate(seq):
            if m is not None:
                tn = t0 + j * 0.25
                if tn < 31.6:
                    add("lead", tn, pluck(m, 0.5, 8), 0.2 if quiet else 0.24)
                    add("lead", tn, pluck(m + 12, 0.3, 3), 0.05)
        t0 += 4.0
        ph += 1
    # end chime on the end card
    for m, d in [(77, 0), (81, 0.08), (84, 0.16), (89, 0.24)]:
        add("fx", 28.0 + d, pluck(m, 1.6, 4), 0.18)
    # final F chord ring-out
    L = int(1.6 * SR)
    for m in [65, 69, 72, 77]:
        add("pad", 31.4, saw(mtof(m), L, 5, (-0.005, 0.005)) * np.exp(-np.arange(L) / SR * 2.2), 0.09)

    # sidechain pump on pad + bass from the drop kicks
    sc = np.ones(n)
    for k in kicks:
        i0 = int(k * SR); L = int(0.4 * SR)
        L = min(L, n - i0)
        env = 1 - 0.65 * np.exp(-np.arange(L) / SR * 9)
        sc[i0:i0 + L] = np.minimum(sc[i0:i0 + L], env)
    mix["pad"] *= sc
    mix["bass"][int(12 * SR):] *= sc[int(12 * SR):]
    # low-pass the night pad, brighter after the drop
    lp = butter(2, 1800 / (SR / 2))
    night = int(12 * SR)
    mix["pad"][:night] = lfilter(*lp, mix["pad"][:night])
    # small room reverb on lead + fx + pad
    Lr = int(1.2 * SR)
    ir = rng.standard_normal(Lr) * np.exp(-np.arange(Lr) / SR * 4.0)
    ir /= np.sqrt(np.sum(ir ** 2))
    wet = fftconvolve(mix["lead"] + 0.5 * mix["fx"] + 0.4 * mix["pad"], ir)[:n] * 0.22
    out = mix["drums"] + mix["bass"] + mix["pad"] + mix["lead"] + mix["fx"] + wet
    out *= np.clip(tt / 0.05, 0, 1) * np.clip((TOTAL - tt) / 1.2, 0, 1)
    out = np.tanh(out / np.max(np.abs(out)) * 1.6) * 0.89
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


SEGS = [(0, 4), (4, 8), (8, 12), (12, 16), (16, 20), (20, 24), (24, 28), (28, 33)]


def render_seg(a, b, outdir):
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
    prep()
    outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    if sys.argv[1] == "test":
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
