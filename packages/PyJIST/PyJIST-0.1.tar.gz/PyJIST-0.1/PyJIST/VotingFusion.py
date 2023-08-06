'''
Created on Feb 19, 2014

@author: asmanaj
'''

import os
from PyJIST import PyJIST

class VotingFusion(PyJIST):
    '''
    classdocs
    '''
    
    __wrapper__ = True
    __shortname__ = 'votefuse'
    __help__ = "Runs Voting Fusion"
    __description__ = "Run Voting Fusion"
    
    @staticmethod
    def set_parser(parser, info):
        
        group = parser.add_argument_group("required arguments")
        group.add_argument('-t', '--target',
                           dest="target",
                           metavar="IMAGE",
                           required=True,
                           help="The target image")
        group.add_argument('-l', '--labels',
                           dest="labels",
                           metavar="LABEL",
                           required=True,
                           nargs="+",
                           help="The atlas label images")
        group.add_argument('-i', '--images',
                           dest="images",
                           metavar="IMAGE",
                           required=True,
                           nargs="+",
                           help="The atlas intensity images")
        group.add_argument('-o', '--output',
                           dest="output",
                           metavar="LABEL",
                           required=True,
                           help="The fused segmentation")
         
        group = parser.add_argument_group("optional arguments")
        group.add_argument('-h', '--help',
                           action="help",
                           help="Display this information and exit.")
        
        return(parser)
    
    def submit(self, args):
        
        # do the preprocessing
        self.preprocess(args)
        
        # set up the run string
        run_str = "edu.vanderbilt.masi.plugins.labelfusion.PluginVotingFusion"
        run_str = '%s -inTarget "%s"' % (run_str, args.target)
        run_str = '%s -inAtlas "%s"' % (run_str, ";".join(args.labels))
        run_str = '%s -inAtlas2 "%s"' % (run_str, ";".join(args.images))
        
        # note the output file has to be an absolute path
        run_str = '%s -outLabel "%s"' % (run_str, os.path.abspath(args.output))
        
        # run the command
        self.run(run_str) 
