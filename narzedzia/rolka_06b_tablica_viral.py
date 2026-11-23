"""Rolka 06b — „Środek, nie koniec”, wersja szybsza / bardziej „viralowa” (poprawka Rodriga 23.11.2026).

Ten sam pomysł (tablica odjazdów przy Dworcu Głównym), ale:
- hak od 1. klatki na ciemnym tle z twarzą Marii (zdjęcie studyjne 06) i mocnym pytaniem,
  klapki przeskakują już w 1,6 s + żółta pieczątka „NIE.”;
- szybszy rytm (24 s), krótkie komunikaty, duże litery;
- muzyka NIE melancholijna: radosny akustyczny indie-pop 104 BPM (gitara akustyczna strumming,
  pianino, bas, klaskanie, shaker, lekka stopa) — energia od 1. sekundy, bez EDM i bez ostrych wysokich.

Użycie (z katalogu repo):  python3 narzedzia/rolka_06b_tablica_viral.py test OUTDIR | full OUT.mp4
"""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rolka_06_tablica as r6
from rolka_06_tablica import *  # noqa (tt_base + tablica)
from tt_muzyka import Song, kick_beats
from pedalboard import Reverb, Compressor, HighpassFilter, LowpassFilter

BPM = 104
BT = 60 / BPM
T_FLIP = 1.6
T_B = 4.0      # „To nie koniec.”
T_C = 7.6      # przystanki
T_D = 14.4     # odjazd
T_E = 19.0     # karta końcowa
TOTAL = 24.2
DARK = (24, 42, 48)
Q = {}


def blobs_dark():
    return r6.blobs(DARK, [(200, 300, 520, (34, 62, 70)), (1100, 1000, 640, (44, 50, 72)),
                           (300, 1900, 600, (30, 58, 60))], 170)


BG_DARK = blobs_dark()


def photo(w, crop):
    ph = Image.open(os.path.join(r6.REPO, "fotos_maria", "06_estudio_fondo_negro_blazer_cuerpo.jpg")).convert("RGB")
    c = ph.crop(crop)
    h = int(w * c.height / c.width)  # tylko równomierne skalowanie
    c = c.resize((w, h), Image.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), 44, fill=255)
    fr, fm = card_sprite(w, h, r=44, fill=(20, 20, 24), shadow=(0, 0, 0, 90))
    fr.paste(c, (fm, fm), mask)
    return fr


def prep():
    r6.prep()
    Q["ph_big"] = photo(480, (150, 40, 930, 900))
    Q["ph_end"] = photo(330, (150, 40, 930, 900))
    hk = ["Menopauza =", "stacja końcowa?"]
    Q["hook"] = text_sprite([[("Menopauza =", WHITE)], [("stacja końcowa?", YEL)]], fit_font(hk, XB, 104, 860),
                            WHITE, gap=1.04, pad=8)
    st = text_sprite(["NIE."], font(XB, 150), BOARD, pad=10)
    stamp = Image.new("RGBA", (st.width + 70, st.height + 20), (0, 0, 0, 0))
    ImageDraw.Draw(stamp).rounded_rectangle((0, 0, stamp.width - 1, stamp.height - 1), 30, fill=YEL + (255,))
    stamp.alpha_composite(st, (35, 10))
    Q["stamp"] = stamp.rotate(-8, expand=True, resample=Image.BICUBIC)
    Q["b_small"] = text_sprite(["Psycholożka mówi wprost:"], font(M, 44), LAVL, pad=6)
    Q["b_big"] = text_sprite([[("To nie koniec.", WHITE)], [("To ", WHITE), ("ŚRODEK.", YEL)]],
                             font(XB, 112), WHITE, gap=1.04, pad=8)
    sub = ["Ciało i emocje się zmieniają —", "i da się z tym pracować."]
    Q["b_sub"] = text_sprite(sub, fit_font(sub, M, 46, 860), WHITE, gap=1.15, pad=6)
    hh = ["Co jest", "w środku trasy?"]
    Q["c_h"] = text_sprite(hh, fit_font(hh, XB, 92, 860), INK, gap=1.04, pad=6)
    Q["d_h"] = text_sprite([[("Pierwszy odjazd:", INK)]], font(XB, 92), INK, pad=6)
    Q["d_sm"] = text_sprite(["mała grupa · stacjonarnie · 6 spotkań"], font(B, 40), LAVD, pad=6)


