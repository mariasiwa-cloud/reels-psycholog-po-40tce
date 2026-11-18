import sys, math, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
import os as _os
F = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "fonts") + "/"
LAV, LAVD, INK, GREEN, BG = (150, 120, 156), (129, 89, 131), (30, 52, 59), (0, 84, 71), (247, 242, 248)
WHITE = (255, 255, 255)


def font(name, size):
    f = ImageFont.truetype(F + name, size)
    if name.startswith("Caveat"):
        f.set_variation_by_axes([700])
    return f


XB, B, M, CV = "Poppins-ExtraBold.ttf", "Poppins-Bold.ttf", "Poppins-Medium.ttf", "Caveat[wght].ttf"


def text_sprite(lines, fnt, color, gap=1.18, align="center", pad=24):
    """lines: list of lines; each line is str or list of (text, color)."""
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


def card_sprite(w, h, r=56, fill=WHITE):
    m = 80
    im = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((m, m + 18, m + w, m + h + 18), r, fill=(90, 60, 100, 70))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))
    ImageDraw.Draw(im).rounded_rectangle((m, m, m + w, m + h), r, fill=fill + (255,))
    return im, m


def paste(base, spr, cx, cy, a=1.0):
    """paste sprite centred at (cx, cy) with opacity a."""
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


# ---------- background (slow drifting lavender light) ----------
def make_bg():
    bw, bh = W + 240, H + 240
    im = Image.new("RGB", (bw, bh), BG)
    d = ImageDraw.Draw(im)
    for (x, y, r, c) in [(180, 320, 520, (232, 220, 236)), (1150, 900, 600, (238, 228, 242)),
                         (300, 1900, 640, (228, 214, 233)), (1100, 2050, 380, (243, 236, 226))]:
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(170))


BGIM = make_bg()


def bg(gt):
    ox = 120 + 100 * math.sin(gt * 0.11)
    oy = 120 + 100 * math.cos(gt * 0.09)
    return BGIM.crop((int(ox), int(oy), int(ox) + W, int(oy) + H)).convert("RGBA")


def dots(base, active, a=1.0):
    """progress: 5 small dots at the top, filled up to `active`."""
    lay = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(5):
        x = W / 2 + (i - 2) * 56
        if i < active:
            d.ellipse((x - 13, 17, x + 13, 43), fill=LAVD + (255,))
        else:
            d.ellipse((x - 13, 17, x + 13, 43), outline=LAV + (255,), width=4)
    paste(base, lay, W / 2, 330, a)


# ---------- scenes ----------
SYM = [
    ("„Skąd to się wzięło?”", ["Lęk,", "którego wcześniej", "nie było"], None),
    ("„Znowu 3:00…”", ["Pobudka w nocy", "i gonitwa myśli"], None),
    ("„Po co ja tu weszłam?”", ["Mgła mózgowa:", "pamięć i skupienie"], None),
    ("„Wszystko mnie drażni.”", ["Drażliwość", "bez wyraźnego", "powodu"], None),
    ("„Serce mi wali.”", ["Kołatanie serca"], "Zawsze sprawdź to u lekarza."),
]

SPR = {}


