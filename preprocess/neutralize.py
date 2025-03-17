import pandas as pd
from sklearn.linear_model import LinearRegression
import utils


# Neutralize, by market value / industry
def neutralize(factor_df, factor_name, mktmv_df=None, industry_df=None):
    neu_factor = factor_df.copy()
    if mktmv_df is not None:
        neu_factor = mktmv_neutralize(neu_factor, factor_name, mktmv_df)
    if industry_df is not None:
        neu_factor = ind_neutralize(neu_factor, factor_name, industry_df)
    return neu_factor


def mktmv_neutralize(factor_df, factor_name, mktmv_df):
    utils.check_sub_columns(mktmv_df, ["mktmv"])
    utils.check_sub_columns(factor_df, [factor_name])

    df = pd.merge(factor_df, mktmv_df, on=["trade_date", "stock_code"])
    g = df.groupby("trade_date", group_keys=False)
    df = g.apply(_mktmv_reg, factor_name)
    df = df.drop(columns=["mktmv"])
    return df


def _mktmv_reg(df, factor_name):
    x = df["mktmv"].values.reshape(-1, 1)
    y = df[factor_name]
    lr = LinearRegression()
    lr.fit(x, y)
    y_predict = lr.predict(x)
    df[factor_name] = y - y_predict
    return df


def ind_neutralize(factor_df, factor_name, industry_df):
    utils.check_sub_columns(factor_df, [factor_name])
    utils.check_sub_columns(industry_df, ["ind_code"])
    # generate dummies to form a new dataframe
    ind_dummies = pd.get_dummies(industry_df["ind_code"], drop_first=True, prefix="ind")
    ind_new = pd.concat([industry_df.drop(columns=["ind_code"]), ind_dummies], axis=1)
    df = pd.merge(factor_df, ind_new, on=["trade_date", "stock_code"])
    # df columns: trade_date, stock_code, factor, industry dummies (30+)
    g = df.groupby("trade_date", group_keys=False)
    df = g.apply(_single_ind_neutralize, factor_name)
    df = df[["trade_date", "stock_code", factor_name]].copy()
    return df


def _single_ind_neutralize(df, factor_name):
    x = df.iloc[:, 3:]  # industry dummies start from column 3
    y = df[factor_name]
    lr = LinearRegression()
    lr.fit(x, y)
    y_predict = lr.predict(x)
    df[factor_name] = y - y_predict
    return df
