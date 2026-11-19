#!/bin/sh
# Pobiera bank instrumentów GeneralUser GS (licencja: dowolne użycie, także komercyjne) do narzedzia/sf
# i biblioteki Pythona do muzyki.
cd "$(dirname "$0")" && mkdir -p sf && cd sf
[ -f GeneralUser-GS/GeneralUser-GS.sf2 ] || git clone --depth 1 https://github.com/mrbumpy409/GeneralUser-GS.git
pip install -q --break-system-packages pedalboard 2>/dev/null || pip install -q pedalboard
pip install -q --break-system-packages --no-deps tinysoundfont 2>/dev/null || pip install -q --no-deps tinysoundfont
