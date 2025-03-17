
import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels import FamaMacBeth
import utils


def get_factor_ic(factor_df, ret_df, factor_name):
    # factor_df未提前
    def calc_corr_func(df):
        return np.corrcoef(df[factor_name], df["ret"])[0, 1]

    prev_factor_df = utils.get_previous_factor(factor_df)
    df = pd.merge(prev_factor_df, ret_df, on=["trade_date", "stock_code"])
    ic_df = df.groupby(["trade_date"], group_keys=False).apply(calc_corr_func)
    ic_df = ic_df.reset_index()
    ic_df.columns = ["trade_date", "IC"]
    return ic_df


def analyze_factor_ic(factor_df, ret_df, factor_name):
    # input factor_df 未提前, columns: trade_date, stock_code, factor_name

    ic_df = get_factor_ic(factor_df, ret_df, factor_name)
    ic_mean = ic_df["IC"].mean()
    ic_std = ic_df["IC"].std()
    ir_ratio = ic_mean / ic_std
    ic0_ratio = 100 * len(ic_df.loc[ic_df["IC"] > 0, :]) / len(ic_df)
    ic002_ratio = 100 * len(ic_df.loc[ic_df["IC"] > 0.02, :]) / len(ic_df)
    dct = {
        "因子名称": [factor_name], "IC均值": [ic_mean], "IC标准差": [ic_std],
        "IR比率": [ir_ratio], "IC>0的比例(%)": [ic0_ratio], "IC>0.02的比例(%)": [ic002_ratio],
    }
    ic_df["trade_date"] = pd.to_datetime(ic_df["trade_date"])
    plot_params_dct = {
        "x1": ic_df["trade_date"], "y1": ic_df["IC"],
        "x2": ic_df["trade_date"], "y2": ic_df["IC"].cumsum(),
        "label1": "因子IC", "label2": "因子IC累计值",
        "xlabel": "日期", "ylabel1": "因子IC", "ylabel2": "因子IC累计值",
        "fig_title": f"因子{factor_name}的IC分析",
    }
    fig = utils.plot_ic(**plot_params_dct)
    return pd.DataFrame(dct), fig

