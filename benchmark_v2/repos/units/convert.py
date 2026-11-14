"""Convert values between units of the same dimension."""
from units import LENGTH, MASS, TEMPERATURE, canonical, dimension


def convert(value: float, src: str, dst: str) -> float:
    """Convert value from unit src to unit dst.

    Unknown units raise KeyError; units of different dimensions raise ValueError.
    """
    src, dst = canonical(src), canonical(dst)
    dim = dimension(src)
    if dimension(dst) != dim:
        raise ValueError(f"cannot convert {src} ({dim}) to {dst}")
    if dim == "temperature":
        scale, offset = TEMPERATURE[src]
        kelvin = (value + offset) * scale
        scale, offset = TEMPERATURE[dst]
        return kelvin / scale - offset
    table = LENGTH if dim == "length" else MASS
    return value * table[src] / table[dst]
