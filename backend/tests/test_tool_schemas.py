from app.services.data_tools import ALLOWED_COLUMNS
from app.schemas.schemas import TOOL_NAMES, build_tool_context, get_tool_schemas


def _schema_by_name(name: str) -> dict:
    return next(schema for schema in get_tool_schemas() if schema["name"] == name)


def test_tool_schemas_expose_expected_tools():
    assert TOOL_NAMES == {"get_schema", "filter_rows", "aggregate_rows"}


def test_filter_rows_schema_uses_allowed_columns_and_operators():
    schema = _schema_by_name("filter_rows")
    params = schema["parameters"]

    filter_item = params["properties"]["filters"]["items"]
    column_enum = set(filter_item["properties"]["column"]["enum"])
    operator_enum = set(filter_item["properties"]["operator"]["enum"])

    assert column_enum == ALLOWED_COLUMNS
    assert operator_enum == {"equals", "contains", ">=", "<=", ">", "<"}
    assert params["properties"]["limit"]["maximum"] == 50


def test_aggregate_rows_schema_requires_group_by_and_metrics():
    schema = _schema_by_name("aggregate_rows")
    params = schema["parameters"]

    assert params["required"] == ["group_by", "metrics"]
    assert set(params["properties"]["group_by"]["enum"]) == ALLOWED_COLUMNS
    assert params["properties"]["metrics"]["minItems"] == 1


def test_tool_context_contains_dataset_schema_and_tools():
    context = build_tool_context()

    assert "dataset_schema" in context
    assert "tool_schemas" in context
    assert "hero" in context["dataset_schema"]["columns"]
    assert len(context["tool_schemas"]) == 3