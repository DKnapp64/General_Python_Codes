#!/bin/env python2
#SBATCH --job-name=multiprocess
#SBATCH --ntasks=1
#SBATCH ...
import multiprocessing, sys, os
from ... import work

# necessary to add cwd to path when script run 
# by slurm (since it executes a copy)
sys.path.append(os.getcwd()) 

try:
    ncpus = int(os.environ["SLURM_JOB_CPUS_PER_NODE"])
except KeyError:
    ncpus = multiprocessing.cpu_count()

p = multiprocessing.Pool(ncpus)
p.map(work, range(100))
