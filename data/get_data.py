from typing import Union, Optional


def transform_date(date: Union[str, int]) -> str:
    # the input date has form YYYYMMDD (str or int)
    # the output has form YYYY.MM.DD
    if isinstance(date, int):
        date = str(date)
    assert isinstance(date, str)
    return date[0:4] + '.' + date[4:6] + '.' + date[6:]


def get_index_daily_ret_statement(start_date, end_date, index_id="000905.SH"):
    # TODO
    return 
    ddb_statement = rf"""
    Placeholder{None}
    """
    return ddb_statement


def get_daily_ret_statement(start_date: Union[str, int], end_date: Union[str, int], stock_id: Optional[int] = None) -> str:
    start_date, end_date = transform_date(start_date), transform_date(end_date)
    id_filter = f"and id == {stock_id}" if stock_id is not None else ""
    ddb_statement = rf"""
    db = database("dfs://CSMAR")
    pt = loadTable(db,`Daily)
    select date as trade_date, id as stock_code, close, volume,
    (close - prev(close)) / prev(close) as ret from pt
    where date >= {start_date} and date <= {end_date} {id_filter}
    context by id csort date
    """
    return ddb_statement


def get_30min_ret_statement(start_date: Union[str, int], end_date: Union[str, int], stock_id: Optional[int] = None) -> str:
    start_date, end_date = transform_date(start_date), transform_date(end_date)
    id_filter = f"and id == {stock_id}" if stock_id is not None else ""
    ddb_statement = rf"""
    db = database("dfs://MinFreq")
    pt = loadTable(db,`baostock_30min)
    select time, id, close, volume,
    (close - prev(close)) / prev(close) as ret from pt
    where date(time) >= {start_date} and date(time) <= {end_date} {id_filter}
    context by id csort time
    """
    return ddb_statement


def get_5min_ret_statement(start_date: Union[str, int], end_date: Union[str, int], stock_id: Optional[int] = None) -> str:
    start_date, end_date = transform_date(start_date), transform_date(end_date)
    id_filter = f"and id == {stock_id}" if stock_id is not None else ""
    ddb_statement = rf"""
    db = database("dfs://MinFreq")
    pt = loadTable(db,`baostock_5min)
    select time, id, close, volume,
    (close - prev(close)) / prev(close) as ret from pt
    where date(time) >= {start_date} and date(time) <= {end_date} {id_filter}
    context by id csort time
    """
    return ddb_statement