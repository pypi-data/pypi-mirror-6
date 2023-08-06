'''
Created on Feb 20, 2014

@author: asmanaj
'''

from PyJIST import PyJIST
from PyJIST import CLIError

class Search(PyJIST):
    '''
    classdocs
    '''
    
    __wrapper__ = False
    __shortname__ = 'search'
    __help__ = "Searches available JIST Modules"
    __description__ = """
Searches available JIST Modules using edu.jhu.ece.iacl.jist.cli.discover.
These available JIST Modules can then be used with the 'generic' framework.

Example 1: JIST-run search -a
Description: Prints all available modules

Example 2: JIST-run search -i STAPLE -x Spatial
Description: Prints all modules that match "STAPLE", but don't match "Spatial"

Example 3: JIST-run search -i STAPLE,Asman Random
Description: Prints all modules that match "STAPLE" and "Asman", and prints
             all modules that contain "Random"

"""
    
    @staticmethod
    def set_parser(parser, info):

        group = parser.add_argument_group("Optional arguments " +
                                          "(at least one must be specified)")
        group.add_argument('-a', '--all',
                           dest='printall',
                           required=False,
                           action="store_true",
                           help='Print all discovered classes')
        group.add_argument('-i', '--include',
                           dest='inclusions',
                           metavar='STR',
                           nargs="+",
                           required=False,
                           help='Inclusion Criteria. Note, comma separated arguments form an "and" condition and space separated arguments form an "or" condition. For example, "-i Asman,STAPLE Random" would include modules that contain Asman and STAPLE, or modules that contain Random.')
        group.add_argument('-x', '--exclude',
                           dest='exclusions',
                           metavar='STR',
                           nargs="+",
                           required=False,
                           help='Exclusion Criteria. Note, comma separated arguments form an "and" condition and space separated arguments form an "or" condition. For example, "-x Asman,STAPLE Random" would exclude modules that contain Asman and STAPLE, or modules that contain Random.')
        
        group = parser.add_argument_group("Additional arguments")
        group.add_argument('-h', '--help',
                           action="help",
                           help="Display this information and exit.")
        
        return(parser)
    
    def submit(self, args):

        # see what was specified
        print_all = args.printall
        use_includes = not(args.inclusions == None or len(args.inclusions) == 0)
        use_excludes = not(args.exclusions == None or len(args.exclusions) == 0)

        # do some error checking
        if (print_all and use_includes):
            raise CLIError("Invalid options, can't specify -a/--all and " +
                           "-i/--include")
        if (print_all and use_excludes):
            raise CLIError("Invalid options, can't specify -a/--all and " +
                           "-x/--exclude")
        if (not(print_all or use_includes or use_excludes)):
            raise CLIError('Invalid options, must specify -a/--all, ' +
                           '-i/--include or -x/--exclude')

        # run the JIST discover utility and store the output string
        self.preprocess(args)
        out_str = self.discover()

        # no inclusions/exclusions specified, print everything
        if print_all:
            print(out_str)

        # only print entries matching specified search criteria
        else:
            split_str = "=========\n";
            entries = out_str.rstrip().split(split_str);

            # apply the exclusions
            if use_excludes:
                for term in map(str.lower, args.exclusions):
                    a_tt = filter(lambda x: len(x) > 0, term.split(","))
                    entries = filter(
                        lambda x: not(all([tt in x.lower() for tt in a_tt])),
                        entries)

            # apply the inclusions
            if use_includes:
                keep = []
                for term in map(str.lower, args.inclusions):
                    a_tt = filter(lambda x: len(x) > 0, term.split(","))
                    keep.extend(
                        filter(
                            lambda x: all([tt in x.lower() for tt in a_tt]),
                            entries))
                entries = set(keep)

            # print the discovered results
            for entry in entries:
                print(split_str + entry),

