import pandas as pd
import numpy as np
from app.agents.profiler_agent import ProfilerAgent
from app.agents.cleaning_agent import CleaningAgent


def test_cleaning_removes_duplicates_and_imputes_missing():
    df = pd.DataFrame({
        "num": [1.0, 2.0, np.nan, 4.0, 4.0],
        "cat": ["a", "b", None, "a", "a"],
    })
    df = pd.concat([df, df.iloc[:1]], ignore_index=True)  # add a duplicate row
    profiling = ProfilerAgent().run(df)

    cleaned, summary, path = CleaningAgent().run(df, profiling)

    assert cleaned["num"].isnull().sum() == 0
    assert cleaned["cat"].isnull().sum() == 0
    assert summary["duplicate_rows_removed"] >= 1
    import os
    assert os.path.exists(path)
    # original df must be untouched
    assert df["num"].isnull().sum() == 1
