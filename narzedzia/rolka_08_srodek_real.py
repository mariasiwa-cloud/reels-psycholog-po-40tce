"""Rolka 08 — „Środek, nie koniec” (tablica odjazdów) — wersja z PRAWDZIWYMI nagraniami (poprawka Rodriga 23.11.2026:
mniej pustych teł, więcej prawdziwych ludzi; teksty jak w rolce 06b).

Koncept: pociąg wjeżdża na peron, tablica „STACJA KOŃCOWA” przeskakuje na „ŚRODEK TRASY” + pieczątka „NIE.”
→ „To nie koniec. To ŚRODEK.” na uśmiechniętej kobiecie → 5 przystanków kursu, każdy z innym ujęciem
(wiatrak = uderzenia gorąca, nocne myśli, zamyślenie, dłonie przy cieście, kobieta w mieście)
→ „Pierwszy odjazd: PT 4 GRUDNIA” na wieczornym przejściu → karta końcowa ze zdjęciem Marii.
Nagrania: Coverr (licencja Coverr) + (tylko Coverr).
Muzyka: Mixkit „Reaching Out” — Michael Ramir C. (Mixkit Stock Music Free License), pogodny, pewny siebie, 117 BPM.
Użycie (z katalogu repo): python3 narzedzia/rolka_08_srodek_real.py test OUTDIR | full OUT.mp4
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "tiktok-sens", "narzedzia"))
import rolka_06_tablica as r6
import rolka_06b_tablica_viral as v
from tt_base import *
from tt_klipy import Clip, music_bed, render_av, smooth

TOTAL = 24.2
T_FLIP, T_B, T_C, T_D, T_E = 1.6, 4.0, 7.6, 14.4, 19.0
CX = 510
IG_SAFE = (80, 250, 940, 1500)
Q = {}
SHOTS = [
    (0.0, 4.0, dict(vid="coverr-train-arriving-2362", start=1.0, x=0.5, zoom=(1.0, 1.08), dark=0.35)),
    (4.0, 7.6, dict(vid="coverr-smiling-woman-with-smartphone-outdoors", start=3.0, x=0.43, zoom=(1.0, 1.05), dark=0.4)),
    (7.6, 9.0, dict(vid="coverr-a-woman-turns-on-a-fan-4983", start=2.0, x=0.43, zoom=(1.0, 1.04), dark=0.2)),
    (9.0, 10.4, dict(vid="coverr-a-woman-working-on-her-computer-late-at-night-3699", start=9.0, x=0.66, zoom=(1.0, 1.04), dark=0.1)),
    (10.4, 11.8, dict(vid="coverr-contemplative-woman-in-city", start=5.0, x=0.28, zoom=(1.0, 1.04), dark=0.2)),
    (11.8, 13.1, dict(vid="coverr-woman-making-a-dough-2982", start=10.0, x=0.5, zoom=(1.0, 1.04), dark=0.2)),
    (13.1, 14.4, dict(vid="coverr-urban-professional-on-city-background", start=6.0, x=0.43, zoom=(1.0, 1.04), dark=0.2)),
    (14.4, 19.0, dict(vid="coverr-evening-crosswalk-contemplation", start=6.0, x=0.45, zoom=(1.0, 1.05), dark=0.35)),
]
CLIPS = []
XF = 0.25


def card_of(sprs, gap=6, pad=(44, 26), alpha=242):
    w = max(s.width for s in sprs) + 2 * pad[0]
    h = sum(s.height for s in sprs) + gap * (len(sprs) - 1) + 2 * pad[1]
    c, m = card_sprite(w, h, r=34, fill=WHITE + (alpha,), shadow=(0, 0, 0, 90))
    y = m + pad[1]
    for s in sprs:
        c.alpha_composite(s, (m + (w - s.width) // 2, y))
        y += s.height + gap
    return c


def prep():
    v.prep()
    for t0, t1, kw in SHOTS:
        kw = dict(kw)
        CLIPS.append((t0, t1, Clip(kw.pop("vid"), kw.pop("start"), t1 - t0 + XF + 0.05, **kw)))
    hh = ["Co jest", "w środku trasy?"]
    Q["c_h"] = text_sprite([[("Co jest", WHITE)], [("w środku trasy?", YEL)]], fit_font(hh, XB, 88, 860), WHITE, gap=1.04, pad=6)
    Q["c_f"] = card_of([r6.S["c_f"]])
    Q["d_h"] = text_sprite(["Pierwszy odjazd:"], font(XB, 92), WHITE, pad=6)
    Q["d_n"] = card_of([v.Q["d_sm"], r6.S["d_note"]], gap=0)


def video(t):
    cur = 0
    for i, (t0, t1, c) in enumerate(CLIPS):
        if t >= t0:
            cur = i
    t0, t1, c = CLIPS[cur]
    im = c.frame(min(t - t0, t1 - t0 + XF))
    if cur > 0 and t - t0 < XF:
        p0, p1, pc = CLIPS[cur - 1]
        im = Image.blend(pc.frame(t - p0), im, smooth((t - t0) / XF))
    return im.copy()


def vignette(im, top=0.5, bottom=0.4):
    y = np.arange(H)[:, None].astype(np.float32)
    g = top * np.clip(1 - y / 760, 0, 1) + bottom * np.clip((y - 1100) / 820, 0, 1)
    lay = np.zeros((H, W, 4), np.uint8)
    lay[..., :3] = (10, 24, 28)
    lay[..., 3] = np.repeat((np.clip(g, 0, 1) * 255).astype(np.uint8), W, 1)
    im.alpha_composite(Image.fromarray(lay, "RGBA"))


def frame(t):
    S = r6.S
    if t >= T_E:
        tt = t - T_E
        im = r6.bgf(r6.BG_LAV, t)
        items = [(v.Q["ph_end"], 470, 0.0), (S["e_sig"], 790, 0.25), (S["e_btn"], 925, 0.45), (S["e_course"], 1040, 0.65),
                 (S["e_ke"], 1125, 0.8), (S["e_www"], 1215, 0.95), (S["logo"], 1300, 1.1)]
        for spr, y, t0 in items:
            a = ramp(tt, t0, 0.4)
            paste(im, spr, CX, y + 18 * (1 - a), a)
        return im
    im = video(t)
    if t < T_C:
        vignette(im, 0.6, 0.45)
        out = 1 - ramp(t, T_C - 0.3, 0.3)
        a = 1 - ramp(t, T_B - 0.25, 0.25)
        paste(im, v.Q["hook"], CX, 420, a)
        v.board_at(im, 1250, "STACJA KOŃCOWA", "ŚRODEK TRASY", t, T_FLIP, out)
        s = ramp(t, T_FLIP + 0.7, 0.25)
        if s > 0 and a > 0:
            sc = 1.6 - 0.6 * s
            st = v.Q["stamp"].resize((int(v.Q["stamp"].width * sc), int(v.Q["stamp"].height * sc)), Image.BICUBIC)
            paste(im, st, 740, 790, min(1, s * 1.4) * a)
        b = ramp(t, T_B, 0.35) * out
        paste(im, v.Q["b_small"], CX, 295 + 14 * (1 - b), b)
        paste(im, v.Q["b_big"], CX, 480 + 18 * (1 - b), b)
        c = ramp(t, T_B + 0.4, 0.4) * out
        paste(im, v.Q["b_sub"], CX, 760, c)
        r6.draw_route(im, t - (T_B + 0.6), ramp(t, T_B + 0.6, 0.3) * out, cy=930, lc=LAVL)
        return im
    if t < T_D:
        tt = t - T_C
        vignette(im, 0.6, 0.3)
        out = 1 - ramp(t, T_D - 0.3, 0.3)
        a = ramp(tt, 0, 0.35) * out
        hc = a * (1 - ramp(tt, 4.1, 0.3))
        paste(im, Q["c_h"], CX, 370 + 16 * (1 - a), hc)
        pan = S["c_panel"].copy()
        for i in range(5):
            p = ramp(tt, 0.4 + i * 0.75, 0.3)
            if p <= 0:
                continue
            r = S[f"t{i}"]
            r2 = r.resize((r.width, max(1, int(r.height * (0.2 + 0.8 * p)))), Image.BICUBIC)
            paste(pan, r2, pan.width / 2, 395 - 248 + i * 124, min(1, p * 1.5))
        pan = pan.resize((int(pan.width * 0.8), int(pan.height * 0.8)), Image.LANCZOS)
        paste(im, pan, CX, 1110, a)
        f = ramp(tt, 4.2, 0.4) * out
        paste(im, Q["c_f"], CX, 380 + 14 * (1 - f), f)
        return im
    tt = t - T_D
    vignette(im, 0.6, 0.35)
    k = ramp(t, T_E - 0.4, 0.4)
    out = 1 - k
    a = ramp(tt, 0, 0.35) * out
    paste(im, Q["d_h"], CX, 370 + 16 * (1 - a), a)
    v.board_at(im, 620, "", "PT 4 GRUDNIA", tt, 0.25, a, "START KURSU", "SENS")
    c = ramp(tt, 1.0, 0.4) * out
    cy = 930 + 20 * (1 - c)
    paste(im, S["d_card"], CX, cy + 8, c)
    paste(im, S["d_a1"], CX, cy - 40, c)
    paste(im, S["d_a2"], CX, cy + 45, c)
    n = ramp(tt, 1.6, 0.4) * out
    paste(im, Q["d_n"], CX, 1260, n)
    if k > 0:
        im = Image.blend(im, r6.bgf(r6.BG_LAV, t), k)
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
        test_sheet([0.1, 2.8, 5.5, 7.3], f"{out}/s1.jpg")
        test_sheet([8.5, 9.7, 11.0, 13.8], f"{out}/s2.jpg")
        test_sheet([15.0, 17.5, 20.0, 23.5], f"{out}/s3.jpg")
        for t in [2.8, 5.5, 13.8, 17.5]:
            frame(t).convert("RGB").save(f"{out}/f_{t}.jpg", quality=88)
    else:
        wav = sys.argv[2] + ".wav"
        music_bed(1154, 20.0, TOTAL, wav, fade_in=0.3, lufs=-15.5, lowpass=12000, shelf_db=-1.0)
        render_av(frame, TOTAL, sys.argv[2], wav)
        os.remove(wav)
