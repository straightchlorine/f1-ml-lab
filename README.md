# f1-ml-lab

Machine learning on Formula 1 timing data. A Master's course project by
Piotr Krzysztof Lis and Jakub Kucharski.

[f1.piotrkrzysztof.dev](https://f1.piotrkrzysztof.dev) (Polish) &middot; [English](https://f1.piotrkrzysztof.dev/en/)

Six Jupyter notebooks take 2023-2024 race data from [FastF1](https://docs.fastf1.dev/)
to two models and an analysis of their errors. Failed attempts stay in on purpose:
the notebooks show why an approach breaks before they show the fix.

| Notebook | Contents |
|---|---|
| `00-data-load` | The FastF1 API on one race (Italian Grand Prix 2024) |
| `01-build-dataset` | 46 races cleaned into the two datasets in `data/` |
| `02-eda` | Lap-time distribution, the track effect, tire degradation, grid position vs podium |
| `03-regression-laptime` | Lap pace: a failed model, more data, a better target, a timed benchmark |
| `04-classification-podium` | Podium from pre-race features: accuracy trap, data leakage, benchmark, class weights, calibration |
| `05-error-analysis` | Where and why both models are wrong |

Results:

- Lap pace relative to the race median, on held-out races: linear regression, R^2 0.55, MAE 0.585 s.
- Podium, out-of-fold: logistic regression, ROC-AUC 0.92, PR-AUC 0.70.

## Running the notebooks

Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv venv --python 3.12
uv pip install -r requirements.txt
.venv/bin/python -m ipykernel install --user --name f1-ml-lab
.venv/bin/jupyter lab
```

Notebooks 02-05 start from the parquet files in `data/`. Notebooks 00 and 01 download
from FastF1 on their first run, which takes a while; the cache goes to `cache/`.
`scripts/build_dataset.py` is the same pipeline as a script, and `--all` rebuilds the
2018-2024 files used in the "will more seasons help?" sections.

## Site

MkDocs Material with mkdocs-jupyter. Polish pages are the notebooks themselves;
English pages are the copies in `docs-en/`, with translated markdown and identical
code and outputs, so a notebook change means updating both. Notebook 00 is the other
way round: it is written in English, and its Polish page is `docs/00-data-load.ipynb`.

Preview:

```bash
uv run --isolated --no-project --python 3.12 --with-requirements requirements-docs.txt scripts/preview.sh
```

Cross-notebook links point at exact lines on GitHub. After editing a notebook, run
`python scripts/link_refs.py`.

## License

Code and notebooks: [MIT](LICENSE). The data in `data/` is derived from Formula 1
timing data through FastF1 and is included so the notebooks run.
