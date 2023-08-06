#!python
#
# Author: Martin Matusiak <numerodix@gmail.com>

from __future__ import with_statement

import glob
import hashlib
import os
import sys
import time


CHUNK = 1024 * 100
BYTES_READ = 0

_units = [
    " B",
    "KB",
    "MB",
    "GB",
    "TB",
    "PB",
    "EB",
    "ZB",
]


try:
    raw_input
except NameError:
    raw_input = input


class File(object):
    def __init__(self, filename):
        self.name = filename
        self.mtime = 0
        self.size = 0
        try:
            st = os.stat(self.name)
            self.mtime = st.st_mtime
            self.size = st.st_size
        except Exception as e:
            write_out("%s\n" % e)


class Record(object):
    def __init__(self, fileobj, data=None, eof=False):
        self.fileobj = fileobj
        self.data = data
        self.eof = eof


def format_size(size):
    if size is None:
        size = -1

    c = 0
    while size > 999:
        size = size / 1024.
        c += 1
    r = "%3.1f" % size
    u = "%s" % _units[c]
    return r.rjust(5) + " " + u.ljust(2)


def format_date(date):
    return time.strftime("%d.%m.%y %H:%M:%S", time.gmtime(date))


def format_file(fileobj):
    size = format_size(fileobj.size)
    try:
        diff = os.path.getsize(fileobj.name) - fileobj.size
        diff_abs = abs(diff)
        if diff < 0:
            size += "-" + format_size(diff_abs).strip()
        elif diff > 0:
            size += "+" + format_size(diff_abs).strip()
    except OSError as e:
        write_out("%s\n" % e)
    return ("%s  %s  %s" % (size, format_date(fileobj.mtime), fileobj.name))


