#!/usr/bin/python
# (C) Copyright 2014 Nuxeo SAS <http://nuxeo.com>
# Authors: Benoit Delbosc <ben@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
"""Send CSV CodaHale metrics to a graphite server
"""
import os
import sys
from time import sleep
from optparse import OptionParser, TitledHelpFormatter
import csv

USAGE = """%prog [options] CSV_FOLDER | nc graphite 2030

You need to change temporary your carbon conf to set
MAX_CREATES_PER_MINUTE = inf

Or use the proper --max_creates_per_minute of %prog.
"""


def get_version():
    """Retrun the package version."""
    from pkg_resources import get_distribution, DistributionNotFound
    try:
        version = get_distribution('csv2graphite').version
    except DistributionNotFound:
        version = "dev"
    return version


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def main():
    parser = OptionParser(USAGE, formatter=TitledHelpFormatter(),
                          version="csv2graphite " + get_version())
    parser.add_option("--prefix", type="string",
                      dest="prefix", default="servers.csv2graphite.nuxeo",
                      help="Setup the metric graphite prefix")
    parser.add_option("--max_creates_per_minute", type="int",
                      default=0,
                      help="The carbon MAX_CREATES_PER_MINUTE used to limit the input")

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    csv_dir = args[0]
    prefix = options.prefix
    max_creates_per_minute = options.max_creates_per_minute

    if not os.path.isdir(csv_dir):
        parser.error("Invalid CSV folder: " + csv_dir)

    wsp_files = 0
    wsp_count = 0
    for csv_file in os.listdir(csv_dir):
        if not csv_file.endswith('.csv'):
            continue
        name = prefix + "." + csv_file[:-4]
        sys.stderr.write("Processing: " + name + "\n")
        with open(os.path.join(csv_dir, csv_file), 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            header = reader.next()
            wsp_count += len(header) - 1
            if wsp_count > max_creates_per_minute:
                wsp_files += wsp_count
                wsp_count = 0
                if max_creates_per_minute > 0:
                    sys.stderr.write("Sleeping 1min before MAX_CREATES_PER_MINUTE is reached")
                    sleep(62)
            for row in reader:
                for i, k in enumerate(header[1:]):
                    v = row[i + 1]
                    if is_number(v):
                        print name + '.' + k, row[i + 1], row[0]
    sys.stderr.write("Done %d metrics processed" % wsp_files)


if __name__ == '__main__':
    main()
