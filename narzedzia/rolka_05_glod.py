"""Rolka 05 — „Jesz wieczorem, choć nie jesteś głodna?” (format: notes / pismo odręczne + przeformułowanie CBT).

Pomysł: kartka w linie. Odręcznie: „Nie mam silnej woli.” → przekreślenie zakreślaczem → „Mam za sobą bardzo
długi dzień.” → „To często głód emocjonalny.” → kolejna kartka: tabela głód fizyczny / emocjonalny →
kolejna kartka: „Czego teraz naprawdę potrzebuję?” z polami do zaznaczenia → „Jeśli zjeść — zjedz. Bez kary.”
→ karta końcowa na ciemnej zieleni (psychodietetyka w SENS).
Kolory: papier kremowy, atrament petrol, lawendowy i żółty zakreślacz; koniec w zieleni SENS.
Muzyka: akustyczny pop 116 BPM (gitara akustyczna, pianino, bas palcowy, perkusja z klaskaniem, shaker).
Filar 2 — Jedzenie i ciało bez wstydu.

Użycie (z katalogu repo):  python3 narzedzia/rolka_05_glod.py test OUTDIR | full OUT.mp4
"""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tiktok-sens", "narzedzia"))
from tt_base import *
from tt_muzyka import Song, kick_beats
from pedalboard import Reverb, Compressor, HighpassFilter, LowpassFilter, Delay, Chorus

BPM = 116
BT = 60 / BPM
TOTAL = 60 * BT  # 31,0 s
T_STRIKE, T_RE, T_NOTE = 6 * BT, 8 * BT, 13 * BT
T_B, T_C, T_D = 20 * BT, 34 * BT, 46 * BT
IG_SAFE = (80, 250, 940, 1500)
CX = 510
PAPER = (250, 246, 238)
HL_Y = (254, 217, 14)
S = {}


