import pandas as pd
import numpy as np
from preprocess.outlier import del_outlier
from preprocess.standardize import standardize
import group_calc
import ic_analysis
import matplotlib.pyplot as plt
import dolphindb
import data.get_data as get_data

if __name__ == '__main__':
    s = dolphindb.session()
    s.connect("localhost", 8848, "admin", "123456")

    # get factor df
    with open("./factor/test_factor.dos", 'r') as file:
        ddb_statement = file.read()
    factor_df = s.run(ddb_statement)  # columns: trade_date, stock_code, factor
    factor_df.columns = ['trade_date', 'stock_code', 'factor']

    # get return dfs
    ret_df = s.run(get_data.get_daily_ret_statement("20200601", "20201130"))
    benchmark_df = s.run(get_data.get_index_daily_ret_statement("20200601", "20201130")).dropna()

    # preprocess
    factor_df = del_outlier(factor_df, 'factor', method='mad', n=3)
    factor_df = standardize(factor_df, 'factor', method='rank')

    # 分组收益计算
    mw_group_ret = group_calc.get_group_ret(factor_df, ret_df, 'factor', 10)

    # IC检验
    ic_df, ic_fig = ic_analysis.analyze_factor_ic(factor_df, ret_df, 'factor')
    print(ic_df)

    # 净值曲线
    backtest_df, fig1, fig2 = group_calc.backtest_group_ret(factor_df, ret_df, 'factor', n_groups=10,
                                                            benchmark=benchmark_df)
    print(backtest_df)
    plt.show()
