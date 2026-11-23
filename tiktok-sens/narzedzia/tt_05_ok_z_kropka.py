"""TikTok SENS #05 — „Ok.” z kropką (myśli vs fakty, dorośli / relacje).

Koncept: wysyłasz długą wiadomość, dostajesz „Ok.” — i głowa w 3 sekundy pisze cały dramat (jest zła, coś zrobiłam,
już mnie nie lubi). Stop: co wiesz na pewno? Tylko „Ok.”. Inne wyjaśnienia. Myśl to nie fakt („czytanie w myślach”).
Wideo: Coverr (licencja Coverr, użycie komercyjne): texting-at-twilight, angry-woman-texting-9562,
contemplative-woman-by-the-roadside, young-woman-checking-smartphone-outdoors, outdoor-messaging-break.
Muzyka: Mixkit „Lo-Fi 02” (Lily J, Stock Music Free License) — miękki lo-fi z cichym bitem, ok. 83 BPM.
Użycie: python3 tt_05_ok_z_kropka.py test OUTDIR | full OUT.mp4
"""
import sys
from tt_base import *
from tt_klipy import smooth, Clip, music_bed, render_av, caption_card, end_card, draw_end

XF = 0.45
SCENES = [
    (0.0, 3.8, dict(vid="coverr-texting-at-twilight", start=2.0, x=0.62, zoom=(1.0, 1.05))),
    (3.8, 7.8, dict(vid="coverr-angry-woman-texting-9562", start=6.0, x=0.40, zoom=(1.15, 1.22))),
    (7.8, 11.6, dict(vid="coverr-contemplative-woman-by-the-roadside", start=13.0, x=0.74, zoom=(1.0, 1.05))),
    (11.6, 20.2, dict(vid="coverr-young-woman-checking-smartphone-outdoors", start=1.0, x=0.45, zoom=(1.0, 1.06),
                      dark=0.25)),
    (20.2, 24.4, dict(vid="coverr-outdoor-messaging-break", start=4.0, x=0.55, zoom=(1.0, 1.05))),
]
FOOT_END, TOTAL = 24.4, 29.6
THOUGHTS = [(4.3, "Jest na mnie zła."), (6.7, "Coś zrobiłam nie tak."), (9.1, "Pewnie już mnie nie lubi.")]
OTHER = [(14.8, "Prowadzi auto."), (16.0, "Jest w pracy."), (17.2, "„Ok.” znaczy po prostu ok.")]
GRAY = (236, 233, 239)
S = {}
CLIPS = []


def vis_h(spr):
    return spr.height - 140


def bubble(lines, fnt, fg, bgc, pad=(34, 22), r=34):
    tx = text_sprite(lines, fnt, fg, gap=1.1, pad=0, align="left")
    im = Image.new("RGBA", (tx.width + 2 * pad[0], tx.height + 2 * pad[1]), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=bgc + (255,))
    im.alpha_composite(tx, (pad[0], pad[1] - 4))
    return im


def chat_panel(show_reply=True):
    w = 860
    out = bubble(["Hej! Sorki za sobotę, wiem,", "że wyszło trochę chaotycznie.", "Wszystko między nami ok?"],
                 font(M, 38), WHITE, LAVD)
    rep = bubble(["Ok."], font(XB, 64), INK, GRAY, pad=(40, 18))
    h = 40 + 56 + 26 + out.height + 26 + rep.height + 40
    c, m = card_sprite(w, h, r=46, shadow=(10, 10, 20, 90))
    d = ImageDraw.Draw(c)
    d.ellipse((m + 36, m + 34, m + 36 + 60, m + 34 + 60), fill=LAVL + (255,))
    d.text((m + 66 - font(B, 32).getlength("P") / 2, m + 44), "P", font=font(B, 32), fill=LAVD)
    d.text((m + 112, m + 36), "Przyjaciółka", font=font(B, 36), fill=INK)
    d.text((m + 114, m + 80), "teraz", font=font(M, 24), fill=(130, 130, 140))
    y = m + 40 + 56 + 26
    c.alpha_composite(out, (m + w - 36 - out.width, y))
    y += out.height + 26
    if show_reply:
        c.alpha_composite(rep, (m + 36, y))
    return c


