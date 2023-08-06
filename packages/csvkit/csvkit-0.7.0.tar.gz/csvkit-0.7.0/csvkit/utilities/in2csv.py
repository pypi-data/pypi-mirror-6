#!/usr/bin/env python

import sys

from csvkit import convert
from csvkit.cli import CSVFileType, CSVKitUtility

class In2CSV(CSVKitUtility):
    description = 'Convert common, but less awesome, tabular data formats to CSV.'
    epilog='Some command line flags only pertain to specific input formats.'
    override_flags = ['f']

    def add_arguments(self):
        self.argparser.add_argument('file', metavar="FILE", nargs='?', default=sys.stdin,
                            help='The CSV file to operate on. If omitted, will accept input on STDIN.')
        self.argparser.add_argument('-f', '--format', dest='format',
                            help='The format of the input file. If not specified will be inferred from the file type. Supported formats: %s.' % ', '.join(sorted(convert.SUPPORTED_FORMATS)))
        self.argparser.add_argument('-s', '--schema', dest='schema', type=CSVFileType(),
                            help='Specifies a CSV-formatted schema file for converting fixed-width files.  See documentation for details.')
        self.argparser.add_argument('-k', '--key', dest='key',
                            help='Specifies a top-level key to use look within for a list of objects to be converted when processing JSON.')
        self.argparser.add_argument('-y', '--snifflimit', dest='snifflimit', type=int,
                            help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('--sheet', dest='sheet',
                            help='The name of the XLSX sheet to operate on.')
        self.argparser.add_argument('--no-inference', dest='no_inference', action='store_true',
                            help='Disable type inference when parsing the input.')


    def main(self):
        if self.args.format:
            format = self.args.format

            if format not in convert.SUPPORTED_FORMATS:
                self.argparser.error('"%s" is not a supported format' % self.args.format)

        elif self.args.schema:
            format = 'fixed'
        elif self.args.key:
            format = 'json'
        else:
            if self.args.file == sys.stdin:
                self.argparser.error('You must specify a format when providing data via STDIN (pipe).')

            format = convert.guess_format(self.args.file)

            if not format:
                self.argparser.error('Unable to automatically determine the format of the input file. Try specifying a format with --format.')

        if isinstance(self.args.file, file):
            f = self.args.file
        elif format in ('xls', 'xlsx'):
            f = open(self.args.file, 'rb')
        else:
            f = open(self.args.file, 'rU')

        kwargs = self.reader_kwargs

        if self.args.schema:
            kwargs['schema'] = self.args.schema

        if self.args.key:
            kwargs['key'] = self.args.key

        if self.args.snifflimit:
            kwargs['snifflimit'] = self.args.snifflimit

        if self.args.sheet:
            kwargs['sheet'] = self.args.sheet

        if self.args.no_inference:
            kwargs['type_inference'] = False

        if format == 'csv' and self.args.no_header_row:
            kwargs['no_header_row'] = True

        # Fixed width can be processed as a stream
        if format == 'fixed':
            kwargs['output'] = self.output_file

        self.output_file.write(convert.convert(f, format, **kwargs))

def launch_new_instance():
    utility = In2CSV()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

