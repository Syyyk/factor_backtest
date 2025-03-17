import numpy as np
import pandas as pd
import backtest
import utils


def get_stock_group(factor_df, factor_name, n_groups):
    # Return格式为trade_date, stock_code, factor_name, factor_name_group
    col_lst = ["trade_date", "stock_code", factor_name]
    utils.check_sub_columns(factor_df, col_lst)
    factor_df = factor_df.copy()
    # 对factor_df中的factor_name进行分组，并进行标记
    g = factor_df.groupby("trade_date", group_keys=False)
    factor_df = g.apply(
        _get_single_period_group, factor_name=factor_name, n_groups=n_groups
    )
    return factor_df


def _get_single_period_group(df, factor_name, n_groups):
    # 将df中的factor_name进行分组
    # 组名从小到大为Group0到Group{n_groups-1}
    df = df.copy()
    group_name = factor_name + "_group"
    labels = ["Group" + str(i) for i in range(n_groups)]
    df[group_name] = pd.cut(df[factor_name].rank(), bins=n_groups, labels=labels)
    return df


def get_group_ret(factor_df, ret_df, factor_name, n_groups, mktmv_df=None):
    # return df: index: trade_date, columns: Group0to9, H-L
    factor_col_lst = ["trade_date", "stock_code", factor_name]
    ret_col_lst = ["trade_date", "stock_code", "ret"]
    utils.check_columns(factor_df, factor_col_lst)
    utils.check_columns(ret_df, ret_col_lst)
    # 对因子数据提前一期
    prev_factor_df = utils.get_previous_factor(factor_df)
    # 拼接
    df = pd.merge(prev_factor_df, ret_df, on=["trade_date", "stock_code"])
    if mktmv_df is not None:
        utils.check_columns(mktmv_df, ["trade_date", "stock_code", "mktmv"])
        mktmv_df = utils.get_previous_factor(mktmv_df)
    else:
        mktmv_df = df[["trade_date", "stock_code"]].copy()
        mktmv_df["mktmv"] = 1

    def get_group_weight_ret(_df):
        _df = _df.copy()
        _df["weight"] = _df["mktmv"] / _df["mktmv"].sum()
        return np.sum(_df["weight"] * _df["ret"])

    # 计算分组
    df = df.copy()  # df columns: trade_date, stock_code, factor_name
    df = get_stock_group(df, factor_name, n_groups)
    df = pd.merge(df, mktmv_df, on=["trade_date", "stock_code"])
    # 此时, df格式为trade_date, stock_code, factor_name, mktmv
    # 分组计算收益率
    group_name = factor_name + "_group"
    g = df.groupby(["trade_date", group_name])
    stacked_group_ret = g.apply(get_group_weight_ret)  # index: yyyymmdd/Group1, column: 0
    stacked_group_ret = stacked_group_ret.reset_index()  # columns: trade_date, factor_group, 0
    stacked_group_ret.columns = ["trade_date", group_name, "ret"]
    # 反堆栈
    group_ret = utils.unstackdf(stacked_group_ret, code_name=group_name)
    # 计算多空收益率
    factor_ret = _get_factor_ret(group_ret, n_groups)
    group_ret["H-L"] = factor_ret
    return group_ret


def _get_factor_ret(group_ret, n_groups):
    # 多空因子收益
    long_group_name = "Group" + str(n_groups - 1)
    short_group_name = "Group0"
    long_group_ret = group_ret[long_group_name]
    short_group_ret = group_ret[short_group_name]
    factor_ret = long_group_ret - short_group_ret
    return factor_ret


def get_group_ret_backtest(group_ret, rf=0, benchmark=None, period="DAILY"):
    """
    group_ret: column: Group0~9
    benchmark: trade_date, ret
    period: DAILY, WEEKLY, MONTHLY

    Return
    columns: groups
    rows: 行名为年化收益率(%), 年化波动率(%), 夏普比率, 最大回撤(%)
    若benchmark不为None，则会额外输出: 超额年化收益率(%),
    超额年化波动率(%). 信息比率, 相对基准胜率(%), 超额收益最大回撤(%)
    """
    if benchmark is not None:
        utils.check_columns(benchmark, ["trade_date", "ret"])
        benchmark = benchmark.set_index("trade_date")
        s1 = set(benchmark.index.tolist())
        s2 = set(group_ret.index.tolist())
        common_time_lst = sorted(list(s1.intersection(s2)))
        group_ret = group_ret.loc[common_time_lst].copy()
        benchmark = benchmark.loc[common_time_lst].copy()
        benchmark_ret = benchmark["ret"]
        benchmark.columns = ["benchmark"]
        group_ret = pd.concat([group_ret, benchmark], axis=1)
    else:
        benchmark_ret = None
    backtest_df = pd.DataFrame()
    for col in group_ret.columns:
        res_dct = backtest.get_backtest_result(
            group_ret[col], rf=rf, benchmark_returns=benchmark_ret, period=period
        )
        res_df = pd.DataFrame(res_dct).T
        backtest_df = pd.concat([backtest_df, res_df], axis=1)
    backtest_df.columns = group_ret.columns
    return backtest_df


def backtest_group_ret(factor_df, ret_df, factor_name, n_groups, rf=0, benchmark=None, period="DAILY"):
    """
    factor_df: 未提前的 trade_date, stock_code, factor_name
    ret_df: trade_date, stock_code, ret
    benchmark: trade_date, ret
    period: DAILY, WEEKLY, MONTHLY
    """
    group_ret = get_group_ret(factor_df, ret_df, factor_name, n_groups)

    backtest_df = get_group_ret_backtest(group_ret, rf, benchmark=None, period=period)  # 回测指标计算
    HL_result = backtest_df['H-L'].tolist()

    # 画图
    fig1 = utils.plot_groupret_bar(backtest_df.iloc[0, :], "Group", "年化收益率", "分组年化收益率")

    time_idx = pd.to_datetime(group_ret.index)
    factor_ret = group_ret["H-L"]
    group_ret = group_ret.drop(columns=["H-L"])
    plot_params_dct = {
        "x_lst_1": [time_idx] * n_groups,
        "y_lst_1": [(group_ret[col] + 1).cumprod() for col in group_ret.columns],
        "x_lst_2": time_idx,
        "y_lst_2": (factor_ret + 1).cumprod(),
        "label_lst": group_ret.columns.tolist(),
        "xlabel": "Date", "ylabel_1": "分组净值", "ylabel_2": "多空净值",
        "fig_title": f"因子{factor_name}的净值曲线",
        "remark_data": HL_result
    }
    if benchmark is not None:
        fill_length = len(time_idx) - benchmark.shape[0]  # this is because benchmark data isn't enough
        plot_params_dct['benchmark'] = pd.concat([pd.Series([1] * fill_length), (benchmark['ret'] + 1).cumprod()])
    fig2 = utils.plot_backtest_netvalue(**plot_params_dct)

    return backtest_df, fig1, fig2
