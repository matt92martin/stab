#!/usr/bin/python
import sys, os, traceback, argparse, textwrap
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


    def case( self, text, ignore ):
        if ignore:
            if type( text ) == list:
                return [ x.lower() for x in text ]
            return text.lower()
        return text


    def get_searches(self, cols):
        searches = []

        for col in cols:
            search = {}
            col = col[ 0 ].split(',')

            try:

                for c in col:
                    key,value = c.split(':')

                    if search.get( key , None):
                        search[ key ].append( value )
                    else:
                        search[ key ] = [ value ]

                searches.append( search )

            except Exception, e:
                self.exit("{} - Looks like something is wrong with your query".format(col))

        self.searches = searches
        return


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
        ignore = self.options.ignorecase
        check = False

        for search in searches:

            for s in search.items():
                col = s[ 0 ]
                if line.get( col, False ) and self.case( line[ col ], ignore ) in self.case( s[ 1 ], ignore ):
                    check = True
                else:
                    check = False
                    break

            if check:
                return True

        return False


    def find_and_print( self ):
        reader = self.reader
        searches = self.searches

        print '\t'.join( [ x for x in self.headers ])
        for line in reader:
            if self.check_line( line, searches):
                print '\t'.join( [ line[ x ] for x in self.headers ])


    def main( self ):
        col = self.options.col

        if self.options.printhead:
            for i,head in enumerate( self.headers, 0 ):
                print "{}) {}".format( i, head )

            self.exit( 0 )

        elif col:
            self.get_searches(col)
            self.find_and_print()




def options( ):
    parser = argparse.ArgumentParser(
        description=textwrap.dedent( """
        (S)earch (Tab)-Delimited Files
        Examples:
           stab -c"Column:Value" File
           stab -c"Column1:Value1,Column2:Value2" File
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
