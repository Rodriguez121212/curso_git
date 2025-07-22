"""Common test utils."""
import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID


def sort_dict_list(
    data: List[Dict[str, Any]],
    expected_keys: List[str] = [],
    ids_in: List[int] = [],
    order_by: str = "",
    sort_fn: Callable[[Dict[str, Any]], Any] = lambda x: x["id"],
    reverse: bool = False,
) -> List[Dict[str, Any]]:
    """Prepare expected results.

    Arguments:
        data -- Data to prepare
        expected_keys -- fields to show
        filter_in -- ids to filter in
        order_by -- key to order by
        sort_fn -- sort function
        reverse -- if the result should be reversed

    Returns:
        prepared data.
    """
    if ids_in:
        data = list(filter(lambda x: x["id"] in ids_in, data))

    if order_by:

        def new_sort_fn(x: Dict[str, Any]) -> Any:
            return x[order_by]

        sort_fn = new_sort_fn

    data = sorted(data, key=sort_fn, reverse=reverse)

    if expected_keys:
        data = [{key: ciclo[key] for key in expected_keys} for ciclo in data]

    return data


def get_date(date_text: str) -> Optional[datetime.datetime]:
    """Try to convert a string to datetime.

    Arguments:
        date_text -- string date with YEAR-MONTH-DAY.

    Returns:
        Datetime if parse is possible else None.
    """
    try:
        return datetime.datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return None


def get_sorting_key(input_record: Dict[str, Any]) -> Any:
    """Get sorting key.

    Arguments:
        input_record -- record to sort.

    Returns:
        A key to use for sorting purposes.
    """
    return input_record["id"]


def is_valid_uuid(value: Any) -> bool:
    """Check if value is a valid uuid.

    Arguments:
        value -- value to validate

    Returns:
        True if value is a valid uuid, False otherwise
    """
    try:
        UUID(str(value))
    except Exception:
        return False
    return True
