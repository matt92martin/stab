#!/usr/bin/python
import sys, os, traceback, argparse, textwrap, re
from csv import DictReader


# Hyut!
# __________________________ ___________________  __
# \                         | (_)___(_)___(_)   } _____
#  `-...................____|_/              )_/ ____


class Stab:

    def __init__(self, options):

        self.options = options
        self.reader = self.csv()
        self.headers = self.headers()
        self.searches = None

    def format_text(self, text):
        if self.options.ignorecase: text = self.case(text)
        if self.options.trim:       text = self.trim(text)
        return text

    def case(self, text):
        if type(text) == list:
            return [(x.lower(), op) for x, op in text]
        return text.lower()

    def trim(self, text):
        if type(text) == list:
            return [(x.strip(), op) for x, op in text]
        return text.strip()

    def get_searches(self, cols):

        searches = []
        # Does it need to be complex?
        word_search = re.compile(r'(?P<header>[\s\w\<\>\\\,\.\!\@\#\$\%\^\&\*\(\)]+):(?P<value>([\s\w\<\>\\\,\.\!\@\#\$\%\^\&\*\(\)]+)||(\s*))(?::?(?P<operator>!=|==|\^|\$))?(?:\|\|)?')

        for query in cols:
            search = {}

            search_groups = [match.groupdict() for match in word_search.finditer(query[0])]

            for group in search_groups:

                if not group['operator']:
                    group['operator'] = '=='

                header = group['header']
                value = group['value']
                operator = group['operator']

                if search.get(header, None):
                    search[header].append((value, operator))
                else:
                    search[header] = [(value, operator)]

            searches.append(search)

        return searches

    def headers(self):

        gcol = self.options.goodcol
        bcol = self.options.badcol
        fieldnames = self.reader.fieldnames

        if gcol and gcol.strip():

            cols = [x.strip() for x in gcol.split(',')]
            return [x for x in fieldnames if x in cols]

        elif bcol and bcol.strip():

            cols = [x.strip() for x in bcol.split(',')]
            return [x for x in fieldnames if x not in cols]

        return fieldnames

    def csv(self):
        return DictReader(open(self.options.file), delimiter=self.options.delim)

    def exit(self, mes):
        sys.exit(mes)

    def exec_equal(self, value, search):
        return search == value

    def exec_notequal(self, value, search):
        return search != value

    def exec_startswith(self, value, search):
        return value.startswith(search)

    def exec_endswith(self, value, search):
        return value.endswith(search)

    # != == ^ $
    def exec_single_search(self, value, search):
        op = search[1]
        if op == '==':
            return self.exec_equal(value, search[0])
        elif op == '!=':
            return self.exec_notequal(value, search[0])
        elif op == '^':
            return self.exec_startswith(value, search[0])
        elif op == '$':
            return self.exec_endswith(value, search[0])
        else:
            return False

    def exec_search_set(self, value, searches):

        check = False
        for search in searches:
            if self.exec_single_search(value, search):
                check = True
            else:
                return False

        return check

    def check_line(self, line, searches):
        # Print line if no searches are specified
        if len(searches) == 0:
            return True

        for search in searches:
            check = False
            for columnName, searchValues in search.items():

                check = self.exec_search_set(
                    self.format_text(line.get(columnName, False)),
                    self.format_text(searchValues)
                )

                if not check:
                    break

            if check:
                return True

        return False

    def find_and_print(self):
        reader = self.reader

        if self.options.headers:
            yield '\t'.join([x for x in self.headers])
        for line in reader:
            if self.check_line(line, self.searches):
                yield '\t'.join([line[x] for x in self.headers])

    def main(self):

        if self.options.printhead:

            for i, head in enumerate(self.headers, 0):
                print "{}) {}".format(i, head)

        else:

            self.searches = self.get_searches(self.options.col or [])

            for line in self.find_and_print():
                print line


def options():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""
        (S)earch (Tab)-Delimited Files
        Examples:
           stab -c"Column:Value" File
           stab -c"Column1:Value1||Column2:Value2" File
           stab -c"Column1:Value1" -c"Column2:Value2" File
           stab -c"Column1:Value1:!=" -c"Column2:Value2:$" File
           stab -c"Column1:Value1:^" -c"Column2:Value2:$" File
        """),
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-c', '--column', help='Column(s) and value(s) for searching', dest='col', type=str, nargs='*',
                        action='append')
    parser.add_argument('-h', '--headers', help='Column(s) to include during print', dest='goodcol', type=str)
    parser.add_argument('-^h', '--^headers', help='Column(s) to supress during print', dest='badcol', type=str)
    parser.add_argument('-d', '--delimiter', help='Field delimiter', dest='delim', type=str, default="\t")
    parser.add_argument('-s', '--show-all', help='Print headers', dest='printhead', action='store_true')
    parser.add_argument('-i', '--ignore-case', help='Ignore case', dest='ignorecase', action='store_true')
    parser.add_argument('-t', '--trim', help='Strip spaces from column values', dest='trim', action='store_true')
    parser.add_argument('--nh', help='Print without headers', dest='headers', action='store_false')

    parser.add_argument('--help', help=argparse.SUPPRESS, action='help')
    parser.add_argument('file', help='File to parse', type=str)

    return parser.parse_args()


if __name__ == '__main__':
    try:
        stab = Stab(options())
        stab.main()
        sys.exit(0)
    except KeyboardInterrupt, e:  # Ctrl-C
        raise e
    except SystemExit, e:  # sys.exit()
        raise e
    # fix bash pipes
    except IOError, e:
        pass
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)
