"""TikTok SENS #04 — ADHD u dorosłych: „Wiem, co mam zrobić. Ale nie mogę zacząć.”

Koncept: dwa liczniki — zadanie zajmuje 10 minut, a „zanim zacznę” rośnie do 2 h 47 min (karteczki: najpierw kawa,
tylko oddzwonię, zrobię plan). Zwrot: to nie zawsze lenistwo; przy ADHD najtrudniejszy bywa sam start.
Narzędzie: „start na 2 minuty” (nie „napiszę maila”, tylko „otworzę maila i wpiszę temat”). Diagnozę stawia specjalista.
Wideo: Mixkit (Stock Video Free License): 49927, 49938, 49934, 49912, 4953, 4957.
Muzyka: Mixkit „Sleepy Cat” (Alejandro Magaña, Stock Music Free License) — spokojny lo-fi, stały puls ok. 68 BPM.
Użycie: python3 tt_04_nie_moge_zaczac.py test OUTDIR | full OUT.mp4
"""
import sys
from tt_base import *
from tt_klipy import smooth, Clip, music_bed, render_av, caption_card, end_card, draw_end

XF = 0.45
SCENES = [
    (0.0, 3.6, dict(vid=49927, start=5.0, x=0.40, zoom=(1.0, 1.05))),
    (3.6, 6.4, dict(vid=49938, start=5.0, x=0.5, zoom=(1.0, 1.05))),
    (6.4, 9.2, dict(vid=49934, start=6.5, x=0.48, zoom=(1.0, 1.05))),
    (9.2, 12.0, dict(vid=49912, start=4.0, x=0.50, zoom=(1.0, 1.05))),
    (12.0, 17.4, dict(vid=49925, start=11.0, x=0.50, zoom=(1.0, 1.06), dark=0.35)),
    (17.4, 22.8, dict(vid=4953, start=1.0, x=0.5, zoom=(1.0, 1.05))),
    (22.8, 25.8, dict(vid=4957, start=3.0, x=0.68, zoom=(1.0, 1.05))),
]
FOOT_END, DIAG0, END0, TOTAL = 25.8, 25.8, 28.6, 32.6
NOTES = [(3.6, 6.4, "Najpierw kawa.", -3), (6.4, 9.2, "Tylko szybko oddzwonię.", 2),
         (9.2, 12.0, "Zrobię najpierw plan…", -2)]
PAPER = (255, 246, 222)
S = {}
CLIPS = []


def vis_h(spr):
    return spr.height - 140


def note(text, rot, w=640, color=PAPER, fnt=None, strike=0.0):
    fnt = fnt or fit_font([text], CV, 92, w - 90)
    tx = text_sprite([text], fnt, INK, pad=0)
    h = tx.height + 120
    m = 50
    im = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((m + 8, m + 18, m + w + 8, m + h + 14), fill=(30, 20, 30, 80))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(im)
    d.rectangle((m, m, m + w, m + h), fill=color + (255,))
    d.rectangle((m, m, m + w, m + 26), fill=tuple(max(0, c - 18) for c in color) + (255,))  # pasek kleju
    x0, y0 = m + (w - tx.width) / 2, m + 60
    im.alpha_composite(tx, (int(x0), int(y0)))
    if strike > 0:
        yy = y0 + tx.height * 0.55
        d.line([(x0 - 10, yy), (x0 - 10 + (tx.width + 20) * strike, yy - 6)], fill=(196, 85, 63, 255), width=9)
    return im.rotate(rot, resample=Image.BICUBIC, expand=True)


_TC = {}


def timer_card(minutes):
    minutes = int(minutes)
    if minutes not in _TC:
        c, m = card_sprite(800, 200, r=40, fill=INK, shadow=(0, 0, 0, 90))
        d = ImageDraw.Draw(c)
        d.text((m + 44, m + 30), "ZADANIE:", font=font(B, 32), fill=LAVL)
        d.text((m + 290, m + 22), "mail do szkoły · 10 min", font=font(B, 40), fill=WHITE)
        d.line([(m + 44, m + 100), (m + 756, m + 100)], fill=(70, 92, 99), width=2)
        d.text((m + 44, m + 128), "ZANIM ZACZNĘ:", font=font(B, 32), fill=YEL)
        h, mm = divmod(minutes, 60)
        txt = f"{h} h {mm:02d} min" if h else f"{mm} min"
        f = font(XB, 50)
        d.text((m + 756 - f.getlength(txt), m + 114), txt, font=f, fill=WHITE)
        _TC[minutes] = c
    return _TC[minutes]


def minutes_at(t):
    if t < 3.6:
        return 0
    if t < 11.6:  # rośnie w trakcie karteczek, spokojnie (skoki co ~0,25 s)
        p = (t - 3.6) / 8.0
        return int(167 * (p ** 1.15))
    return 167


