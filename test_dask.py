from distributed import LocalCluster

c = LocalCluster(processes=False)

c.scheduler(

from dask_jobqueue import SLURMCluster
from dask.distributed import Client
from distributed import Scheduler
from tornado.ioloop import IOLoop
from threading import Thread


cluster = SLURMCluster(processes=12, queue="DGE", project="davek", memory="36GB")

cluster.start_workers(12)

client = Client(cluster)

def inc(x):
  return x + 1


x = client.submit(inc,10)

L = client.map(inc, range(1000))