def thought(text):
    fnt = font(CV, 76)
    tx = text_sprite([text], fnt, WHITE, pad=0)
    w, h = tx.width + 100, tx.height + 50
    im = Image.new("RGBA", (w + 80, h + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 14, 40 + w, 14 + h), h // 2, fill=(20, 10, 30, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 4, 40 + w, 4 + h), h // 2, fill=LAVD + (255,))
    d.ellipse((26, h - 4, 50, h + 20), fill=LAVD + (255,))
    d.ellipse((8, h + 22, 22, h + 36), fill=LAVD + (255,))
    im.alpha_composite(tx, (40 + 50, 4 + 21))
    return im


def chip(text):
    return caption_card([text], font(B, 52), pad=(44, 26), r=36)


def prep():
    for a, b, kw in SCENES:
        kw = dict(kw)
        CLIPS.append((a, b, Clip(kw.pop("vid"), kw.pop("start"), b - a + XF + 0.1, **kw)))
    S["panel"] = chat_panel()
    S["panel_y"] = 250 + vis_h(S["panel"]) / 2
    S["kropka"] = caption_card([[("Z kropką.", WHITE)]], font(XB, 80), bgc=LAVD, pad=(60, 30))
    S["head"] = caption_card(["Twoja głowa", [("3 sekundy później:", LAVD)]], font(XB, 56), pad=(50, 32))
    S["thoughts"] = [(t0, thought(txt)) for t0, txt in THOUGHTS]
    S["stop"] = caption_card([[("STOP.", (196, 85, 63))], [("Co wiesz na pewno?", INK)]], font(XB, 70), pad=(60, 40))
    S["only"] = bubble(["Ok."], font(XB, 64), INK, GRAY, pad=(40, 18))
    S["only_l"] = text_sprite([[("Tylko tyle.", WHITE)]], font(CV, 80), WHITE, pad=10)
    S["oth_h"] = caption_card([[("Inne możliwe wyjaśnienia:", INK)]], font(XB, 54), pad=(50, 32))
    S["chips"] = [(t0, chip(txt)) for t0, txt in OTHER]
    S["e1"] = caption_card([[("Myśl", INK), (" to nie ", INK), ("fakt.", LAVD)]], font(XB, 92), pad=(64, 40))
    S["e2"] = caption_card(["Psychologowie nazywają to", [("„czytaniem w myślach”.", LAVD)]], font(B, 48), pad=(50, 32))
    S["end"] = end_card("Zapisz na następne „ok.”")


def footage(t):
    cur = [(a, b, c) for a, b, c in CLIPS if a <= t < b + XF]
    a, b, c = cur[0]
    im = c.frame(t - a)
    if len(cur) > 1 and t >= cur[1][0]:
        a2, b2, c2 = cur[1]
        im = Image.blend(im, c2.frame(t - a2), smooth((t - a2) / XF))
    return im.copy()


def over(im, t):
    if t < 3.8:  # hak: czat od pierwszej klatki
        o = 1 - ramp(t, 3.45, 0.35)
        paste(im, S["panel"], CX, S["panel_y"], o)
        a = ramp(t, 1.2, 0.4) * o
        paste(im, S["kropka"], CX, S["panel_y"] + vis_h(S["panel"]) / 2 + 60 + vis_h(S["kropka"]) / 2
              + 16 * (1 - ramp(t, 1.2, 0.4)), a)
    if 3.8 <= t < 11.6:
        o = 1 - ramp(t, 11.25, 0.35)
        paste(im, S["head"], CX, 330, ramp(t, 3.9, 0.4) * o)
        y = 330 + vis_h(S["head"]) / 2 + 40
        for t0, spr in S["thoughts"]:
            a = ramp(t, t0, 0.4) * o
            paste(im, spr, CX + 10, y + spr.height / 2 + 14 * (1 - ramp(t, t0, 0.4)), a)
            y += spr.height + 18
        assert y < 1360
    if 11.6 <= t < 14.6:
        o = 1 - ramp(t, 14.25, 0.35)
        paste(im, S["stop"], CX, 620, ramp(t, 11.8, 0.4) * o)
        a = ramp(t, 12.6, 0.4) * o
        paste(im, S["only"], CX - 120, 900, a)
        paste(im, S["only_l"], CX + 140, 900, a)
    if 14.6 <= t < 20.2:
        o = 1 - ramp(t, 19.85, 0.35)
        paste(im, S["oth_h"], CX, 420, ramp(t, 14.6, 0.4) * o)
        y = 420 + vis_h(S["oth_h"]) / 2 + 40
        for t0, spr in S["chips"]:
            a = ramp(t, t0, 0.4) * o
            paste(im, spr, CX, y + vis_h(spr) / 2 + 14 * (1 - ramp(t, t0, 0.4)), a)
            y += vis_h(spr) + 26
        assert y < 1360
    if 20.2 <= t < FOOT_END + 0.4:
        o = 1 - ramp(t, FOOT_END - 0.05, 0.4)
        paste(im, S["e1"], CX, 760, ramp(t, 20.4, 0.45) * o)
        a = ramp(t, 21.6, 0.45) * o
        paste(im, S["e2"], CX, 760 + vis_h(S["e1"]) / 2 + 30 + vis_h(S["e2"]) / 2 + 16 * (1 - ramp(t, 21.6, 0.45)), a)
    return im


def light(t):
    im = bg(LIGHT, t)
    draw_end(im, t, FOOT_END + 0.2, S["end"])
    return im


def frame(t):
    if t < FOOT_END:
        return over(footage(t), t)
    if t < FOOT_END + XF:
        a = over(footage(FOOT_END - 0.01), t)
        return Image.blend(a, light(t), smooth((t - FOOT_END) / XF))
    return light(t)


def music(path):
    music_bed(764, 2.0, TOTAL, path, fade_in=0.5, fade_out=2.0, lufs=-17.5)


if __name__ == "__main__":
    prep()
    if sys.argv[1] == "test":
        out = sys.argv[2]
        sheet(frame, [0.0, 2.0, 5.0, 10.0], f"{out}/a.jpg")
        sheet(frame, [13.5, 18.5, 22.5, 28.0], f"{out}/b.jpg")
    elif sys.argv[1] == "frame":
        frame(float(sys.argv[2])).convert("RGB").save(sys.argv[3], quality=90)
    elif sys.argv[1] == "music":
        music(sys.argv[2])
    else:
        wav = sys.argv[2] + ".music.wav"
        music(wav)
        render_av(frame, TOTAL, sys.argv[2], wav)
        os.remove(wav)
