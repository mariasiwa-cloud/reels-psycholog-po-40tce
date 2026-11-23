"""Prawdziwe nagrania (stock) i gotowa muzyka do filmów TikTok SENS.

Źródła (sprawdzone 23.11.2026):
- wideo: Coverr (cdn.coverr.co, licencja Coverr: użycie komercyjne bez atrybucji; bez klipów „AI generated”
  i bez „premium”).
- wideo: Mixkit, tylko klipy z „Mixkit Stock Video Free License” (użycie komercyjne i w social mediach firmy,
  bez atrybucji). Klipy z „Restricted License” NIE wolno używać (tylko projekty prywatne).
- muzyka: Mixkit, „Mixkit Stock Music Free License” (social media, reklamy online; nie wolno remiksować
  ani rejestrować w Content ID). Utwór przycinamy, wyciszamy i ustawiamy jako tło — bez przeróbek.
Pliki pobierają się same do narzedzia/klipy/ (ignorowane przez git).

Clip(id, start, dur, x=0.5) — klip przycięty do 9:16 (x = poziome położenie kadru 0..1), powolny zoom 1.00→1.06.
music_bed(...) — fragment utworu: wejście/wyjście, łagodny EQ (bez ostrych 5–10 kHz), głośność −17 LUFS, TP −1,5 dB.
"""
import os, subprocess, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "klipy")
W, H, FPS = 1080, 1920, 30


def smooth(x):
    """łagodne przejście (smoothstep) — bez gwałtownego startu przy przenikaniu jasne/ciemne"""
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def mixkit_video(vid):
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, f"mixkit_{vid}_1080.mp4")
    if not os.path.exists(fn) or os.path.getsize(fn) < 10000:
        subprocess.run(["curl", "-s", "-f", "-o", fn, f"https://assets.mixkit.co/videos/{vid}/{vid}-1080.mp4"], check=True)
    return fn


def coverr_video(slug):
    """Coverr (licencja Coverr: darmowe użycie komercyjne, bez atrybucji; nie używać klipów z oznaczeniem AI)."""
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, f"{slug}_1080.mp4")
    if not os.path.exists(fn) or os.path.getsize(fn) < 10000:
        subprocess.run(["curl", "-s", "-f", "-L", "-o", fn, f"https://cdn.coverr.co/videos/{slug}/1080p.mp4"], check=True)
    return fn


def mixkit_music(mid):
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, f"mixkit_music_{mid}.mp3")
    if not os.path.exists(fn) or os.path.getsize(fn) < 10000:
        subprocess.run(["curl", "-s", "-f", "-o", fn, f"https://assets.mixkit.co/music/{mid}/{mid}.mp3"], check=True)
    return fn


def probe(fn):
    o = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height:format=duration", "-of", "json", fn],
                                  capture_output=True, text=True).stdout)
    return o["streams"][0]["width"], o["streams"][0]["height"], float(o["format"]["duration"])


GRADE = "eq=contrast=0.96:saturation=0.88:gamma=1.02,colorbalance=rs=0.03:gs=0.01:bs=-0.03:rm=0.02:bm=-0.02"


class Clip:
    """Klip 9:16. start/dur w sekundach źródła (dur = długość na ekranie), speed<1 zwalnia.
    x, y = położenie kadru 9:16 w źródle (0..1). zoom: (z0, z1) powolne przybliżenie w czasie klipu.
    dark: przyciemnienie 0..1 (pod jasny tekst)."""

    def __init__(self, vid, start, dur, x=0.5, y=0.5, zoom=(1.0, 1.06), speed=1.0, dark=0.0, grade=GRADE, mirror=False):
        self.fn = mixkit_video(vid) if isinstance(vid, int) else coverr_video(vid) if vid.startswith("coverr-") else vid
        self.vid, self.start, self.dur, self.speed = vid, start, dur, speed
        sw, sh, sd = probe(self.fn)
        assert start + dur * speed <= sd + 0.05, (vid, start, dur, sd)
        self.z0, self.z1, self.dark = zoom[0], zoom[1], dark
        zr = max(zoom) / min(zoom)
        if sw / sh > W / H:  # poziome źródło: wycinamy pionowy pas
            ch_, cw_ = sh, int(sh * W / H) // 2 * 2
        else:
            cw_, ch_ = sw, int(sw * H / W) // 2 * 2
        ox, oy = int((sw - cw_) * x) // 2 * 2, int((sh - ch_) * y) // 2 * 2
        self.bw, self.bh = int(W * zr) // 2 * 2, int(H * zr) // 2 * 2
        vf = [f"crop={cw_}:{ch_}:{ox}:{oy}", f"setpts=PTS/{speed}" if speed != 1 else None, f"fps={FPS}",
              f"scale={self.bw}:{self.bh}:flags=lanczos", "hflip" if mirror else None, grade, "unsharp=5:5:0.4"]
        self.vf = ",".join(v for v in vf if v)
        self.p, self.pos, self.last, self.last_buf = None, None, None, None

    def _open(self, n):
        if self.p:
            self.p.kill()
        t = self.start + n / FPS * self.speed
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", self.fn, "-vf", self.vf, "-an",
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL)
        self.pos = n

    def frame(self, lt):
        """lt = czas lokalny w klipie (s) -> PIL RGBA 1080x1920"""
        n = max(0, min(int(round(lt * FPS)), int(self.dur * FPS) - 1))
        if self.last is not None and self.last[0] == n:
            return self.last[1]
        if self.p is None or n < self.pos or n > self.pos + 45:
            self._open(n)
        fsz = self.bw * self.bh * 3
        buf = None
        while self.pos <= n:
            b = self.p.stdout.read(fsz)
            if len(b) < fsz:
                break
            buf = self.last_buf = b
            self.pos += 1
        buf = buf or self.last_buf
        a = np.frombuffer(buf, np.uint8).reshape(self.bh, self.bw, 3)
        p = n / max(1, self.dur * FPS - 1)
        z = self.z0 + (self.z1 - self.z0) * p
        k = min(self.z0, self.z1) / z  # 1 = całe okno, mniej = przybliżenie
        cw, ch = self.bw * k, self.bh * k
        x0, y0 = (self.bw - cw) / 2, (self.bh - ch) / 2
        im = Image.fromarray(a)
        im = im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
        if self.dark > 0:
            im = Image.blend(im, Image.new("RGB", (W, H), (14, 28, 32)), self.dark)
        im = im.convert("RGBA")
        self.last = (n, im)
        return im

    def close(self):
        if self.p:
            self.p.kill()
            self.p = None


