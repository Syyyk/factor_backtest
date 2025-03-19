# ddb can run in this env: python 3.10, numpy 1.24.4, pandas 2.2, matplotlib 3.10
# SciPy 1.8, statsmodels 0.14.4, dolphindb 3.0.2.4, linearmodels 6.1
# TODO: requirements


import pyarrow.ipc as pa_ipc
import dolphindb as ddb
import pandas as pd
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# Connect to DolphinDB and init database
s = ddb.session()
s.connect("localhost", 8848, "admin", "123456")
CreateDBStatement="""
    dbPath = "dfs://MinFreq"
    db = database(dbPath, HASH, [DATE, 100])
"""
s.run(CreateDBStatement)
column_names = ["InstrumentId", "TradeDate", "TradeTime", "Open", "High", "Low", "Close", "Volume", "Amount", "TradeDateTime"]


# Add table 1
feather_file = r"E:\StockData\MinFreq\baostock_30min.feather"
reader = pa_ipc.open_file(feather_file)

for i in range(reader.num_record_batches):
    batch = reader.get_batch(i)
    batch_pd = batch.to_pandas()
    batch_pd["date"] = pd.to_datetime(batch_pd["date"], format="%Y-%m-%d").dt.date
    batch_pd["time"] = batch_pd["time"].astype(str)
    batch_pd["datetime"] = pd.to_datetime(batch_pd["time"].str[:14], format="%Y%m%d%H%M%S", errors="coerce")
    batch_pd["time"] = batch_pd["datetime"].dt.time
    batch_pd.columns = column_names
    s.upload({"batch_data": batch_pd})
    if i==0:
        s.run("pt = db.createPartitionedTable(batch_data, `baostock_30min, `TradeDate)")
    s.run("append!(pt, batch_data)")
    if i%300==0:
        logging.info(f"Batch {i} completed.")



# Add table 2
feather_file = r"E:\StockData\MinFreq\baostock_5min.feather"
reader = pa_ipc.open_file(feather_file)

for i in range(reader.num_record_batches):
    batch = reader.get_batch(i)
    batch_pd = batch.to_pandas()
    batch_pd["date"] = pd.to_datetime(batch_pd["date"], format="%Y-%m-%d").dt.date
    batch_pd["time"] = batch_pd["time"].astype(str)
    batch_pd["datetime"] = pd.to_datetime(batch_pd["time"].str[:14], format="%Y%m%d%H%M%S", errors="coerce")
    batch_pd["time"] = batch_pd["datetime"].dt.time
    batch_pd.columns = column_names
    s.upload({"batch_data": batch_pd})
    if i==0:
        s.run("pt = db.createPartitionedTable(batch_data, `baostock_5min, `TradeDate)")
    s.run("append!(pt, batch_data)")
    if i%300==0:
        logging.info(f"Batch {i} completed.")


