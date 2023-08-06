"""A simple tool for converting CSV"""
import argparse
import csv
import sys

parser = argparse.ArgumentParser(description='Convert CSV file')
parser.add_argument(
    '-fd', '--from-delimiter', default=',', help='The delimiter in input file'
)
parser.add_argument(
    '-td', '--to-delimiter', default=',', help='The delimiter in output file'
)
parser.add_argument(
    '-fq', '--from-quote', default='"', help='The quotechar in input file'
)
parser.add_argument(
    '-tq', '--to-quote', default='"', help='The quotechar in output file'
)
parser.add_argument(
    '-q', '--quote-mode', choices=['MINIMAL', 'NONNUMERIC', 'ALL'],
    default='MINIMAL', help='The quoting mode in output file',
)
parser.add_argument(
    '-o', '--output', default='-',
    help='Output file',
)
parser.add_argument('file')

def convert():
    """Entry point for converting csv."""
    args = parser.parse_args()
    quote_mode = {
        'MINIMAL': csv.QUOTE_MINIMAL,
        'NONNUMERIC': csv.QUOTE_NONNUMERIC,
        'ALL': csv.QUOTE_ALL,
    }[args.quote_mode]

    if args.file == '-':
        input_stream = sys.stdin
    else:
        input_stream = open(args.file, 'r')

    if args.output == '-':
        output_stream = sys.stdout
    else:
        output_stream = open(args.output, 'w')

    reader = csv.reader(
        input_stream,
        delimiter=args.from_delimiter,
        quotechar=args.from_quote,
    )
    writer = csv.writer(
        output_stream,
        delimiter=args.to_delimiter,
        quotechar=args.to_quote,
        quoting=quote_mode,
    )
    writer.writerows(reader)

    if input_stream != sys.stdin:
        input_stream.close()
    if output_stream != sys.stdout:
        output_stream.close()
