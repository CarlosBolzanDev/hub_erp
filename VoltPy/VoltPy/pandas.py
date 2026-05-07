"""Controlled pandas facade for VoltPy apps."""

from importing.hook import import_real_module

_pandas = import_real_module("pandas")
if not hasattr(_pandas, "DataFrame"):
    raise ImportError(f"Real pandas did not expose DataFrame; loaded from {getattr(_pandas, '__file__', None)}")

DataFrame = _pandas.DataFrame
Series = _pandas.Series
read_csv = _pandas.read_csv
concat = _pandas.concat

__all__ = ["DataFrame", "Series", "read_csv", "concat"]
