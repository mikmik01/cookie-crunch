import pandas as pd

ALLOWED_COLUMNS = {
    "rank",
    "lane",
    "hero",
    "tier",
    "win_rate",
    "ban_rate",
    "pick_rate",
    "roles",
}

ALLOWED_OPERATORS = {
    "equals",
    "contains",
    ">=",
    "<=",
    ">",
    "<",
}

ALLOWED_DIRECTIONS = {
    "asc",
    "desc",
}


def get_schema() -> dict:
    return {
        "columns": {
            "rank": "Hero rank in the source statistics table.",
            "lane": "Source-provided lane label.",
            "hero": "Hero name.",
            "tier": "Source-provided tier.",
            "win_rate": "Overall hero-level win rate percentage.",
            "ban_rate": "Overall hero-level ban rate percentage.",
            "pick_rate": "Overall hero-level pick rate percentage.",
            "roles": "Hero role labels.",
        },
    }


def filter_rows(
    df: pd.DataFrame,
    filters: list[dict] | None = None,
    sort: list[dict] | None = None,
    limit: int = 10,
) -> list[dict]:
    out = df.copy()

    filters = filters or []

    for f in filters:
        column = f.get("column")
        operator = f.get("operator")
        value = f.get("value")

        if column not in ALLOWED_COLUMNS:
            raise ValueError(f"Unsupported column: {column}")

        if operator not in ALLOWED_OPERATORS:
            raise ValueError(f"Unsupported operator: {operator}")

        if operator == "equals":
            out = out[
                out[column].astype(str).str.lower()
                == str(value).lower()
            ]

        elif operator == "contains":
            out = out[
                out[column]
                .astype(str)
                .str.lower()
                .str.contains(str(value).lower(), na=False)
            ]

        elif operator in {">=", "<=", ">", "<"}:
            numeric_col = pd.to_numeric(out[column], errors="coerce")
            numeric_value = float(value)

            if operator == ">=":
                out = out[numeric_col >= numeric_value]
            elif operator == "<=":
                out = out[numeric_col <= numeric_value]
            elif operator == ">":
                out = out[numeric_col > numeric_value]
            elif operator == "<":
                out = out[numeric_col < numeric_value]

    sort = sort or []

    if sort:
        sort_columns = []
        ascending = []

        for s in sort:
            column = s.get("column")
            direction = s.get("direction")

            if column not in ALLOWED_COLUMNS:
                raise ValueError(f"Unsupported sort column: {column}")

            if direction not in ALLOWED_DIRECTIONS:
                raise ValueError(f"Unsupported sort direction: {direction}")

            sort_columns.append(column)
            ascending.append(direction == "asc")

        out = out.sort_values(sort_columns, ascending=ascending)

    safe_limit = max(1, min(int(limit or 10), 50))

    return out.head(safe_limit).to_dict(orient="records")


ALLOWED_AGG_FUNCS = {
    "mean",
    "median",
    "max",
    "min",
    "count",
}


def aggregate_rows(
    df: pd.DataFrame,
    group_by: str,
    metrics: list[dict],
    sort: list[dict] | None = None,
    limit: int = 10,
) -> list[dict]:
    if group_by not in ALLOWED_COLUMNS:
        raise ValueError(f"Unsupported group_by column: {group_by}")

    if not metrics:
        raise ValueError("At least one metric is required")

    agg_spec = {}

    for metric in metrics:
        column = metric.get("column")
        func = metric.get("function")

        if column not in ALLOWED_COLUMNS:
            raise ValueError(f"Unsupported metric column: {column}")

        if func not in ALLOWED_AGG_FUNCS:
            raise ValueError(f"Unsupported aggregation function: {func}")

        output_name = f"{column}_{func}"

        if func == "count":
            agg_spec[output_name] = (column, "count")
        else:
            agg_spec[output_name] = (column, func)

    grouped = (
        df.groupby(group_by, dropna=False)
        .agg(**agg_spec)
        .reset_index()
    )

    sort = sort or []

    if sort:
        sort_columns = []
        ascending = []

        for s in sort:
            column = s.get("column")
            direction = s.get("direction")

            if column not in grouped.columns:
                raise ValueError(f"Unsupported sort column: {column}")

            if direction not in ALLOWED_DIRECTIONS:
                raise ValueError(f"Unsupported sort direction: {direction}")

            sort_columns.append(column)
            ascending.append(direction == "asc")

        grouped = grouped.sort_values(sort_columns, ascending=ascending)

    safe_limit = max(1, min(int(limit or 10), 50))

    return grouped.head(safe_limit).to_dict(orient="records")