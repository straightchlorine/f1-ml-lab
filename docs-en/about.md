# About

This site is the record of a Master's-level machine learning course project: six Jupyter notebooks that go from raw Formula 1 data to two models and an analysis of their errors. The notebooks are pre-executed - the Plotly charts are interactive without running anything.

## Data

- Source: [FastF1](https://docs.fastf1.dev/) - official F1 timing, weather and telemetry.
- Seasons 2023-2024: 46 races, 39,647 clean laps ([`laps_clean.parquet`](https://github.com/straightchlorine/f1-ml-lab/blob/master/data/laps_clean.parquet)) and 918 driver-race pairs including 138 podiums ([`driver_race.parquet`](https://github.com/straightchlorine/f1-ml-lab/blob/master/data/driver_race.parquet)).
- For the "will more seasons help?" experiments - the same datasets for seasons 2018-2024 ([`laps_all.parquet`](https://github.com/straightchlorine/f1-ml-lab/blob/master/data/laps_all.parquet), [`driver_race_all.parquet`](https://github.com/straightchlorine/f1-ml-lab/blob/master/data/driver_race_all.parquet)).
- The ready-made files live in the repository's [`data/`](https://github.com/straightchlorine/f1-ml-lab/tree/master/data) folder, so notebooks 02-05 run without downloading anything.

## How to read it

- The model failures are in the notebooks on purpose: negative `R^2` in the regression, the accuracy trap and data leakage in the classification. We first show why something does not work, and only then the fix.
- Every model comes with a benchmark that times training and prediction, because the simple model is often both the best and the cheapest.
- In the English version the commentary (markdown cells) is translated; code, printed output and chart labels remain in Polish.

## How to run it

```bash
git clone https://github.com/straightchlorine/f1-ml-lab.git
cd f1-ml-lab
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/jupyter lab   # notebooks in notebooks/, in order 00 -> 05
```

Notebook 01 downloads data from FastF1 (the first run takes long, later runs read from cache). The remaining notebooks start from the parquet files.

## Authors

- **Piotr Krzysztof Lis** - [piotrkrzysztof.dev](https://piotrkrzysztof.dev) | [GitHub](https://github.com/straightchlorine) | [Codeberg](https://codeberg.org/piotrkrzysztof) | [LinkedIn](https://www.linkedin.com/in/straightchlorine/)
- **Jakub Kucharski** - [GitHub](https://github.com/kubson2002k) | [LinkedIn](https://www.linkedin.com/in/jakub-kucharski-360811305/)

Source code: [straightchlorine/f1-ml-lab](https://github.com/straightchlorine/f1-ml-lab). Built with MkDocs Material and mkdocs-jupyter.
