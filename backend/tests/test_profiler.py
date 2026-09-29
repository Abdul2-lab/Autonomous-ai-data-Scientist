import pandas as pd
import numpy as np
from app.agents.profiler_agent import ProfilerAgent


def test_profiler_detects_missing_and_duplicates():
    df = pd.DataFrame({
        "a": [1, 2, None, 4, 4],
        "b": ["x", "y", "z", "x", "x"],
    })
    result = ProfilerAgent().run(df)
    assert result["rows"] == 5
    assert result["columns"] == 2
    assert result["missing_values"]["a"] == 1
    assert result["duplicate_rows"] == 1
    assert "a" in result["numeric_columns"]
    assert "b" in result["categorical_columns"]


def test_profiler_detects_constant_column():
    df = pd.DataFrame({"a": [1, 2, 3], "const": [5, 5, 5]})
    result = ProfilerAgent().run(df)
    assert "const" in result["constant_columns"]
