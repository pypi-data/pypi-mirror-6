#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward <cward@redhat.com>

import csv
import cStringIO
import os
import re
from urllib2 import urlopen

from metrique import pyclient


class Rows(pyclient):
    """
    Object used for extracting data from CSV files

    It's possible to load from a http(s):// or file://.

    The field names are defined by the column headers,
    therefore column heders are required in the csv.
    """
    name = 'csvdata_rows'

    def get_objects(self, uri, _oid=None, _start=None, type_map=None,
                    quotechar='"', delimiter=',',):
        self.quotechar = quotechar
        self.delimiter = delimiter
        # FIXME: replace with cache + pd.read_csv
        objects = self.loaduri(uri)
        objects = self.set_column(objects, 'uri', uri)
        objects = self.set_column(objects, '_oid', _oid)
        objects = self.set_column(objects, '_start', _start)
        self.objects = objects
        return objects

    def header_fields_dialect(self, csv_str):
        '''
        Given a newline separated string of csv, load it
        as a file like object.

        Then, try to sniff out the header to get the field
        names to be used in the objects extracted. If
        there is no header, raise `ValueError`, since
        otherwise we would have no way to know how to
        name the fields.

        While we have the csv file handy, sniff it to
        figure out the dialect of the csv. Dialect refers
        to properties of the csv itself, like which
        type of quotes are used, what separator character,
        etc. A common dialect is `Excel`.
        '''
        csvfile = cStringIO.StringIO(csv_str)

        sample = csvfile.read(1024)
        try:
            dialect = csv.Sniffer().sniff(sample)
            if not csv.Sniffer().has_header(sample):
                self.logger.warn("CSV header NOT DETECTED!")
        except Exception:
            dialect = csv.excel
            dialect.delimiter = self.delimiter
            dialect.quotechar = self.quotechar
            pass
        csvfile.seek(0)

        reader = csv.reader(csvfile, dialect)
        rows = list(reader)
        fields = rows.pop(0)
        return rows, fields, dialect

    def loaduri(self, uri, mode='rU'):
        '''
        Load csv from a given uri.
        Supports: http(s) or from file

        :param string mode:
            file open mode. Default: 'rU' (read/universal newlines)
        '''
        self.logger.debug("Loading CSV: %s" % uri)
        if re.match('https?://', uri):
            content = urlopen(uri).readlines()
        else:
            uri = re.sub('^file://', '', uri)
            uri = os.path.expanduser(uri)
            with open(uri, mode=mode) as f:
                content = f.readlines()
        return self.loadi(content)

    def loads(self, csv_str):
        '''
        Given a string of newline spaced csv, try
        to sniff out the header to aquire the field
        names, and also guess the *csv dialect*.
        '''
        rows, fields, dialect = self.header_fields_dialect(csv_str)
        objects = []
        for row in rows:
            row = [s.strip() for s in row]
            obj = {}
            for i, field in enumerate(fields):
                obj[field] = row[i]
            objects.append(obj)
        return objects

    def loadi(self, csv_iter):
        '''
        Given an iterator, strip and join all results
        into a newline separated string to load
        the csv as a string and return it.
        '''
        return self.loads('\n'.join([s.strip('[\n\r]*$') for s in csv_iter]))

    # FIXME: REFACTOR to split out header_fields and dialect
    # into two separate methods?
    def set_column(self, objects, key, value):
        '''
        Save an additional column/field to all objects in memory
        '''
        if type(value) is type or hasattr(value, '__call__'):
            # we have class or function; use the resulting object after
            # init/exec
            [o.update({key: value(o)}) for o in objects]
        elif key == '_oid':
            if value is None:
                # _oid maps to the item's index in the object list
                # which shouldn't change if the same file is being opened
                # more than once (appended to, overtime, forexample)
                [o.update({key: str(i)})
                 for i, o in enumerate(objects)]
            else:
                try:
                    [o.update({key: o[value]}) for o in objects]
                except KeyError:
                    raise KeyError(
                        "Invalid key object (%s). Available: %s" % (
                            value, o.keys()))
        else:
            [o.update({key: value}) for o in objects]
        return objects


if __name__ == '__main__':
    from metriquec.argparsers import cube_cli
    cube_cli(Rows)
