#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys, argparse, csv
from jinja2 import Environment, FileSystemLoader

__author__ = '@natjohan'
__credits__= 'KISS philosophy : Keep it simple, stupid'

def dieWith(msg) :
    sys.stderr.write('Ooops ' + str(msg) + '\n :( \n')
    sys.exit(-1)

def readCSV(input_file, csv_delimiter):
    file = open(input_file.name) # , encoding='utf-8')
    try:
        data = [row for row in csv.DictReader(file, delimiter=csv_delimiter)]
    except Exception as e:
        dieWith(e)
    finally:
        file.close()
    return data

def readTemplate(file):
    env = Environment(loader=FileSystemLoader(''), newline_sequence='\n')
    #if template == 'stdin' :
    #    file = sys.stdin
    #else:
    #    file = open(template)
    template = env.get_template(file.name)
    return template

def main():
    parser = argparse.ArgumentParser(description='This script will populate a Jinja2 template \
     ((http://jinja.pocoo.org/docs/) with some input data (CSV format) and output\
      one entire file or one file per line.\n ', epilog='--Hey Hey--')

    parser.add_argument('-v','--version', action='version', version='%(prog)s 0.1.4')
    parser.add_argument('-i','--input', help='Input file name CSV', type=argparse.FileType('rt'), required=True)
    parser.add_argument('-t','--template', help='Your template file', type=argparse.FileType('rt'), required=True)
    parser.add_argument('-d','--delimiter', help='Delimiter for your CSV file, default is ;', default=';')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-so','--simpleoutput',help='Output file name, stdout if not specified', nargs='?', const='stdout')
    group.add_argument('-mo','--multipleoutput',help='Generate one file per line, you must specify the\
     name of the column where are the names of files to generate, stdout if not specified', nargs='?', const='stdout')

    parser.add_argument('-a','--append', help='Appending the output to the end of the file if it exists',\
     nargs='?', choices=['w', 'a'], const='a', default='w')

    args = parser.parse_args()
     
    # Show values
    print ("-----------------------------------------\n")
    print ("Input file : %s" % args.input.name )
    print ("Template file : %s" % args.template.name )
    print ("Delimiter : %s \n" % args.delimiter)
    print ("-----------------------------------------\n")

    # Read CSV data & template
    data = readCSV(args.input, args.delimiter)
    template = readTemplate(args.template)

    output_from_template = ''
    # For outputting in a single file
    if args.simpleoutput :
        for row in data :
            output_from_template += str(template.render(row)) + '\n'
        
        if args.simpleoutput == 'stdout' :
            out = sys.stdout
            out.write(output_from_template)
        else :
            out = open(args.simpleoutput, args.append)
            out.write(output_from_template)
            sys.stderr.write('*** File %s was generated ***\n' % args.simpleoutput)

    # For outputting in multiple files
    else :
        if args.multipleoutput == 'stdout' :
            for row in data :
                output_from_template += str(template.render(row)) + '\n'
            out = sys.stdout
            out.write(output_from_template)
        else :
            counter = 0
            for row in data :
                output_from_template = template.render(row)
                outFilename = row[str(args.multipleoutput)]
                out = open(outFilename, args.append)
                out.write(output_from_template)
                counter += 1
                sys.stderr.write('File %s was generated \n' % outFilename )
            sys.stderr.write('\n *** Good job my buddy ! %s Files were generated *** \n' % counter)
