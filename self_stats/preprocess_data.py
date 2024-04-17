import pandas as pd
from typing import Tuple
import ruptures as rpt
from pathlib import Path
from typing import Union


def load_and_preprocess_data(file_path: Union[str | Path])  -> pd.DataFrame:
    """
    Loads data from a CSV file, preprocesses it by extracting relevant datetime features,
    and filters the data based on a changepoint analysis.

    Returns:
        pd.DataFrame: A DataFrame with preprocessed and filtered data.
    """
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)

    df['Hour'] = df['Date'].dt.hour
    df['Date'] = df['Date'].dt.date

    daily_counts = df.groupby('Date').size()
    data = daily_counts.values.reshape(-1, 1)
    algo = rpt.Binseg(model='l2').fit(data)
    result = algo.predict(n_bkps=1)

    if result:
        changepoint_date = daily_counts.index[result[0] - 1]
    else:
        changepoint_date = daily_counts.index.min()

    return df[df['Date'] >= changepoint_date]

df = load_and_preprocess_data('/home/bio/Python_projects/self_stats/data/extracted_watch_history_data.csv')

df.to_csv('/home/bio/Python_projects/self_stats/data/filtered_watch_history_data.csv', index=False)
