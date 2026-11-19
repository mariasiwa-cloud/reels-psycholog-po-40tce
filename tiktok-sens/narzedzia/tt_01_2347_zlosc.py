"""TikTok SENS #01 — seria „23:47”: „czy to normalne, że moje dziecko ciągle wybucha złością?”

Noc, telefon, wyszukiwarka → podpowiedzi innych rodziców („Nie tylko Ty o to pytasz.”) → świt:
złość to normalna emocja → 3 sygnały, kiedy warto skonsultować → zdanie na dziś wieczór → karta SENS.
Użycie: python3 tt_01_2347_zlosc.py test OUTDIR  |  python3 tt_01_2347_zlosc.py full OUT.mp4
"""
import sys, math
from tt_base import *

TOTAL = 30.0
QL = ["czy to normalne, że moje", "dziecko ciągle wybucha", "złością?"]
Q = " ".join(QL)
SUGG = ["dziecko krzyczy i rzuca rzeczami", "napady złości u 5-latka", "jak uspokoić dziecko w złości",
        "czy to już ADHD?"]
SIG = [["wybuchy są bardzo częste", "i bardzo silne"], ["dziecko robi krzywdę", "sobie lub innym"],
       ["złość utrudnia życie w domu,", "przedszkolu lub szkole"]]
CARD_T = [12.5, 15.0, 17.5]
S = {}


