"""TikTok SENS #06 — seria „Mit czy fakt?” / rodzice i ekrany: „Oddaj telefon. Natychmiast.”

Koncept: zabranie telefonu w połowie gry działa jak zgaszenie światła jednym pstryknięciem (PSTRYK — ciemność
i protest). Lepiej działa ściemniacz: 3 kroki (za 10 min, za 2 min, koniec + odłożenie telefonu), a lampa
w tle przygasa krok po kroku. Granica zostaje ta sama, zmienia się sposób.
Wideo: Coverr (licencja Coverr, użycie komercyjne): playing-candy-crush-on-android-7219 (ekran telefonu rozmyty —
bez znaków towarowych), touch-lamp-6697. Dziecka nie widać (tylko dłonie).
Muzyka: Mixkit „Forever in My Heart” (Michael Ramir C., Stock Music Free License) — ciepły akustyczny folk z gitarą.
Użycie: python3 tt_06_sciemniacz.py test OUTDIR | full OUT.mp4
"""
import sys
from tt_base import *
from tt_klipy import smooth, Clip, music_bed, render_av, caption_card, end_card, draw_end

XF = 0.45
GAME = "coverr-playing-candy-crush-on-android-7219"
LAMP = "coverr-touch-lamp-6697"
# (start, koniec, klip, jasność(t) -> 0..1 przyciemnienia)
TOTAL = 30.0
OFF_T = 5.3
S = {}
CLIPS = []


def vis_h(spr):
    return spr.height - 140


_BC = {}


def blur_screen(im, key):
    """rozmycie ekranu telefonu: środek = mediana mocno nasyconych pikseli gry (S>140), miękka elipsa
    (wygładzana w czasie) — gra i logo nieczytelne, dłonie i kanapa ostre"""
    a = np.asarray(im.convert("RGB").resize((270, 480), Image.BILINEAR).convert("HSV")).astype(int)
    ys, xs = np.nonzero((a[:, :, 1] > 140) & (a[:, :, 2] > 120))
    if len(xs) > 20:
        cx, cy = np.median(xs) * 4, np.median(ys) * 4
        if key in _BC:
            px, py = _BC[key]
            cx, cy = px + (cx - px) * 0.25, py + (cy - py) * 0.25
        _BC[key] = (cx, cy)
    cx, cy = _BC.get(key, (540, 800))
    rx, ry = 300, 370
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(40))
    box = (int(max(0, cx - rx - 120)), int(max(0, cy - ry - 120)), int(min(W, cx + rx + 120)), int(min(H, cy + ry + 120)))
    reg = im.crop(box).filter(ImageFilter.GaussianBlur(30))
    im.paste(reg, box[:2], mask.crop(box))
    return im


def darken(im, k):
    if k <= 0.001:
        return im
    return Image.blend(im, Image.new("RGBA", im.size, (8, 14, 18, 255)), min(1.0, k))


def lamp_level(t):
    """0 = pełne światło, 1 = ciemno"""
    if t < OFF_T:
        return 0.0
    if t < 7.6:
        return 0.93  # PSTRYK
    if t < 8.4:
        return 0.93 * (1 - ease((t - 7.6) / 0.8))  # wraca światło
    if t < 11.4:
        return 0.45 * ease((t - 8.9) / 2.2) if t > 8.9 else 0.0  # płynne ściemnianie
    return 0.45


def dimmer(level):
    """suwak ściemniacza: level 0..1 (1 = pełne światło)"""
    c, m = card_sprite(640, 120, r=60, shadow=(10, 10, 20, 80))
    d = ImageDraw.Draw(c)
    d.text((m + 40, m + 36), "ŚWIATŁO", font=font(B, 34), fill=INK)
    x0, x1, y = m + 250, m + 600, m + 60
    d.rounded_rectangle((x0, y - 9, x1, y + 9), 9, fill=(225, 218, 228))
    xe = x0 + (x1 - x0) * level
    d.rounded_rectangle((x0, y - 9, max(x0 + 18, xe), y + 9), 9, fill=YEL)
    d.ellipse((xe - 24, y - 24, xe + 24, y + 24), fill=WHITE, outline=INK, width=5)
    return c


