import pytest

from app.services.extractor import extract_stats
from app.schemas.schemas import STAT_FIELDS


def test_extract_stats_returns_records_with_expected_schema():
    html = """
    <html>
      <body>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Lane</th>
              <th>Hero</th>
              <th>Tier</th>
              <th>Win Rate</th>
              <th>Ban Rate</th>
              <th>Pick Rate</th>
              <th>Roles</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>1</td>
              <td></td>
              <td>Cecilion</td>
              <td>S</td>
              <td>53.20%</td>
              <td>12.50%</td>
              <td>8.10%</td>
              <td>Mage</td>
            </tr>
            <tr>
              <td>2</td>
              <td></td>
              <td>Granger</td>
              <td>A</td>
              <td>51.00%</td>
              <td>20.00%</td>
              <td>10.00%</td>
              <td>Marksman</td>
            </tr>
          </tbody>
        </table>
      </body>
    </html>
    """

    rows = extract_stats(html)

    assert len(rows) == 2

    for row in rows:
        assert list(row.keys()) == STAT_FIELDS

    assert rows[0] == {
        "rank": "1",
        "lane": "Unknown",
        "hero": "Cecilion",
        "tier": "S",
        "win_rate": "53.20%",
        "ban_rate": "12.50%",
        "pick_rate": "8.10%",
        "roles": "Mage",
    }

    assert rows[1]["hero"] == "Granger"
    assert rows[1]["roles"] == "Marksman"


def test_extract_stats_ignores_incomplete_rows():
    html = """
    <html>
      <body>
        <table>
          <tr>
            <th>Rank</th>
            <th>Lane</th>
            <th>Hero</th>
            <th>Tier</th>
            <th>Win Rate</th>
            <th>Ban Rate</th>
            <th>Pick Rate</th>
            <th>Roles</th>
          </tr>
          <tr>
            <td>1</td>
            <td></td>
            <td>Cecilion</td>
            <td>S</td>
            <td>53.20%</td>
            <td>12.50%</td>
            <td>8.10%</td>
            <td>Mage</td>
          </tr>
          <tr>
            <td>2</td>
            <td>Incomplete row</td>
          </tr>
        </table>
      </body>
    </html>
    """

    rows = extract_stats(html)

    assert len(rows) == 1
    assert rows[0]["hero"] == "Cecilion"


def test_extract_stats_fails_when_table_is_missing():
    html = """
    <html>
      <body>
        <p>No statistics table exists here.</p>
      </body>
    </html>
    """

    with pytest.raises(RuntimeError, match="Could not find any table"):
        extract_stats(html)


def test_extract_stats_fails_when_no_valid_rows_exist():
    html = """
    <html>
      <body>
        <table>
          <tr>
            <th>Rank</th>
            <th>Lane</th>
            <th>Hero</th>
            <th>Tier</th>
            <th>Win Rate</th>
            <th>Ban Rate</th>
            <th>Pick Rate</th>
            <th>Roles</th>
          </tr>
          <tr>
            <td>Incomplete</td>
          </tr>
        </table>
      </body>
    </html>
    """

    with pytest.raises(RuntimeError, match="No stats rows were extracted"):
        extract_stats(html)