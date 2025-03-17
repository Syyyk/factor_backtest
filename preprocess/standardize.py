import utils


# Standardize
def standardize(factor_df, factor_name, method="rank"):
    # method: rank(default) or zscore
    utils.check_sub_columns(factor_df, [factor_name])
    if method == "zscore":
        g = factor_df.groupby("trade_date", group_keys=False)
        factor_df = g.apply(_single_zscore_standardize, factor_name)
    elif method == "rank":
        g = factor_df.groupby("trade_date", group_keys=False)
        factor_df = g.apply(_single_rank_standardize, factor_name)
    else:
        raise ValueError("method must be rank or zscore")
    return factor_df


def _single_rank_standardize(factor_df, factor_name):
    factor_df[factor_name] = factor_df[factor_name].rank()
    return _single_zscore_standardize(factor_df, factor_name)


def _single_zscore_standardize(factor_df, factor_name):
    factor_mean = factor_df[factor_name].mean()
    factor_std = factor_df[factor_name].std()
    factor_df[factor_name] = (factor_df[factor_name] - factor_mean) / factor_std
    return factor_df
