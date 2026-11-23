"""Rolka 04 — „Czy tylko ja tak mam?” (format: czat / wiadomości + prawdziwe zdjęcie sali SENS).

Pomysł: nocna wiadomość do przyjaciółek → „Ja też.” → lawina „Ja też.” zalewa ekran → „Nie tylko Ty.”
→ czat zamienia się w prawdziwą salę SENS z pustymi krzesłami („Jedno z tych krzeseł może być Twoje.”)
→ tematy kursu jako dymki czatu → CTA jako wysyłana wiadomość „ŚRODEK”.
Kolory: noc w ciemnym petrolu → krem i lawenda. Muzyka: neo-soul/pop 100 BPM na prawdziwych instrumentach
(piano elektryczne, gitara akustyczna, bas palcowy, zestaw perkusyjny), „drop” przy „Nie tylko Ty.”.
Filar 1 + zaproszenie na kurs „Środek, nie koniec” (start pt 4.12.2026).

Użycie (z katalogu repo):
  python3 narzedzia/rolka_04_ja_tez.py test OUTDIR
  python3 narzedzia/rolka_04_ja_tez.py full OUT.mp4
Wymaga: sh narzedzia/pobierz_fonty.sh, sh tiktok-sens/narzedzia/pobierz_dzwieki.sh
"""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tiktok-sens", "narzedzia"))
from tt_base import *
from tt_muzyka import Song, kick_beats
from pedalboard import Reverb, Compressor, HighpassFilter, LowpassFilter, Delay, Chorus

BPM = 100
BT = 60 / BPM  # 0,6 s
TOTAL = 52 * BT  # 31,2 s
T_B2, T_B3, T_B4 = 3 * BT, 7 * BT, 9 * BT
T_CASC, T_DROP, T_SUB, T_DOC = 12 * BT, 14 * BT, 16 * BT, 17.5 * BT
T_C, T_D, T_E = 22 * BT, 30 * BT, 40 * BT
IG_SAFE = (80, 250, 940, 1500)   # Instagram: tekst między y 250 a 1500, z dala od przycisków po prawej
CX = 510
PETROL = (16, 44, 48)
CREAM = (248, 243, 236)
S = {}


def bubble(lines, fnt, fg, bgc, side="right", padx=44, pady=26, r=40):
    tx = text_sprite(lines, fnt, fg, gap=1.1, pad=0, align="left")
    w, h = tx.width + 2 * padx, tx.height + 2 * pady
    m = 40
    im = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((m, m + 10, m + w, m + h + 10), r, fill=(0, 0, 0, 60))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((m, m, m + w, m + h), r, fill=bgc + (255,))
    # „ogonek” dymka — zaokrąglony róg zastąpiony ostrym w dolnym rogu
    if side == "right":
        d.rectangle((m + w - r, m + h - r, m + w, m + h), fill=bgc + (255,))
    else:
        d.rectangle((m, m + h - r, m + r, m + h), fill=bgc + (255,))
    im.alpha_composite(tx, (m + padx, m + pady - 4))
    return im


