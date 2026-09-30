# Machine Learning in F1

Machine learning on Formula 1 data (timing + telemetry via [FastF1](https://docs.fastf1.dev/)).
A notebook series going from raw data to models and error analysis:

1. [First look at the data](00-data-load.ipynb) - the FastF1 API on a single session (Monza 2024)
2. [Building the dataset](01-build-dataset.ipynb) - from raw laps to a feature table
3. [Exploratory data analysis (EDA)](02-eda.ipynb) - what's in the data and what breaks models
4. [Regression: lap time](03-regression-laptime.ipynb) - predicting lap times
5. [Classification: podium](04-classification-podium.ipynb) - who finishes on the podium?
6. [Error analysis](05-error-analysis.ipynb) - where and why the models get it wrong

Data: seasons 2023-2024 (46 races, about 39.6k clean laps, 918 driver-race pairs), pulled via FastF1 and available in the repository as parquet files. The model failures along the way are deliberate - they show why something does not work before we show the fix. More in [About](about.md).

The notebooks are pre-executed - the (Plotly) charts are interactive without running anything.
Source code: [straightchlorine/f1-ml-lab](https://github.com/straightchlorine/f1-ml-lab).
