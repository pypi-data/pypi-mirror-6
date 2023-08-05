#!/sw/opt/python/2.7.3/bin/python

'''
--------------------------------------
common.ngseq.summarizeWigPerFeature.py
--------------------------------------

This stand-alone script reads a wig or bigwig file and a gff or gtf annotation 
file and then sumarizes the data in the wig file for a specified feature type 
from the annotation file. The result is output as a tab delimited text file.
Options are available to control the feature type and the numbers that are 
output in the file.

.. moduleauthor:: Nick Schurch <nschurch@dundee.ac.uk>

:module_version: 1.0
:created_on: 2014-01-07

Command-line Arguments
======================

**usage\:** 
    summarizeWigPerFeature.py
    :param: <output tsv file> 
    :param: <input wig/bigwig file>
    :param: <input gtf/gff file>
    :option:`-l|--log` *<file>* 
    [:option:`--tmpdir`] 
    [:option:`-v|--verbose`] 
    [:option:`--version`] 
    [:option:`--help`]

Required Parameters
-------------------

:param: <output tsv file>

  The filename of the output text file. Tab-seperated values. 

:param: <input wig/bigwig file>

  The input file in wig or bigwig format

:param: <input gtf/gff file>

  The input annotation file. Currently only gff v3 is supported.

:option:`--logfile|-l`

  The name (inc. path) of the log file from the wrapper.

Optional Parameter
------------------

:option:`--help|-h`

  Print a basic description of the tool and its options to STDOUT.

:option:`--version`    

  Show program's version number and exit.
    
:option:`--verbose|-v`     

  Turn on verbose logging (recommended).

Output
======

A tsv file with the summarization stats for each feature in the annotation.

'''

__version__ = "1.0"
__usage__ = "\n\t%s <output tsv file> <input wig/bigwig file> " \
            "\t\n<input gtf/gff file> -l|--logfile <file> [--version] " \
            "\t\n[-v|--verbose] [--help]"
__progdesc__ = '''
This stand-alone script reads a wig or bigwig file and a gff or gtf annotation 
file and then sumarizes the data in the wig file for a specified feature type 
from the annotation file. The result is output as a tab delimited text file.
Options are available to control the feature type and the numbers that are 
output in the file.
'''
__progepi__ = '''
--------------------------------------
common.ngseq.summarizeWigPerFeature.py
--------------------------------------
'''

import sys, os, logging
import script_options.standard_parsers as sp
import script_logging.standard_logging as sl
import script_options.custom_callables as cc
import parsing_routines.wig_tools as wig 
import parsing_routines.gff_gtf_tools as gff

