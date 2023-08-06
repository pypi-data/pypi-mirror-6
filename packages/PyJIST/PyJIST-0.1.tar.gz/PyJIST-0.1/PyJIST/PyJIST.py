'''
Created on Feb 19, 2014

@author: asmanaj
'''

import sys
import os
import subprocess
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self

class PyJIST(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        self.default_mipav = None
        self.default_plugindir = None
        self.default_java = None
        self.default_jvmsize = "8000M"
        self.default_debuglvl = 2
        self.cmd_prefix = ""
        self.cmd_suffix = ""
        homedir = os.path.expanduser("~")
        
        # intelligently set default file locations
        if os.path.isdir("/Applications/mipav/"):
            self.default_mipav = "/Applications/mipav/"
        elif os.path.isdir(os.path.join(homedir, "mipav/")):
            self.default_mipav = os.path.join(homedir, "mipav/")

        if os.path.isdir(os.path.join(self.default_mipav, "plugins/")):
            self.default_plugindir = os.path.join(self.default_mipav, "plugins/")
        elif os.path.isdir(os.path.join(homedir, "mipav/plugins")):
            self.default_plugindir = os.path.join(homedir, "mipav/plugins")
            
        if os.path.isfile(os.path.join(self.default_mipav, "jre/bin/java")):
            self.default_java = os.path.join(self.default_mipav, "jre/bin/java")
        else:
            for path in os.environ["PATH"].split(":"):
                if os.path.exists(os.path.join(path, "java")):
                    self.default_java = os.path.join(path, "java")

    def add_JIST_arguments(self, parser):
        
        group = parser.add_argument_group("General JIST arguments")
    
        # add all of the arguments
        group.add_argument("--debuglvl",
                            dest="debuglvl",
                            type=int,
                            metavar="LVL",
                            default=self.default_debuglvl,
                            help="Set debugging level [default: %d]" % (self.default_debuglvl))
        group.add_argument("--mipav",
                            dest="mipav",
                            metavar="DIR",
                            default=self.default_mipav,
                            help="Set the mipav location [default: %s]" % (self.default_mipav))
        group.add_argument("--plugindir",
                            dest="plugindir",
                            metavar="DIR",
                            default=self.default_plugindir,
                            help="Set the mipav plugin location [default: %s]" % (self.default_plugindir))
        group.add_argument("--java",
                            dest="java",
                            metavar="FILE",
                            default=self.default_java,
                            help="Location of java [default: %s]." % self.default_java)
        group.add_argument("--jvmsize",
                            dest="jvmsize",
                            metavar="SIZE",
                            default=self.default_jvmsize,
                            help="JVM Heap size [default: %s]." % self.default_jvmsize)
        group.add_argument("--addjardirs",
                            dest="jardirs",
                            metavar="DIR",
                            nargs="+",
                            help="List of directories to recursively search for jar files. [default: None]")
        group.add_argument("--addclassdirs",
                            dest="classdirs",
                            metavar="DIR",
                            nargs="+",
                            help="List of directories to add to the java classpath. [default: None]")
    
    def preprocess(self, args):
        
        # get the list of jar files
        jarlist = []
        jardirs = [args.mipav]
        if args.plugindir:
            jardirs.append(args.plugindir)
        if args.jardirs:
            jardirs += args.jardirs
        for path in jardirs:
            for (dirpath, _, filenames) in os.walk(path):
                for name in filter(lambda x: x.endswith('.jar'), filenames):
                    jarlist.append(os.path.join(dirpath, name))
        jarlist = list(set(jarlist))
        jarlist_str = ":".join(jarlist)
         
        # get the class folder list
        if (args.plugindir and args.plugindir != "None"):
            classlist_str = args.plugindir
        else:
            classlist_str = ""
        if args.classdirs:
            for d in args.classdirs:
                if classlist_str == "":
                   classlist_str = d
                else:
                    classlist_str = ":".join([classlist_str, d])

        # construct the final command strings
        self.classlist_str = classlist_str
        classpath_str = args.mipav + ":" + classlist_str + ":" + jarlist_str
         
        self.cmd_prefix = '%s -Xmx%s -classpath "%s"' % (args.java,
                                                         args.jvmsize,
                                                         classpath_str)
        self.cmd_suffix = "-xDebugLvl %d" % (args.debuglvl)
        self.cmd_run = "edu.jhu.ece.iacl.jist.cli.run"
        self.cmd_run_layout = "edu.jhu.ece.iacl.jist.cli.runLayout"
        self.cmd_discover = "edu.jhu.ece.iacl.jist.cli.discover"
        
    def run(self, run_str):
        os.system("%s %s %s %s" % (self.cmd_prefix,
                                   self.cmd_run,
                                   run_str,
                                   self.cmd_suffix))

    def run_layout(self, run_str):
        os.system("%s %s %s %s" % (self.cmd_prefix,
                                   self.cmd_run_layout,
                                   run_str,
                                   self.cmd_suffix))

    def discover(self):
        cmd = '%s %s "%s"' % (self.cmd_prefix,
                              self.cmd_discover,
                              self.classlist_str)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        return(out)
        
    def go(self, argv, info):
        try:
            # Setup argument parser
            parser = ArgumentParser(description=info['program_license'],
                                    formatter_class=RawDescriptionHelpFormatter,
                                    add_help=False)
            
            # add the subparsers
            subparsers = parser.add_subparsers(title="Available modules",
                                               metavar="",
                                               dest="func")
            
            # append the help option
            group = parser.add_argument_group("optional arguments")
            group.add_argument('-h', '--help',
                               action="help",
                               help="Display this information and exit.")
                
            # Add all of the possible sub-commands
            # - Note, we want them sorted with the general methods first,
            #   followed by all of the wrapper methods.
            sub_list = PyJIST.__subclasses__()
            key_func = lambda cls: str(cls.__wrapper__) + cls.__shortname__
            for cls in sorted(sub_list, key=key_func):

                # add each parser individually
                cls_parser = subparsers.add_parser(
                                    cls.__shortname__,
                                    help=cls.__help__,
                                    description=cls.__description__,
                                    formatter_class=RawDescriptionHelpFormatter,
                                    add_help=False)
                cls.set_parser(cls_parser, info)
                self.add_JIST_arguments(cls_parser)
            
            # parse the arguments
            args = parser.parse_args()
            
            # run the chosen class (beautiful)
            filter(lambda x: x.__shortname__ == args.func,
                   PyJIST.__subclasses__())[0]().submit(args)

        except CLIError as e:
            module = argv[1]
            sys.stderr.write("%s %s: error:\n" % (info['program_name'], module))
            sys.stderr.write("-> " + str(e.msg) + "\n")
            sys.stderr.write("-> use -h/--help for more information\n")
            sys.exit(1)

