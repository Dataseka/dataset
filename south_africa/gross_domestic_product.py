import marimo

__generated_with = "0.23.9"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # South African Gross Domestic Product (GDP)

    This notebook ingests quarterly GDP releases from [StatsSA](https://www.statssa.gov.za/publications/P0441), transforms the source workbook into the Dataseka target format, and exports a clean CSV for downstream use.

    The core steps of the data pipeline are:
    1. **Extract:** Download the latest GDP publication files.
    2. **Transform:** Parse and normalize GDP time series data.
    3. **Load:** Export the unified dataset as CSV.

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Add imports

    We import the GDP connector for file downloads and the GDP adapter for transformation.

    ```python
    from adapters import gdp as adapters
    from connectors import gdp as connectors

    DATA_FOLDER = "./south_africa/data"
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1. Ingest Raw Data

    Build download URLs from known StatsSA release filenames and fetch each workbook asynchronously.

    **💡 Future Improvement:** The filenames are release-specific. A future version can discover the latest publication dynamically from the StatsSA releases page.

    ```python
    filenames = [
        "GDP P0441 - GDP Time series Q1 2026.xlsx",
        "GDP P0441- Q1 2026.xlsx",
    ]

    for filename in filenames:
        url = f"https://www.statssa.gov.za/publications/P0441/{filename}"
        await connectors.download(url=url)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2. Transform and Export GDP Data

    Process the GDP time-series workbook through the GDP adapter and write the transformed result to CSV.

    ```python
    file = f"{DATA_FOLDER}/gdp-p0441-gdp-time-series-q1-2026.xlsx"
    gdp_df = adapters.transform(file=file)
    gdp_df.write_csv(f"{DATA_FOLDER}/south_africa_stats_gdp.csv")
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
