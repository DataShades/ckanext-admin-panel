from __future__ import annotations

from typing import Any

from ckanext.ap_support import config as support_config


def ap_support_get_category_options() -> list[dict[str, Any]]:
    return [
        {"value": category, "text": category}
        for category in support_config.get_ticket_categories()
    ]


def ap_support_calculate_priority(value: int, threshold: int) -> str:
    """Calculate the priority of a value based on a threshold.

    Args:
        value: The value to calculate the priority for
        threshold: The threshold to compare the value to

    Returns:
        The priority of the value

    Example:
        ```python
        from ckanext.ap_main.helpers import calculate_priority

        priority = calculate_priority(10, 100)
        print(priority) # low
        ```
    """
    percentage = value / threshold * 100

    if percentage < 25:
        return "low"
    if percentage < 50:
        return "medium"
    if percentage < 75:
        return "high"

    return "urgent"
