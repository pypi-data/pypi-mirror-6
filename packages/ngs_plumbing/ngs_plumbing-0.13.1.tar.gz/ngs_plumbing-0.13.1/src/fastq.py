""" Yet another FASTQ parsing set of tools """

import warnings
import io, gzip
from collections import namedtuple

SeqQualEntry = namedtuple('Entry', 'header sequence quality')
Entry = SeqQualEntry

class FastqError(ValueError):
    pass


#Compatibility with Python 3
import sys
_python2 = sys.version_info[0] == 2

if _python2:
    import itertools
    zip = itertools.izip


class FastqFile(io.BufferedReader):
    """ FASTQ file.
    The default iterator will go through the entries in the file (not the rows) 
    """

    def __init__(self, filename, **kwargs):
        stream = io.FileIO(filename)
        super(FastqFile, self).__init__(stream, **kwargs)

    def __iter__(self):
        wrap = io.OpenWrapper(self.fileno(), closefd = False)
        return iter_entries(wrap)

    def iter_seqqual(self):
        wrap = io.OpenWrapper(self.fileno(), closefd = False)
        return iter_seqqual(wrap)
        
    def readcount(self):
        pos = self.tell()
        for i, entry in enumerate(read_fastq):
            pass
        return i+1

class FastqFilePair(object):
    """ Pair of FASTQ files
    The default iterator will go through the paired entries in the file
    (not the rows), assuming that they are in the same order.
    No check that this is the case (using IDs) is performed.
    """

    def __init__(self, filename1, filename2, **kwargs):
        if _python2:
            fh1 = FastqFile(filename1, **kwargs)
            fh2 = FastqFile(filename2, **kwargs)
        else:
            stream = io.FileIO(filename1)
            fh1 = FastqFile(stream, **kwargs)
            stream = io.FileIO(filename2)
            fh2 = FastqFile(stream, **kwargs)
        self._fh1 = fh1
        self._fh2 = fh2

    def __iter__(self):
        wrap1 = io.OpenWrapper(self._fh1.fileno(), closefd = False)
        wrap2 = io.OpenWrapper(self._fh2.fileno(), closefd = False)
        return iter_entry_pairs(wrap1, wrap2)

    def iter_seqqual_pairs(self):
        """ Iterate over the pairs of (sequence+quality) in 
        the file. """
        wrap1 = io.OpenWrapper(self._fh1.fileno(), closefd = False)
        wrap2 = io.OpenWrapper(self._fh2.fileno(), closefd = False)
        return iter_seqqual_pairs(wrap1, wrap2)
        
    def readcount(self):
        pos = self.tell()
        for i, entry in enumerate(read_fastq):
            pass
        return i+1
    

class GzipFastqFile(gzip.GzipFile):
    """ Gzip-compressed FASTQ file. 
    The default iterator will go over the entries in the file.
    """

    def __iter__(self):
        return read_fastq(self)

    def iter_seqqual(self):
        return iter_seqqual(self)

def iter_seqqual(stream):
    """ Return an iterator over FASTQ entries in a stream
    (an iterable) of _bytes_ """

    sequence = list()
    quality = list()
    stream_iter = iter(stream)
    row = next(stream_iter)
    if row.startswith(b'@'):
        header = row.rstrip()
    else:
        raise FastqError('First row does not look like a Fastq header.')
    
    for row in stream_iter:
        row = row.rstrip()
        if header is not None:
            # sequence
            sequence.append(row)
            for row in stream_iter:
                row = row.rstrip()
                if row.startswith(b'+'):
                    if len(sequence) == 0:
                        raise FastqError('Empty Sequence')
                    break
                else:
                    sequence.append(row)
            # quality
            for row in stream_iter:
                row = row.rstrip()
                if row.startswith(b'@'):
                    if len(quality) == len(sequence):
                        break
                    else:
                        quality.append(row)
                elif row.startswith(b'+'):
                    if len(quality) >= len(sequence):
                        raise FastqError('Problem with the Fastq file '+\
                                         '(nearby header is %s)' % header)
                    else:
                        quality.append(row)
                else:
                    quality.append(row)
            sequence = b''.join(sequence)
            quality = b''.join(quality)
            yield Entry(header, sequence, quality)
            # reset for next round
            header = row
            sequence = list()
            quality = list()
    # do not miss the last entry
    sequence = b''.join(sequence)
    quality = b''.join(quality)
    if header is None:
        raise FastqError('Missing FASTQ header.')
    if row != header:
        yield SeqQualEntry(header, sequence, quality)        