def write_out(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def write_err(s):
    sys.stderr.write(s)
    sys.stderr.flush()


def clear_err():
    write_err(79 * " " + "\r")


def delete(filename):
    try:
        os.unlink(filename)
    except OSError as e:
        write_out("%s\n" % e)


def write_fileline(prefix, fileobj):
    write_out("%s %s\n" % (prefix, format_file(fileobj)))


def get_hash(idx, data):
    m = hashlib.md5()
    data = bytes(idx) + data
    m.update(data)
    return m.hexdigest().encode('ascii')


def get_filelist(pattern=None, lst=None):
    files = []
    it = lst or glob.iglob(pattern)
    for filename in it:
        filename = filename.strip()
        if os.path.isfile(filename) and not os.path.islink(filename):
            files.append(Record(File(filename)))
    return files


def get_chunk(offset, length, filename):
    try:
        with open(filename, 'rb') as f:
            f.seek(max(offset, 0))
            data = f.read(length)
            ln = len(data)
            global BYTES_READ
            BYTES_READ += ln
            return ln, data
    except IOError as e:
        write_out("%s\n" % e)
        return 0, ""


def short_name(lst):
    lst.sort(key=lambda x: (len(x.name), x.name))
    return lst


def rev_file_size(lst):
    lst.sort(reverse=True, key=lambda x: x.size)
    return lst


def rec_file_size(lst):
    lst.sort(key=lambda x: x.fileobj.size)
    return lst


def compute(pattern=None, lst=None):
    zerosized = []
    incompletes = {}
    duplicates = {}

    offsets = {}
    offsets[0] = {}
    key = get_hash(0, b"")

    write_err("Building file list..\r")
    offsets[0][key] = get_filelist(pattern=pattern, lst=lst)

    offsets_keys = [k for k in offsets.keys()]
    for offset in offsets_keys:
        offset_hashes = [(h, r) for (h, r) in
                         offsets[offset].items() if len(r) > 1]
        buckets = len(offset_hashes)
        for (hid, (hash, rs)) in enumerate(offset_hashes):
            # sort by shortest to not read redundant data
            rs = rec_file_size(rs)
            reads = []
            readsize = CHUNK
            for (rid, record) in enumerate(rs):
                ln, data = get_chunk(offset, readsize, record.fileobj.name)
                s = ("%s | Offs %s | Buck %s/%s | File %s/%s | Rs %s" %
                     (format_size(BYTES_READ),
                      format_size(offset),
                      hid + 1,
                      buckets,
                      rid + 1,
                      len(rs),
                      format_size(readsize))).ljust(79)
                write_err("%s\r" % s)
                if ln == 0:
                    record.eof = True
                else:
                    r = Record(record.fileobj, data=data)
                    if ln < readsize:
                        readsize = ln
                    reads.append(r)


            if reads:
                new_offset = offset + readsize
                if new_offset not in offsets:
                    offsets[new_offset] = {}
                    offsets_keys.append(new_offset)
                    offsets_keys.sort()

            for (ri, r) in enumerate(reads):
                # print update
                s = ("%s | Offs %s | Buck %s/%s | Hashing %s/%s" %
                     (format_size(BYTES_READ),
                      format_size(offset),
                      hid + 1,
                      buckets,
                      ri,
                      len(reads))).ljust(79)
                write_err("%s\r" % s)

                new_hash = get_hash(new_offset, hash + r.data[:readsize])
                r.data = None
                if new_hash not in offsets[new_offset]:
                    offsets[new_offset][new_hash] = []
                offsets[new_offset][new_hash].append(r)
    clear_err()  # terminate offset output

    offsets_keys = [k for k in offsets.keys()]
    offsets_keys.sort(reverse=True)
    for offset in offsets_keys:
        offset_hashes = offsets[offset]
        for (hash, rs) in offset_hashes.items():
            if offset == 0:
                zerosized = [r.fileobj for r in rs if r.eof]
            else:
                if len(rs) > 1:
                    eofs = [r for r in rs if r.eof]
                    n_eofs = [r for r in rs if not r.eof]
                    if len(eofs) >= 2 and len(n_eofs) == 0:
                        duplicates[eofs[0].fileobj.name] = \
                            [r.fileobj for r in eofs]
                    if len(eofs) >= 1 and len(n_eofs) >= 1:
                        largest = rev_file_size([r.fileobj for r in n_eofs])[0]
                        key = largest.name
                        if not key in incompletes:
                            incompletes[key] = [largest]
                        for r in eofs:
                            if r.fileobj not in incompletes[key]:
                                incompletes[key].append(r.fileobj)

    return zerosized, incompletes, duplicates


def main(pattern=None, lst=None):
    zerosized, incompletes, duplicates = compute(pattern=pattern, lst=lst)
    if zerosized or incompletes or duplicates:

        kill = " X "
        keep = " = "

        q_zero = []
        q_inc = []
        q_dupe = []

        if zerosized:
            write_out("Empty files:\n")
            for fileobj in zerosized:
                q_zero.append(fileobj)
                write_fileline(kill, fileobj)

        if incompletes:
            write_out("Incompletes:\n")
            for (idx, (_, fs)) in enumerate(incompletes.items()):
                fs = rev_file_size(fs)
                for (i, fileobj) in enumerate(fs):
                    prefix = keep
                    if fileobj.size < fs[0].size:
                        q_inc.append(fileobj)
                        prefix = kill
                    write_fileline(prefix, fileobj)
                if idx < len(incompletes) - 1:
                    write_out('\n')

        if duplicates:
            write_out("Duplicates:\n")
            for (idx, (_, fs)) in enumerate(duplicates.items()):
                fs = short_name(fs)
                for (i, fileobj) in enumerate(fs):
                    prefix = keep
                    if i > 0:
                        q_dupe.append(fileobj)
                        prefix = kill
                    write_fileline(prefix, fileobj)
                if idx < len(duplicates) - 1:
                    write_out('\n')

        prompt = "Kill files? (all/empty/incompletes/duplicates) [a/e/i/d/N] "
        write_err(prompt)
        inp = raw_input()

        if "e" in inp or "a" in inp:
            for fileobj in q_zero:
                delete(fileobj.name)
        if "i" in inp or "a" in inp:
            for fileobj in q_inc:
                delete(fileobj.name)
        if "d" in inp or "a" in inp:
            for fileobj in q_dupe:
                delete(fileobj.name)



if __name__ == "__main__":
    pat = '*'
    if len(sys.argv) > 1:
        if sys.argv[1] == "-h":
            write_err("Usage:  %s ['<glob pattern>'|--file <file>]\n" %
                      os.path.basename(sys.argv[0]))
            sys.exit(2)
        elif sys.argv[1] == "--file":
            lst = open(sys.argv[2], 'r').readlines()
            main(lst=lst)
        else:
            pat = sys.argv[1]
            main(pattern=pat)
    else:
        main(pattern='*')
