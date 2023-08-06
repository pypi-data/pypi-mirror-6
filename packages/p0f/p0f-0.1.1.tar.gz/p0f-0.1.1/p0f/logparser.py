"""
Parser for p0f3 log output. Start p0f with "-o path/to/logfile" option.

Example output:

[2014/03/02 15:35:00] mod=mtu|cli=192.168.0.100/56512|srv=75.215.216.121/5012|subj=cli|link=Ethernet or modem|raw_mtu=1500
[2014/03/02 15:35:00] mod=uptime|cli=192.168.0.100/56512|srv=75.215.216.121/5012|subj=cli|uptime=8 days 12 hrs 52 min (modulo 62 days)|raw_freq=832.76 Hz


Usage:

  p0flog = P0fLog("/path/to/p0f_output.txt")

  for line in p0flog.parse():
    print line.date
    print line.raw
    print line.content
"""

import datetime
import re
import logging

class P0fLogEntry:
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

class P0fLog:
    def __init__(self, filename = None):
        self.log = logging.getLogger(__name__)
        if filename:
            self.filename = filename
            self.parse()

    def parse(self, filename = None):
        """ Parse log file. """
        if not filename:
            try:
                filename = self.filename
            except AttributeError:
                raise AttributeError("No filename provided")
        logfile = open(filename)
        for line in logfile:
            data = self.parse_line(line)
            if data:
                yield data

    @classmethod
    def parse_uptime(cls, uptime_value):
        """ Parse uptime value to seconds and modulo days. """
        ret = {"uptime_raw": uptime_value}
        parsed = re.match("^([0-9]+) day(s|) ([0-9]+) hrs ([0-9]+) min \(modulo ([0-9]+) days\)$", uptime_value)
        if not parsed:
            return ret
        uptime_sec = int(parsed.group(1)) * 86400 + int(parsed.group(3)) * 3600 + int(parsed.group(4)) * 60
        uptime_mod_days = int(parsed.group(5))
        ret["uptime_sec"] = uptime_sec
        ret["uptime_mod_days"] = uptime_mod_days
        return ret

    @classmethod
    def parse_line(cls, line):
        """ Parse a single p0f log file line """
        line = line.strip()
        groups = re.match("^\[(.*)\] (.*)$", line)
        if not groups:
            self.log.debug("Invalid line: %s", line)
            return
        date = groups.group(1)
        content = groups.group(2)
        parsed_date = datetime.datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
        data = {}
        for entry in content.split("|"):
            k, v = entry.split("=", 1)
            if v == "none":
                v = None
            try:
                v = int(v)
            except (ValueError, TypeError):
                pass
            if k == "srv" or k == "cli":
                v = v.split("/")
                data["%s_ip" % k] = v[0]
                data["%s_port" % k] = int(v[1])
                continue
            if k == "uptime":
                data.update(cls.parse_uptime(v))
                continue

            data[k] = v
        return P0fLogEntry(date=parsed_date, raw=line, content=data)
