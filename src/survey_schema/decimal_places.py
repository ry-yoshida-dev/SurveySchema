from decimal import Decimal


def count_decimal_places(value: Decimal) -> int:
    """
    Count the digits a finite decimal needs after the decimal point.

    Digits are counted numerically, so trailing zeros do not count.

    Parameters
    ----------
    value : Decimal
        Finite value.

    Returns
    -------
    int
        Number of digits after the decimal point.

    Raises
    ------
    ValueError
        If ``value`` is not finite.

    Examples
    --------
    >>> count_decimal_places(Decimal("1.50"))
    1
    >>> count_decimal_places(Decimal("1E+3"))
    0
    """
    if not value.is_finite():
        raise ValueError(f"{value} is not finite.")
    _, digits, exponent = value.as_tuple()
    # Finite decimals always have an int exponent; the literal forms mark NaN and infinity.
    if not isinstance(exponent, int):
        raise ValueError(f"{value} is not finite.")
    if not any(digits):
        return 0
    # Count trailing zeros by hand: normalize() would round to the context precision.
    trailing_zero_count = len(digits) - len("".join(map(str, digits)).rstrip("0"))
    return max(0, -(exponent + trailing_zero_count))
