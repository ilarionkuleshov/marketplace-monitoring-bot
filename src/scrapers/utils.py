def crop_str(str_value: str, max_length: int) -> str:
    """Returns cropped string.

    Args:
        str_value (str): String value.
        max_length (int): Maximum length of the string.

    """
    if len(str_value) > max_length:
        return str_value[:max_length-3] + "..."
    return str_value
