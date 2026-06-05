# Projekt: F1 ML (FastF1, sezon 2024)

Projekt uczenia maszynowego na danych Formuły 1 pobieranych przez **FastF1**.
Dwa zadania na tych samych danych źródłowych:

1. **Regresja** — przewidywanie czasu okrążenia (`LapTime_s`) na podstawie opon, paliwa, pogody.
2. **Klasyfikacja** — czy kierowca skończy na podium (regresja logistyczna), cechy przedwyścigowe.

Plus EDA i analiza błędów. Wizualizacje: **Plotly**.

## Stos i konwencje

- Python, Jupyter, FastF1, pandas, numpy, scikit-learn, plotly.
- Notebooki numerowane (`00`–`05`), uruchamiane **po kolei**, leżą w `notebooks/`.
- Cache FastF1: `../cache/` (gitignored). Dane pośrednie: `../data/` (parquet).
- Datasety budowane raz w `01`, potem czytane z parquet — **nie przerabiaj ładowania
  FastF1 w notebookach modelujących**, mają startować natychmiast z parquet.

## Notebooki

| Plik | Rola | Wejście | Wyjście |
|------|------|---------|---------|
| `00-data-load.ipynb` | demo jednej sesji (Monza 2024), eksploracja API | — | — |
| `01-build-dataset.ipynb` | pętla po całym sezonie 2024, czyszczenie | FastF1 | `laps_clean.parquet`, `driver_race.parquet` |
| `02-eda.ipynb` | EDA + wykresy Plotly | parquet | — |
| `03-regression-laptime.ipynb` | regresja czasu okrążenia | `laps_clean` | `reg_predictions.parquet` |
| `04-classification-podium.ipynb` | klasyfikacja podium | `driver_race` | `clf_predictions.parquet` |
| `05-error-analysis.ipynb` | analiza błędów obu modeli | `reg_/clf_predictions` | — |

`01` jest wolny (ładuje 24 wyścigi z FastF1, pierwszy raz pobiera) — dlatego parquet
jest „szwem", który pozwala szybko iterować na `03`/`04`.

## Datasety (po `01`)

**`laps_clean.parquet`** — jeden wiersz = jedno czyste okrążenie. Kolumny:
`Round, EventName, Driver, Team, LapNumber, Stint, Compound, TyreLife, FreshTyre,
AirTemp, TrackTemp, Humidity, Pressure, WindSpeed, Rainfall, LapTime_s`.

Czyszczenie zastosowane w `01` (nie cofać bez powodu):
- usunięte okrążenia bez `LapTime`,
- usunięte in/out-lapy (niepuste `PitInTime`/`PitOutTime`),
- tylko zielona flaga (`TrackStatus == '1'` — bez SC/VSC/żółtych),
- tylko `IsAccurate == True`,
- reguła 107% per wyścig (odcięcie outlierów: traffic, lift&coast).

**`driver_race.parquet`** — jeden wiersz = kierowca × wyścig. Kolumny:
`Round, EventName, Driver, Team, GridPosition, Position, Points, Status,
quali_gap_s, podium`. Target: `podium = (Position <= 3)`.

## Decyzje modelowe — NIE łamać bez wyraźnej prośby

### Regresja (`03`)
- Target `LapTime_s`. Cechy kategoryczne: `Compound`, `Team`; numeryczne: `TyreLife`,
  `FreshTyre`, `Stint`, `LapNumber`, pogoda.
- **LEAKAGE — krytyczne:** nigdy nie dodawaj do cech `Sector1/2/3Time` ani
  `SpeedI1/I2/FL/ST`. Są policzone z tego samego okrążenia → model „ściąga" target.
  Te kolumny są celowo wyrzucone już w `01`.
- **Split per wyścig** (`GroupShuffleSplit` po `Round`) — okrążenia z jednego GP nie
  mogą trafić naraz do train i test. Nie zamieniaj na zwykły random split.
- Model główny: `HistGradientBoostingRegressor` z natywnymi kategoriami
  (`categorical_features=...`, bez one-hot). Baseline: `LinearRegression` (z one-hot).
  Powód doboru: zależność opona→czas jest nieliniowa + kategorie + interakcje.
- Uwaga interpretacyjna: `LapNumber` (proxy paliwa) jest skorelowany z `TyreLife`.

### Klasyfikacja (`04`)
- Target `podium`. Cechy: `GridPosition`, `Team`, `quali_gap_s` — **wyłącznie
  przedwyścigowe** (znane przed startem). To ma być uczciwe *przewidywanie*, nie opis
  po fakcie. Nie dodawaj cech z przebiegu wyścigu (tempo, liczba pitstopów) do modelu
  głównego — chyba że robisz świadomie osobny wariant „opisowy" (zaznacz to w markdown).
- **Klasy niezbalansowane** (~15% podium). Oceniaj przez precision/recall, ROC-AUC,
  PR-AUC i macierz pomyłek — **nie przez accuracy** (model „nigdy podium" ma ~85%).
- Model główny: `LogisticRegression(class_weight='balanced')` — przy jednym sezonie
  (~480 wierszy, ~70 podiów) jest wiarygodniejszy i interpretowalny. HGB tylko do
  porównania; nie czyń go głównym bez większego zbioru.
- Walidacja: `StratifiedKFold(5)` + `cross_val_predict` (mało danych → CV, nie jeden split).

## Stan i co dalej

- Zrobione: wszystkie notebooki `01`–`05`, struktura kompletna, kod gotowy do odpalenia.
- Aktualnie tylko **sezon 2024**. Klasyfikacja jest „chwiejna" przez małą liczbę
  podiów — najtańsza poprawa to rozszerzenie `01` o kolejne sezony (pętla po latach
  z zapisem do tego samego parquet). Wtedy zmienia się tylko `01`, reszta bez zmian.
- Możliwe kierunki: tuning HGB (`03`), kalibracja prawdopodobieństw (`04`),
  dodanie cechy toru/`Round` jako kategorii, walidacja czasowa (trenuj na wcześniejszych
  rundach, testuj na późniejszych).

## Jak uruchomić

```bash
# z katalogu notebooks/
jupyter lab
# odpal po kolei: 01 (wolny, raz) -> 02 -> 03 -> 04 -> 05
```

Jeśli `01` rzuci błąd sieci na którymś GP — pętla ma `try/except`, pomija rundę i leci dalej.