def prep():
    S["clock"] = text_sprite(["23:47"], font(XB, 170), WHITE)
    moon = Image.new("RGBA", (130, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(moon)
    d.ellipse((10, 10, 120, 120), fill=YEL + (255,))
    d.ellipse((42, 0, 140, 98), fill=(0, 0, 0, 0))
    S["moon"] = moon
    c, m = card_sprite(860, 290, r=60, shadow=(0, 0, 0, 90))
    d = ImageDraw.Draw(c)
    x0, y0 = m + 46, m + 56
    d.ellipse((x0, y0, x0 + 40, y0 + 40), outline=LAV + (255,), width=6)
    d.line((x0 + 35, y0 + 35, x0 + 52, y0 + 52), fill=LAV + (255,), width=7)
    S["search"], S["sm"] = c, m
    S["sugg"] = []
    for s in SUGG:
        tx = text_sprite([s], font(M, 40), (235, 236, 240), pad=0)
        im = Image.new("RGBA", (860, 92), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        dd.rounded_rectangle((0, 0, 859, 91), 46, fill=(255, 255, 255, 30))
        dd.ellipse((36, 30, 66, 60), outline=(200, 200, 210, 255), width=4)
        dd.line((62, 57, 74, 69), fill=(200, 200, 210, 255), width=5)
        im.alpha_composite(tx, (104, (92 - tx.height) // 2 - 3))
        S["sugg"].append(im)
    S["notalone"] = text_sprite(["Nie tylko Ty", "o to pytasz."], font(CV, 116), LAVL, gap=1.0)
    # świt
    S["calm_lbl"] = text_sprite(["S P O K O J N I E"], font(M, 36), LAVD)
    S["calm1"] = text_sprite(["Złość to", "normalna emocja."], fit_font(["normalna emocja."], XB, 98, 820), INK, gap=1.08)
    S["calm2"] = text_sprite(["U małych dzieci wybuchy", [("złości zdarzają się ", INK), ("często.", LAVD)]],
                             font(M, 56), INK)
    # sygnały
    S["sig_h"] = text_sprite(["Warto skonsultować się,", [("gdy:", LAVD)]], fit_font(["Warto skonsultować się,"], XB, 74, 820), INK, gap=1.1)
    cw, ch = 860, 200
    card, cm = card_sprite(cw, ch, r=44)
    S["cards"] = []
    for i, lines in enumerate(SIG):
        im = card.copy()
        d = ImageDraw.Draw(im)
        d.ellipse((cm + 34, cm + ch / 2 - 52, cm + 138, cm + ch / 2 + 52), fill=LAV + (255,))
        num = text_sprite([str(i + 1)], font(XB, 70), WHITE, pad=0)
        im.alpha_composite(num, (int(cm + 86 - num.width / 2), int(cm + ch / 2 - num.height / 2 - 6)))
        tx = text_sprite(lines, fit_font([l for ls in SIG for l in ls], B, 48, 640), INK, align="left", gap=1.1, pad=0)
        im.alpha_composite(tx, (cm + 172, int(cm + ch / 2 - tx.height / 2 - 4)))
        S["cards"].append(im)
    # dziś wieczorem
    S["eve_h"] = text_sprite(["Dziś wieczorem spróbuj:"], font(B, 62), LAVD)
    qc, qm = card_sprite(820, 420, r=50)
    q = text_sprite(["„Widzę, że czujesz", "dużą złość.", "Jestem obok.”"], font(CV, 104), INK, gap=1.02, pad=0)
    qc.alpha_composite(q, (int(qm + 410 - q.width / 2), int(qm + 210 - q.height / 2 - 8)))
    S["quote"] = qc.rotate(-2, expand=True, resample=Image.BICUBIC)
    S["eve_s"] = text_sprite(["Najpierw spokój.", [("Rozmowa — ", INK), ("później.", LAVD)]], font(M, 56), INK)
    # karta końcowa
    S["logo"] = asset("logo_pion.png", 560)
    S["motto"] = text_sprite(["Każda emocja ma sens."], font(CV, 92), LAVD)
    S["btn"] = pill("Bezpłatna rozmowa wstępna", font(B, 46), WHITE, LAVD, padx=56, h=124)
    S["btn2"] = text_sprite(["15–20 min · telefon lub wideo"], font(M, 40), INK)
    S["www"] = text_sprite(["senswroclaw.pl · Wrocław"], font(B, 48), INK)


def frame(t):
    night = 1 - ramp(t, 7.0, 0.8)
    im = bg(LIGHT, t)
    if night > 0.003:
        dk = bg(DARK, t)
        if night < 0.997:
            im = Image.blend(im, dk, night)
        else:
            im = dk
    # --- NOC (0–8) ---
    if t < 7.5:
        out = 1 - ramp(t, 6.9, 0.5)
        up = 230 * ramp(t, 4.1, 0.6)  # wszystko podjeżdża w górę, robi miejsce na „Nie tylko Ty”
        ca = out * (1 - ramp(t, 4.1, 0.4))
        paste(im, S["moon"], CX - 245, 330 - up, ca)
        paste(im, S["clock"], CX + 60, 330 - up, ca)
        # wyszukiwarka (pisanie: 45% widać od pierwszej klatki)
        k = min(1.0, 0.45 + 0.55 * max(0.0, t - 0.15) / 1.25)
        n = int(len(Q) * k)
        sp = S["search"].copy()
        d = ImageDraw.Draw(sp)
        f = font(M, 52)
        m = S["sm"]
        left, i = n, 0
        lines = []
        for L in QL:
            lines.append(L[:max(0, left)])
            left -= len(L) + 1
        blink = (t <= 1.4) or (int(t * 2.2) % 2 == 0)
        last = max(i for i, L in enumerate(lines) if L or i == 0)
        for i, L in enumerate(lines):
            txt = L + ("|" if (i == last and blink) else "")
            d.text((m + 118, m + 40 + i * 74), txt, font=f, fill=INK)
        paste(im, sp, CX, 650 - up, out)
        # podpowiedzi innych rodziców
        for i, s_ in enumerate(S["sugg"]):
            a = ramp(t, 2.1 + i * 0.28, 0.35)
            dim = 1 - 0.6 * ramp(t, 4.2, 0.5)
            paste(im, s_, CX, 880 + i * 104 + 20 * (1 - a) - up, a * dim * out)
        a = ramp(t, 4.4, 0.5) * out
        paste(im, S["notalone"], CX, 1215 + 26 * (1 - ramp(t, 4.4, 0.5)), a)
        return im
    # --- ŚWIT: złość jest normalna (8–12) ---
    if t < 12.0:
        out = 1 - ramp(t, 11.65, 0.35)
        paste(im, S["calm_lbl"], CX, 520, ramp(t, 7.5, 0.4) * out)
        a = ramp(t, 7.95, 0.5)
        paste(im, S["calm1"], CX, 720 + 30 * (1 - a), a * out)
        b = ramp(t, 9.0, 0.5)
        paste(im, S["calm2"], CX, 1010 + 24 * (1 - b), b * out)
        p = ramp(t, 8.4, 0.7)  # podkreślenie rysuje się samo
        if p > 0:
            d = ImageDraw.Draw(im)
            wl = fit_font(["normalna emocja."], XB, 98, 820).getlength("normalna emocja") 
            pts = [(CX - wl / 2 + i * 7, 838 + 8 * math.sin(i / 10.0)) for i in range(int(wl / 7 * p) + 1)]
            if len(pts) > 1:
                d.line(pts, fill=LAV + (int(255 * out),), width=10, joint="curve")
        return im
    # --- SYGNAŁY (12–21) ---
    if t < 21.0:
        out = 1 - ramp(t, 20.65, 0.35)
        a = ramp(t, 12.0, 0.45)
        paste(im, S["sig_h"], CX, 440 + 24 * (1 - a), a * out)
        for i, c in enumerate(S["cards"]):
            k = ramp(t, CARD_T[i], 0.45)
            paste(im, c, CX + 60 * (1 - k), 700 + i * 236, k * out)
        return im
    # --- DZIŚ WIECZOREM (21–25) ---
    if t < 25.0:
        out = 1 - ramp(t, 24.65, 0.35)
        paste(im, S["eve_h"], CX, 470, ramp(t, 21.0, 0.4) * out)
        k = ramp(t, 21.25, 0.5)
        paste(im, S["quote"], CX, 790 + 40 * (1 - k), k * out)
        b = ramp(t, 22.3, 0.5)
        paste(im, S["eve_s"], CX, 1150 + 20 * (1 - b), b * out)
        return im
    # --- KARTA SENS (25–30) ---
    items = [("logo", 560, 25.0), ("motto", 940, 25.5), ("btn", 1085, 26.0), ("btn2", 1180, 26.2), ("www", 1290, 26.5)]
    for k, y, t0 in items:
        a = ramp(t, t0, 0.5)
        paste(im, S[k], CX, y + 20 * (1 - a), a)
    return im


def music(path):
    mx = Mix(TOTAL, seed=47)
    beat = 0.5  # 120 BPM
    # noc: Am F C G — ciepłe arpeggio, lekki puls
    night = [(57, [69, 72, 76]), (53, [69, 72, 77]), (48, [67, 72, 76]), (55, [67, 71, 74])]
    for bar in range(4):
        t0 = bar * 2.0
        root, ch = night[bar]
        mx.add("bass", t0, mx.bass(root - 12, 1.95), 0.32)
        for e in range(8):
            mx.add("arp", t0 + e * 0.25, mx.pluck(ch[e % 3] + (12 if e in (3, 7) else 0), 0.35, 5, 7), 0.16)
        for b in range(4):
            mx.add("drums", t0 + b * beat + 0.25, mx.hat(), 0.10)
            if bar >= 2:
                mx.add("drums", t0 + b * beat, mx.kick(), 0.45 if b % 2 == 0 else 0.0)
    for i in range(len("ciągle wybucha złością?")):  # pisanie
        mx.add("fx", 0.25 + i * 1.35 / 23, mx.tick(), 0.18)
    for i in range(4):  # podpowiedzi
        mx.add("fx", 2.1 + i * 0.28, mx.blip(81 + [0, 3, 5, 7][i]), 0.22)
    mx.add("fx", 6.6, mx.riser(1.4), 0.35)  # przejście noc → świt
    # świt i refren: C G Am F, wesoły groove
    prog = [(48, [64, 67, 72]), (43, [62, 67, 71]), (45, [64, 69, 72]), (41, [65, 69, 72])]
    hook = [76, 79, 81, 79, 76, 74, 72, 74]  # chwytliwy motyw (8 ósemek / 2 takty)
    t0, bar = 8.0, 0
    while t0 < TOTAL - 0.01:
        root, ch = prog[bar % 4]
        calm = 21.0 <= t0 < 25.0
        for e in range(8):  # akordy staccato zamiast padów
            if e in (0, 3, 6):
                for m in ch:
                    mx.add("keys", t0 + e * 0.25, mx.keys(m, 0.5), 0.07)
            bm = root - 12 + (12 if e in (3, 6) else 0)
            mx.add("bass", t0 + e * 0.25, mx.bass(bm, 0.22), 0.0 if calm else 0.38)
        for b in range(4):
            tb = t0 + b * beat
            if not calm:
                mx.add("drums", tb, mx.kick(), 0.8)
                if b % 2 == 1:
                    mx.add("drums", tb, mx.clap(), 0.4)
                mx.add("drums", tb + 0.25, mx.hat(True), 0.10)
            else:
                if b == 0:
                    mx.add("drums", tb, mx.kick(), 0.45)
            mx.add("drums", tb + 0.125, mx.hat(), 0.05)
            mx.add("drums", tb + 0.375, mx.hat(), 0.05)
        if not calm and (12.0 <= t0 < 21.0 or t0 >= 25.0 or bar % 2 == 1):
            for j in range(4):
                mx.add("lead", t0 + j * 0.5, mx.pluck(hook[(bar % 2) * 4 + j], 0.45, 6, 5), 0.20)
        t0 += 2.0
        bar += 1
    for tc in CARD_T:  # akcent przy kartach
        mx.add("fx", tc, mx.blip(88), 0.25)
    mx.add("fx", 7.95, mx.clap(), 0.3)
    mx.save(path, {"drums": 1.0, "bass": 1.0, "keys": 1.0, "arp": 1.0, "lead": 1.0, "fx": 1.0})


if __name__ == "__main__":
    prep()
    if sys.argv[1] == "test":
        out = sys.argv[2]
        sheet(frame, [0.0, 1.0, 3.6, 6.0, 7.4], f"{out}/sheet1.jpg")
        sheet(frame, [7.6, 10.5, 13.5, 19.5], f"{out}/sheet2.jpg")
        sheet(frame, [22.0, 23.5, 26.0, 29.0], f"{out}/sheet3.jpg")
    else:
        music("/tmp/tt01.wav")
        render(frame, TOTAL, sys.argv[2], "/tmp/tt01.wav")