def board_at(im, py, old, new, t, t0, a, lab1="KIERUNEK", lab2="PERON 40+"):
    S = r6.S
    paste(im, S["panel"], CX, py, a)
    l1 = S["k_lab"] if lab1 == "KIERUNEK" else S["d_lab"]
    l2 = S["peron"] if lab2 == "PERON 40+" else S["d_lab2"]
    paste(im, l1, 100 + 40 + l1.width / 2, py - 80, a)
    paste(im, l2, 920 - 40 - l2.width / 2, py - 80, a)
    paste(im, r6.flap_row(old, new, t, t0, step=0.07, stagger=0.035), CX, py + 30, a)


def frame(t):
    S = r6.S
    if t < T_C:
        im = r6.bgf(BG_DARK, t)
        out = 1 - ramp(t, T_C - 0.3, 0.3)
        # twarz Marii (od 1. klatki, lekki ruch w górę)
        pa = 1 - ramp(t, T_B - 0.25, 0.25)
        paste(im, Q["ph_big"], CX, 860 - 10 * ramp(t, 0, 4), pa * out)
        a = 1 - ramp(t, T_B - 0.25, 0.25)
        paste(im, Q["hook"], CX, 365, a)
        board_at(im, 1250, "STACJA KOŃCOWA", "ŚRODEK TRASY", t, T_FLIP, out)
        s = ramp(t, T_FLIP + 0.7, 0.25)
        if s > 0 and a > 0:
            sc = 1.6 - 0.6 * s
            st = Q["stamp"].resize((int(Q["stamp"].width * sc), int(Q["stamp"].height * sc)), Image.BICUBIC)
            paste(im, st, 730, 770, min(1, s * 1.4) * a)
        b = ramp(t, T_B, 0.35) * out
        paste(im, Q["b_small"], CX, 295 + 14 * (1 - b), b)
        paste(im, Q["b_big"], CX, 480 + 18 * (1 - b), b)
        # po zdjęciu: trasa „Jesteś tutaj” + podtytuł
        r6.draw_route(im, t - (T_B + 0.6), ramp(t, T_B + 0.6, 0.3) * out, cy=930, lc=LAVL)
        # draw_route rysuje na y≈1080 — tekst pod nim nad tablicą
        c = ramp(t, T_B + 0.4, 0.4) * out
        paste(im, Q["b_sub"], CX, 760, c)
        return im
    if t < T_D:
        tt = t - T_C
        im = r6.bgf(r6.BG_CREAM, t)
        out = 1 - ramp(t, T_D - 0.3, 0.3)
        a = ramp(tt, 0, 0.35) * out
        paste(im, Q["c_h"], CX, 385 + 16 * (1 - a), a)
        paste(im, S["c_panel"], CX, 876, a)
        for i in range(5):
            p = ramp(tt, 0.4 + i * 0.75, 0.3)
            if p <= 0:
                continue
            r = S[f"t{i}"]
            r2 = r.resize((r.width, max(1, int(r.height * (0.2 + 0.8 * p)))), Image.BICUBIC)
            paste(im, r2, CX, 628 + i * 124, min(1, p * 1.5) * out)
        f = ramp(tt, 4.2, 0.4) * out
        paste(im, S["c_f"], CX, 1290 + 14 * (1 - f), f)
        return im
    if t < T_E:
        tt = t - T_D
        k = ramp(t, T_E - 0.4, 0.4)
        im = r6.bgf(r6.BG_CREAM, t)
        if k > 0:
            im = Image.blend(im, r6.bgf(r6.BG_LAV, t), k)
        out = 1 - k
        a = ramp(tt, 0, 0.35) * out
        paste(im, Q["d_h"], CX, 370 + 16 * (1 - a), a)
        board_at(im, 620, "", "PT 4 GRUDNIA", tt, 0.25, a, "START KURSU", "SENS")
        c = ramp(tt, 1.0, 0.4) * out
        cy = 930 + 20 * (1 - c)
        paste(im, S["d_card"], CX, cy + 8, c)
        paste(im, S["d_a1"], CX, cy - 40, c)
        paste(im, S["d_a2"], CX, cy + 45, c)
        n = ramp(tt, 1.6, 0.4) * out
        paste(im, Q["d_sm"], CX, 1150, n)
        paste(im, S["d_note"], CX, 1262, n)
        return im
    tt = t - T_E
    im = r6.bgf(r6.BG_LAV, t)
    items = [(Q["ph_end"], 470, 0.0), (S["e_sig"], 790, 0.25), (S["e_btn"], 925, 0.45), (S["e_course"], 1040, 0.65),
             (S["e_ke"], 1125, 0.8), (S["e_www"], 1215, 0.95), (S["logo"], 1300, 1.1)]
    for spr, y, t0 in items:
        a = ramp(tt, t0, 0.4)
        paste(im, spr, CX, y + 18 * (1 - a), a)
    return im


