"""Muzyka do filmów TikTok SENS — prawdziwe instrumenty (bank GeneralUser GS, licencja pozwala na
użycie komercyjne) + efekty studyjne (pedalboard): pogłos, kompresja, „pompowanie” (sidechain), filtr.

Zamiast „piszczących” tonów sinusowych: piano elektryczne, gitara, bas, perkusja, syntezatory.
Instalacja (raz): sh pobierz_dzwieki.sh  (+ pip install pedalboard; pip install --no-deps tinysoundfont)

Użycie:
    s = Song(bpm=108, total=29.5)
    ep = s.track("ep", 0, 4)            # bank 0, program GM 4 (Tine Electric Piano)
    ep.chord(beat=0, notes=[53,57,60,64], dur=0.4, vel=80)
    dr = s.drums(kit=26)                # 26 = Dance, 25 = 808/909, 24 = Electronic, 0 = Standard
    dr.hit(beat=0, note=36, vel=110)    # 36 stopa, 38 werbel, 39 klask, 42 hi-hat, 46 otwarty, 49 crash
    s.render("music.wav", sidechain=[...beaty stopy...], fx={"ep": {...}})

Unikać: dzwoneczków, celesty, kalimby, pozytywki (brzmią dziecinnie), prostych arpeggiów durowych
i długich, wolnych padów. Lepiej: akordy septymowe/nonowe, rytm house/pop, bas synkopowany.
"""
import os
import numpy as np
import tinysoundfont
from pedalboard import (Pedalboard, Reverb, Compressor, HighpassFilter, LowpassFilter, Limiter, Delay,
                        Chorus, Gain)

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
SF2 = os.path.join(HERE, "sf", "GeneralUser-GS", "GeneralUser-GS.sf2")


class Track:
    def __init__(self, song, name, bank, preset, drums=False):
        self.song, self.name, self.bank, self.preset, self.drums = song, name, bank, preset, drums
        self.ev = []  # (time_s, note, dur_s, vel)

    def note(self, beat, note, dur, vel=90):
        b = self.song.beat
        self.ev.append((beat * b, int(note), max(0.03, dur * b), int(max(1, min(127, vel)))))

    def chord(self, beat, notes, dur, vel=85, strum=0.0):
        for i, n in enumerate(notes):
            self.note(beat + i * strum, n, dur, vel - 3 * i)

    def hit(self, beat, note, vel=100, dur=0.25):
        self.note(beat, note, dur, vel)

    def render(self):
        syn = tinysoundfont.Synth(samplerate=SR, gain=0)
        sid = syn.sfload(SF2)
        ch = 9 if self.drums else 0
        syn.program_select(ch, sid, self.bank, self.preset)
        n = int(self.song.total * SR) + SR
        out = np.zeros((n, 2), dtype=np.float32)
        evs = []
        for t, note, d, v in self.ev:
            evs.append((t, 1, note, v))
            evs.append((t + d, 0, note, 0))
        evs.sort(key=lambda e: (e[0], e[1]))
        pos = 0
        for t, on, note, v in evs:
            i = min(n, int(t * SR))
            if i > pos:
                buf = np.frombuffer(syn.generate(i - pos), dtype=np.float32).reshape(-1, 2)
                out[pos:i] = buf
                pos = i
            if on:
                syn.noteon(ch, note, v)
            else:
                syn.noteoff(ch, note)
        if pos < n:
            out[pos:] = np.frombuffer(syn.generate(n - pos), dtype=np.float32).reshape(-1, 2)
        return out