def make_paper():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    for y in range(300, H, 86):
        d.line([(0, y), (W, y)], fill=(222, 214, 230), width=2)
    d.line([(150, 0), (150, H)], fill=(214, 170, 190), width=3)
    rng = np.random.default_rng(5)
    noise = rng.normal(0, 4, (H, W, 1)).astype(np.int16)
    a = np.clip(np.asarray(im).astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(a).convert("RGBA")


def hand(lines, size, color, maxw=800, rot=0):
    f = fit_font(lines, CV, size, maxw)
    s = text_sprite(lines, f, color, gap=1.05, pad=14)
    return s.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else s


def reveal(spr, p):
    """odsłanianie od lewej (jak pisanie)."""
    if p <= 0:
        return None
    if p >= 1:
        return spr
    w = int(spr.width * p)
    out = Image.new("RGBA", spr.size, (0, 0, 0, 0))
    out.alpha_composite(spr.crop((0, 0, max(1, w), spr.height)), (0, 0))
    return out


def highlighter(w, h, col, a=150):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(w)
    pts = [(0, h * 0.25), (w, h * 0.18), (w, h * 0.85), (0, h * 0.92)]
    d.polygon(pts, fill=col + (a,))
    return im.filter(ImageFilter.GaussianBlur(1.5))


def prep():
    S["paper"] = make_paper()
    S["tag"] = text_sprite(["wtorek, 21:30"], font(M, 34), LAVD, pad=6)
    S["hook"] = text_sprite(["Jesz wieczorem,", "choć nie jesteś głodna?"], fit_font(["choć nie jesteś głodna?"], XB, 82, 860),
                            INK, gap=1.08, pad=8)
    S["l1"] = hand(["Nie mam silnej woli."], 112, INK, 820, rot=1.5)
    S["l2"] = hand(["Mam za sobą", "bardzo długi dzień."], 108, LAVD, 820, rot=-1)
    nt = ["To nie brak silnej woli.", "To często głód emocjonalny."]
    S["note"] = text_sprite(nt, fit_font(nt, B, 52, 840), INK, gap=1.15, pad=8)
    S["note_hl"] = highlighter(int(font(B, 52).getlength("głód emocjonalny")) + 30, 64, HL_Y, 170)
    # tabela
    S["b_h"] = text_sprite(["Jak je odróżnić?"], font(XB, 72), INK, pad=8)
    S["colA"] = text_sprite(["GŁÓD", "FIZYCZNY"], font(XB, 44), GREEN, gap=1.0, pad=6)
    S["colB"] = text_sprite(["GŁÓD", "EMOCJONALNY"], font(XB, 44), LAVD, gap=1.0, pad=6)
    rows = [(["narasta", "stopniowo"], ["przychodzi", "nagle"]),
            (["zjesz różne", "rzeczy"], ["chcesz czegoś", "konkretnego"]),
            (["po jedzeniu", "mija"], ["często zostaje", "poczucie winy"])]
    S["rows"] = [(hand(a, 66, INK, 380), hand(b, 66, INK, 380)) for a, b in rows]
    S["b_foot"] = text_sprite(["To wskazówka, nie test diagnostyczny."], font(M, 34), INK, pad=6)
    # pytanie
    S["c_l"] = text_sprite(["Zanim sięgniesz po coś, zapytaj siebie:"], fit_font(["Zanim sięgniesz po coś, zapytaj siebie:"], M, 44, 800), INK, pad=6)
    S["c_q"] = hand(["Czego teraz", "naprawdę potrzebuję?"], 118, LAVD, 780)
    S["c_opts"] = [hand([o], 84, INK, 600) for o in ["odpocząć", "z kimś pogadać", "chwili ciszy", "zjeść"]]
    ft = ["Jeśli zjeść — zjedz.", "Bez kary i bez wstydu."]
    S["c_f"] = text_sprite(ft, fit_font(ft, XB, 60, 840), WHITE, gap=1.12, pad=0)
    # koniec
    S["logo"] = asset("logo_bialy.png", 280)
    S["d_h"] = text_sprite(["Jedzenie i emocje?", "Porozmawiajmy bez wstydu."], fit_font(["Porozmawiajmy bez wstydu."], XB, 70, 860),
                           WHITE, gap=1.1, pad=6)
    S["d_p"] = pill("Psychodietetyka w SENS", font(B, 50), INK, HL_Y, padx=56, h=118)
    S["d_s"] = text_sprite(["umów konsultację: senswroclaw.pl"], font(M, 42), LAVL, pad=6)
    S["d_cv"] = text_sprite(["Każda emocja ma sens."], font(CV, 86), WHITE, pad=6)
    S["d_w"] = text_sprite(["@senswroclaw · ul. Dyrekcyjna 37/47, Wrocław"], fit_font(["@senswroclaw · ul. Dyrekcyjna 37/47, Wrocław"], M, 38, 860), WHITE, pad=6)
    S["d_sig"] = text_sprite(["dr Maria Siwa — psycholożka i psychodietetyczka,", "psychoterapeutka CBT w trakcie szkolenia"],
                             font(M, 32), LAVL, gap=1.15, pad=6)


def paper(t):
    return S["paper"].copy()


def checkbox(im, x, y, size, ticked, a):
    d = ImageDraw.Draw(im)
    c = INK + (int(255 * a),)
    d.rounded_rectangle((x, y, x + size, y + size), 10, outline=c, width=6)
    if ticked > 0:
        p = ticked
        pts = [(x + 12, y + size * 0.5), (x + size * 0.42, y + size - 14), (x + size + 14, y - 10)]
        seg1 = min(1, p * 2)
        q = (pts[0][0] + (pts[1][0] - pts[0][0]) * seg1, pts[0][1] + (pts[1][1] - pts[0][1]) * seg1)
        d.line([pts[0], q], fill=LAVD + (255,), width=11)
        if p > 0.5:
            s2 = (p - 0.5) * 2
            r = (pts[1][0] + (pts[2][0] - pts[1][0]) * s2, pts[1][1] + (pts[2][1] - pts[1][1]) * s2)
            d.line([pts[1], r], fill=LAVD + (255,), width=11)


def scene_a(t):
    im = paper(t)
    paste(im, S["tag"], 790, 330)
    paste(im, S["hook"], CX, 500)
    # „Nie mam silnej woli.”
    l1 = reveal(S["l1"], (t - 0.25) / 1.0)
    y1 = 800
    if l1 is not None:
        paste(im, l1, CX, y1)
    # przekreślenie zakreślaczem
    p = ramp(t, T_STRIKE, 0.35)
    if p > 0:
        d = ImageDraw.Draw(im)
        x0, x1 = CX - S["l1"].width / 2 + 10, CX - S["l1"].width / 2 + 10 + (S["l1"].width - 20) * p
        d.line([(x0, y1 + 8), (x1, y1 - 4)], fill=LAVD + (255,), width=12)
    l2 = reveal(S["l2"], (t - T_RE) / 1.1)
    if l2 is not None:
        paste(im, l2, CX, 1040)
    a = ramp(t, T_NOTE, 0.45)
    if a > 0:
        hl = S["note_hl"]
        nx = CX + S["note"].width / 2 - 8 - hl.width
        k = ramp(t, T_NOTE + 0.5, 0.5)
        if k > 0:
            im.alpha_composite(hl.crop((0, 0, max(1, int(hl.width * k)), hl.height)), (int(nx), int(1340 - 10)))
        paste(im, S["note"], CX, 1310 + 16 * (1 - a), a)
    return im


def scene_b(t):
    im = paper(t)
    paste(im, S["b_h"], CX, 360, ramp(t, 0, 0.4))
    d = ImageDraw.Draw(im)
    a = ramp(t, 0.3, 0.4)
    xa, xb = 300, 730
    for x, spr, col in [(xa, S["colA"], (200, 228, 214)), (xb, S["colB"], (226, 212, 232))]:
        hl = highlighter(spr.width + 20, 120, col, 255)
        paste(im, hl, x, 520, a)
        paste(im, spr, x, 515, a)
    # linie tabeli rysowane
    p = ramp(t, 0.4, 0.6)
    if p > 0:
        d.line([(CX, 450), (CX, 450 + 820 * p)], fill=INK + (200,), width=4)
        d.line([(100, 612), (100 + 820 * p, 612)], fill=INK + (200,), width=4)
    for i, (ra, rb) in enumerate(S["rows"]):
        t0 = 0.9 + i * 0.95
        y = 740 + i * 220
        ga = reveal(ra, (t - t0) / 0.55)
        gb = reveal(rb, (t - t0 - 0.35) / 0.55)
        if ga is not None:
            paste(im, ga, xa, y)
        if gb is not None:
            paste(im, gb, xb, y)
    paste(im, S["b_foot"], CX, 1420, ramp(t, 4.2, 0.5))
    return im


def scene_c(t):
    im = paper(t)
    paste(im, S["c_l"], CX, 350, ramp(t, 0, 0.4))
    q = reveal(S["c_q"], (t - 0.15) / 1.0)
    if q is not None:
        paste(im, q, CX, 540)
    for i, o in enumerate(S["c_opts"]):
        t0 = 1.0 + i * 0.3
        a = ramp(t, t0, 0.3)
        y = 760 + i * 120
        checkbox(im, 250, y - 32, 64, ramp(t, 2.6, 0.45) if i == 3 else 0, a)
        paste(im, o, 350 + o.width / 2, y, a)
    a = ramp(t, 3.0, 0.45)
    if a > 0:
        f = S["c_f"]
        box = Image.new("RGBA", (f.width + 100, f.height + 70), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle((0, 0, box.width - 1, box.height - 1), 40, fill=GREEN + (255,))
        box.alpha_composite(f, (50, 32))
        paste(im, box, CX, 1340 + 18 * (1 - a), a)
    return im


DGBG = None


def scene_d(t):
    global DGBG
    if DGBG is None:
        from tt_base import _blobs
        DGBG = _blobs((0, 70, 60), [(200, 300, 520, (0, 92, 78)), (1100, 1100, 640, (20, 60, 66)),
                                    (300, 1900, 620, (0, 84, 71))], 170)
    im = bg(DGBG, T_D + t)
    items = [("logo", 400, 0.0), ("d_h", 690, 0.2), ("d_p", 900, 0.6), ("d_s", 1010, 0.8),
             ("d_cv", 1130, 1.1), ("d_w", 1235, 1.3), ("d_sig", 1355, 1.5)]
    for k, y, t0 in items:
        a = ramp(t, t0, 0.5)
        paste(im, S[k], CX, y + 18 * (1 - a), a)
    return im


def slide(a_im, b_im, p):
    """kartka odjeżdża w lewo, nowa wjeżdża z prawej."""
    e = ease(p)
    out = Image.new("RGBA", (W, H), (60, 50, 70, 255))
    out.alpha_composite(a_im, (int(-W * e), 0))
    out.alpha_composite(b_im, (int(W * (1 - e)), 0))
    return out


def frame(t):
    TR = 0.45
    if t < T_B:
        im = scene_a(t)
        if t > T_B - TR:
            im = slide(im, scene_b(0), (t - (T_B - TR)) / TR)
        return im
    if t < T_C:
        im = scene_b(t - T_B)
        if t > T_C - TR:
            im = slide(im, scene_c(0), (t - (T_C - TR)) / TR)
        return im
    if t < T_D:
        im = scene_c(t - T_C)
        if t > T_D - 0.5:
            im = Image.blend(im, scene_d(0), ramp(t, T_D - 0.5, 0.5))
        return im
    return scene_d(t - T_D)


# ---------------- muzyka: akustyczny pop 116 BPM ----------------
def music(path):
    s = Song(BPM, TOTAL)
    gt = s.track("gt", 0, 25)      # gitara akustyczna
    pn = s.track("pn", 0, 0)       # pianino
    bs = s.track("bass", 0, 33)    # bas palcowy
    ld = s.track("lead", 0, 0)     # pianino — motyw
    dr = s.drums(kit=0)            # Standard
    prog = [([48, 52, 55, 59, 62], 36), ([45, 52, 55, 60, 64], 45), ([41, 48, 53, 57, 64], 41), ([43, 50, 55, 59, 65], 43)]
    hook = [(0, 76), (0.5, 79), (1.0, 81), (1.5, 79), (2.5, 76), (3.0, 74), (3.5, 72)]
    strum = [0, 0.5, 0.75, 1.25, 1.5, 2.0, 2.5, 2.75, 3.25, 3.5]
    end_b = TOTAL / BT
    # intro: gitara + shaker + lekka stopa (beaty 0–6)
    for b0 in (0, 4):
        ch, root = prog[(b0 // 4) % 4]
        for off in strum:
            if b0 + off < 6:
                gt.chord(b0 + off, [n + 12 for n in ch[:4]], 0.3, 70 if off % 1 == 0 else 56, strum=0.012)
        for k in range(8):
            if b0 + k * 0.5 < 6:
                dr.hit(b0 + k * 0.5, 70, 54 if k % 2 else 40)
        dr.hit(b0, 36, 80)
    for k, b in enumerate([5, 5.25, 5.5, 5.75]):
        dr.hit(b, 38, 64 + k * 10)
    # groove od beatu 6
    b0, i = 6.0, 0
    while b0 < end_b - 0.01:
        ch, root = prog[i % 4]
        brk = 34 <= b0 < 46
        if b0 >= 54:
            gt.chord(b0, [n + 12 for n in ch[:4]], 4, 84, strum=0.03)
            pn.chord(b0, ch, 4, 80)
            bs.note(b0, root, 3, 90)
            dr.hit(b0, 49, 90)
            dr.hit(b0, 36, 100)
            break
        for off in strum:
            gt.chord(b0 + off, [n + 12 for n in ch[:4]], 0.3, (82 if off % 1 == 0 else 64) - (12 if brk else 0), strum=0.01)
        for e in range(4):
            pn.chord(b0 + e + 0.5, ch[1:], 0.35, 62 if not brk else 54)
        for off, oc, v in [(0, 0, 104), (1.5, 0, 86), (2.0, 7, 92), (3.0, 12, 82), (3.5, 0, 80)]:
            bs.note(b0 + off, root + oc, 0.45, v - (10 if brk else 0))
        if not brk and i % 2 == 1:
            for off, n in hook:
                ld.note(b0 + off, n, 0.4, 72)
        for b in range(4):
            tb = b0 + b
            if brk:
                if b in (0, 2):
                    dr.hit(tb, 36, 92 if b == 0 else 70)
                if b == 2:
                    dr.hit(tb, 39, 82)
            else:
                dr.hit(tb, 36, 108 if b % 2 == 0 else 80)
                if b % 2 == 1:
                    dr.hit(tb, 39, 104)
                    dr.hit(tb, 38, 70)
            for k in range(2):
                dr.hit(tb + k * 0.5, 70, 56)
                dr.hit(tb + k * 0.5 + 0.25, 70, 40)
            dr.hit(tb + 0.5, 42, 58)
        b0 += 4
        i += 1
    for stb in (6, 20, 46):
        dr.hit(stb, 49, 98)
        s.impact(stb, 0.35)
    s.riser(43, 3, 0.03)
    kicks = kick_beats(6, 34, every=2) + kick_beats(46, 54, every=2)
    s.render(path,
             gains={"gt": 0.42, "pn": 0.4, "bass": 0.8, "lead": 0.38, "drums": 0.85, "fx": 0.5,
                    "_duck": ("gt", "pn", "bass")},
             fx={"gt": [HighpassFilter(200), Reverb(room_size=0.35, wet_level=0.14)],
                 "pn": [HighpassFilter(160), Reverb(room_size=0.5, wet_level=0.2)],
                 "lead": [Delay(delay_seconds=BT * 0.75, feedback=0.25, mix=0.2), Reverb(room_size=0.6, wet_level=0.25)],
                 "bass": [LowpassFilter(1000), Compressor(threshold_db=-18, ratio=3)],
                 "drums": [Compressor(threshold_db=-14, ratio=2.2, attack_ms=5, release_ms=80)]},
             sidechain=kicks, duck=0.3, lowpass_until=(0, 6, 1800))


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
        test_sheet([0.0, 1.0, 4.0, 9.0], f"{out}/s1.jpg")
        test_sheet([10.2, 12.5, 16.5, 17.4], f"{out}/s2.jpg")
        test_sheet([18.6, 22.5, 24.0, 30.0], f"{out}/s3.jpg")
        for t in [0.0, 9.0, 16.5, 22.5, 30.0]:
            frame(t).convert("RGB").save(f"{out}/f_{t}.jpg", quality=88)
    elif sys.argv[1] == "music":
        music(sys.argv[2])
    else:
        wav = sys.argv[2] + ".wav"
        music(wav)
        render(frame, TOTAL, sys.argv[2], wav)
        os.remove(wav)
