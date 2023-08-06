'''
Created on Feb 19, 2014

@author: asmanaj
'''

import os
from PyJIST import PyJIST

class StatisticalFusion(PyJIST):
    '''
    classdocs
    '''
    
    __wrapper__ = True
    __shortname__ = 'statfuse'
    __help__ = "Runs Statistical Fusion"
    __description__ = "Run Generalized Statistical Fusion Algorithm"
    
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
        
        group = parser.add_argument_group("Semi-Required arguments")
        group.add_argument('-t', '--target',
                           dest="target",
                           metavar="IMAGE",
                           default=None,
                           help="The target image")
        group.add_argument('-i', '--images',
                           dest="images",
                           metavar="IMAGE",
                           nargs="+",
                           default=None,
                           help="The atlas intensity images")
        
        group = parser.add_argument_group("Non-Local correspondence arguments")
        group.add_argument('-sr', '--search',
                           dest="search",
                           metavar="XxYxZxV",
                           default="3x3x3x0",
                           help="Search window radii [default: %(default)s]")
        group.add_argument('-pr', '--patch',
                           dest="patch",
                           metavar="XxYxZxV",
                           default="2x2x2x0",
                           help="Patch window radii [default: %(default)s]")
        group.add_argument('-sd', '--search-stdev',
                           dest="searchstdev",
                           metavar="XxYxZxV",
                           default="1.5x1.5x1.5x0",
                           help="Search window standard deviations [default: %(default)s]")
        group.add_argument('-wt', '--weight-type',
                           dest="weighttype",
                           choices=['MSD', 'LNCC', 'Mixed'],
                           default='MSD',
                           help="Weight Type [default: %(default)s]")
        group.add_argument('-ws', '--weight-stdev',
                           dest="weightstdev",
                           metavar="FLOAT",
                           type=float,
                           default=0.25,
                           help="Weight Standard Deviation [default: %(default)s]")
        group.add_argument('-ls', '--local-sel',
                           dest="localsel",
                           metavar="FLOAT",
                           type=float,
                           default=0.1,
                           help="Local Selection Threshold [default: %(default)s]")
        group.add_argument('-gs', '--global-sel',
                           dest="globalsel",
                           metavar="FLOAT",
                           type=float,
                           default=0,
                           help="Global Selection Threshold [default: %(default)s]")
        group.add_argument('-n', '--no-norm',
                           dest="no_norm",
                           action='store_false',
                           default=True,
                           help="Do not intensity normalize")
        
        group = parser.add_argument_group("Patch selection arguments")
        group.add_argument('--sel-type',
                           dest="sel_type",
                           choices=['Jaccard', 'SSIM', 'None'],
                           default="Jaccard",
                           help="Selection Type [default: %(default)s]")
        group.add_argument('--sel-thresh',
                           dest="sel_thresh",
                           metavar="FLOAT",
                           default=0.05,
                           type=float,
                           help="Selection Threshold [default: %(default)s]")
        group.add_argument('--sel-keep',
                           dest="sel_keep",
                           metavar="NUM",
                           default=150,
                           type=int,
                           help="Maximum number of patches to keep [default: %(default)s]")
        
        group = parser.add_argument_group("Local performance arguments")
        group.add_argument('-w', '--window',
                           dest="sv_window",
                           metavar="XxYxZxV",
                           default="5x5x5x0",
                           help="Local performance window radii [default: %(default)s]")
        group.add_argument('-b', '--bias',
                           dest="sv_bias",
                           metavar="RATIO",
                           type=float,
                           default=0,
                           help="Global performance bias [default: %(default)s]")
        group.add_argument('-a', '--augment',
                           dest="sv_augment",
                           action='store_true',
                           default=False,
                           help="Augment local performance model [default %(default)s]")
        
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
        if args.target:
            run_str = '%s -inTarget "%s"' % (run_str, args.target)
        if args.images:
            run_str = '%s -inAtlas2 "%s"' % (run_str, ";".join(args.images))
            
        run_str = '%s -inConvergence %f' % (run_str, args.convergence)
        run_str = '%s -inMaximum %d' % (run_str, args.maxiters)
        run_str = '%s -inConsensus %f' % (run_str, args.consensus_thresh)
        run_str = '%s -inPrior %s' % (run_str, args.prior)
        if args.hierarchy:
            run_str = '%s -inHierarchy %s' % (run_str, args.hierarchy)
        run_str = '%s -inWindow %d' % (run_str, int(args.sv_window.split('x')[0]))
        run_str = '%s -inWindow2 %d'% (run_str, int(args.sv_window.split('x')[1]))
        run_str = '%s -inWindow3 %d'% (run_str, int(args.sv_window.split('x')[2]))
        run_str = '%s -inWindow4 %d'% (run_str, int(args.sv_window.split('x')[3]))
        run_str = '%s -inBias %f' % (run_str, args.sv_bias)
        run_str = '%s -inAugment %s' % (run_str, str(args.sv_augment).lower())
        run_str = '%s -inWeighting %s' % (run_str, args.weighttype)
        run_str = '%s -inDifference %f'% (run_str, args.weightstdev)        
        run_str = '%s -inSearch %d' % (run_str, int(args.search.split('x')[0]))
        run_str = '%s -inSearch2 %d'% (run_str, int(args.search.split('x')[1]))
        run_str = '%s -inSearch3 %d'% (run_str, int(args.search.split('x')[2]))
        run_str = '%s -inSearch4 %d'% (run_str, int(args.search.split('x')[3]))
        run_str = '%s -inSearch5 %f' % (run_str, float(args.searchstdev.split('x')[0]))
        run_str = '%s -inSearch6 %f'% (run_str, float(args.searchstdev.split('x')[1]))
        run_str = '%s -inSearch7 %f'% (run_str, float(args.searchstdev.split('x')[2]))
        run_str = '%s -inSearch8 %f'% (run_str, float(args.searchstdev.split('x')[3]))
        run_str = '%s -inPatch %d' % (run_str, int(args.patch.split('x')[0]))
        run_str = '%s -inPatch2 %d'% (run_str, int(args.patch.split('x')[1]))
        run_str = '%s -inPatch3 %d'% (run_str, int(args.patch.split('x')[2]))
        run_str = '%s -inPatch4 %d'% (run_str, int(args.patch.split('x')[3]))
        run_str = '%s -inGlobal %f'% (run_str, args.globalsel)
        run_str = '%s -inLocal %f'% (run_str, args.localsel)
        run_str = '%s -inUse %s'% (run_str, str(args.no_norm).lower())
        run_str = '%s -inSelection %s'% (run_str, args.sel_type)
        run_str = '%s -inSelection2 %f'% (run_str, args.sel_thresh)
        run_str = '%s -inNumber %d'% (run_str, args.sel_keep)
         
        # note the output file has to be an absolute path
        run_str = '%s -outLabel "%s"' % (run_str, os.path.abspath(args.output))
        
        # run the command
        self.run(run_str)
