import utils


# Delete outlier, method: mad or sigma
def del_outlier(factor_df, factor_name, method="mad", n=3):
    # n is the number of biases or medians
    utils.check_sub_columns(factor_df, [factor_name])
    factor_df = factor_df.copy()
    if method == "mad":
        g = factor_df.groupby("trade_date", group_keys=False)
        factor_df = g.apply(_single_mad_del, factor_name, n)
    elif method == "sigma":
        g = factor_df.groupby("trade_date", group_keys=False)
        factor_df = g.apply(_single_sigma_del, factor_name, n)
    if method not in ["mad", "sigma"]:
        raise ValueError("method must be mad or sigma")
    return factor_df


def _single_mad_del(factor_df, factor_name, n):
    # MAD去离群值
    factor_median = factor_df[factor_name].median()
    bias_sr = abs(factor_df[factor_name] - factor_median)
    new_median = bias_sr.median()
    dt_up = factor_median + n * new_median
    dt_down = factor_median - n * new_median
    factor_df[factor_name] = factor_df[factor_name].clip(dt_down, dt_up, axis=0)
    return factor_df


def _single_sigma_del(factor_df, factor_name, n):
    # sigma去离群值
    factor_mean = factor_df[factor_name].mean()
    factor_std = factor_df[factor_name].std()
    dt_up = factor_mean + n * factor_std
    dt_down = factor_mean - n * factor_std
    factor_df[factor_name] = factor_df[factor_name].clip(dt_down, dt_up, axis=0)
    return factor_df
