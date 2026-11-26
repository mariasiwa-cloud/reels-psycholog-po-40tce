"""Rolka 11 — „Środek, nie koniec”: MENO-PAUZA (kurs, start pt 4 grudnia 2026).

Koncept w jednym zdaniu: w słowie „menopauza” jest „pauza”, nie „stop” — prawdziwe nagranie zatrzymuje się
pilotem jak film (stop-klatka + ikona pauzy), pasek odtwarzania pokazuje, że jesteś w środku filmu, nie na
napisach końcowych; ćwiczenie „naciśnij pauzę” (3 kroki CBT) → „Następny odcinek” = kurs w SENS.
Format: interfejs odtwarzacza wideo (pauza, pasek postępu, menu pauzy, „następny odcinek”) na prawdziwych
nagraniach Coverr; dominanta: jasny krem + lawenda, mały żółty akcent (główka paska). Wczoraj: ciemny petrol.
Oś: 0–5,4 hak (pilot, stop-klatka, „meno·pauza”) → 5,4–11,8 zwrot: „Pauza nie kończy filmu” + pasek „środek”
→ 11,8–18 ćwiczenie „naciśnij pauzę” → 18–23,4 „Następny odcinek” = kurs → 23,4–28,9 jasna karta końcowa
ze zdjęciem 07 (studyjne).
Nagrania: Coverr (licencja Coverr: komercyjnie, bez atrybucji): a-woman-watching-tv-3282,
a-woman-reading-a-book-and-giving-a-shy-smile-5951.
Muzyka: Mixkit „We'll Be Okay” — Michael Ramir C. (ID 1081, Mixkit Stock Music Free License), spokojne piano,
ok. 70 BPM; tło −16,5 LUFS, low-pass 9,5 kHz.
Użycie (z katalogu repo): python3 narzedzia/rolka_11_pauza.py test OUTDIR | full OUT.mp4
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "tiktok-sens", "narzedzia"))
from tt_base import *
from tt_klipy import Clip, music_bed, render_av, smooth
from PIL import ImageEnhance

TOTAL = 28.9
T_B, T_C, T_D, T_E = 5.4, 11.8, 18.0, 23.4
FREEZE_A = 2.0          # w scenie A nagranie zatrzymuje się (pauza)
RESUME_B = 7.0          # w scenie B film rusza dalej
CX = 510
IG_SAFE = (80, 250, 940, 1360)
CREAM = (248, 242, 232)
Q = {}
CL = {}


def cream_card(sprs, w=None, gap=6, pad=(52, 36), fill=CREAM, alpha=248, r=34, align="center"):
    w = w or max(s.width for s in sprs) + 2 * pad[0]
    h = sum(s.height for s in sprs) + gap * (len(sprs) - 1) + 2 * pad[1]
    c, m = card_sprite(w, h, r=r, fill=fill + (alpha,), shadow=(40, 30, 50, 70))
    y = m + pad[1]
    for s in sprs:
        x = m + (w - s.width) // 2 if align == "center" else m + pad[0]
        c.alpha_composite(s, (x, y))
        y += s.height + gap
    return c


# ---------- elementy odtwarzacza ----------
def pause_icon(d=230, play=False):
    im = Image.new("RGBA", (d + 40, d + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((20, 26, 20 + d, 26 + d), fill=(20, 30, 36, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    dr = ImageDraw.Draw(im)
    dr.ellipse((20, 20, 20 + d, 20 + d), fill=CREAM + (236,))
    c = 20 + d / 2
    if play:
        dr.polygon([(c - d * 0.13, c - d * 0.2), (c - d * 0.13, c + d * 0.2), (c + d * 0.21, c)], fill=LAVD + (255,))
    else:
        bw, bh = d * 0.11, d * 0.38
        for dx in (-d * 0.11, d * 0.11):
            dr.rounded_rectangle((c + dx - bw / 2, c - bh / 2, c + dx + bw / 2, c + bh / 2), 8, fill=INK + (255,))
    return im


def progress_bar(w, frac, dot=True):
    h = 64
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = h // 2
    d.rounded_rectangle((14, y - 7, w - 14, y + 7), 7, fill=(30, 52, 59, 50))
    x = 14 + (w - 28) * frac
    if frac > 0.01:
        d.rounded_rectangle((14, y - 7, x, y + 7), 7, fill=LAVD + (255,))
    if dot:
        d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=YEL + (255,), outline=INK + (255,), width=4)
    return im


def photo07(w):
    ph = Image.open(os.path.join(REPO, "fotos_maria", "07_estudio_fondo_negro_retrato_horizontal.jpg")).convert("RGB")
    c = ph.crop((440, 0, 1400, 800))  # twarz w całości z zapasem, ramiona; bez rozciągania
    h = int(w * c.height / c.width)   # tylko równomierne skalowanie
    c = c.resize((w, h), Image.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=255)
    fr, fm = card_sprite(w, h, r=36, fill=(12, 14, 16), shadow=(40, 30, 50, 90))
    fr.paste(c, (fm, fm), mask)
    ImageDraw.Draw(fr).rounded_rectangle((fm - 1, fm - 1, fm + w, fm + h), 37, outline=LAV + (255,), width=3)
    return fr


def prep():
    CL["a"] = Clip("coverr-a-woman-watching-tv-3282", 3.0, T_B + 0.5, x=0.15, zoom=(1.0, 1.04))
    CL["b"] = Clip("coverr-a-woman-watching-tv-3282", 8.0, T_C - T_B + 1.0, x=0.72, zoom=(1.0, 1.05))
    CL["d"] = Clip("coverr-a-woman-reading-a-book-and-giving-a-shy-smile-5951", 1.0, T_E - T_D + 1.0, x=0.5,
                   zoom=(1.06, 1.0))
    # A — hak
    a0 = text_sprite(["Przeczytaj powoli:"], font(B, 46), INK, pad=2)
    a1 = text_sprite([[("meno", INK), ("pauza", LAVD)]], font(XB, 128), INK, pad=4)
    Q["a_hook"] = cream_card([a0, a1], gap=0, pad=(60, 34))
    a2 = text_sprite([[("Pauza. ", INK), ("Nie stop.", LAVD)]], font(XB, 70), INK, pad=4)
    Q["a_sub"] = cream_card([a2], pad=(48, 22))
    Q["pause"] = pause_icon(230)
    Q["play"] = pause_icon(230, play=True)
    Q["pause_s"] = pause_icon(120)
    Q["play_s"] = pause_icon(120, play=True)
    # B — zwrot
    b1 = ["Pauza nie kończy filmu."]
    Q["b1"] = cream_card([text_sprite(b1, fit_font(b1, XB, 74, 780), INK, pad=2)])
    b2 = ["To chwila, żeby złapać oddech", "i zobaczyć, co dalej."]
    Q["b2"] = cream_card([text_sprite(b2, fit_font(b2, B, 50, 760), INK, gap=1.15, pad=2)], pad=(46, 28))
    b3a = text_sprite(["Jesteś w środku filmu,"], fit_font(["Jesteś w środku filmu,"], XB, 64, 760), INK, pad=2)
    b3b = text_sprite(["nie na napisach końcowych."], fit_font(["nie na napisach końcowych."], XB, 64, 760),
                      LAVD, pad=2)
    Q["b3_txt"] = (b3a, b3b)
    Q["bar_w"] = 760
    # C — ćwiczenie „naciśnij pauzę”
    c0 = text_sprite(["Ćwiczenie na dziś"], font(B, 44), LAVD, pad=2)
    c1 = text_sprite(["Naciśnij pauzę."], font(XB, 84), INK, pad=2)
    Q["c_head"] = cream_card([c0, c1], gap=0, pad=(56, 30))
    rows = [("1", ["Zatrzymaj się", "na 3 spokojne oddechy."]),
            ("2", ["Nazwij myśl: „Mam myśl,", "że to już koniec”."]),
            ("3", ["Zapytaj: co jeszcze", "jest prawdą?"])]
    for i, (n, ln) in enumerate(rows):
        tx = text_sprite(ln, fit_font(ln, B, 48, 600), INK, gap=1.12, align="left", pad=2)
        w, h = 820, max(tx.height + 60, 170)
        c, m = card_sprite(w, h, r=30, fill=WHITE + (246,), shadow=(40, 30, 50, 60))
        d = ImageDraw.Draw(c)
        d.ellipse((m + 34, m + h / 2 - 46, m + 126, m + h / 2 + 46), fill=LAVD + (255,))
        nn = text_sprite([n], font(XB, 52), WHITE, pad=0)
        c.alpha_composite(nn, (int(m + 80 - nn.width / 2), int(m + h / 2 - nn.height / 2 - 3)))
        c.alpha_composite(tx, (m + 160, int(m + (h - tx.height) / 2)))
        Q[f"c_row{i}"] = c
    cf = ["Myśl to nie fakt. Pauza daje wybór."]
    Q["c_foot"] = text_sprite(cf, fit_font(cf, M, 42, 780), INK, pad=4)
    # D — „Następny odcinek”
    dw = 820
    lab = pill("Następny odcinek", font(B, 34), WHITE, LAVD, padx=30, h=64)
    title = text_sprite(["Środek, nie koniec"], fit_font(["Środek, nie koniec"], XB, 88, dw - 100), INK, pad=2)
    sub = ["kurs dla kobiet w peri- i menopauzie"]
    sub = text_sprite(sub, fit_font(sub, M, 40, dw - 100), INK, pad=2)
    when = text_sprite([[("Premiera: ", INK), ("piątek, 4 grudnia", LAVD)]],
                       fit_font(["Premiera: piątek, 4 grudnia"], XB, 60, dw - 100), INK, pad=2)
    rr = ["6 spotkań · stacjonarnie w SENS", "ul. Dyrekcyjna 37/47, Wrocław",
          "psychoedukacja + ćwiczenia CBT w małej grupie"]
    rr = text_sprite(rr, fit_font(rr, M, 38, dw - 100), INK, gap=1.25, pad=2)
    sep = Image.new("RGBA", (dw - 120, 3), LAV + (255,))
    bar = progress_bar(dw - 120, 0.0, dot=False)
    Q["d_card"] = cream_card([lab, title, sub, sep, when, rr], w=dw, gap=14, pad=(50, 40))
    sm = ["To nie terapia grupowa.", "Objawy z ciała zawsze skonsultuj z lekarzem."]
    Q["d_small"] = cream_card([text_sprite(sm, fit_font(sm, M, 34, 720), INK, gap=1.22, pad=2)], pad=(40, 24),
                              alpha=240)
    # E — jasna karta końcowa
    Q["logo"] = asset("logo_poziom.png", 420)
    Q["e_photo"] = photo07(520)
    sg = ["dr Maria Siwa — psycholożka i psychodietetyczka,", "psychoterapeutka CBT w trakcie szkolenia"]
    Q["e_sig"] = text_sprite(sg, fit_font(sg, M, 34, 860), INK, gap=1.2, pad=6)
    Q["e_ke"] = text_sprite(["Każda emocja ma sens."], font(CV, 84), LAVD, pad=6)
    Q["e_btn"] = pill("Zapisy: senswroclaw.pl", font(B, 48), WHITE, LAVD, padx=56, h=116)
    ck = ["kurs „Środek, nie koniec” · start: piątek, 4 grudnia"]
    Q["e_course"] = text_sprite(ck, fit_font(ck, B, 36, 860), INK, pad=6)
    ft = ["SENS · ul. Dyrekcyjna 37/47, Wrocław", "senswroclaw.pl · @senswroclaw"]
    Q["e_www"] = text_sprite(ft, fit_font(ft, M, 34, 860), LAVD, gap=1.2, pad=6)


def paused(im, k):
    """wygląd stop-klatki: lekko mniej koloru i jaśniej (k 0..1)"""
    if k <= 0:
        return im
    g = ImageEnhance.Color(im.convert("RGB")).enhance(1 - 0.45 * k)
    g = Image.blend(g, Image.new("RGB", (W, H), CREAM), 0.12 * k)
    return g.convert("RGBA")


def shade_top(im, k=0.25):
    y = np.arange(H)[:, None].astype(np.float32)
    g = k * np.clip(1 - y / 1000, 0, 1) + 0.22 * np.clip((y - 1150) / 770, 0, 1)
    lay = np.zeros((H, W, 4), np.uint8)
    lay[..., :3] = (30, 40, 46)
    lay[..., 3] = np.repeat((np.clip(g, 0, 1) * 255).astype(np.uint8), W, 1)
    im.alpha_composite(Image.fromarray(lay, "RGBA"))


def scene_a(t):
    lt = min(t, FREEZE_A)
    im = CL["a"].frame(lt)
    k = ramp(t, FREEZE_A, 0.35)
    im = paused(im, k)
    shade_top(im, 0.2)
    paste(im, Q["a_hook"], CX, 440)  # od klatki 0
    # ikona pauzy — łagodne pojawienie się (bez skoków)
    a = ramp(t, FREEZE_A, 0.4)
    if a > 0:
        s = 0.86 + 0.14 * a
        ic = Q["pause"].resize((int(Q["pause"].width * s), int(Q["pause"].height * s)), Image.LANCZOS)
        paste(im, ic, CX, 960, a)
    b = ramp(t, 2.6, 0.45)
    paste(im, Q["a_sub"], CX, 1240 + 16 * (1 - b), b)
    return im


def scene_b(t):
    tt = t - T_B
    lt = 0.0 if t < RESUME_B else (t - RESUME_B)
    im = CL["b"].frame(lt)
    im = paused(im, 1 - ramp(t, RESUME_B, 0.5))
    shade_top(im, 0.22)
    # pauza → odtwarzanie
    pa = 1 - ramp(t, RESUME_B - 0.35, 0.35)
    paste(im, Q["pause_s"], CX, 900, pa)
    pl = ramp(t, RESUME_B - 0.1, 0.25) * (1 - ramp(t, RESUME_B + 0.6, 0.4))
    paste(im, Q["play_s"], CX, 900, pl)
    out = 1 - ramp(t, T_C - 0.4, 0.4)
    a = ramp(tt, 0.2, 0.45)
    paste(im, Q["b1"], CX, 420 + 18 * (1 - a), a * out)
    b = ramp(tt, 1.2, 0.45) * (1 - ramp(t, 9.0, 0.3))
    paste(im, Q["b2"], CX, 1180 + 18 * (1 - b), b * out)
    # pasek postępu: przesuwa się do połowy
    c = ramp(tt, 3.85, 0.45)
    if c > 0:
        frac = 0.5 * smooth((tt - 3.95) / 1.0)
        bar = progress_bar(Q["bar_w"], frac)
        b3a, b3b = Q["b3_txt"]
        mid = text_sprite(["środek"], font(B, 34), LAVD, pad=2)
        card = cream_card([b3a, b3b, bar, mid], w=860, gap=6, pad=(50, 30))
        paste(im, card, CX, 1180 + 18 * (1 - c), c * out)
    return im


def scene_c(t):
    tt = t - T_C
    base = CL["b"].frame(T_C - RESUME_B).filter(ImageFilter.GaussianBlur(16)).convert("RGB")
    base = Image.blend(base, Image.new("RGB", (W, H), CREAM), 0.62).convert("RGBA")
    im = base
    a = ramp(tt, 0.2, 0.45)
    paste(im, Q["c_head"], CX, 430 + 16 * (1 - a), a)
    for i in range(3):
        r = ramp(tt, 0.9 + 1.1 * i, 0.45)
        paste(im, Q[f"c_row{i}"], CX, 712 + i * 220 + 16 * (1 - r), r)
    f = ramp(tt, 4.2, 0.45)
    paste(im, Q["c_foot"], CX, 1335, f)
    return im


def scene_d(t):
    tt = t - T_D
    im = CL["d"].frame(tt).filter(ImageFilter.GaussianBlur(9))
    im = Image.blend(im.convert("RGB"), Image.new("RGB", (W, H), CREAM), 0.30).convert("RGBA")
    out = 1 - ramp(t, T_E - 0.3, 0.3)
    a = ramp(tt, 0.3, 0.5)
    paste(im, Q["d_card"], CX, 700 + 30 * (1 - a), a * out)
    b = ramp(tt, 1.8, 0.45)
    paste(im, Q["d_small"], CX, 1220 + 16 * (1 - b), b * out)
    return im


def scene_e(t):
    tt = t - T_E
    im = bg(LIGHT, t)
    items = [(Q["logo"], 330, 0.1), (Q["e_photo"], 625, 0.3), (Q["e_sig"], 910, 0.55), (Q["e_ke"], 1003, 0.75),
             (Q["e_btn"], 1110, 0.95), (Q["e_course"], 1206, 1.15), (Q["e_www"], 1286, 1.3)]
    for spr, y, t0 in items:
        a = ramp(tt, t0, 0.45)
        paste(im, spr, CX, y + 16 * (1 - a), a)
    return im


def frame(t):
    if t >= T_E:
        im = scene_e(t)
        if t - T_E < 0.9:
            im = Image.blend(scene_d(t), im, smooth((t - T_E) / 0.9))
        return im
    if t >= T_D:
        im = scene_d(t)
        if t - T_D < 0.9:
            im = Image.blend(scene_c(t), im, smooth((t - T_D) / 0.9))
        return im
    if t >= T_C:
        im = scene_c(t)
        if t - T_C < 0.9:
            im = Image.blend(scene_b(t), im, smooth((t - T_C) / 0.9))
        return im
    if t >= T_B:
        im = scene_b(t)
        if t - T_B < 0.4:
            im = Image.blend(scene_a(t), im, smooth((t - T_B) / 0.4))
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
        test_sheet([0.0, 1.0, 3.2, 5.0], f"{out}/s1.jpg")
        test_sheet([6.0, 7.5, 9.0, 10.5], f"{out}/s2.jpg")
        test_sheet([12.5, 16.0, 17.6, 19.5], f"{out}/s3.jpg")
        test_sheet([22.0, 23.8, 25.5, 28.5], f"{out}/s4.jpg")
        for t in [3.2, 10.0, 16.0, 21.5, 27.5]:
            frame(t).convert("RGB").save(f"{out}/f_{t}.jpg", quality=88)
    else:
        wav = sys.argv[2] + ".wav"
        music_bed(1081, 0.0, TOTAL, wav, fade_in=0.4, fade_out=2.2, lufs=-16.5)
        render_av(frame, TOTAL, sys.argv[2], wav)
        os.remove(wav)
