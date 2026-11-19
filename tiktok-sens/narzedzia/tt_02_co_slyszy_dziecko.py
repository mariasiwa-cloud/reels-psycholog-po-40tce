"""TikTok SENS #02 — seria „Co słyszy dziecko, gdy mówisz…”

3 rundy: MÓWISZ (biały dymek) → DZIECKO MOŻE USŁYSZEĆ (lawendowy dymek) → SPRÓBUJ (zielona karta).
Między rundami przesunięcie w bok jak w karuzeli. Potem: „Nie chodzi o idealne słowa. Chodzi o kontakt.”
Muzyka: nowoczesny pop/house 108 BPM na prawdziwych instrumentach (tt_muzyka.py).
Użycie: python3 tt_02_co_slyszy_dziecko.py test OUTDIR | full OUT.mp4
"""
import sys
from tt_base import *
from tt_muzyka import Song, kick_beats
from pedalboard import Reverb, Compressor, HighpassFilter, LowpassFilter, Delay, Chorus

BPM = 108
BEAT = 60 / BPM
TOTAL = 29.5
ROUND = 12 * BEAT  # 6,67 s
OUTRO0, END0 = 36 * BEAT, 44 * BEAT  # 20,0 s / 24,44 s

ROUNDS = [
    ("„Uspokój się!”", ["Moje emocje", "są problemem…"], ["„Widzę, że jest Ci ciężko.", "Pomogę Ci się uspokoić.”"]),
    ("„Nie płacz,", ["To, co czuję,", "się nie liczy…"], ["„Co się stało?", "Opowiesz mi?”"]),
    ("„Ile razy mam", ["Znowu robię", "wszystko źle…"], ["„Spójrz na mnie.", "Teraz buty, potem wychodzimy.”"]),
]
SAY2 = [None, "nic się nie stało.”", "powtarzać?!”"]
S = {}


