# Copyright 2008 VPAC
#
# This file is part of alogger-ng.
#
# alogger-ng is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# alogger-ng is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with alogger-ng  If not, see <http://www.gnu.org/licenses/>.


"""
Declare log parsing methods here.

methods take a line of a log and return a python dict containing

Key           | type     | Description
----------------------------------------------
user          | string   | username
project       | string   | pid
est_wall_time | int      | estimated wall time
act_wall_time | int      | actual wall time
cpu_usage     | int      | CPU usage in seconds
queue         | datetime | 
ctime         | datetime | 
qtime         | datetime | 
etime         | datetime |
start         | datetime |
jobid	      | string   |
cores	      | int      | number of cores
jobname       | string   | Job name
exit_status   | int      | Exit status

Optional
mem           | int      | memory used
vmem          | int      | virtual memory used
list_mem      | int      | memory requested
list_vmem     | int      | virtual memory requested
list_pmem     | int      | memory requested (per processor)
list_pvmem    | int      | virtual memory requested (per processor)

Raises value error if funky wall time

"""

import datetime
import logging

from alogger.utils import get_in_seconds, get_mem_in_kb, get_mem_in_mb


def pbs_to_dict(line):
    """
    Parses a PBS log file line into a python dict
    
    raises KeyError when line not valid
    raises ValueError when time over 3 years

    """
    logging.debug('Parsing line:')
    logging.debug(line)
    # Split line into parts, only care about raw_data
    date, random, job_num, raw_data = line.split(';')
    
    raw_data = raw_data.split(' ')
    
    data = {}
    formatted_data = {}
    
    formatted_data['jobid'] = job_num

    # Make into a dict using values key=value
    for d in raw_data:
        try:
            key, value = d.split('=')
            data[key] = value
        except:
            continue

    # Check to see if line worth proccessing
    if not 'resources_used.walltime' in data:
        raise KeyError


    formatted_data['user'] = data['user']
    if 'account' in data:
        formatted_data['project'] = data['account']

    formatted_data['jobname'] = data['jobname']
    formatted_data['group'] = data['group']
    try:
        formatted_data['act_wall_time'] = get_in_seconds(data['resources_used.walltime'])
    except:
        logging.error('Failed to parse act_wall_time value: %s' % data['resources_used.walltime'])
        raise ValueError
        
    try:
        formatted_data['est_wall_time'] = get_in_seconds(data['Resource_List.walltime'])
    except:
        logging.error('Failed to parse est_wall_time value: %s' % data['Resource_List.walltime'])
        raise ValueError

    formatted_data['exec_hosts'] = [x[:-2] for x in data['exec_host'].split('+')]
    cores = data['exec_host'].count('/')
    formatted_data['cores'] = cores
    formatted_data['cpu_usage'] = cores * formatted_data['act_wall_time']
    
    formatted_data['queue'] = data['queue']

    formatted_data['mem'] = get_mem_in_kb(data.get('resources_used.mem', '0kb'))
    formatted_data['vmem'] = get_mem_in_kb(data.get('resources_used.vmem', '0kb'))

    formatted_data['list_pmem'] = get_mem_in_mb(data.get('Resource_List.pmem', '0kb'))
    formatted_data['list_mem'] = get_mem_in_mb(data.get('Resource_List.mem', '0kb'))

    formatted_data['list_vmem'] = get_mem_in_mb(data.get('Resource_List.vmem', '0kb'))
    formatted_data['list_pvmem'] = get_mem_in_mb(data.get('Resource_List.pvmem', '0kb'))
    
    formatted_data['exit_status'] = data['Exit_status']

    formatted_data['ctime'] = datetime.datetime.fromtimestamp(int(data['ctime'])).isoformat(' ')
    formatted_data['qtime'] = datetime.datetime.fromtimestamp(int(data['qtime'])).isoformat(' ')
    formatted_data['etime'] = datetime.datetime.fromtimestamp(int(data['etime'])).isoformat(' ')
    formatted_data['start'] = datetime.datetime.fromtimestamp(int(data['start'])).isoformat(' ')

    logging.debug("Parsed following data")
    for k,v in formatted_data.items():
        logging.debug("%s = %s" % (k, v))

    return formatted_data