if __name__ == '__main__':
    
    # parse command line options
    # Set standard parser
    parser, pos_args, kw_args = sp.standard_parser(__version__,
                                                   prog = sys.argv[0], 
                                                   usage = __usage__,
                                                   description = __progdesc__,
                                                   epilog = __progepi__,
                                                   infile = False,
                                                   outfile = True,
                                                   tmpdir = True)
    
    # add additional options
    infiles_group = parser.add_argument_group('Input Files (required)')
    wigfilehelp = "Specify an input wig or bigwig file (inc. path if " \
                 "different from the current working directory) to be " \
                 "consumed by this script."

    infiles_group.add_argument('wigfile',
                               action = 'store',
                               type = cc.input_file,
                               help = wigfilehelp 
                               )
    
    annotfilehelp = "Specify an input gtf or gff file (inc. path if " \
                    "different from the current working directory) to be " \
                    "consumed by this script."

    infiles_group.add_argument('gfffile',
                               action = 'store',
                               type = cc.input_file,
                               help = annotfilehelp 
                               )
    
    script_options_group = parser.add_argument_group('Options')

    script_options_group.add_argument('--bigwig',
                                      action = 'store_true',
                                      dest = 'isBigWig',
                                      help = "Specify that the input wig " \
                                             "file is a bigwig file."
                                      )
    
    script_options_group.add_argument('--bigwigBinary',
                                      action = 'store',
                                      dest = 'BigWigPath',
                                      type = str,
                                      default = "../parsing_routines/external_libraries/bigWigToWig",
                                      help = "Specify that the input wig " \
                                             "file is a bigwig file."
                                      )

    script_options_group.add_argument('--feature',
                                      action = 'store',
                                      dest = 'feature',
                                      default = 'genes',
                                      type = str,
                                      help = "Specify a feature type present " \
                                             "in the gft/gff file."
                                      )
       
    script_options_group.add_argument('--mean',
                                      action = 'store_false',
                                      dest = 'mean',
                                      help = "Include the mean in the " \
                                             "reported stats."
                                      )

    script_options_group.add_argument('--median',
                                      action = 'store_false',
                                      dest = 'median',
                                      help = "Include the median in the " \
                                             "reported stats."
                                      )

    script_options_group.add_argument('--pbmean',
                                      action = 'store_false',
                                      dest = 'pbmean',
                                      help = "Include the per_base_mean in " \
                                             "the reported stats."
                                      )

    script_options_group.add_argument('--baseFrac',
                                      action = 'store_false',
                                      dest = 'baseFrac',
                                      help = "Include the fraction of bases " \
                                             "with signal in the wig file in " \
                                             "the reported stats."
                                      )
    
    script_options_group.add_argument('--stddev',
                                      action = 'store_false',
                                      dest = 'stddev',
                                      help = "Include the standard deviation " \
                                             "in the reported stats."
                                      )

    script_options_group.add_argument('--min',
                                      action = 'store_false',
                                      dest = 'min',
                                      help = "Include the min value in the " \
                                             "reported stats."
                                      )

    script_options_group.add_argument('--max',
                                      action = 'store_false',
                                      dest = 'max',
                                      help = "Include the max value in the " \
                                             "reported stats."
                                      )

    # parse arguments
    args = parser.parse_args()
    
    # setup standard logging information
    root_logger = logging.getLogger(__name__)
    root_logger.setLevel(logging.INFO)
    if args.verbose:
        root_logger.setLevel(logging.DEBUG)
    logfile_handler = sl.get_logfile_handler(args)
    root_logger.addHandler(logfile_handler)
    sl.standard_logger(__version__, sys.argv, args, pos_args, 
                       kw_args, logbase=__name__)
    
    # read wig file
    root_logger.info("Reading input wig/bigwig file...")
    x=wig.wigData(args.wigfile, isBigWig=args.isBigWig,
                  path_to_binary=args.BigWigPath)

    # read annotation file
    root_logger.info("Reading input gtf/gff file...")
    sc = gff.annotation(args.gfffile, filetype="gff3")
    
    # set feature
    root_logger.info("Getting features...")
    sc.set_feature(args.feature)
    sc_genes=sc.get_selection()
    
    # process feature regions
    fileout = open(args.outfile,"w")
    cols = "Name"
    if args.mean:
        cols = "%s\tmean" % cols
    if args.median:
        cols = "%s\tmedian" % cols
    if args.pbmean:
        cols = "%s\tper_base_mean" % cols
    if args.baseFrac:
        cols = "%s\tfraction_of_bases_with_signal" % cols
    if args.stddev:
        cols = "%s\tstddev" % cols
    if args.min:
        cols = "%s\tmin" % cols
    if args.max:
        cols = "%s\tmax" % cols
    cols = "%s\n" % cols
    fileout.write(cols)
    
    for region in sc_genes:
        root_logger.info("Processing region: %s - %s:%i-%i..." % (region.name,
                                                                  region.chrid,
                                                                  region.start,
                                                                  region.stop))
        try:
            x.set_region(region)
            root_logger.info("\tfound.")
            writestr = region.name
            if args.mean:
                writestr = "%s\t%.2f" % (writestr,
                                         x.tracks[region.chrid].region_mean())
            if args.median:
                writestr = "%s\t%.2f" % (writestr,
                                         x.tracks[region.chrid].region_median())
            if args.pbmean:
                writestr = "%s\t%.2f" % (writestr,
                                         x.tracks[region.chrid].region_mean_per_base())
            if args.baseFrac:
                writestr = "%s\t%.2f" % (writestr,
                                         x.tracks[region.chrid].region_fracbases())
            if args.stddev:
                writestr = "%s\t%.4f" % (writestr,
                                         x.tracks[region.chrid].region_stddev())
            if args.min:
                writestr = "%s\t%.2f" % (writestr,
                                         x.tracks[region.chrid].region_min()[0])
            if args.max:
                writestr = "%s\t%.2f" % (writestr,
                                         x.tracks[region.chrid].region_max()[0])
            writestr = "%s\n" % writestr            
            fileout.write(writestr)
        except ValueError:
            root_logger.info("\tskipping.")
    
    fileout.close()
    
    root_logger.info("Output saved to file: %s" % (args.outfile))
    root_logger.info("finished.")