class Song:
    def __init__(self, bpm, total):
        self.bpm, self.total = bpm, total
        self.beat = 60.0 / bpm
        self.tracks = {}
        self.extra = {}  # nazwa -> stereo array (efekty: riser, uderzenie)

    def track(self, name, bank, preset):
        self.tracks[name] = Track(self, name, bank, preset)
        return self.tracks[name]

    def drums(self, kit=26, name="drums"):
        self.tracks[name] = Track(self, name, 128, kit, drums=True)
        return self.tracks[name]

    def t(self, beat):
        return beat * self.beat

    # --- efekty dźwiękowe zrobione w kodzie ---
    def riser(self, start_beat, beats, gain=0.25):
        L = int(self.t(beats) * SR)
        x = np.random.default_rng(3).standard_normal(L).astype(np.float32)
        env = (np.arange(L) / L) ** 2.5
        out = np.zeros((L, 2), np.float32)
        hp = HighpassFilter(cutoff_frequency_hz=400)
        blk = 2048
        for i in range(0, L, blk):  # filtr otwiera się w górę
            hp.cutoff_frequency_hz = 400 + 6000 * (i / L) ** 2
            seg = hp.process(x[i:i + blk].reshape(1, -1), SR, reset=False)[0]
            out[i:i + len(seg), 0] = seg
            out[i:i + len(seg), 1] = seg
        out *= env[:, None] * gain
        out = Pedalboard([LowpassFilter(9000), Reverb(room_size=0.7, wet_level=0.35, dry_level=0.8)])(out.T.copy(), SR).T
        self._place("fx", self.t(start_beat), out)

    def impact(self, beat, gain=0.5):
        L = int(1.6 * SR)
        t = np.arange(L) / SR
        f = 38 + 60 * np.exp(-t * 18)
        s = (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)).astype(np.float32)
        out = np.stack([s, s], 1) * gain
        out = Pedalboard([Reverb(room_size=0.85, wet_level=0.25, dry_level=0.9)])(out.T.copy(), SR).T
        self._place("fx", self.t(beat), out)

    def _place(self, name, t0, arr):
        n = int(self.total * SR) + SR
        a = self.extra.setdefault(name, np.zeros((n, 2), np.float32))
        i0 = int(t0 * SR)
        L = min(len(arr), n - i0)
        if L > 0:
            a[i0:i0 + L] += arr[:L]

    # --- miks ---
    def render(self, path, gains=None, fx=None, sidechain=None, duck=0.55, lowpass_until=None):
        """sidechain: lista beatów stopy (ścisza akordy/bas — nowoczesne „pompowanie”).
        lowpass_until: (beat_od, beat_do, hz_start) — filtr otwierający się na intro."""
        gains = gains or {}
        fx = fx or {}
        n = int(self.total * SR) + SR
        mix = np.zeros((n, 2), np.float32)
        tt = np.arange(n) / SR
        duck_env = np.ones(n, np.float32)
        if sidechain:
            for b in sidechain:
                k = self.t(b)
                i = int(k * SR)
                seg = tt[i:i + int(0.35 * SR)] - k
                duck_env[i:i + len(seg)] = np.minimum(duck_env[i:i + len(seg)],
                                                      1 - duck * np.exp(-seg / 0.09) * (seg >= 0))
        for name, tr in self.tracks.items():
            a = tr.render()
            chain = fx.get(name)
            if chain:
                a = Pedalboard(chain)(a.T.copy(), SR).T
            if name in gains.get("_duck", ()):
                a = a * duck_env[:, None]
            mix += a * gains.get(name, 1.0)
        for name, a in self.extra.items():
            mix += a * gains.get(name, 1.0)
        if lowpass_until:
            b0, b1, hz = lowpass_until
            lp = LowpassFilter(cutoff_frequency_hz=hz)
            i0, i1 = int(self.t(b0) * SR), int(self.t(b1) * SR)
            blk = 1024
            seg = mix[:i1].T.copy()
            outp = np.zeros_like(seg)
            for i in range(0, i1, blk):
                p = max(0.0, (i - i0) / max(1, i1 - i0))
                lp.cutoff_frequency_hz = hz * (18000 / hz) ** (p ** 1.6)
                outp[:, i:i + blk] = lp.process(seg[:, i:i + blk], SR, reset=False)
            mix[:i1] = outp.T
        master = Pedalboard([HighpassFilter(30), Compressor(threshold_db=-16, ratio=2.5, attack_ms=10,
                                                            release_ms=120), Limiter(threshold_db=-1.5)])
        mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.8
        mix = master(mix.T.copy(), SR).T
        L = int(self.total * SR)
        fade = np.clip((self.total - np.arange(L) / SR) / 1.4, 0, 1)
        mix = mix[:L] * fade[:, None]
        write_wav(path, mix)


def write_wav(path, stereo):
    import wave
    a = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(a.tobytes())


def kick_beats(start, end, every=1.0, skip=()):
    out, b = [], start
    while b < end - 1e-6:
        if not any(s0 <= b < s1 for s0, s1 in skip):
            out.append(b)
        b += every
    return out
