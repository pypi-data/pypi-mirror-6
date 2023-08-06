import re
import logging

try:
    from graphite_api.intervals import Interval, IntervalSet
    from graphite_api.node import LeafNode, BranchNode
except ImportError:
    from graphite.intervals import Interval, IntervalSet
    from graphite.node import LeafNode, BranchNode

from influxdb import InfluxDBClient


def config_to_client(config=None):
    if config is not None:
        cfg = config.get('influxdb', {})
        host = cfg.get('host', 'localhost')
        port = cfg.get('port', 8086)
        user = cfg.get('user', 'graphite')
        passw = cfg.get('pass', 'graphite')
        db = cfg.get('db', 'graphite')
    else:
        from django.conf import settings
        host = getattr(settings, 'INFLUXDB_HOST', 'localhost')
        port = getattr(settings, 'INFLUXDB_PORT', 8086)
        user = getattr(settings, 'INFLUXDB_USER', 'graphite')
        passw = getattr(settings, 'INFLUXDB_PASS', 'graphite')
        db = getattr(settings, 'INFLUXDB_DB', 'graphite')

    return InfluxDBClient(host, port, user, passw, db)


class InfluxdbReader(object):
    __slots__ = ('path', 'client')

    def __init__(self, client, path):
        self.client = client
        self.path = path

    def fetch(self, start_time, end_time):
        data = self.client.query("select time, value from %s where time > %ds and time < %ds order asc" % (self.path, start_time, end_time))
        datapoints = []
        start = 0
        end = 0
        step = 0
        try:
            points = data[0]['points']
            start = points[0][0]
            end = points[-1][0]
            step = points[1][0] - start
            datapoints = [p[2] for p in points]
        except Exception:
            pass
        time_info = start, end, step
        return time_info, datapoints

    def get_intervals(self):
        last_data = self.client.query("select * from %s limit 1" % self.path)
        first_data = self.client.query("select * from %s limit 1 order asc" % self.path)
        last = 0
        first = 0
        try:
            last = last_data[0]['points'][0][0]
            first = first_data[0]['points'][0][0]
        except Exception:
            pass
        return IntervalSet([Interval(first, last)])


class InfluxdbFinder(object):
    __slots__ = ('client', 'logger')

    def __init__(self, config=None):
        self.client = config_to_client(config)
        # from graphite_api.app import app
        # self.logger = app.logger
        logging.basicConfig()
        self.logger = logging.getLogger("FUCK")
        self.logger.setLevel(logging.DEBUG)

    def find_nodes(self, query):
        # query.pattern is basically regex, though * should become [^\.]+ and . \.
        # but list series doesn't support pattern matching/regex yet
        regex = query.pattern.replace('.', '\.').replace('*', '[^\.]+')
        self.logger.info("find_nodes query: %s -> %s" % (query.pattern, regex))
        regex = re.compile(regex)
        series = self.client.query("list series")
        for s in series:
            self.logger.info("matching %s" % s['name'])
        series = [s['name'] for s in series if regex.match(s['name']) is not None]
        seen_branches = set()
        # for leaf "a.b.c" we should yield branches "a" and "a.b"
        for s in series:
            self.logger.info("leaf %s" % s)
            yield LeafNode(s, InfluxdbReader(self.client, s))
            branch = s.rpartition('.')[0]
            while branch != '' and branch not in seen_branches:
                self.logger.info("branch %s" % branch)
                yield BranchNode(branch)
                seen_branches.add(branch)
                branch = branch.rpartition('.')[0]
