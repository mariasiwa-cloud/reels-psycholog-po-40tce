#!/bin/sh
# Pobiera fonty marki SENS (Poppins, Caveat) do narzedzia/fonts
cd "$(dirname "$0")" && mkdir -p fonts && cd fonts
for u in poppins/Poppins-Bold.ttf poppins/Poppins-ExtraBold.ttf poppins/Poppins-Medium.ttf; do curl -sSLO "https://raw.githubusercontent.com/google/fonts/main/ofl/$u"; done
curl -sSL -o "Caveat[wght].ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/Caveat%5Bwght%5D.ttf"
