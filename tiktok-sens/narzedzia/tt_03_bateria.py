"""TikTok SENS #03 — „Bateria” (przeciążenie / zmęczenie mamy). NOWY FORMAT (test tygodnia).

Koncept: dzień mamy pokazany jak bateria telefonu — telefon ładujesz co noc, a siebie? Od rana 64%,
po południu 18%, w nocy 3%. Zwrot: jeśli od tygodni budzisz się już „na 10%”, to sygnał, nie słabość.
Ładowanie to nie luksus. Karta SENS z bezpłatną rozmową wstępną (15 min).
Wideo: Mixkit (Stock Video Free License): 4758, 4749, 4820, 4548, 51388, 51386.
Muzyka: Mixkit „We'll Be Okay” (Michael Ramir C., Stock Music Free License) — spokojne piano/film, 70 BPM.
Użycie: python3 tt_03_bateria.py test OUTDIR | full OUT.mp4
"""
import sys
from tt_base import *
from tt_klipy import smooth, Clip, music_bed, render_av, caption_card, end_card, draw_end

XF = 0.45  # przenikanie między ujęciami
XL = 0.9  # dłuższe, łagodne przejście z ciemnego nagrania na jasne tło
# (start na ekranie, koniec, klip)
SCENES = [
    (0.0, 3.8, dict(vid=4758, start=0.2, x=0.74, zoom=(1.0, 1.05))),
    (3.8, 7.6, dict(vid=4749, start=5.4, x=0.70, zoom=(1.02, 1.08))),
    (7.6, 11.4, dict(vid=4820, start=4.0, x=0.04, zoom=(1.0, 1.06))),
    (11.4, 15.2, dict(vid=4548, start=3.0, x=0.92, zoom=(1.0, 1.05))),
    (15.2, 19.0, dict(vid=51388, start=3.0, x=0.69, zoom=(1.0, 1.06))),
    (19.0, 23.4, dict(vid=51386, start=8.5, x=0.57, zoom=(1.0, 1.05), dark=0.45)),
]
CHG0, END0, TOTAL = 23.4, 27.0, 31.0
# bateria: (czas, etykieta, godzina, procent)
BAT = [(0.0, "Telefon", "06:40", 100), (3.8, "Ty", "06:40", 64), (7.6, "Ty", "08:15", 41),
       (11.4, "Ty", "17:30", 18), (15.2, "Ty", "23:10", 3)]
CAPS = [
    (0.0, 3.8, None),
    (3.8, 7.6, ["Dzień jeszcze", "się nie zaczął."]),
    (7.6, 11.4, ["Śniadanie, szkoła,", "korki, praca."]),
    (11.4, 15.2, [[("„Mamo, a gdzie…?”", INK)], [("× 27", LAVD)]]),
    (15.2, 19.0, ["Pranie, lekcje, maile.", "I jeszcze tylko jedno…"]),
]
S = {}
CLIPS = []


