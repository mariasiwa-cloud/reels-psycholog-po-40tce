"""Kontrola dźwięku gotowego filmu (nie słyszymy muzyki, więc mierzymy):
- głośność całości (ffmpeg ebur128): cel ok. −16/−17 LUFS, true peak ≤ −1,5 dBTP,
- RMS w odcinkach co 3 s (przerwy nie mogą spadać do ciszy, brak nagłych skoków),
- udział energii 5–10 kHz (ostre „syczące” wysokie) + obraz spektrogramu.
Użycie: python3 tt_sprawdz_audio.py FILM.mp4 [SPEKTROGRAM.png]
"""
import sys, subprocess, re
import numpy as np

f = sys.argv[1]
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f, "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
summ = r[r.rfind("Summary:"):]
I = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
LRA = float(re.search(r"LRA:\s+(-?[\d.]+) LU", summ).group(1))
TP = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1))
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "22050", "-f", "f32le", "-"],
                     capture_output=True).stdout
y = np.frombuffer(raw, np.float32)
sr = 22050
seg = 3.0
rms = [20 * np.log10(np.sqrt(np.mean(y[int(i * sr):int((i + seg) * sr)] ** 2)) + 1e-9)
       for i in np.arange(0, len(y) / sr - 1.0, seg)]
S = np.abs(np.fft.rfft(y[: len(y) // 4096 * 4096].reshape(-1, 4096) * np.hanning(4096), axis=1)) ** 2
fr = np.fft.rfftfreq(4096, 1 / sr)
tot = S.sum()
hi = S[:, (fr >= 5000) & (fr < 10000)].sum() / tot * 100
print(f"{f.split('/')[-1]}: I={I} LUFS, TP={TP} dBTP, LRA={LRA} LU, 5–10 kHz={hi:.2f}% energii")
print("RMS co 3 s (dBFS):", " ".join(f"{v:.0f}" for v in rms))
ok = (-18.5 <= I <= -15.0) and TP <= -1.4 and hi < 1.5 and min(rms[:-1]) > max(rms) - 14
print("OK" if ok else "SPRAWDŹ")
if len(sys.argv) > 2:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.specgram(y, NFFT=2048, Fs=sr, noverlap=1024, cmap="magma", vmin=-120)
    ax.axhspan(5000, 10000, color="cyan", alpha=0.08)
    ax.set_title(f"{f.split('/')[-1]}  I={I} LUFS  TP={TP}  5–10k={hi:.2f}%")
    plt.tight_layout(); plt.savefig(sys.argv[2], dpi=60)
