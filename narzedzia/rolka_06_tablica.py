"""Rolka 06 — „Środek, nie koniec” jako tablica odjazdów (format: tablica dworcowa / split-flap).

Pomysł: SENS jest tuż przy Dworcu Głównym we Wrocławiu. Tablica odjazdów pokazuje kierunek
„STACJA KOŃCOWA” przy słowie „Menopauza” — klapki przeskakują na „ŚRODEK TRASY” (zwrot ~1/3),
pod tablicą linia trasy z punktem „Jesteś tutaj” pośrodku. Potem „przystanki” = 5 tematów kursu,
„odjazd” = piątek 4 grudnia, ul. Dyrekcyjna 37/47 przy Dworcu Głównym, karta końcowa ze zdjęciem
Marii (04, fioletowa bluzka, kremowa ściana) i podpisem.
Kolory: ciepły krem + ciemny petrol tablicy, żółte akcenty „dworcowe”; koniec w jasnej lawendzie.
Muzyka: akustyczny indie-folk 80 BPM — gitara nylonowa fingerpicking, miękkie pianino, kontrabas,
perkusja szczotkowa (bank GeneralUser GS, prawdziwe sample). Bez riserów i uderzeń. Muzyka −17 LUFS.
Strefa tekstu wspólna dla IG i TikToka: x 80–940, y 250–1360 (rolka idzie też na TikTok/IG SENS).

Użycie (z katalogu repo):  python3 narzedzia/rolka_06_tablica.py test OUTDIR | full OUT.mp4
"""
import sys, os, random, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tiktok-sens", "narzedzia"))
from tt_base import *
from tt_muzyka import Song
from pedalboard import Reverb, Compressor, HighpassFilter, LowpassFilter

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BPM = 80
BT = 60 / BPM
T_FLIP = 6 * BT          # 4,5 s — zwrot
T_C = 14 * BT            # 10,5 s — przystanki
T_D = 26 * BT            # 19,5 s — odjazd
T_E = 33 * BT            # 24,75 s — karta końcowa
TOTAL = 42 * BT          # 31,5 s
SAFE2 = (80, 250, 940, 1360)
CX = 510
CREAM = (250, 245, 236)
BOARD, CELL, CELL2 = (30, 52, 59), (38, 66, 74), (33, 58, 66)
FLAPTXT = (246, 238, 222)
S = {}
NCELL, CW, CH, CG = 14, 57, 108, 4


def blobs(base, spots, blur):
    im = Image.new("RGB", (W + 240, H + 240), base)
    d = ImageDraw.Draw(im)
    for x, y, r, c in spots:
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    return im.filter(ImageFilter.GaussianBlur(blur))


BG_CREAM = blobs(CREAM, [(200, 300, 520, (244, 234, 222)), (1150, 1000, 620, (238, 228, 238)),
                         (250, 1900, 600, (236, 226, 236)), (1100, 2000, 420, (247, 238, 214))], 170)
BG_LAV = blobs(BG, [(180, 320, 520, (232, 220, 236)), (1150, 900, 600, (238, 228, 242)),
                    (300, 1900, 640, (228, 214, 233)), (1100, 2050, 380, (243, 236, 226))], 170)


def bgf(img, gt):
    ox = 120 + 90 * math.sin(gt * 0.10)
    oy = 120 + 90 * math.cos(gt * 0.08)
    return img.crop((int(ox), int(oy), int(ox) + W, int(oy) + H)).convert("RGBA")


# ---------- tablica ----------
FF = None
CHARS = "ABCDEFGHIJKLMNOPRSTUWZĄĘŚŻŃ0123456789"


