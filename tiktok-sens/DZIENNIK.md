# Dziennik TikTok SENS

## 2026-11-19 — start
- Konto @senswroclaw: 3 wcześniejsze filmy (wszystkie reklamowały bezpłatną rozmowę wstępną).
  7 dni: 726 wyświetleń, 9 polubień, 0 komentarzy, 0 udostępnień, 1 obserwujący.
  Najlepsze: „Problemy w szkole… 23:47” (wyszukiwarka nocą) 358 wyśw.; „Proszenie o pomoc…” 354 wyśw.
- Wniosek: same reklamy dają wyświetlenia, ale nie budują obserwujących → 4/5 wartość, 1/5 zaproszenie.
- Zrobiono `tt_01_2347_zlosc` (seria „23:47”): „czy to normalne, że moje dziecko ciągle wybucha złością?”
  → złość jest normalna → 3 sygnały do konsultacji → „Widzę, że czujesz dużą złość. Jestem obok.” → karta SENS
  z bezpłatną rozmową wstępną (15–20 min, telefon lub wideo — tak jest na stronie 19.11.2026).
- Tematy już użyte: złość / napady złości u dziecka; (wcześniej, poza repo) problemy w szkole, prośba o pomoc.
- TUS z klockami LEGO zakończony — nie promować.

## 2026-11-19 — tt_02_poznaj_sens
- Przeróbka nagrania strony senswroclaw.pl od Rodrigo (z wklejonymi napisami): usunięty błąd w 1. sekundzie,
  nowy hak „Psycholog? Terapeuta? Diagnoza? / Nie musisz wiedzieć, od czego zacząć.”, nagranie w ramce telefonu,
  czyste nagłówki nad telefonem, karta końcowa SENS, oryginalna muzyka, −14 LUFS. 32,7 s.
- Gdyby Rodrigo przysłał nagranie bez napisów, można zrobić czystszą wersję.
- Publikacja: PostSyncer (konektor w Claude). `tt_01_2347_zlosc` zaplanowany na pt 20.11.2026 20:30
  (post PostSyncer id 182049). Cykl darmowego planu: 19.11–18.12 → 1/20 wykorzystane.
- 19.11 wieczorem: Rodrigo sam wrzucił wcześniej `tt_01` (złość / 23:47) na TikToka → zaplanowany post 182049
  zamieniony na `tt_02_co_slyszy_dziecko` (seria „Co słyszy dziecko, gdy mówisz…”), pt 20.11 20:30.
- Krytyka Rodrigo: filmy ładne, efekty dobre, ale muzyka okropna (podstawowa, dziecinna, nudna, nie pasuje).
  Od tt_02 nowy silnik muzyki `tt_muzyka.py` (prawdziwe instrumenty + efekty). Obserwować reakcję.
- Tematy użyte: złość u dziecka (23:47); komunikacja: „Uspokój się!”, „Nie płacz, nic się nie stało”, „Ile razy mam powtarzać?!”.

## 2026-11-23 — analiza danych + tydzień 24–28.11
### Liczby (PostSyncer, ostatni odczyt 23.11 02:09; darmowy plan: ręczny sync zablokowany, tylko 7 dni, bez czasu oglądania i zapisów)
| Film | Publikacja | Wyśw. | ❤ | Kom. | Udost. | ER |
|---|---|---|---|---|---|---|
| „Problemy w szkole… nocą w wyszukiwarce” | wt 17.11 17:09 | 358 | 4 | 0 | 0 | 1,1% |
| „Proszenie o pomoc nie jest słabością” | pn 16.11 12:44 | 354 | 5 | 0 | 0 | 1,4% |
| tt_02 „Co słyszy dziecko, gdy mówisz…” (pop/house) | pt 20.11 20:33 | 280 | 5 | 0 | 0 | 1,8% |
| tt_02_poznaj_sens „Psycholog? Terapeuta? Diagnoza?” | czw 19.11 17:16 | 241 | 7 | 0 | 1 | 3,3% |
| konsultacja orientacyjna (długi opis) | nd 15.11 | 2 (stare dane) | 1 | 0 | 0 | – |
- Konto: 1 obserwujący, 0 komentarzy. Film o ADHD, o którym pisze Rodrigo, nie jest w PostSyncer (wrzucony ręcznie?) — brak liczb.
- Wnioski (mało danych: 5 filmów, < 1000 wyśw.): najwięcej wyświetleń daje hak z rozpoznawalnym problemem (szkoła nocą,
  „nie wiesz, od czego zacząć”); jedyne udostępnienie i najwyższe ER — film o tym, od czego zacząć (prawdziwa strona SENS).
  Reklama z długim opisem — prawie zero. Godziny 12:44–20:33 bez wyraźnej różnicy → zostają wieczory 19:00–20:30.
  Zero komentarzy → w opisie jedno proste pytanie, w filmie CTA „wyślij / zapisz”.
- Feedback Rodrigo (23.11): filmy zbyt generyczne i nudne → 1 jasny koncept na film + prawdziwe nagrania (Mixkit, Coverr);
  muzyka do ADHD zbyt głośna/popowa/drażniąca → ciepłe, spokojne tło. Agencje Marafiki i Greenfield już nie biorą udziału —
  SENS robi marketing sam z Claude. Kurs „Środek, nie koniec” startuje w piątek 4.12.2026.
