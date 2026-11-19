"""TikTok SENS #02 — „Poznaj SENS” (przeróbka nagrania strony senswroclaw.pl od Rodrigo).

Hak (pytania: psycholog? terapeuta? diagnoza?) → nagranie strony w ramce telefonu, nad nim czyste nagłówki
→ karta końcowa SENS. Oryginalne nagranie ma wklejone napisy, więc trafia do mniejszej ramki telefonu,
a czytelny przekaz niosą nagłówki nad telefonem. Muzyka oryginalna.
Użycie: python3 tt_02_poznaj_sens.py SRC.mp4 test OUTDIR | python3 tt_02_poznaj_sens.py SRC.mp4 full OUT.mp4
"""
import sys, subprocess
from tt_base import *

SRC = sys.argv[1]
SRC_IN, SRC_OUT, SPEED = 1.0, 24.1, 0.9  # pomijamy zepsuty 1. sekundę, lekko zwalniamy przewijanie
HOOK = 3.4
PH_T = HOOK
PH_DUR = (SRC_OUT - SRC_IN) / SPEED
END_T = PH_T + PH_DUR
TOTAL = END_T + 3.6
SW, SH = 600, 1066  # ekran telefonu
PX, PY = CX, 580 + SH // 2  # środek ekranu

# nagłówki zsynchronizowane z nagraniem (czas w nagraniu źródłowym)
HEADS = [(1.0, 6.0, ["Poznaj SENS"], "diagnoza · terapia · rozwój"),
         (6.0, 8.6, ["Nie wiesz,", "od czego zacząć?"], None),
         (8.6, 14.0, ["Zacznij od", "bezpłatnej rozmowy"], "telefon lub wideo"),
         (14.0, 18.6, ["Dobierzemy", "formę wsparcia"], "dla dziecka, nastolatka lub dorosłego"),
         (18.6, 24.1, ["Poznaj nasz zespół"], "psycholodzy · psychoterapeuci · logopedzi")]


def out_t(src_t):
    return PH_T + (src_t - SRC_IN) / SPEED


S = {}


def prep():
    S["q"] = [text_sprite([w], font(XB, 128), c) for w, c in
              [("Psycholog?", INK), ("Terapeuta?", LAVD), ("Diagnoza?", INK)]]
    S["q_sub"] = text_sprite(["Nie musisz wiedzieć,", "od czego zacząć."], font(M, 58), INK)
    S["heads"] = []
    for a, b, h, sub in HEADS:
        hf = fit_font([l for _, _, hh, _ in HEADS for l in hh], XB, 82, 830)
        hs = text_sprite(h, hf, INK, pad=10, gap=1.04)
        ss = text_sprite([sub], fit_font([sub], M, 44, 840), LAVD, pad=10) if sub else None
        S["heads"].append((out_t(a), out_t(b), hs, ss))
    # telefon
    body = Image.new("RGBA", (SW + 40 + 160, SH + 40 + 160), (0, 0, 0, 0))
    sh = Image.new("RGBA", body.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((80, 100, 80 + SW + 40, 100 + SH + 40), 70, fill=(50, 30, 60, 90))
    body.alpha_composite(sh.filter(ImageFilter.GaussianBlur(34)))
    ImageDraw.Draw(body).rounded_rectangle((80, 80, 80 + SW + 40, 80 + SH + 40), 70, fill=INK + (255,))
    S["body"] = body
    mask = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, SW - 1, SH - 1), 52, fill=255)
    S["mask"] = mask
    # karta końcowa
    S["logo"] = asset("logo_pion.png", 560)
    S["motto"] = text_sprite(["Każda emocja ma sens."], font(CV, 92), LAVD)
    S["btn"] = pill("Umów bezpłatną rozmowę", font(B, 46), WHITE, LAVD, padx=56, h=124)
    S["btn2"] = text_sprite(["15–20 min · telefon lub wideo"], font(M, 40), INK)
    S["www"] = text_sprite(["senswroclaw.pl · Wrocław"], font(B, 48), INK)


def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        nxt = (cur + " " + w).strip()
        if fnt.getlength(nxt) <= maxw:
            cur = nxt
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    if len(lines) == 2 and len(lines[1].split()) == 1 and len(lines[0].split()) > 2:  # bez sierotek
        a = lines[0].split(); lines = [" ".join(a[:-1]), a[-1] + " " + lines[1]]
    return lines


