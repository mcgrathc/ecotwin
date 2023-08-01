import pandas as pd

daily_raw_file = 'C:/Users/mcgr323/projects/ecotwin/ecopod_soil_wcm_temp_and_par.csv'
daily_raw_df = pd.read_csv(daily_raw_file)


def get_daily_means(df):
    # convert "Date" column to datetime
    df["Date"] = pd.to_datetime(df["Date"])

    # group by date and calculate mean
    daily_means = df.groupby(pd.Grouper(key="Date", freq="D")).mean()

    return daily_means


daily_means_lab = get_daily_means(daily_raw_df)

daily_means_lab = daily_means_lab.drop(['Hour'], axis=1)

