#!/usr/bin/python
import sys, os, traceback, argparse, textwrap, re
from csv import DictReader


# Hyut!
# __________________________ ___________________  __
# \                         | (_)___(_)___(_)   } _____
#  `-...................____|_/              )_/ ____



class Stab:

    def __init__( self, options ):

        self.options = options
        self.reader  = self.csv()
        self.headers = self.headers()
        self.searches = None


    def case( self, text ):
        if self.options.ignorecase:
            if type( text ) == list:
                return [ x.lower() for x in text ]
            return text.lower()
        return text



    def get_searches(self, cols):

        searches = []
        word_search = re.compile(r'(?P<header>[\s\w\<\>\\\,\.\!\@\#\$\%\^\&\*\(\)]+?):(?P<value>[\s\w\<\>\\\,\.\!\@\#\$\%\^\&\*\(\)]+)(?::?(?P<operator>!=|==|\^|\$))?(?:\|\|)?')

        for query in cols:
            search = {}

            search_groups = [ match.groupdict() for match in word_search.finditer( query[0] ) ]

            for group in search_groups:
                # print group
                if not group['operator']:
                    group[ 'operator' ] = '=='

                header   = group['header']
                value    = group['value']
                operator = group['operator']

                if search.get( header , None):
                    search[ header ].append( ( value, operator ) )
                else:
                    search[ header ] = [ ( value, operator ) ]

            searches.append( search )

        return searches


    def headers( self ):

        gcol = self.options.goodcol
        bcol = self.options.badcol
        fieldnames = self.reader.fieldnames

        if gcol and gcol.strip():

            cols = [ x.strip() for x in gcol.split(',') ]
            return [ x for x in fieldnames if x in cols ]

        elif bcol and bcol.strip():

            cols = [ x.strip() for x in bcol.split(',') ]
            return [ x for x in fieldnames if x not in cols ]

        return fieldnames


    def csv( self ):
        return DictReader( open( self.options.file ), delimiter=self.options.delim )


    def exit( self, mes ):
        sys.exit( mes )


    def check_line( self, line, searches ):

        check = False
        for search in searches:

            for s in search.items():
                # print s
                col = s[ 0 ]
                line_col = line.get( col, False )

                if line_col and self.case( line_col ) in self.case( s[ 1 ] ):
                    check = True
                else:
                    check = False
                    break

            if check:
                return True

        return False


    def find_and_print( self ):
        reader = self.reader

        yield '\t'.join( [ x for x in self.headers ])
        for line in reader:
            if self.check_line( line, self.searches):
                yield '\t'.join( [ line[ x ] for x in self.headers ])


    def main( self ):

        if self.options.printhead:

            for i,head in enumerate( self.headers, 0 ):
                print "{}) {}".format( i, head )

            self.exit( 0 )

        else:

            self.searches = self.get_searches(self.options.col or [])

            print self.searches
            for line in self.find_and_print():
                print line


def options( ):
    parser = argparse.ArgumentParser(
        description=textwrap.dedent( """
        (S)earch (Tab)-Delimited Files
        Examples:
           stab -c"Column:Value" File
           stab -c"Column1:Value1||Column2:Value2" File
           stab -c"Column1:Value1" -c"Column2:Value2" File
        """ ),
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument( '-c', '--column',        help='Column(s) and values',     dest='col',       type=str,
                         nargs='*',
                         action='append'
                         )
    parser.add_argument( '-h', '--headers',       help='Column(s) to include',     dest='goodcol',   type=str )
    parser.add_argument( '-^h', '--^headers',     help='Column(s) to supress',     dest='badcol',    type=str )
    parser.add_argument( '-d', '--delimiter',     help='Specify headers to print', dest='delim',     type=str,
                         default="\t"
                         )
    parser.add_argument( '-s', '--show-all',      help='Print headers',            dest='printhead',
                         action='store_true'
                         )
    parser.add_argument( '-i', '--ignore-case',   help='Ignore case',              dest='ignorecase',
                         action='store_true'
                         )
    parser.add_argument( '--help',                help=argparse.SUPPRESS, action='help' )
    parser.add_argument( 'file',                  help='File to parse',                               type=str )

    return parser.parse_args( )


if __name__ == '__main__':
    try:
        stab = Stab( options() )
        stab.main()
        sys.exit( 0 )
    except KeyboardInterrupt, e:  # Ctrl-C
        raise e
    except SystemExit, e:  # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str( e )
        traceback.print_exc()
        os._exit( 1 )
