'''
Created on Feb 20, 2014

@author: asmanaj
'''

import os
from PyJIST import PyJIST

class STAPLE(PyJIST):
    '''
    classdocs
    '''
    
    __wrapper__ = True
    __shortname__ = 'STAPLE'
    __help__ = "Runs STAPLE"
    __description__ = "Run the STAPLE Statistical Fusion Algorithm"
    
    @staticmethod
    def set_parser(parser, info):
        
        group = parser.add_argument_group("Required arguments")
        group.add_argument('-l', '--labels',
                           dest="labels",
                           metavar="LABEL",
                           required=True,
                           nargs="+",
                           help="The atlas label images")
        group.add_argument('-o', '--output',
                           dest="output",
                           metavar="LABEL",
                           required=True,
                           help="The fused segmentation")
        
        group = parser.add_argument_group("EM arguments")
        group.add_argument('-e', '--convergence',
                           dest="convergence",
                           metavar="FLOAT",
                           type=float,
                           default=1e-4,
                           help="Convergence threshold [default: %(default)s]")
        group.add_argument('-m', '--maxiters',
                           dest="maxiters",
                           metavar="NUM",
                           type=int,
                           default=100,
                           help="Maximum number of iterations [default %(default)s]")
        group.add_argument('-c', '--consensus-thresh',
                           dest="consensus_thresh",
                           metavar="FLOAT",
                           type=float,
                           default=0.99,
                           help="Consensus threshold [default: %(default)s]")
        group.add_argument('-p', '--prior',
                           dest="prior",
                           default="Voxelwise",
                           choices=['Voxelwise', 'Global', 'Weighted-Voxelwise'],
                           help="Prior type [default: %(default)s]")
        group.add_argument('-hier', '--hierarchy',
                           dest="hierarchy",
                           metavar="FILE",
                           default=None,
                           help="Hierarchy file [default: %(default)s]")
         
        group = parser.add_argument_group("Additional arguments")
        group.add_argument('-h', '--help',
                           action="help",
                           help="Display this information and exit.")
        
        return(parser)
    
    def submit(self, args):
        
        # do the pre-processing
        self.preprocess(args)
        
        # set up the run string
        run_str = "edu.vanderbilt.masi.plugins.labelfusion.PluginStatisticalFusion"
        run_str = '%s -inAtlas "%s"' % (run_str, ";".join(args.labels))
        run_str = '%s -inConvergence %f' % (run_str, args.convergence)
        run_str = '%s -inMaximum %d' % (run_str, args.maxiters)
        run_str = '%s -inConsensus %f' % (run_str, args.consensus_thresh)
        run_str = '%s -inPrior %s' % (run_str, args.prior)
        if args.hierarchy:
            run_str = '%s -inHierarchy %s' % (run_str, args.hierarchy)
        run_str = '%s -inBias %f' % (run_str, 1.0)
         
        # note the output file has to be an absolute path
        run_str = '%s -outLabel "%s"' % (run_str, os.path.abspath(args.output))
        
        # run the command
        self.run(run_str)
