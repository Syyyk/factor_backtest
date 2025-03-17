# ddb can run in this env: python 3.10, numpy 1.23, pandas 2.2, matplotlib 3.10

import pyarrow.ipc as pa_ipc
import dolphindb as ddb
import pandas as pd
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# Connect to DolphinDB and init database
s = ddb.session()
s.connect("localhost", 8848, "admin", "123456")
CreateDBStatement="""
    drop database "dfs://MinFreq"
    dbPath = "dfs://MinFreq"
    db = database(dbPath, HASH, [INT, 100])
"""
s.run(CreateDBStatement)


# Add table 1
feather_file = r"E:\StockData\MinFreq\baostock_30min.feather"
reader = pa_ipc.open_file(feather_file)

for i in range(reader.num_record_batches):
    batch = reader.get_batch(i)
    batch_pd = batch.to_pandas()
    batch_pd["time"] = batch_pd["time"].astype(str)
    batch_pd["time"] = pd.to_datetime(batch_pd["time"].str[:14], format="%Y%m%d%H%M%S", errors="coerce")
    s.upload({"batch_data": batch_pd})
    if i==0:
        s.run("pt = db.createPartitionedTable(batch_data, `baostock_30min, `id)")
    s.run("append!(pt, batch_data)")
    if i%300==0:
        logging.info(f"Batch {i} completed.")


# Add table 2
feather_file = r"E:\StockData\MinFreq\baostock_5min.feather"
reader = pa_ipc.open_file(feather_file)

for i in range(reader.num_record_batches):
    batch = reader.get_batch(i)
    batch_pd = batch.to_pandas()
    batch_pd["time"] = batch_pd["time"].astype(str)
    batch_pd["time"] = pd.to_datetime(batch_pd["time"].str[:14], format="%Y%m%d%H%M%S", errors="coerce")
    s.upload({"batch_data": batch_pd})
    if i==0:
        s.run("pt = db.createPartitionedTable(batch_data, `baostock_5min, `id)")
    s.run("append!(pt, batch_data)")
    if i%300==0:
        logging.info(f"Batch {i} completed.")
