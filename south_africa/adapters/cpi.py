import polars as pl
import polars.selectors as cs

from south_africa.shared import CPI_STANDARD_SCHEMA


def transform_avg_prices_all_urban(data: pl.DataFrame) -> pl.DataFrame:
    return (
        data.select(
            pl.col("H01").alias("catalog_code"),
            pl.col("H02").alias("catalog_name"),
            pl.col("H03").alias("data_code"),
            pl.col("H04").alias("data_name"),
            pl.col("H06").str.to_titlecase().alias("frequency"),
            pl.col("H08"),
            cs.matches(r"^M\d{6}$"),
        )
        .unpivot(
            index=[
                "catalog_code",
                "catalog_name",
                "data_code",
                "data_name",
                "frequency",
                "H08",
            ],
            variable_name="period_raw",
            value_name="value",
        )
        .with_columns(pl.col("value").cast(pl.Float64, strict=False))
        .drop_nulls("value")
        .with_columns(
            pl.lit("Price").alias("data_type"),
            pl.lit("Urban areas").alias("region"),
            pl.lit("2024-12-01").str.to_date().alias("base_period"),
            (pl.col("period_raw").str.slice(1) + "01")
            .str.to_date("%Y%m%d")
            .alias("period"),
            pl.col("H08").str.extract(r"^([\d\.]+)").cast(pl.Float64).alias("quantity"),
            pl.col("H08").str.extract(r"^[\d\.]+\s+(.*)$").alias("unit"),
        )
        .select(CPI_STANDARD_SCHEMA)
    )


def transform_avg_prices_provinces(data: pl.DataFrame) -> pl.DataFrame:
    return (
        data.select(
            pl.col("H01").alias("catalog_code"),
            pl.col("H02").alias("catalog_name"),
            pl.col("H03").alias("data_code"),
            pl.col("H04").alias("data_name"),
            pl.col("H06").str.to_titlecase().alias("frequency"),
            pl.col("H08"),
            pl.col("H09").alias("region"),
            cs.matches(r"^M\d{6}$"),
        )
        .unpivot(
            index=[
                "catalog_code",
                "catalog_name",
                "data_code",
                "data_name",
                "frequency",
                "H08",
                "region",
            ],
            variable_name="period_raw",
            value_name="value",
        )
        .with_columns(pl.col("value").cast(pl.Float64, strict=False))
        .drop_nulls("value")
        .with_columns(
            pl.lit("Price").alias("data_type"),
            pl.lit("2024-12-01").str.to_date().alias("base_period"),
            (pl.col("period_raw").str.slice(1) + "01")
            .str.to_date("%Y%m%d")
            .alias("period"),
            pl.col("H08").str.extract(r"^([\d\.]+)").cast(pl.Float64).alias("quantity"),
            pl.col("H08").str.extract(r"^[\d\.]+\s+(.*)$").alias("unit"),
        )
        .select(CPI_STANDARD_SCHEMA)
    )


def transform_indices_history(data: pl.DataFrame) -> pl.DataFrame:
    return (
        data.select(
            pl.col("H01").alias("catalog_code"),
            pl.col("H02").alias("catalog_name"),
            pl.col("H03").alias("data_code"),
            pl.col("H04")
            .str.replace("Analytical series - ", "")
            .str.replace("All urban areas", "Urban areas"),
            pl.col("H05"),
            pl.col("H13").str.replace("All urban areas", "Urban areas").alias("region"),
            pl.col("H17").alias("data_type"),
            pl.col("H18").alias("base_period"),
            pl.col("H25").str.to_titlecase().alias("frequency"),
            cs.matches(r"^MO\d{6}$"),
        )
        .unpivot(
            index=[
                "catalog_code",
                "catalog_name",
                "data_code",
                "H04",
                "H05",
                "region",
                "data_type",
                "base_period",
                "frequency",
            ],
            variable_name="period_raw",
            value_name="value",
        )
        .with_columns(pl.col("value").cast(pl.Float64, strict=False))
        .drop_nulls("value")
        .with_columns(
            pl.when(pl.col("H05").is_not_null() & (pl.col("H05") != ""))
            .then(pl.col("H04") + " (" + pl.col("H05") + ")")
            .otherwise(pl.col("H04"))
            .alias("data_name"),
            (pl.col("base_period").str.extract(r"([A-Za-z]{3}\s\d{4})") + " 01")
            .str.to_date("%b %Y %d")
            .alias("base_period"),
            ("01" + pl.col("period_raw").str.slice(2))
            .str.to_date("%d%m%Y")
            .alias("period"),
            pl.lit(None, dtype=pl.String).alias("unit"),
            pl.lit(None, dtype=pl.Float64).alias("quantity"),
        )
        .select(CPI_STANDARD_SCHEMA)
    )


def transform_residential_property(data: pl.DataFrame) -> pl.DataFrame:
    return (
        data.select(
            pl.col("H01").alias("catalog_code"),
            pl.col("H02").alias("catalog_name"),
            pl.col("H03").alias("data_code"),
            pl.col("H04").alias("data_name"),
            pl.col("H05").alias("region"),
            pl.col("H17").alias("data_type"),
            pl.col("H18").alias("base_period"),
            cs.matches(r"^m\d{6}$"),
        )
        .unpivot(
            index=[
                "catalog_code",
                "catalog_name",
                "data_code",
                "data_name",
                "region",
                "data_type",
                "base_period",
            ],
            variable_name="period_raw",
            value_name="value",
        )
        .with_columns(pl.col("value").cast(pl.Float64, strict=False))
        .drop_nulls("value")
        .with_columns(
            pl.lit("monthly").alias("frequency"),
            pl.lit(None, dtype=pl.String).alias("unit"),
            pl.lit(None, dtype=pl.Float64).alias("quantity"),
            pl.col("data_type").str.to_lowercase(),
            (pl.col("period_raw").str.slice(1) + "01")
            .str.to_date("%Y%m%d")
            .alias("period"),
            (
                pl.col("base_period").str.extract(r"([A-Za-z]{3}\s\d{4})") + " 01"
            ).str.to_date("%b %Y %d"),
        )
        .select(CPI_STANDARD_SCHEMA)
    )