- Pomiar: stary tt_02 (pop/house) −14,2 LUFS, TP −0,7 dBTP, 4,2% energii w 5–10 kHz (stąd „piszczy”).
  Nowe filmy: −17,0…−17,4 LUFS, TP ≤ −1,5 dBTP, 0,00–0,06% w 5–10 kHz (zmiana celu renderu: −14 → −17 LUFS).

### Muzyka — research (23.11)
- Marki wellbeing / zdrowie psychiczne w Reels/TikTok (biblioteki „wellness / mental health” Epidemic Sound, Soundstripe,
  PremiumBeat; artykuły Soundstripe „trending sounds for brands”, Adweek o audio i zdrowiu psychicznym, Hypebot „what music
  means for wellness brands”): dominują akustyk/indie-folk, miękkie piano, lo-fi/chillhop i ambient z delikatnym pulsem
  ok. 70–95 BPM; muzyka jako tło pod tekst, bez dropów. Konta firmowe na TikToku nie mogą brać modnych piosenek spoza
  Commercial Music Library → wgrywamy licencjonowane utwory w plik.
- Wybór: Mixkit (Stock Music Free License): „We'll Be Okay” (piano/film), „Sleepy Cat” (spokojny lo-fi, ADHD),
  „Lo-Fi 02” (lo-fi z cichym bitem), „Forever in My Heart” (akustyczny folk z gitarą). Analiza przed wyborem: tempo,
  spektrogram, udział 5–10 kHz; odrzucone utwory z jaskrawym popem (np. „Pop 07”, „Pop 08”).

### Źródła i ograniczenia
- senswroclaw.pl: WebFetch nie zadziałał w trybie automatycznym → użyto tylko faktów z polecenia (bezpłatna 15-min rozmowa
  wstępna ważna do 31.12.2026; kurs od pt 4.12.2026). Nagrania: Mixkit (tylko Free License) i Coverr; Pexels/Pixabay 403.

### Filmy tygodnia (szczegóły i id postów: TEKSTY_2026-11-23.md)
| Dzień | Plik | Koncept w jednym zdaniu | Muzyka |
|---|---|---|---|
| wt 24.11 | tt_03_bateria | Dzień mamy jako bateria telefonu: 64% → 3%; telefon ładujesz co noc, a siebie? (NOWY FORMAT, test) | We'll Be Okay — piano/film, 70 BPM |
| śr 25.11 | tt_04_nie_moge_zaczac | ADHD: zadanie 10 min, „zanim zacznę” 2 h 47 min; to nie zawsze lenistwo; start na 2 minuty | Sleepy Cat — spokojny lo-fi, ok. 68 BPM |
| czw 26.11 | tt_07_reuse_srodek_nie_koniec | Rolka Marii (tablica odjazdów): menopauza to nie stacja końcowa, start kursu pt 4.12 (zaproszenie) | indie-folk 80 BPM (bank instrumentów) |
| pt 27.11 | tt_05_ok_z_kropka | „Ok.” z kropką → głowa pisze dramat → co wiesz na pewno? Myśl to nie fakt | Lo-Fi 02 — lo-fi, ok. 83 BPM |
| sob 28.11 | tt_06_sciemniacz | Zabranie telefonu w połowie gry = PSTRYK światła; lepiej działa ściemniacz w 3 krokach | Forever in My Heart — akustyczny folk |

### Pomysły — użyte / w kolejce
- Użyte (TikTok SENS): złość u dziecka (23:47); „Uspokój się / Nie płacz / Ile razy…”; problemy w szkole; prośba o pomoc;
  „od czego zacząć” (psycholog/terapeuta/diagnoza); przeciążenie mamy (bateria); ADHD dorosłych — start zadania;
  myśli vs fakty („Ok.”); telefon/ekrany — kończenie gry; kurs „Środek, nie koniec” (reuse rolki Marii).
- W kolejce: jak trafić do SENS (6. piętro, obok Żabki, przecznica od Wroclavii, 2 domofony z kodem, winda — POV spacer);
  co się dzieje w bezpłatnej 15-min rozmowie (do 31.12); przypomnienie kursu Środek 2–3.12; stres przed sprawdzianem /
  próbny egzamin ósmoklasisty (grudzień); dziecko „wybucha” po szkole (rozładowanie po całym dniu); granice bez krzyku;
  nastolatek i lęk społeczny; ADHD: nadwrażliwość na odrzucenie, impulsywne decyzje, przeciążenie bodźcami; głód
  emocjonalny (psychodietetyka); święta i napięcia rodzinne; SENS dla Firm: wypalenie w pracy, neuroróżnorodność
  w pracy (wersja pod LinkedIn).
- Do sprawdzenia w przyszłym tygodniu: wynik testu „Bateria” (nowy format), czy CTA „wyślij/zapisz” daje udostępnienia,
  czy prawdziwe nagrania podnoszą wyświetlenia vs karty z tekstem.
