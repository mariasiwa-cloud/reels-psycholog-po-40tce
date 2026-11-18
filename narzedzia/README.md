# Narzędzia do rolek „psycholog po 40tce”

- `pobierz_fonty.sh` — pobiera fonty marki (Poppins, Caveat). Uruchom raz przed renderem.
- `base.py` — wspólne funkcje: kolory SENS, tło lawendowe, karty, tekst, płynne animacje.
- `rolka_02_zegar.py` — przykład: noc → świt, zegar 3:00, myśli wpadają do notesu, muzyka 120 BPM z „dropem”.
- `rolka_03_burze.py` — przykład: prognoza pogody w domu, dwa fronty, piorun, słońce, 3 zdania, muzyka 120 BPM.

Każdy skrypt: `python3 skrypt.py test OUT 0,5,10` (klatki testowe → OUT/sheet.jpg),
`python3 skrypt.py music OUT`, `python3 skrypt.py full OUT`, potem
`ffmpeg -f concat -safe 0 -i OUT/list.txt -c copy OUT/silent.mp4` i
`ffmpeg -i OUT/silent.mp4 -i OUT/music.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest rolka.mp4`.

Gotowe rolki trzymamy w katalogu głównym repozytorium (publiczny link raw → Metricool).
