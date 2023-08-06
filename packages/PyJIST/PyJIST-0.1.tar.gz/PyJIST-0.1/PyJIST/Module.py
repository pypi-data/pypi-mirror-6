'''
Created on Feb 20, 2014

@author: asmanaj
'''

from PyJIST import PyJIST

class Module(PyJIST):
    '''
    classdocs
    '''
    
    __wrapper__ = False;
    __shortname__ = 'module'
    __help__ = "Runs JIST Module"
    __description__ = '''
Run a JIST Module by specifying full class definition

Example:
JIST-run module -c edu.jhu.bme.smile.demo.RandomVol -- -outRand1 ~/test.nii.gz

'''
    
    @staticmethod
    def set_parser(parser, info):
        
        group = parser.add_argument_group("Required arguments")
        group.add_argument('-c', '--class',
                           dest='classname',
                           metavar='CLASS',
                           required=True,
                           help='The full class definition')
        
        group.add_argument('opts',
                           metavar='OPT',
                           nargs="+",
                           help='The JIST options. Note, these options MUST be preceeded by "-- " to ensure that the options are correctly passed to the module')
        
        group = parser.add_argument_group("Additional arguments")
        group.add_argument('-h', '--help',
                           action="help",
                           help="Display this information and exit.")
        
        return(parser)
    
    def submit(self, args):
        
        # do the pre-processing
        self.preprocess(args)
        
        # set up the run string
        run_str = '%s %s' % (args.classname, " ".join(args.opts))
        
        # run the command
        self.run(run_str)