def music_bed(mid, start, total, out_wav, fade_in=0.6, fade_out=1.6, lufs=-17.0, lowpass=9500, shelf_db=-2.5):
    """Fragment utworu Mixkit jako tło: [start, start+total], miękkie wejście/wyjście, łagodny EQ,
    normalizacja dwuprzebiegowa do `lufs` (TP -1.5)."""
    src = mixkit_music(mid)
    af = (f"atrim=start={start}:duration={total},asetpts=PTS-STARTPTS,"
          f"afade=t=in:st=0:d={fade_in},afade=t=out:st={total - fade_out}:d={fade_out},"
          f"lowpass=f={lowpass}:p=1,highshelf=f=6000:g={shelf_db},highpass=f=35")
    tmp = out_wav + ".pre.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", af, "-ar", "44100", "-ac", "2", tmp], check=True)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp, "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=7:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(r[r.rfind("{"):r.rfind("}") + 1])
    ln = (f"loudnorm=I={lufs}:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", ln, "-ar", "44100", out_wav], check=True)
    os.remove(tmp)
    return out_wav


def render_av(frame_fn, total, out_mp4, music_wav):
    """Obraz z frame_fn + gotowe tło muzyczne (już znormalizowane) — bez dodatkowego loudnorm."""
    silent = out_mp4 + ".silent.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "19", "-preset", "medium",
                          "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    for n in range(int(round(total * FPS))):
        p.stdin.write(frame_fn(n / FPS).convert("RGB").tobytes())
    p.stdin.close()
    assert p.wait() == 0
    tmp = out_mp4 + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", music_wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest",
                    "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, out_mp4)
    os.remove(silent)


# ---------- wspólne elementy graficzne (karty, karta końcowa) ----------
def caption_card(lines, fnt, w=None, fg=None, bgc=(255, 255, 255), pad=(48, 34), r=40, alpha=255, align="center"):
    """Biała (lub kolorowa) karta z tekstem. lines jak w text_sprite (str albo lista (tekst, kolor))."""
    from tt_base import text_sprite, card_sprite, INK
    tx = text_sprite(lines, fnt, fg or INK, gap=1.12, pad=0, align=align)
    cw = w or tx.width + 2 * pad[0]
    ch = tx.height + 2 * pad[1]
    c, m = card_sprite(cw, ch, r=r, fill=bgc + (alpha,), shadow=(20, 20, 30, 70))
    x = m + (cw - tx.width) // 2 if align == "center" else m + pad[0]
    c.alpha_composite(tx, (int(x), m + pad[1] - 4))
    return c


def end_card(cta, sub=None, logo_w=460):
    """Sprite'y karty końcowej SENS: logo + motto + CTA + (podpis) + www."""
    from tt_base import asset, text_sprite, pill, font, CV, B, M, LAVD, INK, WHITE
    S = {"logo": asset("logo_pion.png", logo_w),
         "motto": text_sprite(["Każda emocja ma sens."], font(CV, 92), LAVD),
         "btn": pill(cta, font(B, 46), WHITE, LAVD, padx=56, h=124),
         "www": text_sprite(["senswroclaw.pl"], font(B, 50), INK)}
    if sub:
        S["sub"] = text_sprite([sub], font(M, 40), INK)
    return S


def draw_end(im, t, t0, S, cx=510):
    """Karta końcowa: elementy wchodzą kolejno od t0. Układ liczony z wysokości sprite'ów (y 300–1340)."""
    from tt_base import paste, ramp
    order = ["logo", "motto", "btn"] + (["sub"] if "sub" in S else []) + ["www"]
    gaps = {"logo": 0, "motto": 22, "btn": 8, "sub": 14, "www": 0}
    tot = sum(S[k].height for k in order) + sum(gaps[k] for k in order)
    y = max(250, 800 - tot / 2)
    for i, k in enumerate(order):
        a = ramp(t, t0 + 0.3 * i, 0.5)
        paste(im, S[k], cx, y + S[k].height / 2 + 18 * (1 - a), a)
        y += S[k].height + gaps[k]
    assert y < 1345, y