def battery_icon(pct, w=150, h=70, charging=False):
    im = Image.new("RGBA", (w + 16, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 16, outline=INK + (255,), width=6)
    d.rounded_rectangle((w + 2, h * 0.32, w + 14, h * 0.68), 4, fill=INK + (255,))
    col = (196, 85, 63) if pct <= 10 else LAVD if pct <= 45 else GREEN
    fw = int((w - 24) * max(0.03, pct / 100))
    d.rounded_rectangle((12, 12, 12 + fw, h - 13), 8, fill=col + (255,))
    if charging:
        cx, cy = w / 2, h / 2
        d.polygon([(cx + 6, cy - 26), (cx - 14, cy + 4), (cx - 1, cy + 4), (cx - 7, cy + 26), (cx + 14, cy - 5),
                   (cx + 1, cy - 5)], fill=YEL + (255,), outline=INK + (255,))
    return im


_WC = {}


def widget(label, hour, pct, charging=False):
    k = (label, hour, int(pct), charging)
    if k not in _WC:
        fl, fh, fp = font(XB, 50), font(M, 36), font(XB, 58)
        lw = max(fl.getlength(label), fh.getlength(hour))
        pt = f"{int(pct)}%"
        ww = int(44 + lw + 40 + 166 + 34 + fp.getlength("100%") + 44)
        c, m = card_sprite(ww, 150, r=44, shadow=(20, 20, 30, 70))
        d = ImageDraw.Draw(c)
        d.text((m + 44, m + 20), label, font=fl, fill=INK)
        d.text((m + 46, m + 86), hour, font=fh, fill=LAVD)
        ic = battery_icon(pct, charging=charging)
        c.alpha_composite(ic, (int(m + 44 + lw + 40), m + 40))
        col = (196, 85, 63) if pct <= 10 else INK
        d.text((m + ww - 44 - fp.getlength(pt), m + 38), pt, font=fp, fill=col)
        _WC[k] = c
    return _WC[k]


def vis_h(spr):
    return spr.height - 140  # karta z card_sprite ma margines 70 px na cień


def prep():
    for a, b, kw in SCENES:
        kw = dict(kw)
        CLIPS.append((a, b, Clip(kw.pop("vid"), kw.pop("start"), b - a + XF + 0.1, **kw)))
    S["hook"] = caption_card(["Telefon ładujesz", "co noc."], font(XB, 76), pad=(60, 40))
    S["hook2"] = caption_card([[("A siebie?", WHITE)]], font(XB, 110), bgc=LAVD, pad=(70, 30))
    y1 = 860
    S["hook_y"] = (y1, y1 + vis_h(S["hook"]) / 2 + 26 + vis_h(S["hook2"]) / 2)
    S["caps"] = [(a, b, caption_card(l, fit_font(l, B, 60, 760), pad=(54, 36)) if l else None) for a, b, l in CAPS]
    S["f1"] = caption_card(["Jeśli od tygodni", "budzisz się już na 10%…"], font(B, 56), pad=(54, 38))
    S["f2"] = caption_card([[("to sygnał,", WHITE)], [("nie słabość.", WHITE)]], font(XB, 84), bgc=LAVD, pad=(60, 40))
    S["f_y"] = (700, 700 + vis_h(S["f1"]) / 2 + 30 + vis_h(S["f2"]) / 2)
    S["g1"] = text_sprite([[("Ładowanie", INK)], [("to nie luksus.", LAVD)]], font(XB, 90), INK, gap=1.06)
    S["g2"] = text_sprite(["Sen. Ruch. Rozmowa.", "Chwila tylko dla siebie."], font(M, 50), INK)
    S["end"] = end_card("Bezpłatna rozmowa · 15 min", sub="Nie musisz zostać z tym sama.")


def bat_state(t):
    i = max(k for k in range(len(BAT)) if BAT[k][0] <= t)
    t0, lab, hr, p = BAT[i]
    if i + 1 < len(BAT):  # spadek ostatnie 0,9 s przed następnym ujęciem
        t1, _, _, p1 = BAT[i + 1]
        if t > t1 - 0.9 and lab == "Ty":
            p = p + (p1 - p) * ease((t - (t1 - 0.9)) / 0.9)
    return lab, hr, p


def footage(t):
    cur = [(a, b, c) for a, b, c in CLIPS if a <= t < b + XF]
    a, b, c = cur[0]
    im = c.frame(t - a)
    if len(cur) > 1 and t >= cur[1][0]:
        a2, b2, c2 = cur[1]
        im = Image.blend(im, c2.frame(t - a2), smooth((t - a2) / XF))
    return im.copy()


def frame(t):
    if t < CHG0 + XL:
        im = footage(min(t, CHG0 - 0.01)) if t < CHG0 else footage(CHG0 - 0.01)
        if t < 19.0 + 0.2:
            lab, hr, p = bat_state(t)
            wa = 1 - ramp(t, 18.8, 0.4)
            if lab == "Telefon":
                wa *= 1 - ramp(t, 3.4, 0.4)
            elif t < 4.2:
                wa *= ramp(t, 3.8, 0.4)
            paste(im, widget(lab, hr, p, charging=(lab == "Telefon")), CX, 320, wa)
        if t < 3.8:  # hak
            o = 1 - ramp(t, 3.4, 0.4)
            y1, y2 = S["hook_y"]
            paste(im, S["hook"], CX, y1, o)
            a2 = ramp(t, 1.0, 0.45) * o
            paste(im, S["hook2"], CX, y2 + 20 * (1 - ramp(t, 1.0, 0.45)), a2)
        for a, b, spr in S["caps"]:
            if spr is not None and a - 0.1 <= t < b:
                v = win(t, a + 0.25, b, 0.4, 0.35)
                paste(im, spr, CX, 1215 + 16 * (1 - ramp(t, a + 0.25, 0.4)), v)
        if t >= 19.0:  # zwrot na ciemnym ujęciu
            v1 = win(t, 19.3, CHG0, 0.45, 0.35)
            paste(im, S["f1"], CX, S["f_y"][0], v1)
            v2 = win(t, 20.6, CHG0, 0.45, 0.35)
            paste(im, S["f2"], CX, S["f_y"][1] + 20 * (1 - ramp(t, 20.6, 0.45)), v2)
        if t >= CHG0:  # przejście do kremowego tła
            im = Image.blend(im, light(t), smooth((t - CHG0) / XL))
        return im
    return light(t)


def light(t):
    im = bg(LIGHT, t)
    if t < END0:
        o = 1 - ramp(t, END0 - 0.35, 0.35)
        p = 3 + 47 * ease((t - CHG0) / 3.2)
        big = battery_icon(p, w=300, h=140, charging=True)
        paste(im, big, CX, 520, ramp(t, CHG0, 0.4) * o)
        paste(im, text_sprite([f"{int(p)}%"], font(XB, 64), INK), CX, 650, ramp(t, CHG0, 0.4) * o)
        paste(im, S["g1"], CX, 880 + 20 * (1 - ramp(t, CHG0 + 0.3, 0.5)), ramp(t, CHG0 + 0.3, 0.5) * o)
        paste(im, S["g2"], CX, 1120, ramp(t, CHG0 + 1.0, 0.5) * o)
        return im
    draw_end(im, t, END0, S["end"])
    return im


def music(path):
    # fragment 18–49 s utworu: cichy początek, łagodne podniesienie ok. 40,5 s (≈ zwrot w 22. s filmu)
    music_bed(1081, 18.0, TOTAL, path, fade_in=0.8, fade_out=2.0, lufs=-17.0)


if __name__ == "__main__":
    prep()
    if sys.argv[1] == "test":
        out = sys.argv[2]
        sheet(frame, [0.2, 2.0, 4.6, 9.0], f"{out}/a.jpg")
        sheet(frame, [12.5, 16.5, 19.6, 21.5], f"{out}/b.jpg")
        sheet(frame, [23.6, 25.5, 27.2, 29.5], f"{out}/c.jpg")
    elif sys.argv[1] == "frame":
        frame(float(sys.argv[2])).convert("RGB").save(sys.argv[3], quality=90)
    elif sys.argv[1] == "music":
        music(sys.argv[2])
    else:
        wav = sys.argv[2] + ".music.wav"
        music(wav)
        render_av(frame, TOTAL, sys.argv[2], wav)
        os.remove(wav)
