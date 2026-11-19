# TikTok SENS (@senswroclaw)

Filmy na TikToka dla SENS – Centrum Diagnozy, Terapii i Rozwoju (ul. Dyrekcyjna 37/47, Wrocław, senswroclaw.pl).
Oddzielone od rolek Instagrama „psycholog po 40tce” (katalog główny repozytorium) — tu nic stamtąd nie zmieniamy.

## Struktura
- `assets/` — logo SENS (oryginalne pliki, nie przerabiać): `logo_pion.png` (jasne tło), `logo_poziom.png`,
  `sygnet.png`, `logo_bialy.png` (ciemne tło). `assets/foto/` — prawdziwe zdjęcia gabinetów, recepcji
  i dużej sali (bez ludzi).
- `narzedzia/tt_base.py` — wspólne funkcje: kolory, fonty, strefa bezpieczna TikToka, tła, muzyka, render.
- `narzedzia/tt_NN_*.py` — skrypt każdego filmu (`test OUTDIR` → arkusze klatek, `full OUT.mp4` → film).
- `filmy/` — gotowe MP4 (publiczny link raw → Metricool).
- `DZIENNIK.md` — co opublikowano, liczby, wnioski. Czytać przed każdym nowym tygodniem.

Fonty: `sh ../narzedzia/pobierz_fonty.sh` (raz).

## Zasady formatu TikTok
- 1080×1920, 30 fps, 20–35 s. Hak czytelny bez dźwięku od pierwszej klatki.
- Tekst tylko w strefie `SAFE` (x 80–940, y 200–1360): na dole opis i nazwa konta, po prawej przyciski.
  Środek treści `CX = 510`.
- Każdy komunikat ≥ 2,4 s na ekranie. Bez wirujących słów, migania, trzęsienia kamery.
- Paleta SENS: krem/jasna lawenda, ciemny petrol (#1e343b), lawenda (#96789c / #815983), żółty tylko akcent.
  Fonty: Poppins (ExtraBold/Bold/Medium), Caveat Bold do „odręcznych” zdań.
- Karta końcowa: logo SENS + „Każda emocja ma sens.” + jedno CTA + senswroclaw.pl. Nigdy nie umieszczać
  osoby w kole logo.
- Muzyka tylko oryginalna (syntetyzowana w kodzie): nowoczesna, rytmiczna, chwytliwa; bez wolnych,
  nudnych padów ambient, bez heavy metalu i hip-hopu. Głośność −14 LUFS, szczyt ≤ −1 dBTP (robi `render`).

## Serie (rotacja, max 2 filmy tygodniowo w tym samym formacie)
1. **„23:47”** — pytanie, które rodzic wpisuje w nocy w wyszukiwarkę → podpowiedzi innych rodziców
   („Nie tylko Ty o to pytasz.”) → spokojna odpowiedź → kiedy warto skonsultować → zdanie na dziś.
2. **„Mit czy fakt?”** — quiz (ADHD, lęk, złość, ekrany, nastolatki); widz odpowiada w komentarzu.
3. **„Co słyszy dziecko, gdy mówisz…”** — co mówisz / co słyszy dziecko / co powiedzieć zamiast.
4. **„1 ćwiczenie w 60 sekund”** — jedno praktyczne narzędzie (oddech, uspokojenie, przed sprawdzianem).
5. **„Zajrzyj do SENS”** — prawdziwe zdjęcia z `assets/foto` + zaproszenie do jednej usługi.
Co tydzień jeden nowy test formatu. Seria „Pieruś” jest pisana przez Rodrigo — nie robić jej samodzielnie.

## Treść i bezpieczeństwo
- Odbiorcy: głównie mamy 25–50 lat (dzieci i nastolatki), także dorośli we Wrocławiu.
- 4 z 5 filmów dają wartość, 1 z 5 zaprasza. Zaproszenia tylko do usług widocznych na senswroclaw.pl
  w dniu tworzenia (np. bezpłatna rozmowa wstępna 15–20 min, diagnoza ADHD, psychoterapia, wsparcie dzieci
  i młodzieży, konsultacje dla rodziców, psychodietetyka, logopedia).
- TUS z klockami LEGO już się nie odbywa — nie wspominać.
- Nigdy nie wymyślać cen, dat, nazwisk, osiągnięć ani historii klientów. Bez zdjęć i opinii klientów,
  bez dzieci na zdjęciach. Bez diagnozowania i obietnic efektów. Objawy somatyczne → lekarz.
  O ADHD/autyzmie: diagnozę stawia specjalista. Bez zawstydzania rodziców.
- Polski poprawny i naturalny, ze wszystkimi znakami (ą ę ś ć ż ź ł ó ń).

## Publikacja (ręcznie, Rodrigo)
Co poniedziałek o 14:00 zadanie robi 5 filmów na wtorek–sobotę i wysyła je Rodrigo w rozmowie razem z tekstami.
Rodrigo planuje je sam w swoim Metricool (konto rcifuentes.sens, marka SENS, TikTok osobisty @senswroclaw;
darmowy plan = 20 publikacji/mies.). Konektor Metricool w Claude należy do konta Marii (Instagram
„psycholog po 40tce”) — NIE używać go do TikToka SENS.
Opis po polsku: hak w 1. linii, 2–4 krótkie linie, jedno pytanie albo jedno CTA, 3–5 hashtagów bez polskich znaków.
Teksty tygodnia: `TEKSTY_RRRR-MM-DD.md` (dzień, godzina, plik, opis).