def prep():
    CLIPS.append((0.0, 3.8, Clip(GAME, 1.0, 3.8 + XF + 0.1, x=0.62, zoom=(1.0, 1.05))))
    CLIPS.append((3.8, 11.4, Clip(LAMP, 11.6, 7.6 + XF + 0.1, x=0.62, zoom=(1.0, 1.06), speed=0.53)))
    CLIPS.append((11.4, 17.4, Clip(GAME, 6.0, 6.0 + XF + 0.1, x=0.62, zoom=(1.03, 1.08))))
    CLIPS.append((17.4, 24.6, Clip(LAMP, 11.6, 7.2 + XF + 0.1, x=0.62, zoom=(1.06, 1.12), speed=0.55)))
    S["h1"] = caption_card(["„Oddaj telefon.", "Natychmiast.”"], font(XB, 76), pad=(60, 40))
    S["h2"] = caption_card([[("…i zaczyna się awantura?", WHITE)]], font(XB, 54), bgc=LAVD, pad=(50, 30))
    S["h_y"] = (600, 600 + vis_h(S["h1"]) / 2 + 26 + vis_h(S["h2"]) / 2)
    S["b1"] = caption_card(["Zabranie telefonu w połowie gry", [("to jak zgaszenie światła:", LAVD)]],
                           font(B, 50), pad=(50, 34))
    S["pstryk"] = text_sprite([[("PSTRYK.", WHITE)]], font(XB, 150), WHITE, pad=20)
    S["b2"] = text_sprite(["Nagle ciemno. I protest."], font(B, 54), LAVL, pad=10)
    S["c1"] = caption_card([[("Lepiej działa ", INK), ("ściemniacz.", LAVD)]], font(XB, 66), pad=(56, 38))
    S["steps"] = [
        (11.4, 14.4, 0.7, caption_card([[("Za 10 minut:", LAVD)], "„Kończymy po tej rundzie.”"], font(B, 54),
                                       pad=(50, 34))),
        (14.4, 17.4, 0.4, caption_card([[("Za 2 minuty:", LAVD)], "„Zapisz grę, zaraz kolacja.”"], font(B, 54),
                                       pad=(50, 34))),
        (17.4, 20.6, 0.12, caption_card([[("Koniec:", LAVD)], "„Opowiesz mi, jak Ci poszło?”",
                                         "Telefon odkładamy razem."], font(B, 52), pad=(50, 34))),
    ]
    S["e1"] = caption_card(["Granica zostaje", "ta sama."], font(XB, 76), pad=(60, 40))
    S["e2"] = caption_card([[("Zmienia się sposób.", WHITE)]], font(XB, 64), bgc=LAVD, pad=(56, 34))
    S["e_y"] = (700, 700 + vis_h(S["e1"]) / 2 + 28 + vis_h(S["e2"]) / 2)
    S["end"] = end_card("Zapisz na wieczór")


def clip_frame(t):
    cur = [(a, b, c) for a, b, c in CLIPS if a <= t < b + XF]
    out = []
    for a, b, c in cur[:2]:
        im = c.frame(t - a).copy()
        if c.vid == GAME:
            p = (t - a) / (b - a)
            blur_screen(im, a)
            if a >= 11.4:  # kroki 1-2: obraz lekko przygasa
                im = darken(im, 0.18 + 0.18 * smooth((t - 14.7) / 0.9))  # krok 2: płynnie ciemniej
        else:
            lv = lamp_level(t) if a < 11.4 else (0.5 + 0.25 * ease((t - 17.4) / 1.2))
            im = darken(im, lv)
        out.append((a, im))
    im = out[0][1]
    if len(out) > 1 and t >= out[1][0]:
        im = Image.blend(im, out[1][1], smooth((t - out[1][0]) / XF))
    return im


