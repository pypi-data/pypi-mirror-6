#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward" <cward@redhat.com>

from calendar import timegm
from datetime import datetime
from dateutil.parser import parse as dt_parse
from hashlib import sha1
import os
import pytz
import re


def batch_gen(data, batch_size):
    '''
    Usage::
        for batch in batch_gen(iter, 100):
            do_something(batch)
    '''
    if not data:
        return

    if batch_size <= 0:
        # override: yield the whole list
        yield data

    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]


def clear_stale_pids(pids, pid_dir, prefix='metriqued'):
    'check for and remove any pids which have no corresponding process'
    procs = os.listdir('/proc')
    running = [pid for pid in pids if pid in procs]
    for pid in pids:
        if pid not in running:
            pid_file = '%s.%s.pid' % (prefix, pid)
            path = os.path.join(pid_dir, pid_file)
            os.remove(path)
    return running


def dt2ts(dt, drop_micro=False):
    ''' convert datetime objects to timestamp seconds (float) '''
    # the equals check to 'NaT' is hack to avoid adding pandas as a dependency
    if repr(dt) == 'NaT':
        return None
    elif not dt:
        return dt
    elif isinstance(dt, (int, long, float, complex)):  # its a ts already
        ts = dt
    elif isinstance(dt, basestring):  # convert to datetime first
        ts = dt2ts(dt_parse(dt))
    else:
        ts = timegm(dt.timetuple())
    if drop_micro:
        return float(int(ts))
    else:
        return float(ts)


def get_pids(pid_dir, prefix='metriqued', clear_stale=True):
    pid_dir = os.path.expanduser(pid_dir)
    # eg, server.22325.pid, server.23526.pid
    pids = []
    for f in os.listdir(pid_dir):
        pid_re = re.search(r'%s.(\d+).pid' % prefix, f)
        if pid_re:
            pids.append(pid_re.groups()[0])
    if clear_stale:
        pids = clear_stale_pids(pids, pid_dir, prefix)
    return map(int, pids)


def jsonhash(obj, root=True, exclude=None):
    '''
    calculate the objects hash based on all field values
    '''
    if isinstance(obj, dict):
        obj = obj.copy()  # don't affect the ref'd obj passed in
        keys = set(obj.keys())
        if root and exclude:
            [obj.__delitem__(f) for f in exclude if f in keys]
        # frozenset's don't guarantee order; use sorted tuples
        # which means different python interpreters can return
        # back frozensets with different hash values even when
        # the content of the object is exactly the same
        result = sorted(
            (k, jsonhash(v, False)) for k, v in obj.items())
    elif isinstance(obj, list):
        result = tuple(jsonhash(e, False) for e in obj)
    else:
        result = obj
    return sha1(repr(result)).hexdigest() if root else result


def set_default(key, default, null_ok=False, err_msg=None):
    if not err_msg:
        err_msg = "non-null value required for %s" % key
    if not null_ok and key is None and default is None:
            raise RuntimeError(err_msg)
    try:
        # if we get 'type' obj, eg `list`
        result = key if key is not None else default()
    except (TypeError, AttributeError):
        result = key if key is not None else default
    return result


def ts2dt(ts, milli=False, tz_aware=True):
    ''' convert timestamp int's (seconds) to datetime objects '''
    # anything already a datetime will still be returned
    # tz_aware, if set to true
    if not ts:
        return ts  # its not a timestamp, throw it back
    elif isinstance(ts, datetime):
        pass
    elif milli:
        ts = float(ts) / 1000.  # convert milli to seconds
    else:
        ts = float(ts)  # already in seconds
    if tz_aware:
        if isinstance(ts, datetime):
            ts.replace(tzinfo=pytz.utc)
            return ts
        else:
            return datetime.fromtimestamp(ts, tz=pytz.utc)
    else:
        if isinstance(ts, datetime):
            return ts
        else:
            return datetime.utcfromtimestamp(ts)


def utcnow(as_datetime=False, tz_aware=False, drop_micro=False):
    if drop_micro:
        now = datetime.utcnow().replace(microsecond=0)
    else:
        now = datetime.utcnow()
    if tz_aware:
        # implise as_datetime=True
        return pytz.UTC.localize(now)
    elif as_datetime:
        return now
    else:
        return dt2ts(now, drop_micro)


def strip_split(item):
    if isinstance(item, basestring):
        return [s.strip() for s in item.split(',')]
    elif item is None:
        return []
    elif not isinstance(item, (list, tuple)):
        raise TypeError('Expected a list/tuple')
    else:  # nothing to do here...
        return item