def prep():
    SPR["label"] = text_sprite(["P E R I M E N O P A U Z A"], font(M, 34), LAVD)
    SPR["h1"] = text_sprite(["5 objawów"], font(XB, 168), INK)
    SPR["h2"] = text_sprite(["perimenopauzy,"], font(XB, 104), LAVD)
    SPR["h3"] = text_sprite(["które nie wyglądają", "jak menopauza"], font(M, 68), INK)
    c, m = card_sprite(960, 470)
    SPR["card"], SPR["cardm"] = c, m
    for i, (th, lines, note) in enumerate(SYM):
        t = text_sprite([th], font(CV, 108), LAVD)
        SPR[f"th{i}"] = t.rotate(3, expand=True, resample=Image.BICUBIC)
        SPR[f"num{i}"] = text_sprite([str(i + 1)], font(XB, 250), LAV)
        fs = 72
        while max(font(B, fs).getlength(l) for l in lines) > 600:
            fs -= 2
        SPR[f"sy{i}"] = text_sprite(lines, font(B, fs), INK, align="left", gap=1.12)
        if note:
            tx = text_sprite([note], font(B, 46), WHITE)
            pill = Image.new("RGBA", (tx.width + 70, 120), (0, 0, 0, 0))
            ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill.width - 1, 119), 60, fill=GREEN + (255,))
            pill.alpha_composite(tx, (35, (120 - tx.height) // 2))
            SPR[f"note{i}"] = pill
    SPR["nw"] = text_sprite(["Nie wariujesz."], font(XB, 132), INK)
    SPR["nw2"] = text_sprite(["To może być", "perimenopauza."], font(M, 72), LAVD)
    SPR["nw3"] = text_sprite(["O objawach porozmawiaj z lekarzem."], font(M, 42), INK)
    # end card
    SPR["e0"] = text_sprite(["KURS W SENS · WROCŁAW"], font(M, 38), LAVD)
    SPR["e1"] = text_sprite(["Środek,", "nie koniec"], font(XB, 128), INK, gap=1.05)
    SPR["e2"] = text_sprite(["dla kobiet w peri- i menopauzie", "start: czwartek 3 grudnia"], font(M, 50), INK)
    tx = text_sprite([[("Napisz ", WHITE), ("ŚRODEK", (254, 217, 14)), (" w wiadomości", WHITE)]], font(B, 52), WHITE)
    btn = Image.new("RGBA", (tx.width + 90, 140), (0, 0, 0, 0))
    ImageDraw.Draw(btn).rounded_rectangle((0, 0, btn.width - 1, 139), 70, fill=LAVD + (255,))
    btn.alpha_composite(tx, (45, (140 - tx.height) // 2))
    SPR["btn"] = btn
    SPR["e3"] = text_sprite(["„Każda emocja ma sens.”"], font(CV, 84), LAVD)
    SPR["e4"] = text_sprite(["senswroclaw.pl · @senswroclaw"], font(B, 44), INK)
    SPR["e5"] = text_sprite(["dr Maria Siwa — psycholożka i psychodietetyczka,", "psychoterapeutka CBT w trakcie szkolenia"],
                            font(M, 32), INK)


def sc_hook(t, gt, dur):
    im = bg(gt)
    out = 1 - ramp(t, dur - 0.35, 0.35)
    k = ramp(t, 0, 0.6)  # visible from frame 0, settles gently
    paste(im, SPR["label"], W / 2, 430, out)
    paste(im, SPR["h1"], W / 2, 690 + 30 * (1 - k), out)
    paste(im, SPR["h2"], W / 2, 880 + 30 * (1 - k), out)
    a3 = ramp(t, 0.5, 0.5)
    paste(im, SPR["h3"], W / 2, 1090 + 24 * (1 - a3), a3 * out)
    # hand-drawn underline that draws itself
    p = ramp(t, 0.9, 0.7)
    if p > 0:
        d = ImageDraw.Draw(im)
        pts = [(250 + i * 6, 978 + 9 * math.sin(i / 11.0)) for i in range(int(97 * p) + 1)]
        if len(pts) > 1:
            d.line(pts, fill=LAV + (int(255 * out),), width=10, joint="curve")
    return im


def sc_sym(i):
    def f(t, gt, dur):
        im = bg(gt)
        out = 1 - ramp(t, dur - 0.3, 0.3)
        dots(im, i + 1, out if i == 4 else 1.0)
        a = ramp(t, 0.0, 0.4)
        paste(im, SPR[f"th{i}"], W / 2, 620 + 26 * (1 - a), a * out)
        c = ramp(t, 0.55, 0.5)
        cy = 1010 + 70 * (1 - c)
        paste(im, SPR["card"], W / 2, cy + 9, c * out)
        paste(im, SPR[f"num{i}"], 215, cy - 6, c * out)
        sy = SPR[f"sy{i}"]
        paste(im, sy, 330 + sy.width / 2, cy, c * out)
        if f"note{i}" in SPR:
            n = ramp(t, 1.2, 0.45)
            paste(im, SPR[f"note{i}"], W / 2, 1345 + 20 * (1 - n), n * out)
        return im
    return f


def sc_nw(t, gt, dur):
    im = bg(gt)
    out = 1 - ramp(t, dur - 0.35, 0.35)
    a = ramp(t, 0, 0.45)
    paste(im, SPR["nw"], W / 2, 760 + 30 * (1 - a), a * out)
    b = ramp(t, 0.9, 0.5)
    paste(im, SPR["nw2"], W / 2, 990 + 24 * (1 - b), b * out)
    c = ramp(t, 1.6, 0.5)
    paste(im, SPR["nw3"], W / 2, 1240, c * out)
    return im


def sc_end(t, gt, dur):
    im = bg(gt)
    items = [("e0", 420, 0.0), ("e1", 640, 0.1), ("e2", 900, 0.45), ("btn", 1110, 0.8),
             ("e3", 1290, 1.2), ("e4", 1400, 1.4), ("e5", 1492, 1.5)]
    for k, y, t0 in items:
        a = ramp(t, t0, 0.5)
        paste(im, SPR[k], W / 2, y + 22 * (1 - a), a)
    return im


SCENES = [("hook", sc_hook, 3.6)] + [(f"s{i+1}", sc_sym(i), 3.4) for i in range(5)] + \
         [("nw", sc_nw, 3.8), ("end", sc_end, 4.8)]


def starts():
    s, acc = [], 0.0
    for _, _, d in SCENES:
        s.append(acc)
        acc += d
    return s, acc


def render_scene(idx, outdir):
    name, fn, dur = SCENES[idx]
    st, _ = starts()
    tmp, final = f"{outdir}/{name}.tmp.mp4", f"{outdir}/{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for n in range(int(round(dur * FPS))):
        t = n / FPS
        p.stdin.write(fn(t, st[idx] + t, dur).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.rename(tmp, final)
    return final


def music(path):
    st, total = starts()
    sr = 44100
    n = int(total * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)
    chords = [[174.61, 220.0, 261.63, 329.63], [146.83, 220.0, 261.63, 349.23],
              [130.81, 196.0, 246.94, 329.63], [174.61, 220.0, 261.63, 392.0]]
    clen = total / 4
    for ci, ch in enumerate(chords):  # warm pad
        t0 = ci * clen
        env = np.clip((t - t0) / 2.0, 0, 1) * np.clip((t0 + clen + 1.5 - t) / 2.0, 0, 1)
        for f in ch:
            out += 0.045 * env * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t))
    notes = [523.25, 587.33, 659.25, 783.99, 659.25, 587.33, 523.25, 783.99]
    for s0, f in zip(st, notes):  # one soft piano-like note per scene
        for off, mul, amp in [(0.0, 1, 0.16), (0.55, 1.5, 0.09)]:
            tt = t - (s0 + off)
            m = tt >= 0
            e = np.zeros(n)
            e[m] = np.exp(-tt[m] * 2.2) * np.clip(tt[m] / 0.01, 0, 1)
            out += amp * e * (np.sin(2 * np.pi * f * mul * t) + 0.25 * np.sin(2 * np.pi * f * mul * 2 * t))
    out *= np.clip(t / 0.8, 0, 1) * np.clip((total - t) / 1.8, 0, 1)
    out = out / np.max(np.abs(out)) * 0.5
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    prep()
    outdir = sys.argv[2]
    if sys.argv[1] == "test":
        st, _ = starts()
        for idx, t in [(0, 0.0), (0, 2.5), (3, 2.0), (5, 2.5), (6, 3.0), (7, 4.0)]:
            SCENES[idx][1](t, st[idx] + t, SCENES[idx][2]).convert("RGB").save(f"{outdir}/t_{idx}_{t}.jpg", quality=88)
    else:
        files = [render_scene(i, outdir) for i in range(len(SCENES))]
        with open(f"{outdir}/list.txt", "w") as f:
            f.writelines(f"file '{x}'\n" for x in files)
        music(f"{outdir}/music.wav")
