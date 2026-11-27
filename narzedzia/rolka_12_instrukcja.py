"""Rolka 12 — „Środek, nie koniec”: INSTRUKCJA OBSŁUGI: BRAK (kurs, start pt 4 grudnia 2026).

Koncept w jednym zdaniu: menopauza przychodzi jak zestaw z etykietą „zawartość opakowania” (uderzenia gorąca,
huśtawka nastroju, pobudki o 3:00…), ale z pieczątką „Instrukcja obsługi: BRAK” — więc piszemy ją razem:
spis treści tej instrukcji = 5 tematów kursu, „strona 1” do zrobienia od razu, potem kurs w SENS.
Format: etykieta/pudełko z papieru pakowego (kraft) + pieczątka na prawdziwych nagraniach Coverr
(starsza dłoń włącza wiatrak; kobieta 40+ czyta przy lampie; dłonie piszą w notesie) + „spis treści” na kartce.
Estetyka: kraft + ciemny petrol (tusz) + lawendowa pieczątka + żółta taśma; karta końcowa ciemna zieleń petrol
(wczoraj: jasny krem + lawenda).
Oś: 0–8,4 hak (etykieta „Menopauza. Zawartość zestawu”, pieczątka BRAK ok. 5,2 s) → 8,4–13,4 „Więc napiszemy ją
razem” → 13,4–19,8 spis treści (tematy kursu) → 19,8–25 „Strona 1 na dziś” (ćwiczenie) + lekarz →
25–29,4 karta kursu → 29,4–33,6 karta końcowa ze zdjęciem maria_siwa_oficjalne.jpg.
Nagrania: Coverr (licencja Coverr: komercyjnie, bez atrybucji): a-woman-turns-on-a-fan-4983,
a-woman-quietly-reading-a-book-near-a-lamp-at-home-8499, close-up-of-handwriting-in-notebook.
Muzyka: Mixkit „Forever in My Heart” — Michael Ramir C. (ID 797, Mixkit Stock Music Free License), ciepły
akustyczny folk z gitarą; tło −16,5 LUFS, low-pass 9,5 kHz.
Użycie (z katalogu repo): python3 narzedzia/rolka_12_instrukcja.py test OUTDIR | full OUT.mp4
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "tiktok-sens", "narzedzia"))
from tt_base import *
from tt_klipy import Clip, music_bed, render_av, smooth

TOTAL = 33.6
T_B, T_C, T_D, T_E, T_F = 8.4, 13.4, 19.8, 25.0, 29.4
CX = 510
IG_SAFE = (80, 250, 940, 1360)
PAPER = (251, 247, 238)
KRAFT = (196, 164, 124)
PET = (14, 60, 62)       # ciemny petrol (karta końcowa)
STAMP = (129, 89, 131)   # lawendowy tusz pieczątki
Q, CL = {}, {}
RNG = np.random.default_rng(7)


# ---------- tekstury ----------
def kraft_bg():
    h, w = H + 200, W + 200
    base = np.zeros((h, w, 3), np.float32) + np.array(KRAFT, np.float32)
    n = RNG.normal(0, 1, (h // 4, w // 4)).astype(np.float32)
    n = np.array(Image.fromarray(((n * 20) + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC),
                 np.float32) - 128
    fib = RNG.normal(0, 1, (h, w // 6)).astype(np.float32)
    fib = np.array(Image.fromarray(((fib * 25) + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BILINEAR),
                   np.float32) - 128
    img = base + 0.55 * n[..., None] + 0.18 * fib[..., None]
    yy, xx = np.mgrid[0:h, 0:w]
    vig = 1 - 0.16 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    img *= vig[..., None]
    return Image.fromarray(img.clip(0, 255).astype(np.uint8))


def kraft(t):
    ox = 100 + 40 * math.sin(t * 0.13)
    oy = 100 + 40 * math.cos(t * 0.1)
    return Q["kraft"].crop((int(ox), int(oy), int(ox) + W, int(oy) + H)).convert("RGBA")


def tape(w=150, h=46, ang=-6):
    im = Image.new("RGBA", (w, h), YEL + (190,))
    a = np.array(im)
    a[..., 3] = (a[..., 3] * (0.85 + 0.15 * RNG.random((h, w)))).astype(np.uint8)
    return Image.fromarray(a).rotate(ang, expand=True, resample=Image.BICUBIC)


def stamp(text):
    f = font(XB, 120)
    tx = text_sprite([text], f, STAMP, pad=10)
    w, h = tx.width + 60, tx.height + 20
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, w - 7, h - 7), 18, outline=STAMP + (255,), width=10)
    im.alpha_composite(tx, (30, 4))
    a = np.array(im)
    worn = (RNG.random((h, w)) > 0.16).astype(np.float32)  # zużyty tusz
    worn = np.array(Image.fromarray((worn * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), np.float32)
    a[..., 3] = (a[..., 3] * (0.35 + 0.65 * worn / 255) * 0.92).astype(np.uint8)
    return Image.fromarray(a).rotate(9, expand=True, resample=Image.BICUBIC)


def paper_card(w, h, r=10, fill=PAPER):
    c, m = card_sprite(w, h, r=r, fill=fill, shadow=(40, 25, 10, 90))
    return c, m


def check_box(sz, ticked):
    im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, sz - 4, sz - 4), 6, outline=INK + (255,), width=4)
    if ticked > 0:
        p = [(sz * 0.2, sz * 0.52), (sz * 0.42, sz * 0.74), (sz * 0.84, sz * 0.22)]
        k = ticked
        if k < 0.5:
            q = p[0][0] + (p[1][0] - p[0][0]) * k * 2, p[0][1] + (p[1][1] - p[0][1]) * k * 2
            d.line([p[0], q], fill=LAVD + (255,), width=8)
        else:
            kk = (k - 0.5) * 2
            q = p[1][0] + (p[2][0] - p[1][0]) * kk, p[1][1] + (p[2][1] - p[1][1]) * kk
            d.line([p[0], p[1], q], fill=LAVD + (255,), width=8, joint="curve")
    return im


ITEMS = ["uderzenia gorąca", "huśtawka nastroju", "pobudki o 3:00", "mgła w głowie",
         "pytania o ciało i jedzenie"]
CHAP = ["Uderzenia gorąca i stres", "Lęk i zmienność nastroju", "Sen i mgła mózgowa",
        "Ciało, jedzenie i metabolizm", "Wiek i ageizm"]
LW = 840  # szerokość etykiety


def photo_maria(w):
    ph = Image.open(os.path.join(REPO, "fotos_maria", "maria_siwa_oficjalne.jpg")).convert("RGB")
    c = ph.crop((0, 20, 1023, 1180))  # od czubka głowy z zapasem do skrzyżowanych rąk; bez rozciągania
    h = int(w * c.height / c.width)    # tylko równomierne skalowanie
    c = c.resize((w, h), Image.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=255)
    fr, fm = card_sprite(w, h, r=30, fill=(240, 234, 224), shadow=(0, 0, 0, 90))
    fr.paste(c, (fm, fm), mask)
    return fr


def prep():
    Q["kraft"] = kraft_bg()
    CL["a"] = Clip("coverr-a-woman-turns-on-a-fan-4983", 0.5, T_B + 0.5, x=0.30, zoom=(1.0, 1.05))
    CL["b"] = Clip("coverr-a-woman-quietly-reading-a-book-near-a-lamp-at-home-8499", 0.0, T_C - T_B + 1.0,
                   x=0.42, zoom=(1.04, 1.0))
    CL["d"] = Clip("coverr-close-up-of-handwriting-in-notebook", 0.0, T_E - T_D + 1.0, x=0.55, zoom=(1.0, 1.05))
    # A — etykieta „zawartość zestawu”
    Q["a_k1"] = text_sprite(["ZESTAW"], font(B, 34), LAVD, pad=0)
    Q["a_h"] = text_sprite(["Menopauza"], font(XB, 104), INK, pad=0)
    Q["a_k2"] = text_sprite(["Zawartość opakowania:"], font(B, 46), INK, pad=0)
    for i, it in enumerate(ITEMS):
        Q[f"it{i}"] = text_sprite([it], fit_font([it], M, 46, LW - 230), INK, pad=0)
    Q["a_ins"] = text_sprite(["Instrukcja obsługi:"], font(XB, 56), INK, pad=0)
    Q["stamp"] = stamp("BRAK")
    Q["tape"] = tape()
    Q["tape2"] = tape(130, 42, 7)
    # B
    b1 = ["Nikt jej nie dołączył."]
    b2 = ["Więc napiszemy ją razem."]
    Q["b1"] = text_sprite(b1, fit_font(b1, B, 54, 740), INK, pad=0)
    Q["b2"] = text_sprite(b2, fit_font(b2, XB, 68, 760), LAVD, pad=0)
    b3 = ["6 spotkań w małej grupie · SENS, Wrocław"]
    Q["b3"] = pill(b3[0], fit_font(b3, B, 38, 720), WHITE, INK, padx=40, h=96)
    # C — spis treści
    Q["c_t"] = text_sprite(["INSTRUKCJA OBSŁUGI"], font(XB, 64), INK, pad=0)
    Q["c_s"] = text_sprite(["(piszemy ją razem)"], font(CV, 64), LAVD, pad=0)
    Q["c_sp"] = text_sprite(["Spis treści"], font(B, 40), INK, pad=0)
    for i, ch in enumerate(CHAP):
        Q[f"ch{i}"] = text_sprite([[(f"{i + 1}.  ", LAVD), (ch, INK)]], fit_font([f"{i + 1}.  " + ch], B, 50, 700),
                                  INK, pad=0)
    cf = ["psychoedukacja + ćwiczenia CBT", "To nie terapia grupowa."]
    Q["c_f"] = text_sprite(cf, fit_font(cf, M, 38, 700), INK, gap=1.2, pad=0)
    # D — strona 1
    Q["d_t"] = text_sprite(["Strona 1 — na dziś:"], font(CV, 76), LAVD, pad=0)
    d1 = ["W trudnej chwili zapisz trzy rzeczy:"]
    Q["d1"] = text_sprite(d1, fit_font(d1, B, 46, 720), INK, pad=0)
    for i, ln in enumerate(["Co się dzieje?", "Co myślę?", "Co czuje ciało?"]):
        Q[f"dq{i}"] = text_sprite([[(f"{i + 1}  ", LAVD), (ln, INK)]], font(XB, 58), INK, pad=0)
    d2 = ["Zapisana myśl to myśl, nie fakt."]
    Q["d2"] = text_sprite(d2, fit_font(d2, M, 40, 720), INK, pad=0)
    dl = ["Objawy z ciała zawsze skonsultuj z lekarzem."]
    Q["d_doc"] = pill(dl[0], fit_font(dl, B, 34, 720), WHITE, GREEN, padx=36, h=84)
    # E — karta kursu
    Q["e_k"] = text_sprite(["KURS W SENS · WROCŁAW"], font(B, 34), LAVD, pad=0)
    Q["e_h"] = text_sprite(["Środek,", "nie koniec"], font(XB, 104), INK, gap=1.02, pad=0)
    e1 = ["dla kobiet w peri- i menopauzie"]
    Q["e1"] = text_sprite(e1, fit_font(e1, M, 44, 700), INK, pad=0)
    Q["e2"] = text_sprite([[("Start: ", INK), ("piątek, 4 grudnia", LAVD)]], font(XB, 60), INK, pad=0)
    e3 = ["6 spotkań · stacjonarnie", "ul. Dyrekcyjna 37/47, Wrocław"]
    Q["e3"] = text_sprite(e3, fit_font(e3, M, 42, 700), INK, gap=1.25, pad=0)
    # F — karta końcowa (ciemny petrol)
    Q["f_logo"] = asset("logo_bialy.png", 170)
    Q["f_photo"] = photo_maria(440)
    sg = ["dr Maria Siwa — psycholożka i psychodietetyczka,", "psychoterapeutka CBT w trakcie szkolenia"]
    Q["f_sig"] = text_sprite(sg, fit_font(sg, M, 34, 840), WHITE, gap=1.2, pad=4)
    Q["f_ke"] = text_sprite(["Każda emocja ma sens."], font(CV, 80), LAVL, pad=4)
    Q["f_btn"] = pill_rich([("Napisz ", INK), ("ŚRODEK", LAVD), (" w wiadomości", INK)], font(B, 46), PAPER)
    Q["f_www"] = text_sprite(["senswroclaw.pl · @senswroclaw"], font(B, 38), WHITE, pad=4)


def pill_rich(parts, fnt, bgc, padx=52, h=110):
    tx = text_sprite([parts], fnt, INK, pad=0)
    im = Image.new("RGBA", (tx.width + 2 * padx, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, h - 1), h // 2, fill=bgc + (255,))
    im.alpha_composite(tx, (padx, (h - tx.height) // 2 - 2))
    return im


def shade(im, top=0.0, bottom=0.0, col=(30, 26, 20)):
    y = np.arange(H)[:, None].astype(np.float32)
    g = top * np.clip(1 - y / 1100, 0, 1) + bottom * np.clip((y - 1100) / 820, 0, 1)
    lay = np.zeros((H, W, 4), np.uint8)
    lay[..., :3] = col
    lay[..., 3] = np.repeat((np.clip(g, 0, 1) * 255).astype(np.uint8), W, 1)
    im.alpha_composite(Image.fromarray(lay, "RGBA"))


# ---------- sceny ----------
def label_sprite(t):
    """etykieta zestawu; t = czas sceny A"""
    h = 1000
    c, m = paper_card(LW, h, r=12)
    d = ImageDraw.Draw(c)
    # podwójna ramka jak na etykiecie produktu
    d.rectangle((m + 22, m + 22, m + LW - 23, m + h - 23), outline=INK + (255,), width=4)
    d.rectangle((m + 32, m + 32, m + LW - 33, m + h - 33), outline=INK + (255,), width=1)
    y = m + 62
    c.alpha_composite(Q["a_k1"], (m + (LW - Q["a_k1"].width) // 2, y))
    y += 44
    c.alpha_composite(Q["a_h"], (m + (LW - Q["a_h"].width) // 2, y))
    y += 150
    d.line((m + 70, y, m + LW - 70, y), fill=INK + (255,), width=3)
    y += 26
    c.alpha_composite(Q["a_k2"], (m + 70, y))
    y += 82
    for i in range(5):
        t0 = 0.8 + 0.7 * i
        a = ramp(t, t0, 0.35)
        if a > 0:
            row = Image.new("RGBA", (LW - 140, 64), (0, 0, 0, 0))
            row.alpha_composite(check_box(48, ramp(t, t0 + 0.15, 0.35)), (0, 8))
            row.alpha_composite(Q[f"it{i}"], (76, (64 - Q[f"it{i}"].height) // 2 - 4))
            if a < 1:
                row.putalpha(row.getchannel("A").point(lambda v: int(v * a)))
            c.alpha_composite(row, (m + 70, y + int(10 * (1 - a))))
        y += 70
    y += 20
    d.line((m + 70, y, m + LW - 70, y), fill=INK + (255,), width=3)
    y += 26
    a = ramp(t, 4.5, 0.4)
    if a > 0:
        s = Q["a_ins"].copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * a)))
        c.alpha_composite(s, (m + 70, y))
    return c, m, y


def scene_a(t):
    im = CL["a"].frame(t)
    shade(im, top=0.25, bottom=0.15)
    lab, m, yins = label_sprite(t)
    cy = 760
    paste(im, lab, CX, cy)
    top = cy - lab.height / 2
    paste(im, Q["tape"], CX - LW / 2 + 40, top + m - 4)
    paste(im, Q["tape2"], CX + LW / 2 - 40, top + m - 4)
    # pieczątka BRAK: krótko większa i przezroczysta → dociśnięta (bez błysków)
    s = ramp(t, 5.2, 0.28)
    if s > 0:
        sc = 1.35 - 0.35 * s
        st = Q["stamp"].resize((int(Q["stamp"].width * sc), int(Q["stamp"].height * sc)), Image.LANCZOS)
        paste(im, st, CX + 30, top + yins + 222, min(1, s * 1.3))
    return im


def scene_b(t):
    tt = t - T_B
    im = CL["b"].frame(tt)
    shade(im, top=0.35, bottom=0.2)
    out = 1 - ramp(t, T_C - 0.35, 0.35)
    a, b = ramp(tt, 0.3, 0.45), ramp(tt, 1.5, 0.45)
    w = 860
    hh = 270
    c, m = paper_card(w, hh, r=14)
    c.alpha_composite(Q["b1"], (m + (w - Q["b1"].width) // 2, m + 60))
    if b > 0:
        s = Q["b2"].copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * b)))
        c.alpha_composite(s, (m + (w - Q["b2"].width) // 2, m + 150 + int(12 * (1 - b))))
    paste(im, c, CX, 1060 + 20 * (1 - a), a * out)
    paste(im, Q["tape"], CX, 1060 - hh / 2 - 2 + 20 * (1 - a), a * out)
    p = ramp(tt, 2.6, 0.45)
    paste(im, Q["b3"], CX, 1285 + 14 * (1 - p), p * out)
    return im


def scene_c(t):
    tt = t - T_C
    im = kraft(t)
    w, h = 860, 960
    c, m = paper_card(w, h, r=8)
    d = ImageDraw.Draw(c)
    d.line((m + 70, m + 296, m + w - 70, m + 296), fill=INK + (255,), width=2)
    y = m + 56
    c.alpha_composite(Q["c_t"], (m + (w - Q["c_t"].width) // 2, y))
    c.alpha_composite(Q["c_s"], (m + (w - Q["c_s"].width) // 2, y + 92))
    c.alpha_composite(Q["c_sp"], (m + 70, m + 240))
    for i in range(5):
        a = ramp(tt, 0.8 + 0.55 * i, 0.4)
        if a > 0:
            s = Q[f"ch{i}"].copy()
            s.putalpha(s.getchannel("A").point(lambda v: int(v * a)))
            c.alpha_composite(s, (m + 70 + int(14 * (1 - a)), m + 318 + i * 96))
    f = ramp(tt, 3.9, 0.45)
    if f > 0:
        s = Q["c_f"].copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * f)))
        d.line((m + 70, m + 810, m + w - 70, m + 810), fill=LAV + (int(255 * f),), width=3)
        c.alpha_composite(s, (m + (w - s.width) // 2, m + 832))
    a = ramp(tt, 0.0, 0.5)
    out = 1 - ramp(t, T_D - 0.3, 0.3)
    paste(im, c, CX, 800 + 24 * (1 - a), out)
    paste(im, Q["tape2"], CX - w / 2 + 60, 800 - h / 2 + 4, out)
    paste(im, Q["tape"], CX + w / 2 - 60, 800 - h / 2 + 4, out)
    return im


def scene_d(t):
    tt = t - T_D
    im = CL["d"].frame(tt)
    shade(im, top=0.15, bottom=0.25)
    out = 1 - ramp(t, T_E - 0.3, 0.3)
    w, h = 860, 640
    c, m = paper_card(w, h, r=14)
    c.alpha_composite(Q["d_t"], (m + 60, m + 34))
    c.alpha_composite(Q["d1"], (m + 60, m + 150))
    for i in range(3):
        a = ramp(tt, 1.0 + 0.6 * i, 0.4)
        if a > 0:
            s = Q[f"dq{i}"].copy()
            s.putalpha(s.getchannel("A").point(lambda v: int(v * a)))
            c.alpha_composite(s, (m + 60 + int(14 * (1 - a)), m + 240 + i * 96))
    f = ramp(tt, 3.0, 0.4)
    if f > 0:
        s = Q["d2"].copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * f)))
        c.alpha_composite(s, (m + 60, m + 548))
    a = ramp(tt, 0.2, 0.45)
    paste(im, c, CX, 560 + 20 * (1 - a), a * out)
    p = ramp(tt, 2.2, 0.45)
    paste(im, Q["d_doc"], CX, 1290, p * out)
    return im


def scene_e(t):
    tt = t - T_E
    im = kraft(t)
    w, h = 860, 860
    c, m = paper_card(w, h, r=12)
    d = ImageDraw.Draw(c)
    d.rectangle((m + 22, m + 22, m + w - 23, m + h - 23), outline=INK + (255,), width=4)
    d.rectangle((m + 32, m + 32, m + w - 33, m + h - 33), outline=INK + (255,), width=1)
    items = [("e_k", 80, 0.2), ("e_h", 140, 0.3), ("e1", 140 + Q["e_h"].height + 24, 0.6), ("e2", 570, 0.9), ("e3", 680, 1.2)]
    for k, y, t0 in items:
        a = ramp(tt, t0, 0.4)
        if a > 0:
            s = Q[k].copy()
            s.putalpha(s.getchannel("A").point(lambda v: int(v * a)))
            c.alpha_composite(s, (m + (w - s.width) // 2, m + y))
    d.line((m + 90, m + 548, m + w - 90, m + 548), fill=LAV + (255,), width=3)
    out = 1 - ramp(t, T_F - 0.3, 0.3)
    paste(im, c, CX, 800, out)
    paste(im, Q["tape"], CX - w / 2 + 60, 800 - h / 2 + 4, out)
    paste(im, Q["tape2"], CX + w / 2 - 60, 800 - h / 2 + 4, out)
    return im


def scene_f(t):
    tt = t - T_F
    im = Image.new("RGBA", (W, H), PET + (255,))
    items = [(Q["f_logo"], 335, 0.1), (Q["f_photo"], 700, 0.3), (Q["f_sig"], 1005, 0.6), (Q["f_ke"], 1103, 0.8),
             (Q["f_btn"], 1212, 1.0), (Q["f_www"], 1312, 1.2)]
    for spr, y, t0 in items:
        a = ramp(tt, t0, 0.45)
        paste(im, spr, CX, y + 14 * (1 - a), a)
    return im


def frame(t):
    seq = [(T_F, scene_f, scene_e, 0.9), (T_E, scene_e, scene_d, 0.7), (T_D, scene_d, scene_c, 0.6),
           (T_C, scene_c, scene_b, 0.6), (T_B, scene_b, scene_a, 0.5)]
    for t0, cur, prev, fd in seq:
        if t >= t0:
            im = cur(t)
            if t - t0 < fd:
                im = Image.blend(prev(t), im, smooth((t - t0) / fd))
            return im
    return scene_a(t)


def test_sheet(times, path):
    ims = [frame(t).convert("RGB").resize((360, 640)) for t in times]
    g = Image.new("RGB", (370 * len(ims), 650), (90, 90, 90))
    d = ImageDraw.Draw(g)
    for i, im in enumerate(ims):
        g.paste(im, (5 + 370 * i, 5))
        x0, y0, x1, y1 = [vv / 3 for vv in IG_SAFE]
        d.rectangle((5 + 370 * i + x0, 5 + y0, 5 + 370 * i + x1, 5 + y1), outline=(255, 0, 0))
    g.save(path, quality=85)


if __name__ == "__main__":
    prep()
    if sys.argv[1] == "test":
        out = sys.argv[2]
        os.makedirs(out, exist_ok=True)
        test_sheet([0.0, 2.5, 6.0, 8.0], f"{out}/s1.jpg")
        test_sheet([9.5, 12.5, 15.0, 19.0], f"{out}/s2.jpg")
        test_sheet([21.0, 24.5, 28.5, 33.0], f"{out}/s3.jpg")
        for t in [0.0, 6.5, 12.5, 18.8, 24.0, 28.5, 32.5]:
            frame(t).convert("RGB").save(f"{out}/f_{t}.jpg", quality=88)
    else:
        wav = sys.argv[2] + ".wav"
        music_bed(797, 2.2, TOTAL, wav, fade_in=0.4, fade_out=2.2, lufs=-16.5)
        render_av(frame, TOTAL, sys.argv[2], wav)
        os.remove(wav)