def cell_img(ch, squash=1.0):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, CW - 1, CH - 1), 7, fill=CELL + (255,))
    d.rectangle((0, CH // 2, CW - 1, CH - 1), fill=CELL2 + (255,))
    if ch.strip():
        g = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((CW / 2, CH / 2), ch, font=FF, fill=FLAPTXT, anchor="mm")
        if squash < 0.999:
            h2 = max(1, int(CH * squash))
            g = g.resize((CW, h2), Image.BICUBIC)
        im.alpha_composite(g, (0, (CH - g.height) // 2))
    d.line((0, CH // 2, CW, CH // 2), fill=(18, 32, 36, 200), width=2)
    return im


CELLCACHE = {}


def cell(ch, sq=1.0):
    k = (ch, round(sq, 2))
    if k not in CELLCACHE:
        CELLCACHE[k] = cell_img(ch, sq)
    return CELLCACHE[k]


def flap_row(old, new, t, t0, step=0.085, nsteps=4, stagger=0.05):
    """wiersz klapek: old -> new od czasu t0, każda klapka z małym opóźnieniem."""
    old, new = old.ljust(NCELL), new.ljust(NCELL)
    row = Image.new("RGBA", (NCELL * (CW + CG) - CG, CH), (0, 0, 0, 0))
    for i in range(NCELL):
        ts = t - (t0 + i * stagger)
        if old[i] == new[i] or ts < 0:
            ch, sq = old[i], 1.0
        else:
            k = int(ts / step)
            if k >= nsteps:
                ch, sq = new[i], 1.0
                if k == nsteps:  # ostatnie domknięcie
                    p = (ts - k * step) / step
                    sq = 0.35 + 0.65 * p
            else:
                rnd = random.Random(i * 31 + k)
                ch = rnd.choice(CHARS) if new[i] != " " or k < nsteps - 1 else " "
                p = (ts - k * step) / step
                sq = max(0.15, abs(1 - 2 * p))
        row.alpha_composite(cell(ch, sq), (i * (CW + CG), 0))
    return row


def board_panel(w, h):
    im, m = card_sprite(w, h, r=30, fill=BOARD, shadow=(40, 40, 50, 70))
    return im


def prep():
    global FF
    FF = font(B, 60)
    S["panel"] = board_panel(860, 250)
    S["k_lab"] = text_sprite(["KIERUNEK"], font(M, 30), LAVL, pad=4)
    S["peron"] = text_sprite(["PERON 40+"], font(B, 30), YEL, pad=4)
    S["men"] = text_sprite(["Menopauza"], font(B, 40), FLAPTXT, pad=4)
    hk = ["Menopauza", "to stacja końcowa?"]
    S["hook"] = text_sprite(hk, fit_font(hk, XB, 92, 860), INK, gap=1.08, pad=8)
    S["hook_s"] = text_sprite(["Tak często się o niej mówi."], font(M, 46), LAVD, pad=6)
    tw = ["To nie koniec.", "To środek trasy."]
    S["twist"] = text_sprite([[("To nie koniec.", INK)], [("To ", INK), ("środek", LAVD), (" trasy.", INK)]],
                             fit_font(tw, XB, 92, 860), INK, gap=1.08, pad=8)
    sub = ["Ciało i emocje się zmieniają.", "Da się to zrozumieć — i z tym pracować."]
    S["twist_s"] = text_sprite(sub, fit_font(sub, M, 44, 850), INK, gap=1.2, pad=6)
    S["here"] = pill("Jesteś tutaj", font(B, 36), WHITE, LAVD, padx=34, h=72)
    S["r_a"] = text_sprite(["40+"], font(M, 30), LAVD, pad=4)
    S["r_b"] = text_sprite(["dalej…"], font(M, 30), LAVD, pad=4)
    # przystanki
    S["c_h"] = text_sprite(["Przystanki kursu"], font(XB, 84), INK, pad=6)
    S["c_h2"] = text_sprite(["„Środek, nie koniec”"], font(CV, 82), LAVD, pad=6)
    S["c_panel"] = board_panel(860, 650)
    topics = ["Uderzenia gorąca i stres", "Lęk i zmienność nastroju", "Sen i mgła mózgowa",
              "Ciało, jedzenie, metabolizm", "Wiek i ageizm"]
    tf = fit_font(topics, B, 46, 640)
    for i, tp in enumerate(topics):
        row = Image.new("RGBA", (820, 112), (0, 0, 0, 0))
        d = ImageDraw.Draw(row)
        d.rounded_rectangle((0, 0, 819, 111), 12, fill=CELL + (255,))
        d.rounded_rectangle((14, 14, 98, 97), 10, fill=YEL + (255,))
        n = text_sprite([str(i + 1)], font(XB, 52), BOARD, pad=0)
        row.alpha_composite(n, (56 - n.width // 2, 56 - n.height // 2 - 4))
        tx = text_sprite([tp], tf, FLAPTXT, pad=0)
        row.alpha_composite(tx, (128, 56 - tx.height // 2 - 4))
        S[f"t{i}"] = row
    cl = ["6 spotkań · psychoedukacja", "+ ćwiczenia CBT w małej grupie"]
    S["c_f"] = text_sprite(cl, fit_font(cl, M, 42, 840), INK, gap=1.15, pad=6)
    # odjazd
    S["d_h"] = text_sprite(["Pierwszy odjazd"], font(XB, 88), INK, pad=6)
    S["d_panel"] = board_panel(860, 250)
    S["d_lab"] = text_sprite(["START KURSU"], font(M, 30), LAVL, pad=4)
    S["d_lab2"] = text_sprite(["SENS"], font(B, 30), YEL, pad=4)
    c, m = card_sprite(860, 250, r=40)
    S["d_card"] = c
    a1 = text_sprite(["SENS, ul. Dyrekcyjna 37/47"], font(B, 50), INK, pad=0)
    a2 = text_sprite(["Wrocław — tuż przy Dworcu Głównym"], font(M, 42), LAVD, pad=0)
    S["d_a1"], S["d_a2"] = a1, a2
    nl = ["To nie terapia grupowa.", "Objawy z ciała zawsze skonsultuj z lekarzem."]
    S["d_note"] = text_sprite(nl, fit_font(nl, M, 38, 840), INK, gap=1.2, pad=6)
    # karta końcowa
    ph = Image.open(os.path.join(REPO, "fotos_maria", "04_blusa_morada_fondo_crema.jpg")).convert("RGB")
    # wycinek z całą twarzą (tylko równomierne skalowanie)
    crop = ph.crop((70, 180, 70 + 760, 180 + 880))
    pw, phh = 380, int(380 * 880 / 760)
    crop = crop.resize((pw, phh), Image.LANCZOS)
    mask = Image.new("L", (pw, phh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw - 1, phh - 1), 40, fill=255)
    fr, fm = card_sprite(pw, phh, r=40)
    fr.paste(crop, (fm, fm), mask)
    S["photo"] = fr
    sg = ["dr Maria Siwa — psycholożka i psychodietetyczka,", "psychoterapeutka CBT w trakcie szkolenia"]
    S["e_sig"] = text_sprite(sg, fit_font(sg, M, 34, 860), INK, gap=1.2, pad=6)
    S["e_ke"] = text_sprite(["Każda emocja ma sens."], font(CV, 82), LAVD, pad=6)
    tx = text_sprite([[("Napisz ", WHITE), ("ŚRODEK", YEL), (" w wiadomości", WHITE)]], font(B, 48), WHITE, pad=0)
    btn = Image.new("RGBA", (tx.width + 100, 120), (0, 0, 0, 0))
    ImageDraw.Draw(btn).rounded_rectangle((0, 0, btn.width - 1, 119), 60, fill=LAVD + (255,))
    btn.alpha_composite(tx, (50, (120 - tx.height) // 2 - 3))
    S["e_btn"] = btn
    ck = ["kurs „Środek, nie koniec” · start: piątek, 4 grudnia"]
    S["e_course"] = text_sprite(ck, fit_font(ck, B, 38, 860), INK, pad=6)
    S["e_www"] = text_sprite(["senswroclaw.pl · @senswroclaw"], font(B, 42), INK, pad=6)
    S["logo"] = asset("logo_poziom.png", 250)


def draw_route(im, t, a, cy=1080, lc=None):
    lc = lc or BOARD
    """linia trasy z punktem „Jesteś tutaj” pośrodku."""
    if a <= 0:
        return
    lay = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    y = 170
    p = ramp(t, 0, 0.9)
    x0, x1 = 150, 870
    xe = x0 + (x1 - x0) * p
    d.line((x0, y, xe, y), fill=lc + (255,), width=10)
    for x in (x0, x1):
        if x <= xe + 1:
            d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=CREAM + (255,), outline=lc + (255,), width=8)
    q = ramp(t, 0.6, 0.5)
    if q > 0:
        r = 26
        d.ellipse((CX - r, y - r, CX + r, y + r), fill=LAVD + (int(255 * q),))
        d.ellipse((CX - 10, y - 10, CX + 10, y + 10), fill=WHITE + (int(255 * q),))
    paste(lay, S["r_a"], x0, y + 50, ramp(t, 0.3, 0.4))
    paste(lay, S["r_b"], x1, y + 50, ramp(t, 0.8, 0.4))
    paste(lay, S["here"], CX, y - 80 + 14 * (1 - q), q)
    paste(im, lay, W / 2, cy, a)


def frame(t):
    if t < T_C:
        im = bgf(BG_CREAM, t)
        out = 1 - ramp(t, T_C - 0.35, 0.35)
        # tablica (od 1. klatki)
        py = 760
        paste(im, S["panel"], CX, py, out)
        paste(im, S["k_lab"], 100 + 40 + S["k_lab"].width / 2, py - 80, out)
        paste(im, S["peron"], 920 - 40 - S["peron"].width / 2, py - 80, out)
        row = flap_row("STACJA KOŃCOWA", "ŚRODEK TRASY", t, T_FLIP + 0.15)
        paste(im, row, CX, py + 30, out)
        # hak / zwrot
        a = 1 - ramp(t, T_FLIP - 0.3, 0.3)
        paste(im, S["hook"], CX, 440, a)
        paste(im, S["hook_s"], CX, 1030 + 18 * (1 - ramp(t, 1.4, 0.5)), ramp(t, 1.4, 0.5) * a)
        b = ramp(t, T_FLIP + 0.2, 0.5) * out
        paste(im, S["twist"], CX, 440 + 20 * (1 - b), b)
        draw_route(im, t - (T_FLIP + 1.0), ramp(t, T_FLIP + 1.0, 0.3) * out)
        c = ramp(t, T_FLIP + 2.4, 0.5) * out
        paste(im, S["twist_s"], CX, 1290 + 18 * (1 - c), c)
        return im
    if t < T_D:
        tt = t - T_C
        im = bgf(BG_CREAM, t)
        out = 1 - ramp(t, T_D - 0.35, 0.35)
        a = ramp(tt, 0, 0.45) * out
        paste(im, S["c_h"], CX, 320 + 18 * (1 - a), a)
        paste(im, S["c_h2"], CX, 425 + 18 * (1 - a), ramp(tt, 0.3, 0.45) * out)
        paste(im, S["c_panel"], CX, 846, a)
        for i in range(5):
            t0 = 0.6 + i * 1.2
            p = ramp(tt, t0, 0.4)
            if p <= 0:
                continue
            r = S[f"t{i}"]
            r2 = r.resize((r.width, max(1, int(r.height * (0.2 + 0.8 * p)))), Image.BICUBIC)
            paste(im, r2, CX, 598 + i * 124, min(1, p * 1.5) * out)
        f = ramp(tt, 6.8, 0.5) * out
        paste(im, S["c_f"], CX, 1262 + 16 * (1 - f), f)
        return im
    if t < T_E:
        tt = t - T_D
        k = ramp(t, T_E - 0.5, 0.5)
        im = bgf(BG_CREAM, t)
        if k > 0:
            im = Image.blend(im, bgf(BG_LAV, t), k)
        out = 1 - k
        a = ramp(tt, 0, 0.45) * out
        paste(im, S["d_h"], CX, 380 + 18 * (1 - a), a)
        py = 650
        paste(im, S["d_panel"], CX, py, a)
        paste(im, S["d_lab"], 100 + 40 + S["d_lab"].width / 2, py - 80, a)
        paste(im, S["d_lab2"], 920 - 40 - S["d_lab2"].width / 2, py - 80, a)
        paste(im, flap_row("", "PT 4 GRUDNIA", tt, 0.35), CX, py + 30, a)
        c = ramp(tt, 1.3, 0.5) * out
        cy = 960 + 24 * (1 - c)
        paste(im, S["d_card"], CX, cy + 8, c)
        paste(im, S["d_a1"], CX, cy - 40, c)
        paste(im, S["d_a2"], CX, cy + 45, c)
        n = ramp(tt, 2.4, 0.5) * out
        paste(im, S["d_note"], CX, 1235 + 16 * (1 - n), n)
        return im
    tt = t - T_E
    im = bgf(BG_LAV, t)
    items = [("photo", 470, 0.0), ("e_sig", 800, 0.35), ("e_ke", 905, 0.6), ("e_btn", 1025, 0.9),
             ("e_course", 1130, 1.2), ("e_www", 1200, 1.4), ("logo", 1290, 1.6)]
    for key, y, t0 in items:
        a = ramp(tt, t0, 0.5)
        paste(im, S[key], CX, y + 20 * (1 - a), a)
    return im


# ---------------- muzyka: akustyczny indie-folk 80 BPM ----------------
def music(path):
    s = Song(BPM, TOTAL)
    gt = s.track("gt", 0, 24)      # gitara nylonowa
    pn = s.track("pn", 0, 0)       # pianino
    bs = s.track("bass", 0, 32)    # kontrabas
    dr = s.drums(kit=40)           # Brush
    # Fmaj7 — Am7 — Dm9 — Bbmaj7(#11) / C — spokojnie, ciepło
    prog = [(41, [53, 57, 60, 64, 67]), (45, [52, 57, 60, 64, 67]), (38, [50, 57, 60, 64, 65]),
            (46, [50, 57, 58, 62, 65])]
    pick = [(0, 0), (0.5, 3), (1.0, 1), (1.5, 4), (2.0, 2), (2.5, 3), (3.0, 1), (3.5, 4)]  # wzór palcowy
    end_b = TOTAL / BT
    bar, b0 = 0, 0.0
    melody = {1: [(0, 72), (1, 74), (1.5, 76), (3, 74)], 3: [(0, 72), (1.5, 69), (2, 67), (3, 69)]}
    while b0 < end_b - 0.01:
        root, ch = prog[bar % 4]
        last = b0 >= end_b - 4.5
        # gitara palcami (od 1. beatu)
        bass_note = root + 12 if root < 45 else root
        gt.note(b0, bass_note, 1.8, 74)
        for off, idx in pick:
            if last and off > 0:
                break
            gt.note(b0 + off, ch[idx] + (12 if idx > 2 else 0) - 12 + 12, 1.2, 66 if off % 1 == 0 else 54)
        if last:
            gt.chord(b0, [n for n in ch], 4, 70, strum=0.05)
            pn.chord(b0, ch, 4, 58)
            bs.note(b0, root - 12 if root > 40 else root, 3.5, 78)
            break
        # pianino: miękkie akordy od 2. taktu, melodia w środku
        if bar >= 1:
            pn.chord(b0, ch[1:], 1.8, 50)
            pn.chord(b0 + 2, ch[1:], 1.6, 44)
        if 4 <= bar <= 7 and (bar % 4) in melody:
            for off, n in melody[bar % 4]:
                pn.note(b0 + off, n, 0.9, 56)
        # kontrabas od 2. taktu
        if bar >= 1:
            r = root - 12 if root > 40 else root
            bs.note(b0, r, 1.6, 80)
            bs.note(b0 + 2, r + 7, 1.2, 66)
            bs.note(b0 + 3.5, r + 12 if bar % 2 else r + 5, 0.45, 56)
        # szczotki: od 2. taktu, bardzo cicho
        if bar >= 1:
            for b in range(4):
                dr.hit(b0 + b, 36, 56 if b % 2 == 0 else 40)
                if b % 2 == 1:
                    dr.hit(b0 + b, 38, 48)
                dr.hit(b0 + b + 0.5, 38, 22)
        b0 += 4
        bar += 1
    s.render(path,
             gains={"gt": 0.6, "pn": 0.45, "bass": 0.55, "drums": 0.35},
             fx={"gt": [HighpassFilter(90), LowpassFilter(6500), Reverb(room_size=0.45, wet_level=0.18)],
                 "pn": [HighpassFilter(140), LowpassFilter(5000), Reverb(room_size=0.6, wet_level=0.22)],
                 "bass": [LowpassFilter(900), Compressor(threshold_db=-20, ratio=2.5)],
                 "drums": [HighpassFilter(60), LowpassFilter(5000), Reverb(room_size=0.4, wet_level=0.15)]})


def render_full(out):
    wav = out + ".wav"
    music(wav)
    silent = out + ".silent.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    for n in range(int(round(TOTAL * FPS))):
        p.stdin.write(frame(n / FPS).convert("RGB").tobytes())
    p.stdin.close()
    assert p.wait() == 0
    tmp = out + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", "loudnorm=I=-17:TP=-2:LRA=7", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                    "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.rename(tmp, out)
    os.remove(silent)
    os.remove(wav)


def test_sheet(times, path):
    ims = [frame(t).convert("RGB").resize((360, 640)) for t in times]
    g = Image.new("RGB", (370 * len(ims), 650), (90, 90, 90))
    d = ImageDraw.Draw(g)
    for i, im in enumerate(ims):
        g.paste(im, (5 + 370 * i, 5))
        x0, y0, x1, y1 = [v / 3 for v in SAFE2]
        d.rectangle((5 + 370 * i + x0, 5 + y0, 5 + 370 * i + x1, 5 + y1), outline=(255, 0, 0))
    g.save(path, quality=85)


if __name__ == "__main__":
    prep()
    if sys.argv[1] == "test":
        out = sys.argv[2]
        os.makedirs(out, exist_ok=True)
        test_sheet([0.0, 2.5, 4.8, 9.5], f"{out}/s1.jpg")
        test_sheet([12.0, 18.0, 21.0, 23.5], f"{out}/s2.jpg")
        test_sheet([27.0, 30.5], f"{out}/s3.jpg")
        for t in [0.0, 9.5, 18.0, 23.5, 30.5]:
            frame(t).convert("RGB").save(f"{out}/f_{t}.jpg", quality=88)
    elif sys.argv[1] == "music":
        music(sys.argv[2])
    else:
        render_full(sys.argv[2])
