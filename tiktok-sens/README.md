# TikTok SENS (@senswroclaw)

Filmy na TikToka dla SENS – Centrum Diagnozy, Terapii i Rozwoju (ul. Dyrekcyjna 37/47, Wrocław, senswroclaw.pl).
Oddzielone od rolek Instagrama „psycholog po 40tce” (katalog główny repozytorium) — tu nic stamtąd nie zmieniamy.

## Struktura
- `assets/` — logo SENS (oryginalne pliki, nie przerabiać): `logo_pion.png` (jasne tło), `logo_poziom.png`,
  `sygnet.png`, `logo_bialy.png` (ciemne tło). `assets/foto/` — prawdziwe zdjęcia gabinetów, recepcji
  i dużej sali (bez ludzi).
- `narzedzia/tt_base.py` — wspólne funkcje: kolory, fonty, strefa bezpieczna TikToka, tła, muzyka, render.
- `narzedzia/tt_NN_*.py` — skrypt każdego filmu (`test OUTDIR` → arkusze klatek, `full OUT.mp4` → film).
- `narzedzia/tt_klipy.py` — prawdziwe nagrania stock (`Clip`: kadr 9:16, powolny zoom, ciepła korekta), gotowa
  muzyka Mixkit jako tło (`music_bed`: EQ bez ostrych wysokich, −17 LUFS, TP −1,5), karty tekstu i karta końcowa SENS
  (`caption_card`, `end_card`, `draw_end`), `render_av`. Klipy i utwory pobierają się same do `narzedzia/klipy/` (git ignoruje).
- `narzedzia/tt_sprawdz_audio.py FILM.mp4 [spektrogram.png]` — kontrola dźwięku (LUFS, true peak, RMS co 3 s, 5–10 kHz).
- `filmy/` — gotowe MP4 (publiczny link raw → PostSyncer).
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
- Muzyka tylko oryginalna, ale na PRAWDZIWYCH instrumentach: `narzedzia/tt_muzyka.py` (bank GeneralUser GS —
  licencja pozwala na użycie komercyjne; `sh narzedzia/pobierz_dzwieki.sh` raz na sesję) + efekty (pogłos, kompresja,
  sidechain, filtr na intro). Wzór: `tt_02_co_slyszy_dziecko.py` (pop/house 108 BPM: piano elektryczne, tłumiona gitara,
  bas syntezatorowy, zestaw Dance, krótki lead, wejścia z crash + uderzeniem). Rodrigo (19.11.2026): muzyka z tonów
  sinusowych (tt_01) jest „okropna, podstawowa, dziecinna, nudna, nie pasuje” — NIE używać już `Mix` z tt_base.
  Unikać: dzwoneczków, celesty, kalimby, pozytywki, prostych arpeggiów durowych, wolnych padów, heavy metalu, hip-hopu.
  Akordy septymowe/nonowe, rytm i energia od 1. sekundy, muzyka dopasowana do nastroju tematu, różne style co tydzień
  (pop/house, akustyczny pop z gitarą, nu-disco, kinowy puls…). Sprawdzać poziomy sekcji (RMS) i spektrogram —
  „whoosh” cicho, przerwa nie może być ciszą. Głośność −14 LUFS, szczyt ≤ −1 dBTP (robi `render`).
- **KOREKTA MUZYKI (Rodrigo, 23.11.2026) — nadrzędna wobec „pop/house” powyżej.** Film o ADHD miał muzykę zbyt
  stridentną, zbyt „popową”, drażniącą. SENS to gabinet psychologiczny: nie dyskoteka i nie reklama środka czystości.
  Muzyka ma być spójna z marką: ciepła, spokojna, pewna, nowoczesna; wspiera przekaz i nie przytłacza go.
  - Styl domyślny: akustyczny/indie-folk z gitarą, miękkie piano, delikatny lo-fi/chillhop, ciepły pulsujący cinematic,
    lekki rytm 70–95 BPM, perkusja szczotki/cichy kick. Wolno: delikatny akcent rytmiczny od 1. sekundy (bez nudnych padów).
    NIE: EDM, house z mocnym sidechainem, jaskrawy pop-lead, ostre wysokie syntezatory, wysokie hi-haty, „drop” na całą moc.
  - Głośność: muzyka ma być TŁEM (ok. −20 do −18 LUFS samej muzyki; całość po `render` ≤ −16 LUFS zamiast −14),
    bez ostrych transjentów i bez ostrych wysokich częstotliwości (sprawdź spektrogram: brak energii „syczącej” 5–10 kHz).
    Risery/uderzenia bardzo cicho albo wcale. Film o ADHD i tematy „głośne” emocjonalnie: jeszcze spokojniej, stały puls,
    bez przeciążania (to widzowie, którzy mają przeciążenie).
  - Przed wyborem stylu zrób RESEARCH (WebSearch): jakiej muzyki używają marki psychologiczne/wellbeing i treści
    o zdrowiu psychicznym na TikToku/Reelsach (PL i świat), jakie gatunki i tempa; zapisz wnioski w DZIENNIK.md.
    Preferuj prawdziwe, produkowane, bezpłatne do użytku komercyjnego utwory (Mixkit, Pixabay Music, YouTube Audio
    Library, Free Music Archive – sprawdź licencję) albo bank instrumentów; zapisz źródło i licencję.
  - Porównaj z poprzednimi filmami: jeśli któryś był „zbyt głośny/stridentny” (film o ADHD), nie powtarzaj jego stylu.
  - Od 23.11.2026: gotowe utwory Mixkit (Stock Music Free License — social media i reklamy online OK; bez remiksu
    i bez rejestracji w Content ID) przez `music_bed` (−17…−17,5 LUFS, TP −1,5, low-pass 9,5 kHz, high-shelf −2,5 dB).
    Dla porównania stary tt_02 (pop/house): −14,2 LUFS, TP −0,7 i 4,2% energii w 5–10 kHz → stąd „piszczał”.

