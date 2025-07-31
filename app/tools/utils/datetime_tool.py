"""DateTime utility tool for the Feito/Conferido agent.

Provides a tool to get the current date and time in Brazilian timezone
for use in validation reports.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Any


def get_current_datetime() -> Dict[str, Any]:
    """Gets the current date and time in Brazilian timezone.

    Returns the current timestamp formatted for use in validation reports,
    using São Paulo timezone (UTC-3).

    Returns:
        Dictionary containing:
            - formatted_datetime: Full datetime string in pt-BR format
            - date: Date only in DD/MM/YYYY format
            - time: Time only in HH:MM:SS format
            - timestamp: ISO format timestamp with timezone

    Example:
        >>> result = get_current_datetime()
        >>> print(result)
        {
            "formatted_datetime": "31/12/2024 14:30:45",
            "date": "31/12/2024",
            "time": "14:30:45",
            "timestamp": "2024-12-31T14:30:45-03:00"
        }
    """
    br_tz = ZoneInfo("America/Sao_Paulo")
    now = datetime.now(br_tz)
    
    formatted_datetime = now.strftime("%d/%m/%Y %H:%M:%S")
    date_only = now.strftime("%d/%m/%Y")
    time_only = now.strftime("%H:%M:%S")
    iso_timestamp = now.isoformat()
    
    return {
        "formatted_datetime": formatted_datetime,
        "date": date_only,
        "time": time_only,
        "timestamp": iso_timestamp
    }