def avatar(letter, col, size=74):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((0, 0, size - 1, size - 1), fill=col + (255,))
    tx = text_sprite([letter], font(B, int(size * 0.48)), INK if col == YEL else WHITE, pad=0)
    im.alpha_composite(tx, ((size - tx.width) // 2, (size - tx.height) // 2 - 3))
    return im


def rounded_photo(path, w, h, r=44):
    im = Image.open(path).convert("RGB")
    sc = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
    return im


def prep():
    # --- czat ---
    S["hdr_t"] = text_sprite(["Przyjaciółki"], font(B, 46), WHITE, pad=0)
    S["hdr_s"] = text_sprite(["3 osoby · online"], font(M, 30), LAVL, pad=0)
    S["av"] = [avatar("A", LAV), avatar("K", GREEN), avatar("M", YEL)]
    S["time"] = text_sprite(["dziś, 23:14"], font(M, 30), LAVL)
    S["b1"] = bubble(["Czy tylko ja tak mam?"], font(XB, 66), WHITE, LAVD)
    S["b2"] = bubble(["Budzę się w nocy zlana potem,", "w pracy gubię słowa,", "a w domu wybucham", "o byle drobiazg."],
                     font(B, 46), WHITE, LAVD)
    S["b3"] = bubble(["Ja też."], font(B, 54), INK, WHITE, side="left")
    S["b4"] = bubble(["Ja też.", "Myślałam, że wariuję."], font(B, 54), INK, WHITE, side="left")
    # lawina „Ja też.”
    rng = random.Random(4)
    S["casc"] = []
    for i in range(30):
        sz = rng.choice([40, 46, 52, 60, 70])
        col = rng.choice([(WHITE, INK), (LAVL, INK), (LAV, WHITE), (WHITE, INK), (YEL, INK)])
        b = bubble(["Ja też."], font(B, sz), col[1], col[0], side=rng.choice(["left", "right"]), padx=34, pady=18, r=34)
        x = rng.uniform(230, 800)
        y = rng.uniform(420, 1480)
        S["casc"].append((T_CASC + i * 0.055 + rng.uniform(0, 0.25), x, y, b))
    S["drop1"] = text_sprite([[("Nie tylko ", WHITE), ("Ty.", YEL)]], font(XB, 136), WHITE, pad=10)
    S["drop2"] = text_sprite(["To może być perimenopauza.", "I nie musisz przechodzić", "przez nią sama."], font(M, 54), LAVL, gap=1.15)
    doc = text_sprite(["Nocne poty i inne objawy fizyczne", "zawsze skonsultuj z lekarzem."], font(M, 36), WHITE, gap=1.12, pad=0)
    p = Image.new("RGBA", (doc.width + 90, doc.height + 56), (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle((0, 0, p.width - 1, p.height - 1), 34, fill=GREEN + (255,))
    p.alpha_composite(doc, (45, 26))
    S["doc"] = p
    # --- sala ---
    S["c_lab"] = text_sprite(["KURS W SENS · WROCŁAW"], font(B, 34), LAVD, pad=6)
    S["c_h"] = text_sprite(["Środek, nie koniec"], fit_font(["Środek, nie koniec"], XB, 104, 860), INK, pad=6)
    S["photo"] = rounded_photo(ASSETS + "foto/sala_duza.jpg", 900, 560)
    S["c_cv"] = text_sprite(["Jedno z tych krzeseł może być Twoje."],
                            fit_font(["Jedno z tych krzeseł może być Twoje."], CV, 80, 860), LAVD, pad=6)
    S["c_p1"] = pill("start: piątek, 4 grudnia", font(B, 46), WHITE, INK, padx=46, h=100)
    S["c_p2"] = pill("6 spotkań · stacjonarnie · mała grupa", font(M, 38), INK, LAVL, padx=40, h=88)
    # --- tematy ---
    S["d_h"] = text_sprite(["O czym porozmawiamy:"], font(XB, 64), INK, pad=6)
    topics = ["uderzenia gorąca i stres", "lęk i zmienne nastroje", "sen i mgła mózgowa",
              "ciało, jedzenie i metabolizm", "wiek i ageizm"]
    S["d_t"] = [bubble([t], font(B, 50), INK if i % 2 == 0 else WHITE, WHITE if i % 2 == 0 else LAVD,
                       side="left" if i % 2 == 0 else "right", padx=40, pady=22) for i, t in enumerate(topics)]
    nt = text_sprite(["Psychoedukacja + ćwiczenia CBT", "w małej grupie. To nie terapia grupowa."], font(M, 38), INK, gap=1.15, pad=0)
    c = Image.new("RGBA", (880, nt.height + 64), (0, 0, 0, 0))
    ImageDraw.Draw(c).rounded_rectangle((0, 0, 879, c.height - 1), 36, fill=(234, 224, 238, 255))
    c.alpha_composite(nt, ((880 - nt.width) // 2, 30))
    S["d_note"] = c
    # --- karta końcowa ---
    S["logo"] = asset("logo_pion.png", 300)
    S["e_l"] = text_sprite(["Chcesz się zapisać? Napisz do mnie:"], font(M, 42), INK, pad=6)
    S["e_cv"] = text_sprite(["Każda emocja ma sens."], font(CV, 84), LAVD, pad=6)
    S["e_w"] = text_sprite(["senswroclaw.pl · @senswroclaw"], font(B, 44), INK, pad=6)
    S["e_a"] = text_sprite(["SENS · ul. Dyrekcyjna 37/47, Wrocław"], font(M, 36), INK, pad=6)
    S["e_sig"] = text_sprite(["dr Maria Siwa — psycholożka i psychodietetyczka,", "psychoterapeutka CBT w trakcie szkolenia"],
                             font(M, 32), INK, gap=1.15, pad=6)


def scaled(spr, k):
    if abs(k - 1) < 0.01:
        return spr
    return spr.resize((max(1, int(spr.width * k)), max(1, int(spr.height * k))), Image.BICUBIC)


def pop(t, t0, d=0.35):
    """skala wejścia dymka: 0.85 → 1.03 → 1."""
    x = max(0.0, min(1.0, (t - t0) / d))
    return 0.85 + 0.18 * ease(x) - 0.03 * max(0.0, (x - 0.7) / 0.3)


def put_bubble(im, spr, side, y, t, t0, a=1.0, x_r=960, x_l=80):
    if t < t0:
        return
    k = pop(t, t0)
    s = scaled(spr, k)
    al = ramp(t, t0, 0.2) * a
    if side == "right":
        paste(im, s, x_r - s.width / 2 + 40, y, al)
    else:
        paste(im, s, x_l + s.width / 2 - 40, y, al)


def chat_frame(t):
    im = bg(DARK, t)
    d = ImageDraw.Draw(im)
    # pasek czatu
    d.rounded_rectangle((60, 250, 1020, 380), 40, fill=(30, 58, 64, 255))
    d.line([(108, 296), (90, 315), (108, 334)], fill=LAVL + (255,), width=6)
    for i, a in enumerate(S["av"]):
        im.alpha_composite(a, (140 + i * 46, 278))
    im.alpha_composite(S["hdr_t"], (330, 268))
    im.alpha_composite(S["hdr_s"], (330, 330))
    paste(im, S["time"], CX, 440)
    # dymki: przesuwają się w górę, gdy przychodzą nowe
    shift = 0
    put_bubble(im, S["b1"], "right", 560 - shift, t, -1)
    put_bubble(im, S["b2"], "right", 830 - shift, t, T_B2)
    put_bubble(im, S["b3"], "left", 1100, t, T_B3, x_l=160)
    if t >= T_B3:
        im.alpha_composite(S["av"][1], (66, 1100 + 10))
    put_bubble(im, S["b4"], "left", 1290, t, T_B4, x_l=160)
    if t >= T_B4:
        im.alpha_composite(S["av"][2], (66, 1290 + 55))
    return im


def frame(t):
    if t < T_C:
        im = chat_frame(t) if t < T_DROP + 0.6 else bg(DARK, t)
        if t >= T_CASC:
            for (t0, x, y, b) in S["casc"]:
                if t >= t0:
                    s = scaled(b, pop(t, t0, 0.25))
                    paste(im, s, x, y, ramp(t, t0, 0.15) * (1 - 0.8 * ramp(t, T_DROP, 0.5)))
        if t >= T_DROP - 0.15:
            ov = Image.new("RGBA", (W, H), PETROL + (int(228 * ramp(t, T_DROP - 0.15, 0.35)),))
            im.alpha_composite(ov)
            k = ramp(t, T_DROP, 0.35)
            paste(im, scaled(S["drop1"], 1.12 - 0.12 * k), CX, 680, k)
            a2 = ramp(t, T_SUB, 0.45)
            paste(im, S["drop2"], CX, 930 + 24 * (1 - a2), a2)
            a3 = ramp(t, T_DOC, 0.45)
            paste(im, S["doc"], CX, 1240 + 20 * (1 - a3), a3)
        if t > T_C - 0.6:  # krem wjeżdża od dołu
            p = ramp(t, T_C - 0.6, 0.6)
            sub = scene_c(0.0)
            im.alpha_composite(sub.crop((0, 0, W, int(H * p) + 1)), (0, int(H * (1 - p))))
        return im
    if t < T_D:
        im = scene_c(t - T_C)
        if t > T_D - 0.5:
            p = ramp(t, T_D - 0.5, 0.5)
            im = Image.blend(im, scene_d(0.0), p)
        return im
    if t < T_E:
        im = scene_d(t - T_D)
        if t > T_E - 0.5:
            im = Image.blend(im, scene_e(0.0), ramp(t, T_E - 0.5, 0.5))
        return im
    return scene_e(t - T_E)


CREAMBG = None


def cream(gt):
    global CREAMBG
    if CREAMBG is None:
        from tt_base import _blobs
        CREAMBG = _blobs(CREAM, [(200, 300, 520, (238, 228, 240)), (1100, 1100, 600, (244, 236, 222)),
                                 (300, 1900, 620, (232, 222, 238))], 170)
    return bg(CREAMBG, gt)


def scene_c(t):
    im = cream(T_C + t)
    paste(im, S["c_lab"], CX, 330, ramp(t, 0.0, 0.4))
    a = ramp(t, 0.1, 0.45)
    paste(im, S["c_h"], CX, 425 + 20 * (1 - a), a)
    # zdjęcie sali — powolny najazd
    z = 1.0 + 0.07 * min(1.0, t / 4.8)
    ph = S["photo"]
    pw, phh = int(900 * z), int(560 * z)
    big = ph.resize((int(ph.width * z), int(ph.height * z)), Image.BICUBIC)
    ox, oy = (big.width - 900) // 2, (big.height - 560) // 2
    crop = big.crop((ox, oy, ox + 900, oy + 560)).convert("RGBA")
    mask = Image.new("L", (900, 560), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 899, 559), 44, fill=255)
    crop.putalpha(mask)
    card, m = card_sprite(900, 560, r=44)
    card.alpha_composite(crop, (m, m))
    paste(im, card, CX, 800)
    a = ramp(t, 0.8, 0.5)
    paste(im, S["c_cv"], CX, 1160 + 18 * (1 - a), a)
    a = ramp(t, 1.3, 0.4)
    paste(im, S["c_p1"], CX, 1300 + 18 * (1 - a), a)
    a = ramp(t, 1.6, 0.4)
    paste(im, S["c_p2"], CX, 1420 + 18 * (1 - a), a)
    return im


def scene_d(t):
    im = cream(T_D + t)
    paste(im, S["d_h"], CX, 340, ramp(t, 0.0, 0.4))
    for i, b in enumerate(S["d_t"]):
        put_bubble(im, b, "left" if i % 2 == 0 else "right", 500 + i * 160, t, 0.35 + i * 0.4, x_r=960, x_l=80)
    a = ramp(t, 2.4, 0.5)
    paste(im, S["d_note"], CX, 1365 + 18 * (1 - a), a)
    return im


def scene_e(t):
    im = cream(T_E + t)
    paste(im, S["logo"], CX, 400, ramp(t, 0.0, 0.5))
    paste(im, S["e_l"], CX, 630, ramp(t, 0.2, 0.4))
    # dymek z „pisaną” wiadomością ŚRODEK
    word = "ŚRODEK"
    n = int(max(0, min(len(word), (t - 0.5) / 0.12 + 1))) if t >= 0.5 else 0
    txt = word[:n]
    f = font(XB, 96)
    bw = int(f.getlength(word)) + 120 + 110
    b = Image.new("RGBA", (bw + 80, 220), (0, 0, 0, 0))
    sh = Image.new("RGBA", b.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 50, 40 + bw, 50 + 150), 48, fill=(60, 30, 70, 70))
    b.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(b)
    d.rounded_rectangle((40, 40, 40 + bw, 40 + 150), 48, fill=LAVD + (255,))
    d.rectangle((40 + bw - 48, 40 + 150 - 48, 40 + bw, 190), fill=LAVD + (255,))
    d.text((40 + 60, 40 + 75), txt, font=f, fill=WHITE, anchor="lm")
    if n < len(word) and int(t * 3) % 2 == 0:
        x = 40 + 60 + f.getlength(txt) + 6
        d.rectangle((x, 72, x + 7, 160), fill=WHITE)
    # przycisk „wyślij”
    sent = ramp(t, 1.35, 0.3)
    cx, cy = 40 + bw - 80, 115
    d.ellipse((cx - 44, cy - 44, cx + 44, cy + 44), fill=YEL + (255,))
    d.polygon([(cx - 18, cy - 22), (cx + 24, cy), (cx - 18, cy + 22), (cx - 8, cy)], fill=INK + (255,))
    paste(im, b, CX, 800, ramp(t, 0.3, 0.3))
    if sent > 0:
        st = text_sprite(["wysłano"], font(M, 30), LAVD, pad=4)
        paste(im, st, CX + bw / 2 - 60, 925, sent)
    a = ramp(t, 1.0, 0.5)
    paste(im, S["e_cv"], CX, 1020 + 16 * (1 - a), a)
    a = ramp(t, 1.3, 0.5)
    paste(im, S["e_w"], CX, 1125, a)
    paste(im, S["e_a"], CX, 1195, a)
    a = ramp(t, 1.6, 0.5)
    d2 = ImageDraw.Draw(im)
    if a > 0:
        d2.line([(CX - 120, 1262), (CX + 120, 1262)], fill=LAV + (int(255 * a),), width=3)
    paste(im, S["e_sig"], CX, 1345, a)
    return im


# ---------------- muzyka ----------------
def music(path):
    s = Song(BPM, TOTAL)
    ep = s.track("ep", 0, 4)       # piano elektryczne
    gt = s.track("gt", 0, 25)      # gitara akustyczna (stalowe struny)
    bs = s.track("bass", 0, 33)    # bas palcowy
    el = s.track("lead", 0, 27)    # czysta gitara elektryczna — krótki motyw
    st = s.track("str", 0, 49)     # smyczki (tylko w przerwie / na końcu)
    dr = s.drums(kit=8)            # zestaw „Room”
    prog = [([53, 57, 60, 64], 41), ([52, 55, 59, 62], 40), ([50, 53, 57, 60, 64], 38), ([55, 59, 62, 65], 43)]
    riff = [(0, 72), (0.5, 74), (1.0, 76), (2.0, 79), (2.5, 76), (3.5, 74)]
    D0 = 14  # „Nie tylko Ty.”
    end_b = TOTAL / BT
    # intro (noc): EP z filtrem, delikatny rytm
    for bar in range(0, 14, 4):
        ch, root = prog[(bar // 4) % 4]
        L = min(4, D0 - bar)
        ep.chord(bar, ch, L * 0.95, 70, strum=0.04)
        ep.chord(bar + 1.5, ch, 0.4, 56)
        bs.note(bar, root, min(L, 3.5) * 0.9, 70)
        for b in range(int(L)):
            dr.hit(bar + b, 36 if b % 2 == 0 else 37, 72 if b % 2 == 0 else 60)
            dr.hit(bar + b + 0.5, 42, 42)
    for k, b in enumerate([12, 12.5, 13, 13.25, 13.5, 13.75]):  # przejście do dropu
        dr.hit(b, 38, 60 + k * 9)
    s.riser(11, 3, 0.04)
    # pełny groove od beatu 14
    b0 = D0
    i = 0
    while b0 < end_b - 0.01:
        ch, root = prog[i % 4]
        brk = 30 <= b0 < 38          # tematy: lżej, ale z pulsem
        if b0 >= 46:                  # końcowy akord
            ep.chord(b0, ch + [ch[1] + 12], 5, 80, strum=0.03)
            st.chord(b0, ch[1:], 5, 70)
            bs.note(b0, root, 3, 88)
            dr.hit(b0, 49, 88)
            dr.hit(b0, 36, 100)
            break
        for e in range(4):
            ep.chord(b0 + e + 0.5, ch, 0.45, 80 if not brk else 68)
        for k in range(8):           # gitara: ósemki „down-up”
            gt.chord(b0 + k * 0.5, [n + 12 for n in ch[:4]], 0.42, (78 if k % 2 == 0 else 60) - (10 if brk else 0),
                     strum=0.012)
        for off, oc, v in [(0, 0, 104), (0.75, 0, 84), (1.5, 12, 80), (2.0, 0, 98), (3.0, 7, 84), (3.5, 12, 80)]:
            bs.note(b0 + off, root + oc, 0.42, v)
        if brk:
            st.chord(b0, ch[1:], 3.8, 64)
        elif i % 2 == 0:
            for off, n in riff:
                el.note(b0 + off, n, 0.35, 76)
        for b in range(4):
            tb = b0 + b
            dr.hit(tb, 36, 112 if b % 2 == 0 else 96)
            if b % 2 == 1:
                dr.hit(tb, 38, 96)
                dr.hit(tb, 39, 70)
            dr.hit(tb + 0.5, 42, 64)
            dr.hit(tb + 0.25, 42, 40)
            dr.hit(tb + 0.75, 42, 46)
            if not brk:
                dr.hit(tb + 0.5, 54, 50)  # tamburyn
        b0 += 4
        i += 1
    for stb in (D0, 22, 40):
        dr.hit(stb, 49, 100)
        s.impact(stb, 0.4)
    s.riser(37, 3, 0.035)
    # cichy „pop” przy każdym dymku (krótki ton, nie dzwonek)
    def blip(sec, g=0.12):
        L = int(0.09 * 44100)
        tt = np.arange(L) / 44100
        f = 900 - 3500 * tt
        x = (np.sin(2 * np.pi * np.cumsum(f) / 44100) * np.exp(-tt * 45)).astype(np.float32) * g
        s._place("fx", sec, np.stack([x, x], 1))
    for sec in [0.02, T_B2, T_B3, T_B4] + [T_D + 0.35 + i * 0.4 for i in range(5)]:
        blip(sec)
    kicks = kick_beats(D0, 46)
    s.render(path,
             gains={"ep": 0.5, "gt": 0.3, "bass": 0.8, "lead": 0.3, "str": 0.28, "drums": 0.85, "fx": 0.6,
                    "_duck": ("ep", "gt", "bass", "str")},
             fx={"ep": [HighpassFilter(140), Chorus(rate_hz=0.5, depth=0.2, mix=0.3), Reverb(room_size=0.5, wet_level=0.2)],
                 "gt": [HighpassFilter(220), Reverb(room_size=0.35, wet_level=0.12)],
                 "lead": [Delay(delay_seconds=BT * 0.75, feedback=0.28, mix=0.22), Reverb(room_size=0.6, wet_level=0.25)],
                 "str": [Reverb(room_size=0.8, wet_level=0.35)],
                 "bass": [LowpassFilter(1000), Compressor(threshold_db=-18, ratio=3)],
                 "drums": [Compressor(threshold_db=-14, ratio=2.2, attack_ms=5, release_ms=80)]},
             sidechain=kicks, duck=0.4, lowpass_until=(0, D0, 1200))


def test_sheet(times, path):
    ims = [frame(t).convert("RGB").resize((360, 640)) for t in times]
    g = Image.new("RGB", (370 * len(ims), 650), (90, 90, 90))
    d = ImageDraw.Draw(g)
    for i, im in enumerate(ims):
        g.paste(im, (5 + 370 * i, 5))
        x0, y0, x1, y1 = [v / 3 for v in IG_SAFE]
        d.rectangle((5 + 370 * i + x0, 5 + y0, 5 + 370 * i + x1, 5 + y1), outline=(255, 0, 0))
    g.save(path, quality=85)


if __name__ == "__main__":
    prep()
    if sys.argv[1] == "test":
        out = sys.argv[2]
        os.makedirs(out, exist_ok=True)
        test_sheet([0.0, 2.4, 6.2, 7.9], f"{out}/s1.jpg")
        test_sheet([8.6, 11.5, 13.0, 15.5], f"{out}/s2.jpg")
        test_sheet([17.9, 20.5, 23.5, 25.0], f"{out}/s3.jpg")
        test_sheet([26.0, 27.5, 29.5, 31.0], f"{out}/s4.jpg")
        for t in [0.0, 6.2, 11.5, 17.0, 23.0, 28.0]:
            frame(t).convert("RGB").save(f"{out}/f_{t}.jpg", quality=88)
    elif sys.argv[1] == "music":
        music(sys.argv[2])
    else:
        wav = sys.argv[2] + ".wav"
        music(wav)
        render(frame, TOTAL, sys.argv[2], wav)
        os.remove(wav)