## Nagrania stock (Rodrigo, 23.11.2026: mniej kart z tekstem, więcej prawdziwego obrazu)
- Mixkit: TYLKO klipy z „Mixkit Stock Video Free License” (sprawdzić na stronie klipu `data-license="videoFree"`).
  „Restricted License” = zakaz w firmowych social mediach. Plik 1080p: `assets.mixkit.co/videos/ID/ID-1080.mp4`.
  Uwaga: po ok. 30 zapytaniach Mixkit włącza blokadę Cloudflare — szukać oszczędnie, nie obchodzić blokady.
- Coverr: licencja Coverr (użycie komercyjne bez atrybucji); NIE używać klipów „premium” (znak wodny) ani AI
  (`user-ai-generation…`, `coverr-temp-…`). Plik: `cdn.coverr.co/videos/SLUG/1080p.mp4`.
- Pexels/Pixabay z tego środowiska: 403/401 (Pexels wymaga klucza API).
- Ludzie podobni do lokalnej publiczności; bez rozpoznawalnych dzieci (dłonie wolno); ekrany z grą/marką rozmyć.
- Jeden koncept na film (zdanie „koncept w jednym zdaniu” w nagłówku skryptu), tekst w kartach, ≥ 2,4 s na komunikat,
  przenikania łagodne (`smooth`), z ciemnego na jasne co najmniej 0,9 s (bez błysków).

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

## Publikacja (automatycznie, PostSyncer)
Co poniedziałek zadanie robi 5 filmów i samo je planuje na wtorek–sobotę przez konektor **PostSyncer**
(workspace „Maria Siwa” id 78389, konto TikTok @senswroclaw id 8260 — sprawdzić `list-accounts`).
`create-post`: `schedule_type: schedule`, `media` = link raw do `filmy/…mp4`, `privacy_level: PUBLIC_TO_EVERYONE`;
film zapraszający do usług SENS: `brand_organic_toggle: true`.
Darmowy plan PostSyncer: 20 publikacji na cykl (cykl zaczyna się 19. dnia miesiąca) — nie przekraczać.
Konektor Metricool w Claude należy do konta Marii (Instagram „psycholog po 40tce”) — NIE używać go do TikToka SENS.
Opis po polsku: hak w 1. linii, 2–4 krótkie linie, jedno pytanie albo jedno CTA, 3–5 hashtagów bez polskich znaków.
Teksty tygodnia: `TEKSTY_RRRR-MM-DD.md` (dzień, godzina, plik, opis, id posta w PostSyncer).

## Reuse z Instagrama Marii i zdjęcia (Rodrigo, 23.11.2026)
- Rolka dnia dla @psycholog_po_40tce o kursie „Środek, nie koniec” (start piątek 4 grudnia 2026) ma być spokojna i
  nadaje się do ponownego użycia w SENS. Przed zrobieniem filmów TikTok sprawdź `do_publikacji/` (najnowsze pliki):
  jeśli jest tam dzisiejsza lub wczorajsza rolka o kursie, użyj jej (wersja 9:16 bez zmian lub z drobną adaptacją i
  kartą końcową SENS) jako JEDEN z 5 filmów tygodnia zamiast robić nowy o tym samym.
- Zdjęcie dr Marii Siwej (Rodrigo, 27.11.2026, dopóki nie powie inaczej): WYŁĄCZNIE `fotos_maria/maria_siwa_oficjalne.jpg`
  (portret firmowy, turkusowy żakiet, kremowe tło). Stare zdjęcia 01–09 usunięte; żadnych innych ani „losowych” zdjęć Marii.
  Tylko gdy temat dotyczy Marii lub jej kursu; zasady w `fotos_maria/README.md` (bez rozciągania, twarz w całości,
  bez filtrów, bez żartów z wyglądu).
- Reuse rolek Marii z `do_publikacji/` tylko wtedy, gdy rolka nie pokazuje Marii albo pokazuje wyłącznie to oficjalne zdjęcie.
  Rolka o kursie ze starym zdjęciem (tt_07_reuse, opublikowana 26.11) nie spodobała się Rodrigowi — usunął ją z TikToka.
