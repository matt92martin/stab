#!/usr/bin/env python
import argparse
import sys, os
import re
import logging
import csv


def get_options():
    dscript = "Search files by column"
    parser = argparse.ArgumentParser(description=dscript)
    parser.add_argument('-c', '--column', help='Column(s) and values to filter', dest='col', type=str, nargs='*', action='append')
    parser.add_argument('-d', '--delimiter', help='Specify a delimiter for your file. Default: \t', dest='delim', type=str)
    parser.add_argument('-s', '--show-all', help='Print headers', dest='printhead', action='store_true')
    parser.add_argument('file', help='File to parse', type=str)
    options = parser.parse_args()
    return options



class Stab:

    def __init__(self, options):
        self.lines = {}
        self.options = options
        self.delim = options.delim or '\t'
        self.headers = []
        self.searches = []

        logging.basicConfig(level=logging.DEBUG,
                            format='%(message)s')
        self.logger = logging.getLogger(__name__)


    def validate_header(self, headers, search=re.compile(r'[^a-zA-Z0-9_]').search):
        validate_chars = []
        heads = []
        dup_heads = []
        for head in headers:
            validate_chars.append(bool(search(head)))
            if head not in heads:
                heads.append(head)
            else:
                dup_heads.append(head)

        if len(dup_heads) == 0:
            return (not any(validate_chars))
        else:
            logging.debug('Dupe headers: [%s]', ', '.join(dup_heads))
            sys.exit(0)

    def get_headers(self, headers):

        if self.validate_header(headers):
            self.headers = headers
            if self.options.printhead:
                for i,head in enumerate(headers):
                    print "%s: %s" % (i, head)
                sys.exit(0)
            elif self.options.col:
                return True
        else:
            logging.debug('Headers contain invalid headers')
            sys.exit(0)

    def search_lines(self, row, line):
        for cond in self.searches:
            if all([cond[c] == row[c] for c in cond]):
                if os.fstat(0) == os.fstat(1):
                    print "\033[92m" + str(line) + ": \033[0m" + '\t'.join([row[col] for col in self.headers])
                else:
                    print '\t'.join([row[col] for col in self.headers])
                return

    def get_searches(self):
        for idx, col in enumerate(self.options.col):
            col = col[0]
            self.searches.append({})

            if ":" in col:
                try:
                    col, ans = col.split(':')
                    col = col.split(',')
                    ans = ans.split(',')
                    if len(col) == len(ans):
                        for i,c in enumerate(col):
                            self.searches[idx][c] = ans[i]
                    else:
                        self.error_messages(1)
                except e:
                    print e
            else:
                self.error_messages(1)

    def error_messages(self, code):
        errors = {
            1: """Make sure you are using the correct search format:
                -c"Column:Value"
                -c"Column1,Column2:Value1,Value2" """,
            2: '',
        }
        logging.debug('Looks like soemthing went wrong:')
        logging.debug(errors[code])
        sys.exit(0)




    def read_lines(self):
        with open(self.options.file, "rb") as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t')
            self.get_headers(reader.fieldnames)
            self.get_searches()


            print '\t'.join([col for col in self.headers])
            for idx,row in enumerate(reader, 1):
                self.search_lines(row, idx)



    def main(self):
        if self.options.printhead or self.options.col:
            self.read_lines()



if __name__ == '__main__':
    try:
        options = get_options()
        cat = Stab(options)
        cat.main()
        sys.exit(0)
    except KeyboardInterrupt, e:
        raise e
    except SystemExit, e:
        raise e
    except Exception, e:
        print str(e)
        os._exit(1)