def bubble(lines, fnt, fg, bgc, w=820, pad=46, tail=None):
    tx = text_sprite(lines, fnt, fg, gap=1.12, pad=0)
    h = tx.height + 2 * pad
    m = 60
    im = Image.new("RGBA", (w + 2 * m, h + 2 * m + 30), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((m, m + 14, m + w, m + h + 14), 44, fill=(40, 30, 50, 55))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((m, m, m + w, m + h), 44, fill=bgc + (255,))
    if tail == "left":
        d.polygon([(m + 90, m + h - 2), (m + 150, m + h - 2), (m + 80, m + h + 30)], fill=bgc + (255,))
    if tail == "right":
        d.polygon([(m + w - 90, m + h - 2), (m + w - 150, m + h - 2), (m + w - 80, m + h + 30)], fill=bgc + (255,))
    im.alpha_composite(tx, (int(m + w / 2 - tx.width / 2), int(m + pad - 6)))
    return im


def prep():
    S["head"] = text_sprite([[("CO SŁYSZY DZIECKO,", INK)], [("GDY MÓWISZ…", LAVD)]], font(XB, 66), INK, gap=1.05)
    S["l_say"] = text_sprite(["MÓWISZ:"], font(B, 34), INK, pad=8)
    S["l_hear"] = text_sprite(["DZIECKO MOŻE USŁYSZEĆ:"], font(B, 34), LAVD, pad=8)
    S["l_try"] = text_sprite(["SPRÓBUJ ZAMIAST TEGO:"], font(B, 34), GREEN, pad=8)
    S["say"], S["hear"], S["try"] = [], [], []
    for i, (say, hear, tr) in enumerate(ROUNDS):
        lines = [say] if not SAY2[i] else [say, SAY2[i]]
        S["say"].append(bubble(lines, fit_font(lines, XB, 58, 740), INK, WHITE, pad=30, tail="right"))
        S["hear"].append(bubble(hear, fit_font(hear, CV, 78, 740), WHITE, LAVD, pad=30, tail="right"))
        card = bubble(tr, fit_font(tr, B, 46, 700), WHITE, GREEN, pad=30)
        d = ImageDraw.Draw(card)  # znaczek ✓
        d.ellipse((60 + 760 - 34, 60 - 34, 60 + 760 + 34, 60 + 34), fill=YEL + (255,))
        d.line([(60 + 760 - 15, 60 + 1), (60 + 760 - 3, 60 + 13), (60 + 760 + 17, 60 - 11)], fill=INK + (255,), width=8)
        S["try"].append(card)
    # układ pionowy liczony z prawdziwych wysokości (bez nachodzenia)
    S["lay"] = []
    for i in range(3):
        y = 425
        lay = {}
        for key, lab in (("say", "l_say"), ("hear", "l_hear"), ("try", "l_try")):
            lay[lab] = y + 16
            y += 40
            spr = S[key][i]
            vis = spr.height - 120 - 30
            lay[key] = y - 60 + spr.height / 2
            y += vis + 30
        S["lay"].append(lay)
        assert y - 30 < 1355, (i, y)
    S["o1"] = text_sprite(["Nie chodzi", "o idealne słowa."], font(XB, 84), INK, gap=1.08)
    S["o2"] = text_sprite([[("Chodzi o ", INK), ("kontakt.", LAVD)]], font(XB, 84), INK)
    S["o3"] = text_sprite(["Każdy rodzic czasem tak mówi.", "Liczy się to, co robisz najczęściej."], font(M, 44), INK)
    S["logo"] = asset("logo_pion.png", 540)
    S["motto"] = text_sprite(["Każda emocja ma sens."], font(CV, 92), LAVD)
    S["btn"] = pill("Wsparcie dla rodziców", font(B, 46), WHITE, LAVD, padx=60, h=124)
    S["www"] = text_sprite(["senswroclaw.pl · Wrocław"], font(B, 48), INK)
    # tło: kremowe z dużą miękką plamą petrolu u góry
    base = bg(LIGHT, 0).copy()
    S["bgshape"] = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((-300, -900, W + 300, 420), fill=(30, 52, 59, 26))
    S["bgshape"] = sh.filter(ImageFilter.GaussianBlur(60))


def dots(im, k, a):
    lay = Image.new("RGBA", (200, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(3):
        x = 100 + (i - 1) * 46
        col = LAVD if i <= k else (210, 196, 214)
        d.ellipse((x - 11, 9, x + 11, 31), fill=col + (255,))
    paste(im, lay, CX, 392, a)


def frame(t):
    im = bg(LIGHT, t)
    im.alpha_composite(S["bgshape"])
    if t < OUTRO0:
        r = min(2, int(t // ROUND))
        lt = t - r * ROUND
        hout = 1 - ramp(t, OUTRO0 - 0.4, 0.4)
        paste(im, S["head"], CX, 285, hout)
        dots(im, r, hout)
        # karuzela: wjazd z prawej, wyjazd w lewo
        xin = 0 if (r == 0 and lt < 0.01) else 700 * (1 - ramp(lt, 0, 0.4)) if r > 0 else 0
        xout = -700 * ramp(lt, ROUND - 0.32, 0.32) if r < 2 else 0
        fo = (1 - ramp(lt, ROUND - 0.4, 0.4)) if r == 2 else 1.0
        dx = xin + xout
        L = S["lay"][r]
        a1 = 1.0 if r == 0 else ramp(lt, 0, 0.3)
        paste(im, S["l_say"], CX - 410 + S["l_say"].width / 2 + dx, L["l_say"], a1 * fo)
        paste(im, S["say"][r], CX + dx, L["say"], a1 * fo)
        a2 = ramp(lt, 1.3, 0.4)
        dim = 1 - 0.3 * ramp(lt, 3.6, 0.5)
        paste(im, S["l_hear"], CX - 410 + S["l_hear"].width / 2 + dx, L["l_hear"], a2 * fo)
        paste(im, S["hear"][r], CX + dx, L["hear"] + 24 * (1 - a2), a2 * dim * fo)
        a3 = ramp(lt, 3.6, 0.45)
        paste(im, S["l_try"], CX - 410 + S["l_try"].width / 2 + dx, L["l_try"], a3 * fo)
        paste(im, S["try"][r], CX + dx, L["try"] + 30 * (1 - a3), a3 * fo)
        return im
    if t < END0:
        out = 1 - ramp(t, END0 - 0.35, 0.35)
        a = ramp(t, OUTRO0, 0.5)
        paste(im, S["o1"], CX, 640 + 30 * (1 - a), a * out)
        b = ramp(t, OUTRO0 + 1.0, 0.5)
        paste(im, S["o2"], CX, 870 + 24 * (1 - b), b * out)
        p = ramp(t, OUTRO0 + 1.6, 0.6)
        if p > 0:
            f = font(XB, 84)
            w0, w1 = f.getlength("Chodzi o "), f.getlength("Chodzi o kontakt.")
            x0 = CX - w1 / 2 + w0
            d = ImageDraw.Draw(im)
            pts = [(x0 + i * 6, 935 + 7 * math.sin(i / 9.0)) for i in range(int((w1 - w0) / 6 * p) + 1)]
            if len(pts) > 1:
                d.line(pts, fill=LAV + (int(255 * out),), width=10, joint="curve")
        c = ramp(t, OUTRO0 + 2.0, 0.5)
        paste(im, S["o3"], CX, 1110, c * out)
        return im
    items = [("logo", 600, END0), ("motto", 960, END0 + 0.5), ("btn", 1110, END0 + 1.0), ("www", 1250, END0 + 1.4)]
    for k, y, t0 in items:
        a = ramp(t, t0, 0.5)
        paste(im, S[k], CX, y + 20 * (1 - a), a)
    return im


def music(path):
    s = Song(BPM, TOTAL)
    ep = s.track("ep", 0, 4)        # Tine Electric Piano
    gt = s.track("gt", 0, 28)       # Muted Guitar
    bs = s.track("bass", 0, 38)     # Synth Bass 1
    ld = s.track("lead", 0, 81)     # Saw Lead (krótko = pluck)
    vx = s.track("vox", 0, 54)      # Synth Voice (tylko w przerwie)
    dr = s.drums(kit=26)            # Dance kit
    prog = [([53, 57, 60, 64], 41), ([55, 59, 62, 69], 43), ([52, 55, 59, 62], 40), ([57, 60, 64, 67, 71], 45)]
    hook = [(0, 76), (0.75, 74), (1.5, 72), (2.5, 69), (3.0, 72), (4.0, 76), (4.75, 79), (5.5, 76), (6.5, 74)]
    end_b = TOTAL / BEAT
    for bar in range(int(end_b // 4) + 1):
        b0 = bar * 4
        ch, root = prog[bar % 4]
        brk = 36 <= b0 < 44
        full = 12 <= b0 < 36 or b0 >= 44
        if b0 >= 52:  # ostatni akord wybrzmiewa
            ep.chord(b0, [57, 60, 64, 67, 71], 4, 78)
            bs.note(b0, 45, 2, 90)
            dr.hit(b0, 49, 90)
            break
        if brk:  # przerwa: lżej, ale muzyka dalej „idzie” (pół-tempo)
            ep.chord(b0, ch, 1.9, 96, strum=0.03)
            ep.chord(b0 + 2, ch, 1.9, 90, strum=0.03)
            vx.chord(b0, ch[1:], 3.8, 78)
            bs.note(b0, root, 3.6, 86)
            dr.hit(b0, 36, 92)
            dr.hit(b0 + 2.5, 36, 70)
            dr.hit(b0 + 1, 39, 70)
            dr.hit(b0 + 3, 39, 76)
            for e in range(8):
                dr.hit(b0 + e * 0.5 + 0.25, 42, 58)
            continue
        for e in range(4):  # akordy na „i” (house)
            ep.chord(b0 + e + 0.5, ch, 0.42, 84 if full else 70)
        if full:
            for k in range(16):  # tłumiona gitara szesnastkami
                n = ch[(k * 3) % len(ch)] + 12
                gt.note(b0 + k * 0.25, n, 0.18, 70 if k % 4 == 2 else 52)
            for off, oc in [(0, 0), (0.75, 0), (1.5, 12), (2.0, 0), (2.75, 0), (3.5, 12)]:
                bs.note(b0 + off, root + oc, 0.45, 100 if off in (0, 2.0) else 84)
            if bar % 2 == 0:
                for off, n in hook:
                    if off < 8:
                        ld.note(b0 + off, n, 0.3, 74)
        else:
            bs.note(b0, root, 1.8, 78)
            bs.note(b0 + 2, root, 1.8, 72)
        for b in range(4):
            tb = b0 + b
            dr.hit(tb, 36, 118 if full else 90)
            if full and b % 2 == 1:
                dr.hit(tb, 39, 100)
            dr.hit(tb + 0.5, 46 if full else 42, 70 if full else 55)
            if full:
                dr.hit(tb + 0.25, 42, 48)
                dr.hit(tb + 0.75, 42, 52)
    for st in (12, 24, 44):  # crash + uderzenie na wejściach
        dr.hit(st, 49, 100)
        s.impact(st, 0.45)
    for v, b in enumerate([22, 22.5, 23, 23.25, 23.5, 23.75]):  # przejście przed rundą 3
        dr.hit(b, 39, 60 + v * 8)
    s.riser(9, 3, 0.035)
    s.riser(41, 3, 0.035)
    for r in range(3):  # jasny akcent przy „SPRÓBUJ”
        ld.note(r * 12 + 6.5, 84, 0.6, 70)
        ld.note(r * 12 + 6.5, 88, 0.6, 62)
    kicks = kick_beats(12, 36) + kick_beats(44, 52) + kick_beats(0, 12)
    s.render(path,
             gains={"ep": 0.55, "gt": 0.32, "bass": 0.75, "lead": 0.28, "vox": 0.3, "drums": 0.9, "fx": 0.6,
                    "_duck": ("ep", "gt", "bass", "lead")},
             fx={"ep": [HighpassFilter(140), Chorus(rate_hz=0.6, depth=0.15, mix=0.25), Reverb(room_size=0.45, wet_level=0.18)],
                 "gt": [HighpassFilter(250), Delay(delay_seconds=BEAT * 0.75, feedback=0.25, mix=0.15)],
                 "lead": [LowpassFilter(3800), Delay(delay_seconds=BEAT * 0.75, feedback=0.3, mix=0.22),
                          Reverb(room_size=0.6, wet_level=0.25)],
                 "vox": [Reverb(room_size=0.8, wet_level=0.4)],
                 "bass": [LowpassFilter(900), Compressor(threshold_db=-18, ratio=3)],
                 "drums": [Compressor(threshold_db=-14, ratio=2.2, attack_ms=5, release_ms=80)]},
             sidechain=kicks, duck=0.5, lowpass_until=(0, 10, 1400))


if __name__ == "__main__":
    prep()
    if sys.argv[1] == "test":
        out = sys.argv[2]
        sheet(frame, [0.0, 2.2, 5.5, 6.55], f"{out}/s1.jpg")
        sheet(frame, [7.4, 12.0, 18.5, 19.9], f"{out}/s2.jpg")
        sheet(frame, [21.0, 23.5, 26.5, 29.0], f"{out}/s3.jpg")
    elif sys.argv[1] == "music":
        music(sys.argv[2])
    else:
        music("/tmp/tt02.wav")
        render(frame, TOTAL, sys.argv[2], "/tmp/tt02.wav")
