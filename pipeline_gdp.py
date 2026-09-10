import marimo

__generated_with = "0.23.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl

    from south_africa.adapters import gdp as adapters
    from south_africa.connectors import gdp as connectors

    DATA_FOLDER = "./south_africa/data"
    return DATA_FOLDER, adapters, connectors, pl


@app.cell
async def _(connectors):
    filenames = [
        "GDP P0441 - GDP Time series Q2 2026.xlsx",
        "GDP P0441- Q2 2026.xlsx",
    ]

    for filename in filenames:
        url = f"https://www.statssa.gov.za/publications/P0441/{filename}"
        await connectors.download(url=url)
    return


@app.cell
def _(DATA_FOLDER, adapters):
    file = f"{DATA_FOLDER}/gdp-p0441-gdp-time-series-q2-2026.xlsx"
    gdp_df = adapters.transform(file=file)
    gdp_df.write_csv(f"{DATA_FOLDER}/south_africa_stats_gdp_q2.csv")
    return (gdp_df,)


@app.cell
def _(gdp_df):
    gdp_df.head()
    return


@app.cell
def _(gdp_df, pl):
    filtered_df = gdp_df.filter((pl.col("value").is_not_null()) & (pl.col("date") == pl.date(1993, 1, 1)))
    filtered_df.head()
    return


if __name__ == "__main__":
    app.run()
