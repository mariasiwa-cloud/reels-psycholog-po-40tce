"""Rolka 07 — „Jesz wieczorem, choć nie jesteś głodna?” — wersja z PRAWDZIWYMI nagraniami (poprawka Rodriga 23.11.2026:
mniej białych teł, więcej prawdziwych ludzi; teksty jak w rolce 05).

Koncept: wieczorne szukanie czegoś w szafce → karteczka „Nie mam silnej woli.” zostaje przekreślona i zamieniona na
„Mam za sobą bardzo długi dzień.” → „To często głód emocjonalny.” → karteczka z tabelą (fizyczny / emocjonalny) →
„Czego teraz naprawdę potrzebuję?” → kobieta z uśmiechem je kanapkę: „Jeśli zjeść — zjedz. Bez kary i bez wstydu.”
→ karta końcowa (psychodietetyka w SENS) na przyciemnionym nagraniu.
Nagrania: Coverr (licencja Coverr, bez premium/AI). Muzyka: Mixkit „A Special Feeling” — Michael Ramir C.
(Mixkit Stock Music Free License), pop, pogodny, 99 BPM.
Filar 2. Użycie (z katalogu repo): python3 narzedzia/rolka_07_glod_real.py test OUTDIR | full OUT.mp4
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tiktok-sens", "narzedzia"))
from tt_base import *
from tt_klipy import Clip, music_bed, render_av, smooth

TOTAL = 31.0
CX = 510
IG_SAFE = (80, 250, 940, 1500)
PAPER = (250, 246, 238)
S = {}

SHOTS = [  # (t0, t1, klip)
    (0.0, 3.6, dict(vid="coverr-woman-searching-cupboard-with-flashlight", start=2.0, x=0.5, zoom=(1.05, 1.12), dark=0.15,
                    grade="eq=brightness=0.06:contrast=1.02:saturation=0.9")),
    (3.6, 7.2, dict(vid="coverr-a-woman-working-on-her-computer-late-at-night-3699", start=1.0, x=0.66, zoom=(1.0, 1.06), dark=0.1)),
    (7.2, 10.8, dict(vid="coverr-eating-sweets-at-a-cafe-5445", start=3.0, x=0.5, zoom=(1.0, 1.05), dark=0.1)),
    (10.8, 14.4, dict(vid="coverr-picking-up-chocolate-candy-3074", start=1.0, x=0.3, zoom=(1.0, 1.06), dark=0.25)),
    (14.4, 18.0, dict(vid="coverr-a-woman-quietly-reading-a-book-near-a-lamp-at-home-8499", start=1.0, x=0.28, zoom=(1.0, 1.05), dark=0.25)),
    (18.0, 21.6, dict(vid="coverr-contemplative-woman-in-city", start=2.0, x=0.28, zoom=(1.0, 1.05), dark=0.15)),
    (21.6, 24.6, dict(vid="coverr-woman-eating-a-sandwich-8810", start=6.0, x=0.43, zoom=(1.0, 1.05))),
    (24.6, 31.0, dict(vid="coverr-a-woman-smelling-and-tasting-an-aromatic-coffee-3726", start=1.0, x=0.76, zoom=(1.0, 1.06), dark=0.4)),
]
CLIPS = []
XF = 0.3  # przenikanie


def paper_note(spr, rot=0.0, padx=50, pady=30, lines=True):
    w, h = spr.width + 2 * padx, spr.height + 2 * pady
    m = 50
    im = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((m + 6, m + 16, m + w + 6, m + h + 16), fill=(0, 0, 0, 110))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(im)
    d.rectangle((m, m, m + w, m + h), fill=PAPER + (255,))
    if lines:
        for y in range(m + 70, m + h, 70):
            d.line([(m, y), (m + w, y)], fill=(224, 216, 232, 255), width=2)
        d.line([(m + 34, m), (m + 34, m + h)], fill=(220, 178, 196, 255), width=3)
    im.alpha_composite(spr, (m + padx, m + pady))
    return im.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else im


def white_card(lines, fnt, fg=INK, w=None, pad=(46, 30), alpha=245):
    tx = text_sprite(lines, fnt, fg, gap=1.1, pad=0)
    cw, ch = w or tx.width + 2 * pad[0], tx.height + 2 * pad[1]
    c, m = card_sprite(cw, ch, r=36, fill=WHITE + (alpha,), shadow=(0, 0, 0, 90))
    c.alpha_composite(tx, (m + (cw - tx.width) // 2, m + pad[1] - 4))
    return c


def hand(lines, size, color, maxw):
    return text_sprite(lines, fit_font(lines, CV, size, maxw), color, gap=1.02, pad=6)


def reveal(spr, p):
    if p <= 0:
        return None
    if p >= 1:
        return spr
    out = Image.new("RGBA", spr.size, (0, 0, 0, 0))
    out.alpha_composite(spr.crop((0, 0, max(1, int(spr.width * p)), spr.height)))
    return out


def prep():
    for t0, t1, kw in SHOTS:
        kw = dict(kw)
        CLIPS.append((t0, t1, Clip(kw.pop("vid"), kw.pop("start"), t1 - t0 + XF + 0.05, **kw)))
    hk = ["Jesz wieczorem,", "choć nie jesteś głodna?"]
    S["hook"] = white_card(hk, fit_font(hk, XB, 74, 800), INK)
    S["n1_txt"] = hand(["Nie mam silnej woli."], 100, INK, 720)
    S["n1"] = paper_note(S["n1_txt"], rot=2.0, lines=False)
    S["n2"] = paper_note(hand(["Mam za sobą", "bardzo długi dzień."], 96, LAVD, 720), rot=-2.0, lines=False)
    nt = [[("To nie brak silnej woli.", INK)], [("To często ", INK), ("głód emocjonalny.", LAVD)]]
    S["twist"] = white_card(nt, fit_font(["To często głód emocjonalny."], XB, 64, 800), INK)
    # tabela na karteczce
    tb = Image.new("RGBA", (860, 900), (0, 0, 0, 0))
    S["tab_bg"] = tb
    S["t_h"] = text_sprite(["Jak je odróżnić?"], font(XB, 66), INK, pad=4)
    S["colA"] = text_sprite(["GŁÓD", "FIZYCZNY"], font(XB, 40), GREEN, gap=1.0, pad=4)
    S["colB"] = text_sprite(["GŁÓD", "EMOCJONALNY"], font(XB, 40), LAVD, gap=1.0, pad=4)
    rows = [(["narasta", "stopniowo"], ["przychodzi", "nagle"]),
            (["zjesz różne", "rzeczy"], ["chcesz czegoś", "konkretnego"]),
            (["po jedzeniu", "mija"], ["często zostaje", "poczucie winy"])]
    S["rows"] = [(hand(a, 62, INK, 360), hand(b, 62, INK, 360)) for a, b in rows]
    S["t_foot"] = text_sprite(["To wskazówka, nie test diagnostyczny."], font(M, 32), INK, pad=4)
    # pytanie
    S["q_l"] = text_sprite(["Zanim sięgniesz po coś, zapytaj siebie:"], fit_font(["Zanim sięgniesz po coś, zapytaj siebie:"], M, 40, 760), INK, pad=4)
    S["q"] = hand(["Czego teraz", "naprawdę potrzebuję?"], 104, LAVD, 740)
    S["opts"] = [hand([o], 76, INK, 520) for o in ["odpocząć", "z kimś pogadać", "chwili ciszy", "zjeść"]]
    ft = ["Jeśli zjeść — zjedz.", "Bez kary i bez wstydu."]
    f = text_sprite(ft, fit_font(ft, XB, 66, 800), WHITE, gap=1.1, pad=0)
    box = Image.new("RGBA", (f.width + 110, f.height + 80), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((0, 0, box.width - 1, box.height - 1), 40, fill=GREEN + (245,))
    box.alpha_composite(f, (55, 36))
    S["eat"] = box
    # koniec
    S["logo"] = asset("logo_bialy.png", 280)
    dh = ["Jedzenie i emocje?", "Porozmawiajmy bez wstydu."]
    S["d_h"] = text_sprite(dh, fit_font(dh, XB, 70, 860), WHITE, gap=1.1, pad=6)
    S["d_p"] = pill("Psychodietetyka w SENS", font(B, 50), INK, YEL, padx=56, h=118)
    S["d_s"] = text_sprite(["umów konsultację: senswroclaw.pl"], font(M, 42), WHITE, pad=6)
    S["d_cv"] = text_sprite(["Każda emocja ma sens."], font(CV, 86), WHITE, pad=6)
    a = "@senswroclaw · ul. Dyrekcyjna 37/47, Wrocław"
    S["d_w"] = text_sprite([a], fit_font([a], M, 38, 860), WHITE, pad=6)
    S["d_sig"] = text_sprite(["dr Maria Siwa — psycholożka i psychodietetyczka,", "psychoterapeutka CBT w trakcie szkolenia"],
                             font(M, 32), LAVL, gap=1.15, pad=6)


def video(t):
    cur = None
    for i, (t0, t1, c) in enumerate(CLIPS):
        if t0 <= t < t1 or (i == len(CLIPS) - 1 and t >= t0):
            cur = i
    t0, t1, c = CLIPS[cur]
    im = c.frame(t - t0)
    if cur > 0 and t - t0 < XF:  # przenikanie z poprzedniego
        p0, p1, pc = CLIPS[cur - 1]
        im = Image.blend(pc.frame(t - p0), im, smooth((t - t0) / XF))
    return im.copy()


def shade(im, top=0.0, bottom=0.0):
    """ciemny gradient u góry/dołu dla czytelności"""
    if top <= 0 and bottom <= 0:
        return
    g = np.zeros((H, 1), np.float32)
    y = np.arange(H)[:, None]
    g += top * np.clip(1 - y / 700, 0, 1)
    g += bottom * np.clip((y - 1100) / 820, 0, 1)
    a = (np.clip(g, 0, 1) * 255).astype(np.uint8)
    lay = np.zeros((H, W, 4), np.uint8)
    lay[..., :3] = (10, 24, 28)
    lay[..., 3] = np.repeat(a, W, 1)
    im.alpha_composite(Image.fromarray(lay, "RGBA"))


def checkbox(im, x, y, size, ticked, a):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, y, x + size, y + size), 10, outline=INK + (int(255 * a),), width=6)
    if ticked > 0:
        pts = [(x + 12, y + size * 0.5), (x + size * 0.42, y + size - 14), (x + size + 14, y - 10)]
        s1 = min(1, ticked * 2)
        d.line([pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * s1, pts[0][1] + (pts[1][1] - pts[0][1]) * s1)], fill=LAVD + (255,), width=11)
        if ticked > 0.5:
            s2 = (ticked - 0.5) * 2
            d.line([pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * s2, pts[1][1] + (pts[2][1] - pts[1][1]) * s2)], fill=LAVD + (255,), width=11)


def paper_panel(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((30, 46, w - 24, h - 14), fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(im)
    d.rectangle((24, 24, w - 30, h - 36), fill=PAPER + (250,))
    for y in range(110, h - 40, 74):
        d.line([(24, y), (w - 30, y)], fill=(226, 218, 234, 255), width=2)
    d.line([(70, 24), (70, h - 36)], fill=(220, 178, 196, 255), width=3)
    return im


def frame(t):
    im = video(t)
    if t < 7.2:
        shade(im, top=0.55, bottom=0.25)
        a = 1 - ramp(t, 6.9, 0.3)
        paste(im, S["hook"], CX, 430, a)
        n1 = S["n1"]
        p = ramp(t, 0.2, 0.9)
        if p > 0:
            nn = n1.copy()
            if p < 1:  # pisanie: odsłanianie tekstu
                nn = paper_note(reveal(S["n1_txt"], p) or Image.new("RGBA", S["n1_txt"].size), rot=2.0, lines=False)
            st = ramp(t, 3.0, 0.35)
            if st > 0:
                d = ImageDraw.Draw(nn)
                y0 = nn.height / 2
                d.line([(70, y0 + 10), (70 + (nn.width - 140) * st, y0 - 6)], fill=LAVD + (255,), width=12)
            paste(im, nn, CX, 900, ramp(t, 0.0, 0.25) * a)
        b = ramp(t, 3.8, 0.4)
        if b > 0:
            paste(im, S["n2"], CX + 10, 1190 + 20 * (1 - b), b * a)
    elif t < 10.8:
        tt = t - 7.2
        shade(im, bottom=0.45)
        a = ramp(tt, 0.1, 0.4) * (1 - ramp(t, 10.5, 0.3))
        paste(im, S["twist"], CX, 1180 + 18 * (1 - a), a)
    elif t < 18.0:
        tt = t - 10.8
        a = ramp(tt, 0.0, 0.4) * (1 - ramp(t, 17.7, 0.3))
        pan = paper_panel(900, 1080)
        paste(pan, S["t_h"], 465, 120)
        d = ImageDraw.Draw(pan)
        xa, xb = 270, 650
        for x, spr, col in [(xa, S["colA"], (200, 228, 214)), (xb, S["colB"], (226, 212, 232))]:
            ImageDraw.Draw(pan).rectangle((x - spr.width / 2 - 8, 215, x + spr.width / 2 + 8, 320), fill=col + (255,))
            paste(pan, spr, x, 268)
        p = ramp(tt, 0.4, 0.6)
        d.line([(460, 200), (460, 200 + 720 * p)], fill=INK + (200,), width=4)
        d.line([(90, 345), (90 + 760 * p, 345)], fill=INK + (200,), width=4)
        for i, (ra, rb) in enumerate(S["rows"]):
            t0 = 0.8 + i * 0.9
            y = 450 + i * 185
            ga, gb = reveal(ra, (tt - t0) / 0.5), reveal(rb, (tt - t0 - 0.3) / 0.5)
            if ga is not None:
                paste(pan, ga, xa, y)
            if gb is not None:
                paste(pan, gb, xb, y)
        paste(pan, S["t_foot"], 465, 990, ramp(tt, 3.8, 0.4))
        pan = pan.resize((int(pan.width * 0.86), int(pan.height * 0.86)), Image.LANCZOS)
        paste(im, pan, CX, 960 + 20 * (1 - a), a)
    elif t < 21.6:
        tt = t - 18.0
        a = ramp(tt, 0.0, 0.4) * (1 - ramp(t, 21.3, 0.3))
        pan = paper_panel(900, 960)
        paste(pan, S["q_l"], 470, 110)
        q = reveal(S["q"], (tt - 0.1) / 0.9)
        if q is not None:
            paste(pan, q, 470, 270)
        for i, o in enumerate(S["opts"]):
            oa = ramp(tt, 0.8 + i * 0.25, 0.3)
            y = 480 + i * 112
            checkbox(pan, 190, y - 30, 60, ramp(tt, 2.2, 0.45) if i == 3 else 0, oa)
            paste(pan, o, 285 + o.width / 2, y, oa)
        pan = pan.resize((int(pan.width * 0.86), int(pan.height * 0.86)), Image.LANCZOS)
        paste(im, pan, CX, 990 + 20 * (1 - a), a)
    elif t < 24.6:
        tt = t - 21.6
        shade(im, bottom=0.35)
        a = ramp(tt, 0.15, 0.4) * (1 - ramp(t, 24.3, 0.3))
        paste(im, S["eat"], CX, 1260 + 18 * (1 - a), a)
    else:
        tt = t - 24.6
        ov = Image.new("RGBA", (W, H), (0, 70, 60, int(80 * ramp(tt, 0, 0.4))))
        im.alpha_composite(ov)
        items = [("logo", 420, 0.0), ("d_h", 700, 0.2), ("d_p", 905, 0.6), ("d_s", 1010, 0.8),
                 ("d_cv", 1130, 1.1), ("d_w", 1235, 1.3), ("d_sig", 1350, 1.5)]
        for k, y, t0 in items:
            a = ramp(tt, t0, 0.5)
            paste(im, S[k], CX, y + 18 * (1 - a), a)
    return im


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
        test_sheet([0.1, 1.5, 3.5, 5.5], f"{out}/s1.jpg")
        test_sheet([8.5, 11.0, 14.5, 17.0], f"{out}/s2.jpg")
        test_sheet([18.5, 21.0, 23.0, 30.0], f"{out}/s3.jpg")
        for t in [5.5, 14.5, 21.0, 23.0, 30.0]:
            frame(t).convert("RGB").save(f"{out}/f_{t}.jpg", quality=88)
    else:
        wav = sys.argv[2] + ".wav"
        music_bed(1087, 30.0, TOTAL, wav, fade_in=0.3, lufs=-15.5, lowpass=12000, shelf_db=-1.0)
        render_av(frame, TOTAL, sys.argv[2], wav)
        os.remove(wav)
