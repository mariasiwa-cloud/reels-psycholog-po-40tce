"""Rolka 10 — „Środek, nie koniec”: AUTOUZUPEŁNIANIE (kurs, start pt 4 grudnia 2026).

Koncept w jednym zdaniu: głowa działa jak klawiatura w telefonie — po „Menopauza to…” sama podpowiada
„koniec / starość / wstyd”; w CBT to myśli automatyczne: podpowiedź, nie fakt — i można dopisać zdanie po swojemu:
„środek, nie koniec.” → wydarzenie w kalendarzu: kurs w SENS, pt 4 grudnia.
Format: prawdziwe nagrania (Coverr: dłonie piszące na telefonie, kobieta 50+ z kubkiem) + interfejs „klawiatury
z podpowiedziami” w ciemnym petrolu; dominanta: ciemny petrol + lawenda, mało kremu (wczoraj: krem + lawenda).
Oś: 0–5,2 hak (podpowiedzi) → 5,2–10,6 zwrot: „W CBT to myśli automatyczne” → 10,6–17 przekreślenie podpowiedzi,
dopisanie „środek, nie koniec.” + ćwiczenie „fakt czy podpowiedź?” → 17–22,6 „Nowe wydarzenie” = kurs →
22,6–28 karta końcowa na ciemnym tle ze zdjęciem 06 (studyjne, czarne tło).
Nagrania: Coverr (licencja Coverr: komercyjnie, bez atrybucji; bez premium/AI).
Muzyka: Mixkit „Music and Life” — Michael Ramir C. (Mixkit Stock Music Free License), folk-pop, gitara akustyczna,
ok. 95 BPM; tło −17 LUFS, low-pass 9,5 kHz.
Użycie (z katalogu repo): python3 narzedzia/rolka_10_autouzupelnianie.py test OUTDIR | full OUT.mp4
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "tiktok-sens", "narzedzia"))
from tt_base import *
from tt_klipy import Clip, music_bed, render_av, smooth

TOTAL = 28.0
T_B, T_C, T_D, T_E = 5.2, 10.6, 17.0, 22.6
CX = 510
IG_SAFE = (80, 250, 940, 1360)
CREAM = (248, 242, 232)
PET = (22, 44, 50)       # panel klawiatury
PET2 = (34, 62, 70)      # klawisze
Q = {}
XF = 0.4
SHOTS = [
    (0.0, T_B, dict(vid="coverr-woman-typing-on-an-iphone-9662", start=0.3, x=0.42, zoom=(1.0, 1.05), dark=0.28)),
    (T_B, T_C + 0.9, dict(vid="coverr-woman-drinking-coffee-from-a-mug-723", start=1.0, x=0.47, zoom=(1.0, 1.06),
                          dark=0.12)),
]
CLIPS = []
D_CLIP = None


def cream_card(sprs, w=None, gap=6, pad=(52, 36), fill=CREAM, alpha=250, r=34):
    w = w or max(s.width for s in sprs) + 2 * pad[0]
    h = sum(s.height for s in sprs) + gap * (len(sprs) - 1) + 2 * pad[1]
    c, m = card_sprite(w, h, r=r, fill=fill + (alpha,), shadow=(5, 15, 20, 90))
    y = m + pad[1]
    for s in sprs:
        c.alpha_composite(s, (m + (w - s.width) // 2, y))
        y += s.height + gap
    return c


# ---------- klawiatura z podpowiedziami ----------
PW = 880
CHIPS = ["koniec", "starość", "wstyd"]


def keyboard_base():
    """panel: pole tekstowe (2 linie) + pasek podpowiedzi + 3 rzędy klawiszy (bez liter — tylko kształt)"""
    ph = 760
    im = Image.new("RGBA", (PW, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, PW - 1, ph - 1), 44, fill=PET + (238,))
    # pole tekstowe
    d.rounded_rectangle((34, 34, PW - 34, 270), 30, fill=CREAM + (255,))
    # pasek podpowiedzi
    d.line([(PW / 3, 310), (PW / 3, 398)], fill=(70, 98, 106, 255), width=3)
    d.line([(2 * PW / 3, 310), (2 * PW / 3, 398)], fill=(70, 98, 106, 255), width=3)
    # klawisze (QWERTZ: 10 / 9 / 7)
    for r, n in enumerate([10, 9, 7]):
        kw, gap = 74, 10
        tw = n * kw + (n - 1) * gap
        x0 = (PW - tw) / 2
        y = 446 + r * 96
        for k in range(n):
            d.rounded_rectangle((x0 + k * (kw + gap), y, x0 + k * (kw + gap) + kw, y + 80), 14, fill=PET2 + (255,))
    # spacja
    d.rounded_rectangle((PW / 2 - 230, 446 + 3 * 96 - 6, PW / 2 + 230, 446 + 3 * 96 + 14), 10, fill=PET2 + (255,))
    return im


QWERTZ = ["qwertzuiop", "asdfghjkl", "yxcvbnm"]


def key_letters():
    im = Image.new("RGBA", (PW, 760), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font(M, 36)
    for r, row in enumerate(QWERTZ):
        n = len(row)
        kw, gap = 74, 10
        tw = n * kw + (n - 1) * gap
        x0 = (PW - tw) / 2
        y = 446 + r * 96
        for k, ch in enumerate(row):
            cx = x0 + k * (kw + gap) + kw / 2
            d.text((cx - f.getlength(ch) / 2, y + 14), ch, font=f, fill=(150, 176, 182, 255))
    return im


def chip_sprite(word, color, bold=False):
    return text_sprite([word], font(B if bold else M, 46), color, pad=4)


def draw_keyboard(im, t, cy, line2="", cursor=True, chips_a=1.0, strike=(0, 0, 0), chips_dim=0.0, a=1.0,
                  hi=-1):
    pan = Q["kb"].copy()
    pan.alpha_composite(Q["kl"])
    d = ImageDraw.Draw(pan)
    # tekst w polu
    l1 = Q["in1"]
    pan.alpha_composite(l1, (70, 52))
    f2 = font(XB, 64)
    if line2:
        tx = text_sprite([line2], f2, LAVD, pad=0)
        pan.alpha_composite(tx, (74, 152))
        cx = 74 + int(f2.getlength(line2)) + 6
    else:
        cx = 76
    if cursor and int(t * 2.2) % 2 == 0:
        d.rectangle((cx, 160, cx + 6, 240), fill=LAVD + (255,))
    # podpowiedzi
    for i, w in enumerate(CHIPS):
        if chips_a <= 0:
            break
        col = WHITE if i == hi else LAVL
        sp = Q[f"chip{i}{'h' if i == hi else ''}"]
        ccx = PW / 6 + i * PW / 3
        aa = chips_a * ramp(chips_a * 3 - i * 0.6, 0, 1) if chips_a < 1 else 1.0
        aa *= (1 - 0.55 * chips_dim)
        paste(pan, sp, ccx, 354, aa)
        if strike[i] > 0:
            hw = sp.width / 2 + 10
            d.line([(ccx - hw, 358), (ccx - hw + 2 * hw * strike[i], 352)], fill=(254, 217, 14, 255), width=7)
    sh, m = card_sprite(PW, 760, r=44, fill=(0, 0, 0, 0), shadow=(0, 10, 14, 120))
    sh.alpha_composite(pan, (m, m))
    paste(im, sh, CX, cy, a)


def photo06(w):
    ph = Image.open(os.path.join(REPO, "fotos_maria", "06_estudio_fondo_negro_blazer_cuerpo.jpg")).convert("RGB")
    c = ph.crop((0, 0, 1064, 1180))  # od góry: twarz w całości, ręce skrzyżowane
    h = int(w * c.height / c.width)  # tylko równomierne skalowanie
    c = c.resize((w, h), Image.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), 40, fill=255)
    fr, fm = card_sprite(w, h, r=40, fill=(12, 14, 16), shadow=(0, 0, 0, 120))
    fr.paste(c, (fm, fm), mask)
    # cienka lawendowa ramka
    ImageDraw.Draw(fr).rounded_rectangle((fm - 1, fm - 1, fm + w, fm + h), 41, outline=LAV + (255,), width=3)
    return fr


def prep():
    global D_CLIP
    for t0, t1, kw in SHOTS:
        kw = dict(kw)
        CLIPS.append((t0, t1, Clip(kw.pop("vid"), kw.pop("start"), t1 - t0 + XF + 0.1, **kw)))
    D_CLIP = Clip("coverr-woman-drinking-coffee-from-a-mug-723", 14.0, T_E - T_D + 1.2, x=0.47, zoom=(1.06, 1.0),
                  dark=0.45)
    Q["kb"] = keyboard_base()
    Q["kl"] = key_letters()
    Q["in1"] = text_sprite(["Menopauza to"], font(XB, 64), INK, pad=0)
    for i, w in enumerate(CHIPS):
        Q[f"chip{i}"] = chip_sprite(w, LAVL)
        Q[f"chip{i}h"] = chip_sprite(w, WHITE, bold=True)
    # A — hak
    h1 = ["Twoja głowa też ma", "autouzupełnianie."]
    Q["a_hook"] = cream_card([text_sprite(h1, fit_font(h1, XB, 76, 740), INK, gap=1.08, pad=2)])
    # B — zwrot
    b1 = text_sprite(["W CBT to się nazywa"], font(B, 50), INK, pad=0)
    b2 = text_sprite(["myśli automatyczne."], fit_font(["myśli automatyczne."], XB, 80, 760), LAVD, pad=2)
    Q["b1"] = cream_card([b1, b2], gap=4)
    bl = ["Wyskakują same.", "I brzmią jak fakty."]
    Q["b2"] = cream_card([text_sprite(bl, fit_font(bl, XB, 64, 700), INK, gap=1.1, pad=2)], fill=CREAM)
    # C — przeformułowanie
    c1 = ["To podpowiedź,", "nie fakt."]
    Q["c_top"] = text_sprite(c1, font(XB, 96), WHITE, gap=1.05, pad=4)
    Q["c_lbl"] = text_sprite(["Możesz dopisać zdanie po swojemu."], fit_font(["Możesz dopisać zdanie po swojemu."],
                                                                            M, 44, 800), LAVL, pad=4)
    e1 = text_sprite(["Ćwiczenie na dziś:"], font(B, 42), LAVD, pad=0)
    e2l = ["Gdy pojawi się „koniec”, zapytaj:", "fakt czy podpowiedź?"]
    e2 = text_sprite(e2l, fit_font(e2l, B, 50, 760), INK, gap=1.12, pad=2)
    Q["c_ex"] = cream_card([e1, e2], gap=6, pad=(46, 30))
    # D — wydarzenie w kalendarzu
    dw = 820
    lab = pill("Nowe wydarzenie", font(B, 34), WHITE, LAVD, padx=30, h=64)
    title = text_sprite(["Środek, nie koniec"], fit_font(["Środek, nie koniec"], XB, 88, dw - 100), INK, pad=2)
    sub = text_sprite(["kurs dla kobiet w peri- i menopauzie"], fit_font(["kurs dla kobiet w peri- i menopauzie"],
                                                                         M, 40, dw - 100), INK, pad=2)
    when = text_sprite([[("Start: ", INK), ("piątek, 4 grudnia", LAVD)]], fit_font(["Start: piątek, 4 grudnia"], XB,
                                                                                    62, dw - 100), INK, pad=2)
    rows = ["6 spotkań · stacjonarnie w SENS", "ul. Dyrekcyjna 37/47, Wrocław",
            "psychoedukacja + ćwiczenia CBT w małej grupie"]
    rr = text_sprite(rows, fit_font(rows, M, 38, dw - 100), INK, gap=1.25, pad=2)
    sep = Image.new("RGBA", (dw - 120, 3), LAV + (255,))
    Q["d_card"] = cream_card([lab, title, sub, sep, when, rr], w=dw, gap=14, pad=(50, 40))
    sm = ["To nie terapia grupowa.", "Objawy z ciała zawsze skonsultuj z lekarzem."]
    Q["d_small"] = cream_card([text_sprite(sm, fit_font(sm, M, 34, 720), INK, gap=1.22, pad=2)], pad=(40, 24),
                              alpha=235)
    # E — karta końcowa (ciemna)
    Q["e_photo"] = photo06(320)
    sg = ["dr Maria Siwa — psycholożka i psychodietetyczka,", "psychoterapeutka CBT w trakcie szkolenia"]
    Q["e_sig"] = text_sprite(sg, fit_font(sg, M, 34, 860), WHITE, gap=1.2, pad=6)
    Q["e_ke"] = text_sprite(["Każda emocja ma sens."], font(CV, 84), LAVL, pad=6)
    Q["e_btn"] = pill("Zapisy: senswroclaw.pl", font(B, 48), WHITE, LAVD, padx=56, h=120)
    ck = ["kurs „Środek, nie koniec” · start: piątek, 4 grudnia"]
    Q["e_course"] = text_sprite(ck, fit_font(ck, B, 38, 860), WHITE, pad=6)
    ft = ["SENS · ul. Dyrekcyjna 37/47, Wrocław", "senswroclaw.pl · @senswroclaw"]
    Q["e_www"] = text_sprite(ft, fit_font(ft, M, 34, 860), LAVL, gap=1.2, pad=6)
    Q["logo"] = asset("logo_bialy.png", 118)


def video(t):
    act = [(i, c) for i, c in enumerate(CLIPS) if c[0] <= t]
    i, (t0, t1, c) = act[-1]
    im = c.frame(t - t0)
    if i > 0 and t - t0 < XF:
        p0, p1, pc = CLIPS[i - 1]
        im = Image.blend(pc.frame(t - p0), im, smooth((t - t0) / XF))
    return im.copy()


def shade(im, top=0.35, bottom=0.3):
    y = np.arange(H)[:, None].astype(np.float32)
    g = top * np.clip(1 - y / 900, 0, 1) + bottom * np.clip((y - 1100) / 820, 0, 1)
    lay = np.zeros((H, W, 4), np.uint8)
    lay[..., :3] = (14, 28, 32)
    lay[..., 3] = np.repeat((np.clip(g, 0, 1) * 255).astype(np.uint8), W, 1)
    im.alpha_composite(Image.fromarray(lay, "RGBA"))


def scene_c(t):
    tt = t - T_C
    im = bg(DARK, t)
    a = ramp(tt, 0.1, 0.45) * (1 - ramp(tt, 3.6, 0.35))
    paste(im, Q["c_top"], CX, 420 + 20 * (1 - a), a)
    st = tuple(smooth((tt - 1.0 - 0.35 * i) / 0.35) for i in range(3))
    typed = "środek, nie koniec."
    k = int(len(typed) * max(0.0, min(1.0, (tt - 2.6) / 1.1)))
    draw_keyboard(im, t, 930, line2=typed[:k], strike=st, chips_dim=ramp(tt, 2.2, 0.5))
    b = ramp(tt, 2.4, 0.4)
    paste(im, Q["c_lbl"], CX, 1365 - 30, b)
    e = ramp(tt, 3.9, 0.45)
    paste(im, Q["c_ex"], CX, 425 + 20 * (1 - e), e)
    return im


def frame(t):
    if t >= T_E:
        tt = t - T_E
        im = bg(DARK, t)
        if tt < 0.9:
            im = Image.blend(D_CLIP.frame(t - T_D).filter(ImageFilter.GaussianBlur(10)), im, smooth(tt / 0.9))
        items = [(Q["logo"], 318, 0.1), (Q["e_photo"], 600, 0.3), (Q["e_sig"], 872, 0.55), (Q["e_ke"], 962, 0.75),
                 (Q["e_btn"], 1070, 0.95), (Q["e_course"], 1166, 1.15), (Q["e_www"], 1242, 1.3)]
        for spr, y, t0 in items:
            a = ramp(tt, t0, 0.45)
            paste(im, spr, CX, y + 18 * (1 - a), a)
        return im
    if t >= T_D:
        tt = t - T_D
        im = D_CLIP.frame(tt).filter(ImageFilter.GaussianBlur(10))
        if tt < 0.9:
            im = Image.blend(scene_c(t), im, smooth(tt / 0.9))
        out = 1 - ramp(t, T_E - 0.3, 0.3)
        a = ramp(tt, 0.3, 0.5)
        paste(im, Q["d_card"], CX, 720 + 40 * (1 - a), a * out)
        b = ramp(tt, 2.0, 0.45)
        paste(im, Q["d_small"], CX, 1250 + 18 * (1 - b), b * out)
        return im
    if t >= T_C:
        im = scene_c(t)
        tt = t - T_C
        if tt < 0.9:
            v = video(t)
            shade(v)
            im = Image.blend(v, im, smooth(tt / 0.9))
        return im
    im = video(t)
    shade(im)
    if t < T_B:
        out = 1 - ramp(t, T_B - 0.35, 0.35)
        paste(im, Q["a_hook"], CX, 425, out)  # od klatki 0
        hi = 0 if 3.0 < t else -1
        draw_keyboard(im, t, 1005, chips_a=min(1.0, 0.35 + t / 0.9), a=out, hi=hi)
        return im
    tt = t - T_B
    out = 1 - ramp(t, T_C - 0.3, 0.3)
    a = ramp(tt, 0.3, 0.45)
    paste(im, Q["b1"], CX, 450 + 20 * (1 - a), a * out)
    b = ramp(tt, 2.8, 0.45)
    paste(im, Q["b2"], CX, 1180 + 20 * (1 - b), b * out)
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
        test_sheet([0.0, 3.5, 6.0, 9.5], f"{out}/s1.jpg")
        test_sheet([11.5, 13.5, 16.0, 17.5], f"{out}/s2.jpg")
        test_sheet([20.0, 22.4, 23.2, 27.5], f"{out}/s3.jpg")
        for t in [3.5, 16.0, 20.0, 27.5]:
            frame(t).convert("RGB").save(f"{out}/f_{t}.jpg", quality=88)
    else:
        wav = sys.argv[2] + ".wav"
        music_bed(852, 0.0, TOTAL, wav, fade_in=0.3, fade_out=2.0, lufs=-17.0)
        render_av(frame, TOTAL, sys.argv[2], wav)
        os.remove(wav)
