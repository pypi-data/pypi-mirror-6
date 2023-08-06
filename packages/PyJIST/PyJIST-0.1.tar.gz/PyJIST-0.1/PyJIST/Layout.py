'''
Created on Feb 20, 2014

@author: asmanaj
'''

from PyJIST import PyJIST

class Layout(PyJIST):
    '''
    classdocs
    '''
    
    __wrapper__ = False;
    __shortname__ = 'layout'
    __help__ = "Runs JIST Layout"
    __description__ = '''
Run a generic JIST Layout by specifying existing layout.
'''
    
    @staticmethod
    def set_parser(parser, info):
        
        group = parser.add_argument_group("Required arguments")
        group.add_argument('-l', '--layout',
                           dest='layout',
                           metavar='LAYOUT',
                           required=True,
                           help='The layout location')
        
        group.add_argument('opts',
                           metavar='OPT',
                           nargs="*",
                           help='The JIST options. Note, these options MUST be preceeded by "-- " to ensure that the options are correctly passed to the layout')
        
        group = parser.add_argument_group("Additional arguments")
        group.add_argument('-h', '--help',
                           action="help",
                           help="Display this information and exit.")
        
        return(parser)
    
    def submit(self, args):
        
        # do the pre-processing
        self.preprocess(args)
        
        # set up the run string
        run_str = '"%s" %s' % (args.layout, " ".join(args.opts))
        
        # run the command
        self.run_layout(run_str)