class Footage:
    def __init__(self):
        self.p = subprocess.Popen(
            ["ffmpeg", "-loglevel", "error", "-ss", str(SRC_IN), "-to", str(SRC_OUT), "-i", SRC, "-vf",
             f"setpts=(PTS-STARTPTS)/{SPEED},fps={FPS},scale={SW}:{SH}:flags=lanczos,eq=saturation=1.06:contrast=1.03",
             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.n, self.last = -1, Image.new("RGB", (SW, SH), BG)

    def at(self, k):
        while self.n < k:
            buf = self.p.stdout.read(SW * SH * 3)
            if len(buf) < SW * SH * 3:
                break
            self.last = Image.frombytes("RGB", (SW, SH), buf)
            self.n += 1
        return self.last


FOOT = None


def frame(t):
    im = bg(LIGHT, t)
    # --- HAK ---
    if t < HOOK + 0.4:
        out = 1 - ramp(t, HOOK - 0.1, 0.4)
        for i, q in enumerate(S["q"]):
            a = ramp(t, i * 0.22, 0.3) if i else 1.0  # 1. słowo od pierwszej klatki
            paste(im, q, CX + 40 * (1 - a), 560 + i * 170, a * out)
        b = ramp(t, 0.9, 0.4)
        paste(im, S["q_sub"], CX, 1190 + 20 * (1 - b), b * out)
    # --- TELEFON ---
    if PH_T - 0.3 <= t < END_T + 0.4:
        k = ramp(t, PH_T - 0.3, 0.6)
        out = 1 - ramp(t, END_T, 0.4)
        dy = 260 * (1 - k)
        a = k * out
        fr = FOOT.at(max(0, int(round((t - PH_T) * FPS)))) if FOOT else Image.new("RGB", (SW, SH), BG)
        scr = fr.convert("RGBA")
        scr.putalpha(S["mask"])
        paste(im, S["body"], PX, PY + dy, a)
        paste(im, scr, PX, PY + dy, a)
        for (h0, h1, hs, ss) in S["heads"]:
            v = win(t, h0, h1 + 0.15, 0.35, 0.3) * out
            if v > 0:
                e = ramp(t, h0, 0.35)
                hy = 330 if hs.height > 150 else 360
                paste(im, hs, CX, hy + 18 * (1 - e), v)
                if ss:
                    paste(im, ss, CX, hy + hs.height / 2 + 22 + 18 * (1 - ramp(t, h0 + 0.15, 0.35)), v)
    # --- KARTA KOŃCOWA ---
    if t >= END_T:
        items = [("logo", 560, 0.0), ("motto", 940, 0.4), ("btn", 1085, 0.8), ("btn2", 1180, 1.0), ("www", 1290, 1.2)]
        for key, y, d in items:
            e = ramp(t, END_T + d, 0.5)
            paste(im, S[key], CX, y + 20 * (1 - e), e)
    return im


def music(path):
    mx = Mix(TOTAL, seed=2)
    bpm = 118; beat = 60 / bpm; bar = 4 * beat
    prog = [(45, [64, 69, 72]), (41, [65, 69, 72]), (48, [64, 67, 72]), (43, [62, 67, 71])]  # Am F C G
    hook = [76, 76, 79, 81, 79, 76, 74, 72]
    t0, b = 0.0, 0
    while t0 < TOTAL:
        root, ch = prog[b % 4]
        intro = t0 < HOOK - 0.01
        for e in range(8):
            ts = t0 + e * beat / 2
            if e in (0, 3, 6):
                for m in ch:
                    mx.add("keys", ts, mx.keys(m, 0.45), 0.07)
            mx.add("bass", ts, mx.bass(root - 12 + (12 if e in (3, 6) else 0), beat / 2 * 0.9), 0.0 if intro else 0.36)
        for q in range(4):
            tb = t0 + q * beat
            if not intro:
                mx.add("drums", tb, mx.kick(), 0.8)
                if q % 2 == 1:
                    mx.add("drums", tb, mx.clap(), 0.38)
                mx.add("drums", tb + beat / 2, mx.hat(True), 0.09)
            mx.add("drums", tb + beat / 4, mx.hat(), 0.05)
            mx.add("drums", tb + 3 * beat / 4, mx.hat(), 0.05)
        if not intro and b % 2 == 0:
            for j, m in enumerate(hook):
                mx.add("lead", t0 + j * beat / 2, mx.pluck(m, 0.4, 6, 6), 0.17)
        t0 += bar
        b += 1
    for i in range(3):  # „pop” przy pytaniach
        mx.add("fx", i * 0.22, mx.blip(84 + 3 * i), 0.25)
    mx.add("fx", HOOK - 1.2, mx.riser(1.2), 0.3)
    for (h0, _, _, _) in S["heads"][1:]:
        mx.add("fx", h0, mx.blip(88), 0.18)
    mx.add("fx", END_T, mx.blip(91), 0.25)
    mx.save(path)


if __name__ == "__main__":
    prep()
    if sys.argv[2] == "test":
        out = sys.argv[3]
        FOOT = Footage()
        times = [0.0, 1.5, 4.4, 10.5, 15.0, 21.0, 26.0, END_T + 2.0]
        sheet(frame, times[:4], f"{out}/s1.jpg")
        sheet(frame, times[4:], f"{out}/s2.jpg")
    else:
        FOOT = Footage()
        music("/tmp/tt02.wav")
        render(frame, TOTAL, sys.argv[3], "/tmp/tt02.wav")
