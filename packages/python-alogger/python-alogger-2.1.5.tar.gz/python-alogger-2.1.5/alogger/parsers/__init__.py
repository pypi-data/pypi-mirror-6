"""
Declare log parsing methods in here.
methods take a line of a log and return a python dict containing
Key           | type     | Description
----------------------------------------------
user          | string   | username
project       | string   | pid
est_wall_time | int      | estimated wall time
act_wall_time | int      | actual wall time
cpu_usage     | int      | CPU usage in seconds
queue         | datetime | 
ctime         | datetime | the time in seconds when the job was Created (first submitted)
qtime         | datetime | the time in seconds when the job was Queued into the current queue
etime         | datetime | time in seconds when the job became Eligible to run
start         | datetime | the time in seconds when job execution Started
jobid         | string   | Expected to also have host name
cores         | int      | number of cores
jobname       | string   | Job name
exit_status   | int      | Exit status - or a string from Slurm !
Optional
mem           | int      | memory used
vmem          | int      | virtual memory used
list_mem      | int      | memory requested
list_vmem     | int      | virtual memory requested
list_pmem     | int      | memory requested (per processor)
list_pvmem    | int      | virtual memory requested (per processor)
Raises value error if funky wall time

So a user submits a job, thats "qtime" (or, probably 'ctime')
eventually, its starts to run, that "start"
finally, it finishes, one way or another, thats "start" + "act_wall_time"

If queue is light, etime can equal qtime, but not if the job is blocked.

"""

from torque import pbs_to_dict
from sge import sge_to_dict
from slurm import slurm_to_dict
from winhpc import winhpc_to_dict
