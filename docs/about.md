# O projekcie

Ten serwis to zapis projektu zaliczeniowego z uczenia maszynowego (studia magisterskie): sześć notebooków Jupyter, które prowadzą od surowych danych Formuły 1 do dwóch modeli i analizy ich błędów. Notebooki są wykonane - wykresy Plotly są interaktywne bez uruchamiania czegokolwiek.

## Dane

- Źródło: [FastF1](https://docs.fastf1.dev/) - oficjalny pomiar czasu F1, pogoda i telemetria.
- Sezony 2023-2024: 46 wyścigów, 39 647 czystych okrążeń ([`laps_clean.parquet`](https://github.com/straightchlorine/f1-ml-lab/blob/master/data/laps_clean.parquet)) i 918 par kierowca-wyścig, w tym 138 podiów ([`driver_race.parquet`](https://github.com/straightchlorine/f1-ml-lab/blob/master/data/driver_race.parquet)).
- Do eksperymentów "czy więcej sezonów pomoże?" - te same zbiory dla sezonów 2018-2024 ([`laps_all.parquet`](https://github.com/straightchlorine/f1-ml-lab/blob/master/data/laps_all.parquet), [`driver_race_all.parquet`](https://github.com/straightchlorine/f1-ml-lab/blob/master/data/driver_race_all.parquet)).
- Gotowe pliki leżą w katalogu [`data/`](https://github.com/straightchlorine/f1-ml-lab/tree/master/data) repozytorium, więc notebooki 02-05 uruchamiają się bez pobierania czegokolwiek.

## Jak czytać

- Porażki modeli są w notebookach celowo: ujemne `R^2` w regresji, pułapka trafności i wyciek danych w klasyfikacji. Najpierw pokazujemy, dlaczego coś nie działa, a dopiero potem naprawę.
- Każdy model ma benchmark z pomiarem czasu uczenia i predykcji, bo prosty model bywa jednocześnie najlepszy i najtańszy.
- W wersji angielskiej przetłumaczone są komentarze (komórki markdown); kod, wydruki i podpisy wykresów pozostają po polsku.

## Jak uruchomić

```bash
git clone https://github.com/straightchlorine/f1-ml-lab.git
cd f1-ml-lab
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/jupyter lab   # notebooki w katalogu notebooks/, po kolei 00 -> 05
```

Notebook 01 pobiera dane z FastF1 (pierwsze uruchomienie trwa długo, kolejne czytają z cache). Pozostałe notebooki startują z plików parquet.

## Autorzy

- **Piotr Krzysztof Lis** - [piotrkrzysztof.dev](https://piotrkrzysztof.dev) | [GitHub](https://github.com/straightchlorine) | [Codeberg](https://codeberg.org/piotrkrzysztof) | [LinkedIn](https://www.linkedin.com/in/straightchlorine/)
- **Jakub Kucharski** - [GitHub](https://github.com/kubson2002k) | [LinkedIn](https://www.linkedin.com/in/jakub-kucharski-360811305/)

Kod źródłowy: [straightchlorine/f1-ml-lab](https://github.com/straightchlorine/f1-ml-lab). Strona zbudowana w MkDocs Material z mkdocs-jupyter.
