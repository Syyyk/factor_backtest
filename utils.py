import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def get_previous_factor(factor_df):
    check_sub_columns(factor_df, ['trade_date'])
    factor_df = factor_df.copy()
    # 将日期往前挪一期，建立本期交易日和上期交易日的映射DataFrame
    this_td_lst = factor_df['trade_date'].drop_duplicates().tolist()
    last_td_lst = [np.nan] + this_td_lst[:-1]
    td_df = pd.DataFrame({
        'this_trade_date': this_td_lst,
        'last_trade_date': last_td_lst
    })
    # 与原来的收益率数据进行合并
    factor_df = pd.merge(td_df,
                         factor_df,
                         left_on='last_trade_date',
                         right_on='trade_date')
    # 将上期交易日修改为本期交易日，这样每个交易日对应的是下期的收益率
    factor_df = factor_df.drop(columns=['last_trade_date', 'trade_date'])
    factor_df = factor_df.rename(columns={'this_trade_date': 'trade_date'})
    # 去除空值
    factor_df = factor_df.dropna().reset_index(drop=True)
    return factor_df


def unstackdf(df, date_name='trade_date', code_name='stock_code'):
    # input: 3 columns: trade_date, group, ret
    # output: index: trade_date, columns: group0-9
    check_sub_columns(df, [date_name, code_name])
    if not (len(df.columns) == 3):
        error_message = 'length of df.columns must be 3'
        raise ValueError(error_message)
    df = df.copy()
    df = df.set_index([date_name, code_name]).unstack()  # index: yyyymmdd, column: ret/Group0-9
    df.columns = df.columns.get_level_values(1).tolist()
    df.index = df.index.tolist()
    return df


# 检查df的列的部分
def check_sub_columns(df, var_lst):
    # check if var_lst \subset df.columns
    if not set(var_lst).issubset(df.columns):
        var_name = ','.join(var_lst)
        raise ValueError(f'{var_name} must be in the columns of df.')


def check_columns(df, var_lst):
    # check if var_lst == df.columns
    lst1 = list(var_lst)
    lst2 = df.columns.tolist()
    if not sorted(lst1) == sorted(lst2):
        var_str = ', '.join(var_lst)
        err = 'The columns of df must be var_lst:{}'.format(var_str)
        raise ValueError(err)


# 日期部分
def get_last_date(date, trade_date_lst):
    # 如果输入为空，返回为空
    if date is np.nan:
        return date
    if date < trade_date_lst[0]:
        raise ValueError('date must be smaller than trade_date_lst[0]')
    # 找未来最近的月频交易日
    for i in range(len(trade_date_lst) - 1):
        if (trade_date_lst[i] <= date) and (date < trade_date_lst[i + 1]):
            return trade_date_lst[i]


def get_next_date(date, trade_date_lst):
    # 如果输入为空，返回为空
    if date is np.nan:
        return date
    # 如果比提取的交易日历中的第一个交易日来的小，返回他
    if date < trade_date_lst[0]:
        return trade_date_lst[0]
    # 找未来最近的月频交易日
    for i in range(len(trade_date_lst) - 1):
        if (trade_date_lst[i] < date) and (date <= trade_date_lst[i + 1]):
            return trade_date_lst[i + 1]


# 画图部分
def plot_ic(x1, y1, x2, y2, label1, label2, xlabel, ylabel1, ylabel2, fig_title):
    # x1, y1 for bar; x2, y2 for line
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    ax1.bar(x1, y1, color='#FF0000', label=label1, width=8)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel1)
    ax2.plot(x2, y2, color='#FFCC00', linewidth=3, label=label2)
    ax2.set_ylabel(ylabel2)
    # 获取主坐标轴和辅助坐标轴的图例和标签
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    # 合并图例和标签
    lines = lines_1 + lines_2
    labels = labels_1 + labels_2
    # 在右上角创建一个新的子图对象，并将图例添加到其中
    ax_legend = fig.add_subplot(111)
    ax_legend.legend(lines, labels, loc=2)
    # 设置标题
    plt.title(fig_title)
    # 隐藏新的子图对象的坐标轴
    ax_legend.axis('off')
    return fig


def plot_groupret_bar(y_series, xlabel, ylabel, fig_title):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(y_series)), y_series)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks(range(len(y_series)))
    ax.set_xticklabels(y_series.index)
    plt.title(fig_title)
    return fig


def plot_backtest_netvalue(x_lst_1, y_lst_1, x_lst_2, y_lst_2, label_lst, xlabel, ylabel_1, ylabel_2,
                           fig_title, remark_data, benchmark=None):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    color_range = np.linspace(0.1, 0.4, len(x_lst_1))

    for i in range(len(x_lst_1)):
        x = x_lst_1[i]
        y = y_lst_1[i]
        label = label_lst[i]
        color = plt.cm.jet(color_range[i])
        plt.plot(x, y, color=color, label=label)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel_1)
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel(ylabel_2)
    ax2.tick_params(axis='y', labelcolor='tab:red')
    ax2.plot(x_lst_2, y_lst_2, color='tab:red', linewidth=3, label='factor')

    if benchmark is not None:
        ax1.plot(x_lst_2, benchmark, color='#00FF00', linewidth=3, label='benchmark')

    ax1.legend(loc=2)
    plt.title(fig_title)
    remark = f"年化收益率{remark_data[0]}    年化波动率{remark_data[1]}    夏普{remark_data[2]}    最大回撤{remark_data[3]}"
    plt.figtext(0.5, 0.01, remark, ha='center', va='bottom')

    return fig
