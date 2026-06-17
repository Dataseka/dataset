import marimo

__generated_with = "0.23.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl

    from south_africa.adapters import cpi as adapters
    from south_africa.connectors import cpi as connectors

    DATA_FOLDER = "./south_africa/data"
    return DATA_FOLDER, adapters, connectors, pl


@app.cell
async def _(connectors):
    filenames = [
        "P0141 - CPI(COICOP) from Jan 2008 (202605).zip",
        "P0141 - CPI Average Prices Provinces (202605).zip",
        "P0141 - CPI Average Prices All urban (202605).zip",
        "P0160 Residential Property Price Index Report(202601).zip"
    ]

    for filename in filenames:
        url = f"https://www.statssa.gov.za/../timeseriesdata/Excel/{filename}"

        await connectors.download(url=url)
    return


@app.cell
def _(DATA_FOLDER, adapters, pl):
    avg_prices_all_urban_df = adapters.transform_avg_prices_all_urban(
        data=pl.read_excel(
            f"{DATA_FOLDER}/cpi-average-prices-all-urban-202605.xlsx",
            infer_schema_length=0
        )
    )
    return (avg_prices_all_urban_df,)


@app.cell
def _(DATA_FOLDER, adapters, pl):
    avg_prices_provinces_df = adapters.transform_avg_prices_provinces(
        data=pl.read_excel(
            f"{DATA_FOLDER}/cpi-average-prices-provinces-202605.xlsx",
            infer_schema_length=0
        )
    )
    return (avg_prices_provinces_df,)


@app.cell
def _(DATA_FOLDER, adapters, pl):
    indices_history_df = adapters.transform_indices_history(
        data=pl.read_excel(
            f"{DATA_FOLDER}/excel-cpi-coicop-from-january-2008-202605.xlsx",
            infer_schema_length=0
        )
    )
    return (indices_history_df,)


@app.cell
def _(DATA_FOLDER, adapters, pl):
    residential_property_df = adapters.transform_residential_property(
        data=pl.read_excel(
            f"{DATA_FOLDER}/residential-property-price-indices-2010-to-2026.xlsx",
            infer_schema_length=0
        )
    )
    return (residential_property_df,)


@app.cell
def _(
        DATA_FOLDER,
        avg_prices_all_urban_df,
        avg_prices_provinces_df,
        indices_history_df,
        pl,
        residential_property_df,
):
    stats_sa_df = pl.concat(
        [
            avg_prices_all_urban_df,
            avg_prices_provinces_df,
            indices_history_df,
            residential_property_df
        ],
        how="vertical"
    )

    stats_sa_df.write_csv(f"{DATA_FOLDER}/south_africa_stats_cpi_202605.csv")

    return


if __name__ == "__main__":
    app.run()
