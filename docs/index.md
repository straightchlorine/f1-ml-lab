# Uczenie maszynowe w F1

Uczenie maszynowe na danych z Formuły 1 (timing + telemetria przez [FastF1](https://docs.fastf1.dev/)).
Seria notebooków prowadzi od surowych danych do modeli i analizy ich błędów:

1. [Pierwszy kontakt z danymi](00-data-load.ipynb) - API FastF1 na przykładzie jednej sesji (Monza 2024)
2. [Budowa zbioru danych](01-build-dataset.ipynb) - z surowych okrążeń do tabeli cech
3. [Eksploracja danych (EDA)](02-eda.ipynb) - co siedzi w danych i co psuje modele
4. [Regresja: czas okrążenia](03-regression-laptime.ipynb) - przewidywanie czasu okrążenia
5. [Klasyfikacja: podium](04-classification-podium.ipynb) - kto stanie na podium?
6. [Analiza błędów](05-error-analysis.ipynb) - gdzie i dlaczego modele się mylą

Dane: sezony 2023-2024 (46 wyścigów, ok. 39,6 tys. czystych okrążeń, 918 par kierowca-wyścig), pobrane przez FastF1 i dostępne w repozytorium jako pliki parquet. Porażki modeli po drodze są celowe - pokazują, dlaczego coś nie działa, zanim pokażemy naprawę. Więcej w [O projekcie](about.md).

Notebooki są wykonane - wykresy (Plotly) są interaktywne bez uruchamiania czegokolwiek.
Kod źródłowy: [straightchlorine/f1-ml-lab](https://github.com/straightchlorine/f1-ml-lab).