def over(im, t):
    if t < 3.8:
        o = 1 - ramp(t, 3.45, 0.35)
        paste(im, S["h1"], CX, S["h_y"][0], o)
        a = ramp(t, 1.1, 0.4) * o
        paste(im, S["h2"], CX, S["h_y"][1] + 16 * (1 - ramp(t, 1.1, 0.4)), a)
    if 3.8 <= t < 7.6:
        o = 1 - ramp(t, 7.25, 0.35)
        paste(im, S["b1"], CX, 380, ramp(t, 3.95, 0.4) * o)
        if t >= OFF_T:
            paste(im, S["pstryk"], CX, 860, o)
            paste(im, S["b2"], CX, 1060, ramp(t, OFF_T + 0.5, 0.4) * o)
    if 7.6 <= t < 11.4:
        o = 1 - ramp(t, 11.05, 0.35)
        paste(im, S["c1"], CX, 380, ramp(t, 8.2, 0.4) * o)
        lvl = 1 - 0.55 * ease((t - 8.9) / 2.2) if t > 8.9 else 1.0
        paste(im, dimmer(lvl), CX, 1230, ramp(t, 8.4, 0.4) * o)
    for a, b, lvl, spr in S["steps"]:
        if a <= t < b:
            o = 1 - ramp(t, b - 0.3, 0.3) if b < 20.6 else 1 - ramp(t, b - 0.35, 0.35)
            v = ramp(t, a + 0.15, 0.35) * o
            paste(im, spr, CX, 420 + vis_h(spr) / 2 - 60 + 14 * (1 - ramp(t, a + 0.15, 0.35)), v)
            prev = 1.0 if a == 11.4 else [s[2] for s in S["steps"] if s[1] == a][0]
            cur = prev + (lvl - prev) * ease((t - a - 0.3) / 0.9)
            paste(im, dimmer(cur), CX, 1230, 1.0 if a > 11.4 else ramp(t, a, 0.3))
    if 20.6 <= t < 24.6:
        o = 1 - ramp(t, 24.25, 0.35)
        paste(im, S["e1"], CX, S["e_y"][0], ramp(t, 20.8, 0.45) * o)
        a = ramp(t, 21.9, 0.45) * o
        paste(im, S["e2"], CX, S["e_y"][1] + 16 * (1 - ramp(t, 21.9, 0.45)), a)
    return im


def light(t):
    im = bg(LIGHT, t)
    draw_end(im, t, 24.8, S["end"])
    return im


def frame(t):
    if t < 24.6:
        return over(clip_frame(t), t)
    if t < 24.6 + 0.9:
        a = over(clip_frame(24.59), t)
        return Image.blend(a, light(t), smooth((t - 24.6) / 0.9))
    return light(t)


def music(path):
    music_bed(797, 2.2, TOTAL, path, fade_in=0.5, fade_out=2.0, lufs=-17.5)


if __name__ == "__main__":
    prep()
    if sys.argv[1] == "test":
        out = sys.argv[2]
        sheet(frame, [0.0, 2.0, 4.6, 6.2], f"{out}/a.jpg")
        sheet(frame, [8.0, 10.6, 13.0, 16.0], f"{out}/b.jpg")
        sheet(frame, [19.0, 22.8, 25.5, 28.5], f"{out}/c.jpg")
    elif sys.argv[1] == "frame":
        frame(float(sys.argv[2])).convert("RGB").save(sys.argv[3], quality=90)
    elif sys.argv[1] == "music":
        music(sys.argv[2])
    else:
        wav = sys.argv[2] + ".music.wav"
        music(wav)
        render_av(frame, TOTAL, sys.argv[2], wav)
        os.remove(wav)