# ---------------- muzyka: radosny akustyczny indie-pop 104 BPM ----------------
def music(path):
    s = Song(BPM, TOTAL)
    gt = s.track("gt", 0, 25)      # gitara akustyczna (stal)
    pn = s.track("pn", 0, 0)       # pianino
    bs = s.track("bass", 0, 33)    # bas palcowy
    dr = s.drums(kit=0)            # Standard
    # D — A — Bm — G (pogodnie, z dodanymi nonami)
    prog = [(38, [62, 66, 69, 76]), (45, [61, 64, 69, 71]), (47, [62, 66, 71, 73]), (43, [62, 67, 71, 74])]
    strum = [0, 0.5, 0.75, 1.25, 1.5, 2.0, 2.5, 2.75, 3.25, 3.5]
    hook = [(0, 78), (0.5, 76), (1.0, 74), (1.5, 76), (2.0, 78), (3.0, 81), (3.5, 78)]
    end_b = TOTAL / BT
    bar, b0 = 0, 0.0
    while b0 < end_b - 0.01:
        root, ch = prog[bar % 4]
        if b0 >= end_b - 4.2:
            gt.chord(b0, ch, 4, 84, strum=0.03)
            pn.chord(b0, [n - 12 for n in ch], 4, 70)
            bs.note(b0, root, 3, 88)
            dr.hit(b0, 36, 96)
            dr.hit(b0, 49, 62)
            break
        for off in strum:
            gt.chord(b0 + off, ch, 0.3, 84 if off % 1 == 0 else 64, strum=0.012)
        for e in range(4):
            pn.chord(b0 + e + 0.5, [n - 12 for n in ch[1:]], 0.3, 54)
        if bar % 2 == 1 and bar >= 2:
            for off, n in hook:
                pn.note(b0 + off, n, 0.45, 66)
        for off, oc, v in [(0, 0, 100), (1.5, 0, 82), (2.0, 7, 88), (3.0, 12, 78), (3.5, 0, 76)]:
            bs.note(b0 + off, root + oc, 0.45, v)
        for b in range(4):
            tb = b0 + b
            dr.hit(tb, 36, 96 if b % 2 == 0 else 70)
            if b % 2 == 1:
                dr.hit(tb, 39, 92)       # klaskanie
                dr.hit(tb, 38, 52)
            for k in range(4):
                dr.hit(tb + k * 0.25, 70, 50 if k % 2 == 0 else 34)  # shaker
        b0 += 4
        bar += 1
    s.render(path,
             gains={"gt": 0.5, "pn": 0.42, "bass": 0.75, "drums": 0.7},
             fx={"gt": [HighpassFilter(180), LowpassFilter(7500), Reverb(room_size=0.35, wet_level=0.14)],
                 "pn": [HighpassFilter(150), LowpassFilter(6000), Reverb(room_size=0.5, wet_level=0.18)],
                 "bass": [LowpassFilter(1000), Compressor(threshold_db=-18, ratio=3)],
                 "drums": [LowpassFilter(7000), Compressor(threshold_db=-14, ratio=2.2, attack_ms=5, release_ms=80)]})


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
                    "-c:v", "copy", "-af", "loudnorm=I=-15:TP=-1.5:LRA=7", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                    "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.rename(tmp, out)
    os.remove(silent)
    os.remove(wav)


if __name__ == "__main__":
    prep()
    if sys.argv[1] == "test":
        out = sys.argv[2]
        os.makedirs(out, exist_ok=True)
        r6.frame = frame
        r6.test_sheet([0.0, 1.9, 2.8, 4.6], f"{out}/v1.jpg")
        r6.test_sheet([6.5, 12.5, 16.5, 22.0], f"{out}/v2.jpg")
    elif sys.argv[1] == "music":
        music(sys.argv[2])
    else:
        render_full(sys.argv[2])
