"""Rolka 09 (v2, poprawka Rodriga 24.11: szybciej, przekreślenie „Ostatni” → żółta karteczka „Środkowy.”,
licznik „strona 186 z 372”, zdjęcie 07 studyjne) — „Środek, nie koniec”: ZAKŁADKA (kurs, start pt 4 grudnia 2026).

Koncept w jednym zdaniu: menopauza to nie „ostatni rozdział”, tylko zakładka w połowie książki —
a kolejne rozdziały to spis treści kursu.
Format: prawdziwe nagrania (książka, czytanie) + edytorski „spis treści” na kremowym papierze z lawendową
wstążką-zakładką. Estetyka: krem papieru + ciemny petrol + lawenda (bez żółtego — wczoraj dominował żółty/tablica).

Oś: 0–5 hak na nagraniu (kobieta czyta przy lampie) „Menopauza. Ostatni rozdział?” → 5–10 zwrot: wstążka
zjeżdża, „Nie. To zakładka w połowie książki.” + fakt (ok. 30 lat) → 10–19,6 spis treści = 5 tematów kursu
(psychoedukacja + ćwiczenia CBT, nie terapia grupowa, objawy fizyczne → lekarz) → 19,6–24,4 „Pierwsze spotkanie:
piątek, 4 grudnia”, 6 spotkań, adres → 24,4–29,5 karta końcowa ze zdjęciem 03 (petrolowa ściana).
Nagrania: Coverr (licencja Coverr: komercyjnie, bez atrybucji; bez premium/AI).
Muzyka: Mixkit „Walking in the Park” — Diego Nava (Mixkit Stock Music Free License): folk-pop, gitara akustyczna
+ bas, spokojny, ok. 86 BPM; tło −17 LUFS, low-pass 9,5 kHz.
Użycie (z katalogu repo): python3 narzedzia/rolka_09_zakladka.py test OUTDIR | full OUT.mp4
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "tiktok-sens", "narzedzia"))
from tt_base import *
from tt_klipy import Clip, music_bed, render_av, smooth

TOTAL = 24.5
T_B, T_C, T_D, T_E = 4.4, 8.4, 15.8, 19.4
CX = 510
IG_SAFE = (80, 250, 940, 1360)
PAPER = (248, 242, 232)
PAPER2 = (241, 233, 220)
Q = {}
XF = 0.35
SHOTS = [
    (0.0, T_B, dict(vid="coverr-a-woman-quietly-reading-a-book-near-a-lamp-at-home-8499", start=0.5, x=0.64,
                    zoom=(1.0, 1.06), dark=0.12)),
    (T_B, T_C + 0.8, dict(vid="coverr-businesswoman-turning-the-pages-of-a-marketing-book-450", start=4.0, x=0.55,
                          zoom=(1.04, 1.0), dark=0.12)),
    (T_D - 0.6, T_E + 0.2, dict(vid="coverr-a-woman-is-holding-a-cat-in-her-hands-461", start=0.0, x=0.36,
                                zoom=(1.0, 1.05), dark=0.1)),
]
CLIPS = []


def paper_card(sprs, w=None, gap=8, pad=(48, 34), alpha=250, r=30):
    w = w or max(s.width for s in sprs) + 2 * pad[0]
    h = sum(s.height for s in sprs) + gap * (len(sprs) - 1) + 2 * pad[1]
    c, m = card_sprite(w, h, r=r, fill=PAPER + (alpha,), shadow=(10, 20, 24, 80))
    y = m + pad[1]
    for s in sprs:
        c.alpha_composite(s, (m + (w - s.width) // 2, y))
        y += s.height + gap
    return c


def ribbon(length, w=74):
    """lawendowa wstążka-zakładka z wcięciem V na końcu"""
    im = Image.new("RGBA", (w, length), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(0, 0), (w, 0), (w, length), (w // 2, length - 34), (0, length)], fill=LAVD + (255,))
    d.line([(10, 0), (10, length - 30)], fill=(150, 112, 152, 255), width=3)
    d.line([(w - 10, 0), (w - 10, length - 30)], fill=(110, 72, 112, 255), width=3)
    sh = Image.new("RGBA", (w + 40, length + 40), (0, 0, 0, 0))
    sh.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, 0)), (20, 20))
    m = im.getchannel("A").point(lambda v: int(v * 0.35))
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 255))
    shadow.putalpha(m)
    sh.alpha_composite(shadow, (26, 24))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    sh.alpha_composite(im, (20, 20))
    return sh


def photo07(w):
    # zdjęcie „logo” Marii (studyjne, Rodrigo 24.11: tylko 06 i 07)
    ph = Image.open(os.path.join(REPO, "fotos_maria", "07_estudio_fondo_negro_retrato_horizontal.jpg")).convert("RGB")
    c = ph.crop((500, 10, 1240, 900))
    h = int(w * c.height / c.width)  # tylko równomierne skalowanie
    c = c.resize((w, h), Image.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), 40, fill=255)
    fr, fm = card_sprite(w, h, r=40, fill=(30, 52, 59), shadow=(20, 30, 40, 90))
    fr.paste(c, (fm, fm), mask)
    return fr


def build_page():
    """spis treści: kremowa strona 860x1080"""
    pw, ph = 860, 1120
    pg = Image.new("RGBA", (pw, ph), PAPER + (255,))
    d = ImageDraw.Draw(pg)
    # delikatna faktura: cień przy grzbiecie
    for i in range(40):
        d.line([(i, 0), (i, ph)], fill=tuple(int(a - (b - a) * 0) for a, b in zip(PAPER2, PAPER)) + (int(110 * (1 - i / 40)),))
    t1 = text_sprite(["„Środek, nie koniec”"], font(B, 38), LAVD, pad=0)
    pg.alpha_composite(t1, ((pw - t1.width) // 2, 70))
    t2 = text_sprite(["Spis treści"], font(XB, 96), INK, pad=0)
    pg.alpha_composite(t2, ((pw - t2.width) // 2, 128))
    d.line([(110, 278), (pw - 110, 278)], fill=LAV + (255,), width=3)
    rows = ["Uderzenia gorąca i stres", "Lęk i zmienność nastroju", "Sen i mgła mózgowa",
            "Ciało, jedzenie i metabolizm", "Wiek i ageizm"]
    f = fit_font(rows, B, 46, 600)
    Q["rows"] = []
    for i, r in enumerate(rows):
        im = Image.new("RGBA", (pw - 140, 112), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        dd.text((0, 14), f"{i + 1}", font=font(XB, 70), fill=LAVD)
        dd.text((96, 34), r, font=f, fill=INK)
        dd.line([(96, 108), (im.width, 108)], fill=(222, 210, 214, 255), width=2)
        Q["rows"].append(im)
    Q["page_note"] = text_sprite(["psychoedukacja + ćwiczenia CBT", "w małej grupie"], font(CV, 58), LAVD, gap=0.98, pad=4)
    sm = ["To nie terapia grupowa.", "Objawy fizyczne zawsze skonsultuj z lekarzem."]
    Q["page_small"] = text_sprite(sm, fit_font(sm, M, 30, 720), INK, gap=1.25, pad=4)
    Q["page"] = pg


def prep():
    for t0, t1, kw in SHOTS:
        kw = dict(kw)
        CLIPS.append((t0, t1, Clip(kw.pop("vid"), kw.pop("start"), t1 - t0 + XF + 0.1, **kw)))
    Q["a_small"] = text_sprite(["Menopauza."], font(B, 62), LAVD, pad=0)
    Q["a_big"] = text_sprite(["Ostatni rozdział?"], fit_font(["Ostatni rozdział?"], XB, 104, 760), INK, pad=4)
    Q["a_card"] = paper_card([Q["a_small"], Q["a_big"]], gap=4, pad=(56, 40))
    fb = fit_font(["Ostatni rozdział?"], XB, 104, 760)
    w = max(Q["a_small"].width, Q["a_big"].width) + 112
    bx = 70 + (w - Q["a_big"].width) // 2 + 4
    by = 70 + 40 + Q["a_small"].height + 4 + 4 + int(fb.getmetrics()[0] * 0.62)
    Q["strike"] = (bx - 8, bx + int(fb.getlength("Ostatni")) + 8, by)
    note = text_sprite(["Środkowy."], font(CV, 108), INK, pad=0)
    st = Image.new("RGBA", (note.width + 80, note.height + 46), YEL + (255,))
    st.alpha_composite(note, (40, 14))
    sh = Image.new("RGBA", (st.width + 60, st.height + 60), (0, 0, 0, 0))
    sm = Image.new("RGBA", st.size, (0, 0, 0, 90))
    sh.alpha_composite(sm, (34, 40)); sh = sh.filter(ImageFilter.GaussianBlur(10)); sh.alpha_composite(st, (30, 30))
    Q["sticky"] = sh.rotate(-4, resample=Image.BICUBIC, expand=True)
    Q["b_no"] = text_sprite(["Nie."], font(XB, 132), LAVD, pad=0)
    bl = ["To zakładka", "w połowie książki."]
    Q["b_txt"] = text_sprite(bl, fit_font(bl, XB, 84, 720), INK, gap=1.06, pad=2)
    Q["b_card"] = paper_card([Q["b_no"], Q["b_txt"]], gap=6, pad=(56, 40))
    fl = ["Po menopauzie żyjemy średnio", "jeszcze ok. 30 lat."]
    Q["b_fact"] = paper_card([text_sprite(fl, fit_font(fl, M, 44, 720), INK, gap=1.15, pad=2)], pad=(44, 28))
    Q["rib_b"] = ribbon(560)
    Q["rib_c"] = ribbon(300, 64)
    build_page()
    d1 = text_sprite(["Pierwsze spotkanie:"], font(B, 52), INK, pad=0)
    d2 = text_sprite(["piątek, 4 grudnia"], font(XB, 92), LAVD, pad=2)
    Q["d_card"] = paper_card([d1, d2], gap=6, pad=(56, 40))
    dl = ["6 spotkań · stacjonarnie w SENS", "ul. Dyrekcyjna 37/47, Wrocław"]
    Q["d_info"] = paper_card([text_sprite(dl, fit_font(dl, M, 42, 720), INK, gap=1.2, pad=2)], pad=(44, 28))
    # karta końcowa
    Q["e_photo"] = photo07(360)
    sg = ["dr Maria Siwa — psycholożka i psychodietetyczka,", "psychoterapeutka CBT w trakcie szkolenia"]
    Q["e_sig"] = text_sprite(sg, fit_font(sg, M, 34, 860), INK, gap=1.2, pad=6)
    Q["e_ke"] = text_sprite(["Każda emocja ma sens."], font(CV, 82), LAVD, pad=6)
    Q["e_btn"] = pill("Zapisy: senswroclaw.pl", font(B, 48), WHITE, LAVD, padx=56, h=120)
    ck = ["kurs „Środek, nie koniec” · start: piątek, 4 grudnia"]
    Q["e_course"] = text_sprite(ck, fit_font(ck, B, 38, 860), INK, pad=6)
    ft = ["SENS · ul. Dyrekcyjna 37/47, Wrocław · @senswroclaw"]
    Q["e_www"] = text_sprite(ft, fit_font(ft, M, 34, 860), INK, pad=6)
    Q["logo"] = asset("logo_poziom.png", 250)
    Q["bg"] = LIGHT


def video(t):
    act = [(i, c) for i, c in enumerate(CLIPS) if c[0] <= t]
    i, (t0, t1, c) = act[-1]
    im = c.frame(t - t0)
    if i > 0 and t - t0 < XF:
        p0, p1, pc = CLIPS[i - 1]
        im = Image.blend(pc.frame(t - p0), im, smooth((t - t0) / XF))
    return im.copy()


def shade(im, top=0.35, bottom=0.25):
    y = np.arange(H)[:, None].astype(np.float32)
    g = top * np.clip(1 - y / 900, 0, 1) + bottom * np.clip((y - 1200) / 720, 0, 1)
    lay = np.zeros((H, W, 4), np.uint8)
    lay[..., :3] = (14, 28, 32)
    lay[..., 3] = np.repeat((np.clip(g, 0, 1) * 255).astype(np.uint8), W, 1)
    im.alpha_composite(Image.fromarray(lay, "RGBA"))


def draw_page(im, t):
    """strona spisu treści; wjeżdża od dołu (jak przewracana kartka)"""
    tt = t - T_C
    s = smooth(tt / 0.7)
    pg = Q["page"].copy()
    for i, r in enumerate(Q["rows"]):
        a = ramp(tt, 0.7 + i * 0.45, 0.35)
        paste(pg, r, pg.width / 2 + 30 + 30 * (1 - a), 352 + i * 110, a)
    a = ramp(tt, 3.1, 0.45)
    paste(pg, Q["page_note"], pg.width / 2, 916, a)
    a = ramp(tt, 3.5, 0.45)
    paste(pg, Q["page_small"], pg.width / 2, 1066, a)
    fr, m = card_sprite(pg.width, pg.height, r=18, fill=PAPER, shadow=(0, 0, 0, 110))
    fr.paste(pg, (m, m))
    y = 805 + (1 - s) * 1300
    paste(im, fr, CX, y)
    # wstążka wisi z góry strony
    rib = Q["rib_c"]
    ry = y - pg.height / 2 - 50 + rib.height / 2 * smooth((tt - 0.5) / 0.6)
    paste(im, rib, CX + 336, ry, ramp(tt, 0.5, 0.3))


def frame(t):
    if t >= T_E:
        tt = t - T_E
        im = bg(Q["bg"], t)
        if tt < 0.9:
            im = Image.blend(video(t), im, smooth(tt / 0.9))
        items = [(Q["e_photo"], 475, 0.3), (Q["e_sig"], 795, 0.55), (Q["e_ke"], 895, 0.75), (Q["e_btn"], 1010, 0.95),
                 (Q["e_course"], 1112, 1.15), (Q["e_www"], 1176, 1.3), (Q["logo"], 1272, 1.45)]
        for spr, y, t0 in items:
            a = ramp(tt, t0, 0.45)
            paste(im, spr, CX, y + 18 * (1 - a), a)
        return im
    if T_C + 0.8 <= t < T_D - 0.6:
        im = bg(Q["bg"], t)
        draw_page(im, t)
        return im
    im = video(t)
    if t < T_B:
        shade(im)
        # hak widoczny od klatki 0
        a = 1 - ramp(t, T_B - 0.35, 0.35)
        card = Q["a_card"].copy()
        p = smooth((t - 1.7) / 0.45)
        if p > 0:
            x0, x1, y = Q["strike"]
            ImageDraw.Draw(card).line([(x0, y), (x0 + (x1 - x0) * p, y - 6 * p)], fill=LAVD + (255,), width=11)
        paste(im, card, CX, 470, a)
        k = smooth((t - 2.05) / 0.3)
        if k > 0:
            sc = 1.25 - 0.25 * k
            stc = Q["sticky"].resize((int(Q["sticky"].width * sc), int(Q["sticky"].height * sc)), Image.BICUBIC)
            paste(im, stc, CX + 60, 760, min(1, k * 1.3) * a)
        return im
    if t < T_C + 0.8:
        shade(im)
        tt = t - T_B
        out = 1 - ramp(t, T_C - 0.3, 0.3)
        # wstążka zjeżdża z góry
        rib = Q["rib_b"]
        ry = -rib.height / 2 + (rib.height * 0.95) * smooth(tt / 0.9)
        paste(im, rib, CX + 310, ry, out)
        a = ramp(tt, 0.35, 0.4) * out
        paste(im, Q["b_card"], CX - 30, 560 + 18 * (1 - a), a)
        f = ramp(tt, 0.8, 0.4) * out
        n = int(round(186 * smooth((tt - 1.0) / 1.2)))
        ctr = text_sprite([[("strona ", INK), (f"{n}", LAVD), (" z 372", INK)]], font(B, 52), INK, pad=2)
        paste(im, paper_card([ctr], w=520, pad=(40, 26)), CX, 1180 + 18 * (1 - f), f)
        if t >= T_C:
            draw_page(im, t)
        return im
    if t < T_D:  # przejście strona → nagranie (strona odjeżdża w górę)
        pass
    # D
    tt = t - T_D
    shade(im, 0.3, 0.3)
    if tt < 0:
        im2 = bg(Q["bg"], t)
        draw_page(im2, t)
        k = smooth((tt + 0.6) / 0.6)
        im = Image.blend(im2, im, k)
        return im
    out = 1 - ramp(t, T_E - 0.3, 0.3)
    a = ramp(tt, 0.1, 0.4)
    paste(im, Q["d_card"], CX, 480 + 18 * (1 - a), a)
    b = ramp(tt, 0.9, 0.4)
    paste(im, Q["d_info"], CX, 1150 + 18 * (1 - b), b)
    return im


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
        test_sheet([0.0, 1.9, 3.0, 6.5], f"{out}/s1.jpg")
        test_sheet([8.8, 11.0, 13.0, 15.5], f"{out}/s2.jpg")
        test_sheet([16.4, 18.5, 20.0, 23.5], f"{out}/s3.jpg")
        for t in [3.0, 6.5, 23.5]:
            frame(t).convert("RGB").save(f"{out}/f_{t}.jpg", quality=88)
    else:
        wav = sys.argv[2] + ".wav"
        music_bed(529, 0.0, TOTAL, wav, fade_in=0.3, fade_out=2.0, lufs=-17.0)
        render_av(frame, TOTAL, sys.argv[2], wav)
        os.remove(wav)
