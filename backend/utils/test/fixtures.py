"""Utils for test fixtures."""
import json
from typing import Any, Dict, List
from uuid import UUID

from utils.test.common import get_date


def get_fixture_data(path: str, fixture_name: str) -> List[Dict[str, Any]]:
    """Prepare DB data from fixture {path}/fixture/{fixture_name}.json file.

    Arguments:
        path -- folder where fixture folder is
        fixture_name -- name of the .json file, without extension.

    Returns:
        Array of objects to be inserted into the database.
    """
    with open(f"{path}/fixtures/{fixture_name}.json") as fixtures:
        json_data: List[Dict[str, Any]] = json.load(fixtures)
        for row in json_data:
            for key, value in row.items():
                if type(value) == str:
                    date = get_date(value)
                    if date:
                        row[key] = date
        return json_data


def key_with_uuids(data: List[Dict[str, Any]], key: str) -> None:
    """Set data key in data dict list as uuid.

    Arguments:
        data -- data dictionary list
        key -- key to convert to uuid type
    """
    for row in data:
        row[key] = UUID(row[key])


def key_with_str_value(data: List[Dict[str, Any]], key: str) -> None:
    """Set data key in data dict list as uuid.

    Arguments:
        data -- data dictionary list
        key -- key to convert to uuid type
    """
    for row in data:
        row[key] = str(row[key])