def prep():
    for a, b, kw in SCENES:
        kw = dict(kw)
        CLIPS.append((a, b, Clip(kw.pop("vid"), kw.pop("start"), b - a + XF + 0.1, **kw)))
    S["h1"] = caption_card(["Wiem, co mam zrobić."], font(XB, 70), pad=(56, 36))
    S["h2"] = caption_card([[("Ale nie mogę zacząć.", WHITE)]], font(XB, 70), bgc=LAVD, pad=(56, 36))
    S["h_y"] = (800, 800 + vis_h(S["h1"]) / 2 + 24 + vis_h(S["h2"]) / 2)
    S["notes"] = [(a, b, note(txt, r)) for a, b, txt, r in NOTES]
    S["c1"] = caption_card(["To nie zawsze", [("lenistwo.", LAVD)]], font(XB, 84), pad=(64, 44))
    S["c2"] = caption_card(["Przy ADHD najtrudniejszy", "bywa sam start."], font(B, 56), pad=(56, 40))
    S["c_y"] = (760, 760 + vis_h(S["c1"]) / 2 + 28 + vis_h(S["c2"]) / 2)
    S["d0"] = caption_card([[("Spróbuj: ", INK), ("start na 2 minuty", LAVD)]], font(XB, 54), pad=(50, 34))
    S["n1"] = [note("Napiszę maila.", -2, strike=k / 8) for k in range(9)]
    S["n2"] = note("Otworzę maila i wpiszę temat.", 2, w=760, color=(232, 244, 238))
    S["d3"] = caption_card([[("Lepszy mały start", INK)], [("niż idealny plan.", LAVD)]], font(XB, 74), pad=(60, 44))
    S["e1"] = text_sprite(["Trwa to od lat", "i utrudnia życie?"], font(XB, 76), INK, gap=1.06)
    S["e2"] = text_sprite([[("Diagnozę ADHD stawia ", INK)], [("specjalista.", LAVD)]], font(B, 58), INK)
    S["end"] = end_card("Wyślij komuś, kto to zna")


def footage(t):
    cur = [(a, b, c) for a, b, c in CLIPS if a <= t < b + XF]
    a, b, c = cur[0]
    im = c.frame(t - a)
    if len(cur) > 1 and t >= cur[1][0]:
        a2, b2, c2 = cur[1]
        im = Image.blend(im, c2.frame(t - a2), smooth((t - a2) / XF))
    return im.copy()


def over(im, t):
    """napisy na nagraniach"""
    if t < 12.4:  # licznik
        a = ramp(t, 1.5, 0.45) * (1 - ramp(t, 12.0, 0.4))
        paste(im, timer_card(minutes_at(t)), CX, 1250 + 16 * (1 - ramp(t, 1.5, 0.45)), a)
    if t < 3.6:
        o = 1 - ramp(t, 3.25, 0.35)
        paste(im, S["h1"], CX, S["h_y"][0], o)
        a2 = ramp(t, 0.9, 0.4) * o
        paste(im, S["h2"], CX, S["h_y"][1] + 18 * (1 - ramp(t, 0.9, 0.4)), a2)
    for a, b, spr in S["notes"]:
        if a - 0.1 <= t < b:
            v = win(t, a + 0.2, b, 0.35, 0.3)
            paste(im, spr, CX, 990 + 20 * (1 - ramp(t, a + 0.2, 0.35)), v)
    if 12.0 <= t < 17.4:
        v1 = win(t, 12.3, 17.4, 0.45, 0.35)
        paste(im, S["c1"], CX, S["c_y"][0], v1)
        v2 = win(t, 14.4, 17.4, 0.45, 0.35)
        paste(im, S["c2"], CX, S["c_y"][1] + 18 * (1 - ramp(t, 14.4, 0.45)), v2)
    if 17.4 <= t < 22.8:
        o = 1 - ramp(t, 22.45, 0.35)
        paste(im, S["d0"], CX, 330, ramp(t, 17.6, 0.4) * o)
        k = int(8 * ramp(t, 18.9, 0.6))
        v1 = ramp(t, 17.8, 0.4) * o
        paste(im, S["n1"][k], CX, 760, v1)
        v2 = ramp(t, 20.0, 0.45) * o
        paste(im, S["n2"], CX, 1110 + 20 * (1 - ramp(t, 20.0, 0.45)), v2)
    if 22.8 <= t < FOOT_END:
        v = win(t, 23.0, FOOT_END + 0.3, 0.45, 0.4)
        paste(im, S["d3"], CX, 900, v)
    return im


def light(t):
    im = bg(LIGHT, t)
    if t < END0:
        o = 1 - ramp(t, END0 - 0.35, 0.35)
        a = ramp(t, DIAG0 + 0.2, 0.45)
        paste(im, S["e1"], CX, 720 + 20 * (1 - a), a * o)
        b = ramp(t, DIAG0 + 0.9, 0.45)
        paste(im, S["e2"], CX, 960 + 20 * (1 - b), b * o)
        return im
    draw_end(im, t, END0, S["end"])
    return im


def frame(t):
    if t < FOOT_END:
        return over(footage(t), t)
    if t < FOOT_END + XF:
        a = over(footage(FOOT_END - 0.01), FOOT_END - 0.01)
        return Image.blend(a, light(t), smooth((t - FOOT_END) / XF))
    return light(t)


def music(path):
    music_bed(135, 8.0, TOTAL, path, fade_in=0.8, fade_out=2.0, lufs=-17.5)


if __name__ == "__main__":
    prep()
    if sys.argv[1] == "test":
        out = sys.argv[2]
        sheet(frame, [0.1, 2.0, 4.5, 7.5], f"{out}/a.jpg")
        sheet(frame, [10.5, 13.0, 15.5, 18.2], f"{out}/b.jpg")
        sheet(frame, [19.5, 21.5, 24.0, 27.0], f"{out}/c.jpg")
        sheet(frame, [29.0, 31.5], f"{out}/d.jpg")
    elif sys.argv[1] == "frame":
        frame(float(sys.argv[2])).convert("RGB").save(sys.argv[3], quality=90)
    elif sys.argv[1] == "music":
        music(sys.argv[2])
    else:
        wav = sys.argv[2] + ".music.wav"
        music(wav)
        render_av(frame, TOTAL, sys.argv[2], wav)
        os.remove(wav)
