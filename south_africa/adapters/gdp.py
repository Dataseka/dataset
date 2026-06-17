import polars as pl


def transform(file: str) -> pl.DataFrame:
    df_annual = pl.read_excel(file, sheet_name="Annual", infer_schema_length=0)
    df_annual_p = pl.read_excel(file, sheet_name="AnnualP", infer_schema_length=0)

    df_quarterly = pl.read_excel(file, sheet_name="Quarterly", infer_schema_length=0)
    df_quarterly_p = pl.read_excel(file, sheet_name="QuarterlyP", infer_schema_length=0)

    h_mapping = {
        "H01": "release_code",
        "H02": "publication",
        "H03": "series_code",
        "H04": "category",
        "H05": "sub_category",
        "H06": "sub_component",
        "H15": "price_type",
        "H16": "seasonal_adjustment",
        "H17": "metric",
        "H25": "frequency",
    }

    # --- Annual Processing ---
    annual_h_cols = [c for c in df_annual_p.columns if c.startswith("H")]
    df_annual_p = df_annual_p.rename({c: h_mapping.get(c, c) for c in annual_h_cols})
    df_annual = df_annual.rename({c: h_mapping.get(c, c) for c in annual_h_cols})
    annual_ids = [h_mapping.get(c, c) for c in annual_h_cols]

    annual_long_p = (
        df_annual_p.unpivot(index=annual_ids, variable_name="raw_date", value_name="value")
        .with_columns(
            date=pl.col("raw_date").str.slice(1).str.to_date("%Y"),
            value=pl.col("value").cast(pl.Float64, strict=False),
        )
        .drop("raw_date")
    )

    annual_long_v = (
        df_annual.unpivot(index=annual_ids, variable_name="raw_date", value_name="value")
        .with_columns(
            date=pl.col("raw_date").str.slice(1).str.to_date("%Y"),
            value=pl.col("value").cast(pl.Float64, strict=False),
            metric=pl.lit("Rand Value"),
        )
        .drop("raw_date")
    )

    # --- Quarterly Processing ---
    quarterly_h_cols = [c for c in df_quarterly_p.columns if c.startswith("H")]
    df_quarterly_p = df_quarterly_p.rename({c: h_mapping.get(c, c) for c in quarterly_h_cols})
    df_quarterly = df_quarterly.rename({c: h_mapping.get(c, c) for c in quarterly_h_cols})
    quarterly_ids = [h_mapping.get(c, c) for c in quarterly_h_cols]

    quarterly_long_p = (
        df_quarterly_p.unpivot(index=quarterly_ids, variable_name="raw_date", value_name="value")
        .with_columns(
            year=pl.col("raw_date").str.slice(0, 4), q_idx=pl.col("raw_date").str.slice(4, 2).cast(pl.Int32)
        )
        .with_columns(month=((pl.col("q_idx") * 3) - 2).cast(pl.String).str.zfill(2))
        .with_columns(
            date=(pl.col("year") + "-" + pl.col("month") + "-01").str.to_date("%Y-%m-%d"),
            value=pl.col("value").cast(pl.Float64, strict=False),
        )
        .drop("raw_date", "year", "q_idx", "month")
    )

    quarterly_long_v = (
        df_quarterly.unpivot(index=quarterly_ids, variable_name="raw_date", value_name="value")
        .with_columns(
            year=pl.col("raw_date").str.slice(0, 4), q_idx=pl.col("raw_date").str.slice(4, 2).cast(pl.Int32)
        )
        .with_columns(month=((pl.col("q_idx") * 3) - 2).cast(pl.String).str.zfill(2))
        .with_columns(
            date=(pl.col("year") + "-" + pl.col("month") + "-01").str.to_date("%Y-%m-%d"),
            value=pl.col("value").cast(pl.Float64, strict=False),
            metric=pl.lit("Rand Value"),
        )
        .drop("raw_date", "year", "q_idx", "month")
    )

    combined_df = pl.concat([annual_long_p, annual_long_v, quarterly_long_p, quarterly_long_v], how="diagonal")

    return combined_df
