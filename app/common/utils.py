from datetime import datetime


def format_timestamp(
    timestamp: datetime, format_string: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """Formats a timestamp into a human-readable string.

    Args:
        timestamp (datetime): The datetime object to format.
        format_string (str): The format in which to display the timestamp.
                             Default is '%Y-%m-%d %H:%M:%S'.

    Returns:
        str: The formatted timestamp as a string, or an empty string if the timestamp is None.
    """
    if timestamp is None:
        return ""
    return timestamp.strftime(format_string)