def iter_seqqual_pairs(stream1, stream2):
    return zip(iter_seqqual(stream1), 
               iter_seqqual(stream2))

def iter_entries(stream):
    """ Iterate through entries in a FASTQ file. """
    return iter_seqqual(stream)

def iter_entry_pairs(stream1, stream2):
    """ Iterate through entries in a FASTQ file. """
    return iter_seqqual_pairs(stream1, stream2)

def read_fastq(stream):
    warnings.warn('read_fastq() is deprecated; use iter_entries()', DeprecationWarning)
    return iter_entries(stream)

def make_htmlreport(fqfile, directory = '.', verbose = True,
                    sample_percent = 0.05):
    from ngs_plumbing import report
    import csv
    import jinja2

    assert(isinstance(fqfile, FastqFile))
    pl = jinja2.PackageLoader('ngs_plumbing', 
                              package_path = os.path.join('data', 'html', 
                                                          'templates'));
    j_env = jinja2.Environment(loader = pl)
    template = j_env.get_template('fastqlibreport.html', 
                                  parent = os.path.join(_pack_installdir, 'data', 'html', 'templates'))
    # get information about the FASTQ file ?
    fn = os.path.basename(fqfile.filename)
    libs = list()
    csv_fn = os.path.join(directory, 
                          'fastqual_%s.csv' % fn)
    if verbose:
        sys.stdout.write('Creating file %s...' % csv_fn)
    f = file(csv_fn, mode = 'w')
    csv_w = csv.writer(f)
    for row in report.fastqual_tocsv_iter(fq):
        csv_w.writerow(row)
    f.close()
    if verbose:
        sys.stdout.write('done.\n')
    LibReport = namedtuple("LibReport", "readcount csv_fn")
    lib = LibReport(lib.readcount(), lib.csv_fn)        
    # render the HTML
    rd = template.render(**{
            'filename': fn,
            'fqinfo': tuple(),
            'lib': lib,
            'sample_percent': sample_percent})

    html_fn = os.path.join(directory, 
                           'fastqual_%s.html' % (fn))
    if verbose:
        sys.stdout.write('Creating file %s...' % html_fn)
    f = file(html_fn, mode = 'w')
    f.writelines(rd)            
    f.close()
    if verbose:
        sys.stdout.write('done.\n')
    # copy the javascript
    js_fn = os.path.join(_pack_installdir, 'data', 'html', 'readqual.js')
    jscp_fn = os.path.join(directory, 'readqual.js')
    if verbose:
        sys.stdout.write('Copying file %s...' % jscp_fn)
    f = file(js_fn, mode = 'r')
    f_cp = file(jscp_fn, mode = 'w')
    f_cp.writelines(row for row in f)
    f.close()
    f_cp.close()
    if verbose:
        sys.stdout.write('done.\n')

def write_fastq(buf, entry, seq_proc = None, qual_proc = None):
    if entry.header[0] != b'@':
        buf.write(b'@')
    buf.write(entry.header)
    buf.write('\n')
    if seq_proc is None:
        buf.write(entry.sequence)
    else:
        buf.write(seq_proc(entry.sequence))
    buf.write('\n+\n')
    if qual_proc is None:
        buf.write(entry.quality)
    else:
        buf.write(qual_proc(entry.quality))
    buf.write('\n')

if __name__ == '__main__':
    import sys, argparse
    from ngs_plumbing.utils import size_parser
    parser = argparse.ArgumentParser(
        description = 'Toolkit for FASTQ files')
    parser.add_argument('fn_in', metavar='<file name>', nargs='+',
                        help='FASTQ file')
    parser.add_argument('-c', '--count',
                        dest = 'count',
                        action = 'store_true',
                        help = 'Count the number of entries')
    parser.add_argument('-b', '--buffer',
                        dest = 'buffer',
                        default = '2Mb',
                        type = size_parser,
                        help = 'Buffer size (default: 2Mb)')
    parser.add_argument('-r', '--report',
                        dest = 'report',
                        action = 'store_true',
                        help = 'Make an HTML report about the content of the file')
        
    for fn_in in options.fn_in:
        sys.stdout.write('fn_in:\n')
        sys.stdout.flush()
        fq = FastqFile(fn_in)

        if options.count:
            rc = fq.readcount()
            sys.stdout.write('  # reads: %i\n' % rc)
            sys.stdout.flush()
