
import numpy as np
mapping_dct = {"DAILY": 252, "WEEKLY": 52, "MONTHLY": 12}


def _convert_returns_type(returns):
    try:
        returns = np.asarray(returns)
    except Exception:
        raise ValueError("returns is not array_like.")
    return returns


def _check_period(period):
    period_lst = list(mapping_dct.keys())
    if period not in period_lst:
        period_str = ",".join(period_lst)
        raise ValueError(f"period must be in {period_str}")
    return


def net_value(returns):
    returns = _convert_returns_type(returns)
    return np.cumprod(1 + returns)


def previous_peak(returns):
    returns = _convert_returns_type(returns)
    nv = net_value(returns)
    return np.maximum.accumulate(nv)


def drawdown(returns):
    returns = _convert_returns_type(returns)
    nv = net_value(returns)
    previous_peaks = previous_peak(returns)
    dd = (nv / previous_peaks - 1) * 100
    return dd


def max_drawdown(returns):
    returns = _convert_returns_type(returns)
    dd = drawdown(returns)
    mdd = np.min(dd)
    return mdd


def annualized_return(returns, period="DAILY"):

    _check_period(period)
    returns = _convert_returns_type(returns)
    ann_factor = mapping_dct[period]

    n = returns.shape[0]
    nv = net_value(returns)
    final_value = nv[-1]
    ann_ret = 100 * (final_value ** (ann_factor / n) - 1)
    return ann_ret


def annualized_volatility(returns, period="DAILY"):

    _check_period(period)
    returns = _convert_returns_type(returns)
    ann_factor = mapping_dct[period]
    ann_vol = 100 * np.std(returns) * np.sqrt(ann_factor)
    return ann_vol


def annualized_sharpe(returns, rf=0, period="DAILY"):

    _check_period(period)
    returns = _convert_returns_type(returns)
    ann_ret = annualized_return(returns, period)
    ann_vol = annualized_volatility(returns, period)
    if ann_vol < 1e-10:
        return 0
    return (ann_ret / 100 - rf) / (ann_vol / 100)


# Compare with benchmark:
def _compare_length(returns, benchmark_returns):
    if len(returns) != len(benchmark_returns):
        message = "Length of returns must be equal to length of benchmark_returns."
        raise ValueError(message)


def er_annual_return(returns, benchmark_returns, period="DAILY"):

    _check_period(period)
    returns = _convert_returns_type(returns)
    benchmark_returns = _convert_returns_type(benchmark_returns)
    _compare_length(returns, benchmark_returns)
    str_ann_ret = annualized_return(returns, period) / 100
    benchmark_ann_ret = annualized_return(benchmark_returns, period) / 100
    er_ann_ret = 100 * ((1 + str_ann_ret) / (1 + benchmark_ann_ret) - 1)
    return er_ann_ret


def er_annual_volatility(returns, benchmark_returns, period="DAILY"):

    _check_period(period)
    returns = _convert_returns_type(returns)
    benchmark_returns = _convert_returns_type(benchmark_returns)
    _compare_length(returns, benchmark_returns)
    er_ret = returns - benchmark_returns
    er_ann_vol = annualized_volatility(er_ret, period)
    return er_ann_vol


def information_ratio(returns, benchmark_returns, period="DAILY"):

    _check_period(period)
    returns = _convert_returns_type(returns)
    benchmark_returns = _convert_returns_type(benchmark_returns)
    _compare_length(returns, benchmark_returns)
    er_ann_ret = er_annual_return(returns, benchmark_returns, period=period)
    er_ann_vol = er_annual_volatility(returns, benchmark_returns, period=period)
    if er_ann_vol < 1e-10:
        return 0
    return er_ann_ret / er_ann_vol


def er_max_drawdown(returns, benchmark_returns):

    returns = _convert_returns_type(returns)
    benchmark_returns = _convert_returns_type(benchmark_returns)
    _compare_length(returns, benchmark_returns)
    # 计算策略和基准的净值,再计算超额收益的净值
    str_nv = np.cumprod(1 + returns)
    benchmark_nv = np.cumprod(1 + benchmark_returns)
    er_nv = str_nv / benchmark_nv
    # 历史最大净值
    er_prev_peaks = np.maximum.accumulate(er_nv)
    # 回撤
    er_dd = 100 * (er_nv / er_prev_peaks - 1)
    # 注意上述drawdown单位已为%
    er_mdd = np.min(er_dd)
    return er_mdd


def winrate(returns, benchmark_returns):

    returns = _convert_returns_type(returns)
    benchmark_returns = _convert_returns_type(benchmark_returns)
    _compare_length(returns, benchmark_returns)
    er_ret = returns - benchmark_returns
    rate = 100 * np.sum(np.where(er_ret > 0, 1, 0)) / len(er_ret)
    return rate


# 总结输出模块
def get_backtest_result(returns, rf=0, benchmark_returns=None, period="DAILY"):

    ann_ret = annualized_return(returns, period)
    ann_vol = annualized_volatility(returns, period)
    ann_sr = annualized_sharpe(returns, rf, period)
    mdd = max_drawdown(returns)
    dct = {
        "年化收益率(%)": [ann_ret],
        "年化波动率(%)": [ann_vol],
        "夏普比率": [ann_sr],
        "最大回撤(%)": [mdd],
    }
    er_dct = dict()
    if benchmark_returns is not None:
        er_ann_ret = er_annual_return(returns, benchmark_returns, period=period)
        er_ann_vol = er_annual_volatility(returns, benchmark_returns, period=period)
        str_ir = information_ratio(returns, benchmark_returns, period)
        str_winrate = winrate(returns, benchmark_returns)
        er_mdd = er_max_drawdown(returns, benchmark_returns)
        er_dct = {
            "超额年化收益率(%)": [er_ann_ret],
            "超额年化波动率(%)": [er_ann_vol],
            "信息比率": [str_ir],
            "相对基准胜率(%)": [str_winrate],
            "超额收益最大回撤(%)": [er_mdd],
        }
    dct.update(er_dct)
    return dct
