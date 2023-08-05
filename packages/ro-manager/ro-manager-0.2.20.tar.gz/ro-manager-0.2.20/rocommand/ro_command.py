# ro_command.py

"""
Basic command functions for ro, research object manager
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys, select
import os
import os.path
import re
import datetime
import logging
import urlparse
import urllib2
from ro_utils import EvoType
from xml.parsers import expat
from httplib2 import RelativeURIError
import time
try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json

log = logging.getLogger(__name__)

import MiscUtils.ScanDirectories

import ro_settings
import ro_utils
import ro_uriutils
from ro_annotation import annotationTypes, annotationPrefixes
from ro_metadata   import ro_metadata
import ro_remote_metadata
from ROSRS_Session import ROSRS_Session
from ROSRS_Session import ROSRS_Error
import ro_rosrs_sync
import ro_evo
from iaeval import ro_eval_minim
from zipfile import ZipFile

RDFTYP = ["RDFXML","N3","TURTLE","NT","JSONLD","RDFA"]
VARTYP = ["JSON","CSV","XML"]

RDFTYPPARSERMAP = (
    { "RDFXML": "xml"
    , "N3":     "n3"
    , "TURTLE": "n3"
    , "NT":     "nt"
    , "JSONLD": "jsonld"
    , "RDFA":   "rdfa"
    })

RDFTYPSERIALIZERMAP = (
    { "RDFXML": "pretty-xml"
    , "N3":     "n3"
    , "TURTLE": "turtle"
    , "NT":     "nt"
    , "JSONLD": "jsonld"
    })

def getoptionvalue(val, prompt):
    if not val:
        if sys.stdin.isatty():
            val = raw_input(prompt)
        else:
            val = sys.stdin.readline()
            if val[-1] == '\n': val = val[:-1]
    return val

def getroconfig(configbase, options, rouri=None):
    ro_config = ro_utils.readconfig(configbase)
    if options.rosrs_uri:
        ro_config['rosrs_uri'] = options.rosrs_uri
    if options.rosrs_access_token:
        ro_config['rosrs_access_token'] = options.rosrs_access_token
    if rouri:
        ro_config['rosrs_uri'] = rouri
    return ro_config

def ro_root_directory(cmdname, ro_config, rodir, restricted=True):
    """
    Find research object root directory

    Returns directory path string, or None if not found, in which
    case an error message is displayed.
    """
    # log.debug("ro_root_directory: cmdname %s, rodir %s"%(cmdname, rodir))
    # log.debug("                   ro_config %s"%(repr(ro_config)))
    if restricted:
        ro_dir = ro_utils.ropath(ro_config, rodir)
    else:
        ro_dir = os.path.abspath(rodir)
    if not ro_dir:
        print ("%s: indicated directory not in configured research object directory tree: %s (%s)" % 
               (cmdname, rodir, ro_config['robase']))
        return None
    if not os.path.isdir(ro_dir):
        print ("%s: indicated directory does not exist: %s" % 
               (cmdname, rodir))
        return None
    manifestdir = None
    ro_dir_next = ro_dir
    ro_dir_prev = ""
    # log.debug("ro_dir_next %s, ro_dir_prev %s"%(ro_dir_next, ro_dir_prev))
    while ro_dir_next and ro_dir_next != ro_dir_prev:
        # log.debug("ro_dir_next %s, ro_dir_prev %s"%(ro_dir_next, ro_dir_prev))
        manifestdir = os.path.join(ro_dir_next, ro_settings.MANIFEST_DIR)
        if os.path.isdir(manifestdir):
            return ro_dir_next
        ro_dir_prev = ro_dir_next
        ro_dir_next = os.path.dirname(ro_dir_next)  # Up one directory level
    print ("%s: indicated directory is not contained in a research object: %s" % 
           (cmdname, ro_dir))
    return None

def ro_root_reference(cmdname, ro_config, rodir, roref=None):
    """
    Find research object root directory.  If the supplied rodir is not a local file
    reference, it is returned as-is, otherwise ro_root_directory is used to locate
    the RO root directory containing the indicated file.

    cmdname     name of ro command, used in diagnostic messages
    ro_config   RO configuration details, used when resolving supplied directory
    rodir       RO directory supplied via -d option.  Must be in configured work area.
    roref       RO reference, supplied by other means, or None.  May be any URI reference,
                resolved against base of file URI for current directory.

    Returns directory path string, or None if not found, in which
    case an error message is displayed.
    """
    if not roref:
        # Process supplied directory option
        roref = ro_uriutils.resolveFileAsUri(rodir)
        if ro_uriutils.isFileUri(roref):
            roref = ro_root_directory(cmdname, ro_config, rodir, restricted=False)
    else:
        if rodir:
            print ("%s: specify either RO directory or URI, not both" % (cmdname))
            return 1
        roref = ro_uriutils.resolveFileAsUri(roref)
    return roref

# Argument count checking and usage summary

def argminmax(min, max):
    return (lambda options, args: (len(args) >= min and (max == 0 or len(args) <= max)))
    
ro_command_usage = (
    [ (["help"], argminmax(2, 2),
          ["help"])
    , (["config"], argminmax(2, 2),
          ["config -b <robase> -n <username> -e <useremail> -r <rosrs_uri> -t <access_token>"])
    , (["create"], argminmax(3, 3),
          ["create <RO-name> [ -d <dir> ] [ -i <RO-ident> ]"])
    , (["status"],argminmax(2, 3),
          ["status [ -d <dir> | <uri> ]"])
    , (["add"], argminmax(2, 3),
          ["add [ -d <dir> ] [ -a ] [ file | directory ]"])
    , (["remove"], argminmax(3, 3),
          ["remove [ -d <dir> ] <file-or-uri>"
          , "remove -d <dir> -w <pattern>"
          ])
    , (["list", "ls"], argminmax(2, 3),
          ["list [ -a ] [ -s ] [ -d <dir> | <uri> ]"
          , "ls   [ -a ] [ -s ] [ -d <dir> | <uri> ]"
          ])
    , (["annotate"], (lambda options, args: (len(args) == 3 if options.graph else len(args) in [4, 5])),
          ["annotate [ -d <dir> ] <file-or-uri> <attribute-name> <attribute-value>"
          , "annotate [ -d <dir> ] <file-or-uri> -g <RDF-graph>"
          , "annotate -d <dir> -w <pattern> <attribute-name> <attribute-value>"
          , "annotate -d <dir> -w <pattern> -g <RDF-graph>"
          ])
    , (["link"], (lambda options, args: (len(args) == 3 if options.graph else len(args) in [4, 5])),
          ["link [ -d <dir> ] <file-or-uri> <attribute-name> <attribute-value>"
          , "link [ -d <dir> ] <file-or-uri> -g <RDF-graph>"
          , "link -d <dir> -w <pattern> <attribute-name> <attribute-value>"
          , "link -d <dir> -w <pattern> -g <RDF-graph>"
          ])
    , (["annotations"], argminmax(2, 3),
          ["annotations [ <file> | -d <dir> ] [ -o <format> ]"])
    , (["evaluate", "eval"], argminmax(5, 6),
          ["evaluate checklist [ -d <dir> ] [ -a | -l <level> ] [ -o <format> ] <minim> <purpose> [ <target> ]"])
    , (["push"], (lambda options, args: (argminmax(2, 3) if options.rodir else len(args) == 3)),
          ["push <zip> | -d <dir> [ -f ] [ -r <rosrs_uri> ] [ -t <access_token> ] [ --asynchronous ]"])
    , (["checkout"], argminmax(2, 3),
          ["checkout <RO-name> [ -d <dir>] [ -r <rosrs_uri> ] [ -t <access_token> ]"])
    , (["dump"], argminmax(2, 3),
          ["dump [ -d <dir> | <rouri> ] [ -o <format> ]"])
    , (["manifest"], argminmax(2, 3),
          ["manifest [ -d <dir> | <rouri> ] [ -o <format> ]"])
    , (["snapshot"],  argminmax(4, 4),
          ["snapshot <live-RO> <snapshot-id> [ --asynchronous ] [ --freeze ] [ -t <access_token> ] [ -r <rosrs_uri> ]"])
    , (["archive"],  argminmax(4, 4),
          ["archive <live-RO> <archive-id> [ --asynchronous ] [ --freeze ] [ -t <access_token> ]"])
    , (["freeze"],  argminmax(3, 3),
          ["freeze <RO-id>"])
    ])

def check_command_args(progname, options, args):
    # Eliminate blank arguments
    args = [ a for a in args if a != "" ]
    # Check argument count for known command
    for (cmds, test, usages) in ro_command_usage:
        if args[1] in cmds:
            if not test(options, args):
                print ("%s %s: wrong number of arguments provided" % 
                       (progname, args[1]))
                # for i in range(len(args)):
                #     print "%d: '%s'"%(i, args[i])
                print "Usage:"
                for u in usages:
                    print "  %s %s" % (progname, u)
                return 2
            return 0
    # Unknown command - show usage for all commands
    print "%s: Unrecognized command (%s)" % (progname, args[1])
    print ""
    print "Available commands are:"
    for (cmds, test, usages) in ro_command_usage:
        for u in usages:
            print "  %s %s" % (progname, u)
    return 2

def help(progname, args):
    """
    Display ro command help.  See also ro --help
    """
    print "Available commands are:"
    for (cmds, test, usages) in ro_command_usage:
        for u in usages:
            print "  %s %s" % (progname, u)
    helptext = (
        [ ""
        , "Supported annotation type names are: "
        , "\n".join([ "  %(name)s - %(description)s" % atype for atype in annotationTypes ])
        , ""
        , "See also:"
        , "  %(progname)s --help"
        , ""
        ])
    for h in helptext:
        print h % {'progname': progname}
    return 0

def config(progname, configbase, options, args):
    """
    Update RO repository access configuration
    """
    robase = os.path.realpath(options.robasedir)
    ro_config = {
        "robase":               getoptionvalue(robase,
                                "RO local base directory:       "),
        "rosrs_uri":            getoptionvalue(options.rosrs_uri,
                                "URI for ROSRS service:         "),
        "rosrs_access_token":   getoptionvalue(options.rosrs_access_token,
                                "Access token for ROSRS service:"),
        "username":             getoptionvalue(options.username,
                                "Name of research object owner: "),
        "useremail":            getoptionvalue(options.useremail,
                                "Email address of owner:        "),
        # Built-in annotation types and prefixes
        "annotationTypes":      annotationTypes,
        "annotationPrefixes":   annotationPrefixes
        }
    ro_config["robase"] = os.path.abspath(ro_config["robase"])
    if options.verbose:
        print "ro config -b %(robase)s" % ro_config
        print "          -r %(rosrs_uri)s" % ro_config
        print "          -t %(rosrs_access_token)s" % ro_config
        print "          -n %(username)s -e %(useremail)s" % ro_config
    ro_utils.writeconfig(configbase, ro_config)
    if options.verbose:
        print "ro configuration written to %s" % (os.path.abspath(configbase))
    return 0

def create(progname, configbase, options, args):
    """
    Create a new Research Object.

    ro create RO-name [ -d dir ] [ -i RO-ident ]
    """
    ro_options = {
        "roname":  getoptionvalue(args[2], "Name of new research object: "),
        "rodir":   options.rodir or "",
        "roident": options.roident or ""
        }
    log.debug("cwd: " + os.getcwd())
    log.debug("ro_options: " + repr(ro_options))
    ro_options['roident'] = ro_options['roident'] or ro_utils.ronametoident(ro_options['roname'])
    # Read local ro configuration and extract creator
    ro_config = getroconfig(configbase, options)
    timestamp = datetime.datetime.now().replace(microsecond=0)
    ro_options['rocreator'] = ro_config['username']
    ro_options['rocreated'] = timestamp.isoformat()
    ro_dir = ro_utils.ropath(ro_config, ro_options['rodir'])
    if not ro_dir:
        print ("%s: research object not in configured research object directory tree: %s" % 
               (ro_utils.progname(args), ro_options['rodir']))
        return 1
    # Create directory for manifest
    if options.verbose:
        print "ro create \"%(roname)s\" -d \"%(rodir)s\" -i \"%(roident)s\"" % ro_options
    manifestdir = os.path.join(ro_dir, ro_settings.MANIFEST_DIR)
    log.debug("manifestdir: " + manifestdir)
    try:
        os.makedirs(manifestdir)
    except OSError:
        if os.path.isdir(manifestdir):
            # Someone else created it...
            # See http://stackoverflow.com/questions/273192/
            #          python-best-way-to-create-directory-if-it-doesnt-exist-for-file-write
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise
    # Create manifest file
    # @@TODO: create in-memory graph and serialize that
    manifestfilename = os.path.join(manifestdir, ro_settings.MANIFEST_FILE)
    log.debug("manifestfilename: " + manifestfilename)
    manifest = (
        """<?xml version="1.0" encoding="utf-8"?>
        <rdf:RDF
          xml:base=".."
          xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
          xmlns:ro="http://purl.org/wf4ever/ro#"
          xmlns:ore="http://www.openarchives.org/ore/terms/"
          xmlns:ao="http://purl.org/ao/"
          xmlns:dcterms="http://purl.org/dc/terms/"
          xmlns:foaf="http://xmlns.com/foaf/0.1/"
        >
          <ro:ResearchObject rdf:about="">
            <dcterms:identifier>%(roident)s</dcterms:identifier>
            <dcterms:title>%(roname)s</dcterms:title>
            <dcterms:description>%(roname)s</dcterms:description>
            <dcterms:creator>%(rocreator)s</dcterms:creator>
            <dcterms:created>%(rocreated)s</dcterms:created>
            <!-- self-reference to include above details as annotation -->
            <ore:aggregates>
              <ro:AggregatedAnnotation>
                <ro:annotatesAggregatedResource rdf:resource="" />
                <ao:body rdf:resource=".ro/manifest.rdf" />
              </ro:AggregatedAnnotation>
            </ore:aggregates>
          </ro:ResearchObject>
        </rdf:RDF>
        """ % ro_options)
    log.debug("manifest: " + manifest)
    manifestfile = open(manifestfilename, 'w')
    manifestfile.write(manifest)
    manifestfile.close()
    return 0

def status(progname, configbase, options, args):
    """
    Display status of a designated research object

    ro status <uri> [ -d dir ]
    """
    # Check command arguments
    ro_config = getroconfig(configbase, options)
    ro_options = {
        "rodir":   options.rodir or "",
        }
    log.debug("ro_options: " + repr(ro_options))
    # Find RO root directory"
    if len(args) == 3 and ro_options['rodir'] != "":
        print "ambiguous status command"
        return 1 
    if len(args) == 3 and ro_options['rodir'] == "":
        return remote_status(progname, configbase, options, args)
    ro_dir = ro_root_directory(progname + " status", ro_config, ro_options['rodir'])
    if not ro_dir: return 1
    # Read manifest and display status
    if options.verbose:
        print "ro status -d \"%(rodir)s\"" % ro_options
    rometa = ro_metadata(ro_config, ro_dir)
    rodict = rometa.getRoMetadataDict()
    print "Research Object status"
    print "  identifier:  %(roident)s, title: %(rotitle)s" % rodict
    print "  creator:     %(rocreator)s, created: %(rocreated)s" % rodict
    print "  path:        %(ropath)s" % rodict
    if rodict['rouri']:
        print "  uri:         %(rouri)s" % rodict
    print "  description: %(rodescription)s" % rodict
    # @@TODO: add ROEVO information
    return 0

def remote_status(progname, configbase, options, args):
    ro_config = getroconfig(configbase, options, args[2])
    ro_options = {
        "uri":                args[2],
        "rosrs_uri":          ro_config['rosrs_uri'],
        "rosrs_access_token": ro_config['rosrs_access_token'],
    }
    if options.verbose:
        print "ro status %(uri)s -r %(rosrs_uri)s -t %(rosrs_access_token)s" % ro_options
    rosrs = ROSRS_Session(ro_options["rosrs_uri"], ro_options["rosrs_access_token"])
    return remote_ro_status(options, args, rosrs)
    #try to get remote status
    
def job_status(options, args, rosrs):
    try:
        if len(rosrs.getJob(args[2])) == 5:
            (status,target,processed,submitted,opType) = rosrs.getJob(args[2])
            print "Job Status: %s" %  status
            print "Target Uri: %s" %  target
            if submitted != "0":
                print "Processed resources/Submitted resources: %s/%s" % (processed,submitted)
            return 0
        else:
            (status,target,finalize,opType) = rosrs.getJob(args[2])
            print "Job Status: %s" %  status
            print "Target Uri: %s" %  target
            print "Finalize: %s" %  finalize
            print "Research Object Type: %s" % opType
            return 0
    except expat.ExpatError as error:
        return -1
    except RelativeURIError as error:
        return -1
    except IndexError as error:
        return -1


def remote_ro_status(options, args, rosrs):
    try:
        result = rosrs.getROEvolution(args[2])
        if result == None:
            return -1
        (status, reason, data, evo_type) = result
        if evo_type == None:
            status =  job_status(options, args, rosrs)
            if status == -1:
                print "Wrong URI was given"
            return status
        elif evo_type == EvoType.LIVE:
            print "Research Object Status: LIVE" 
        elif evo_type == EvoType.SNAPSHOT:
            print "Research Object Status: SNAPSHOT"
        elif evo_type == EvoType.ARCHIVE:
            print "Research Object Status: ARCHIVE"
        elif evo_type == EvoType.UNDEFINED:
            print "Research Object Status: UNDEFINED"
    except ROSRS_Error as error:
        return job_status(options, args, rosrs)
    return 0
    
def add(progname, configbase, options, args):
    """
    Add files to a research object manifest

    ro add [ -d dir ] file
    ro add [ -d dir ] [-a] [directory]

    Use -a/--all to add subdirectories recursively

    If no file or directory specified, defaults to current directory.
    """
    ro_config = getroconfig(configbase, options)
    ro_options = {
        "rodir":        options.rodir or "",
        "rofile":       args[2] if len(args) == 3 else ".",
        "recurse":      options.all,
        "recurseopt":   "-a" if options.all else ""
        }
    log.debug("ro_options: " + repr(ro_options))
    # Find RO root directory
    ro_dir = ro_root_directory(progname + " add", ro_config, ro_options['rodir'])
    if not ro_dir: return 1
    # Read and update manifest
    if options.verbose:
        print "ro add -d %(rodir)s %(recurseopt)s %(rofile)s" % ro_options
    rometa = ro_metadata(ro_config, ro_dir)
    rometa.addAggregatedResources(ro_options['rofile'],
        recurse=ro_options['recurse'], includeDirs=not ro_options['recurse'])
    return 0

def remove(progname, configbase, options, args):
    """
    Remove a specified research object component or components

    remove [ -d <dir> ] <file-or-uri>
    remove -d <dir> -w <pattern>
    """
    ro_config = getroconfig(configbase, options)
    rodir = options.rodir or (not options.wildcard and os.path.dirname(args[2]))
    ro_options = {
        # Usding graph annotation form
        "rofile":       args[2],
        "rodir":        rodir,
        "wildcard":     options.wildcard,
        "wild":         "-w " if options.wildcard else "",
        "rocmd":        progname,
        }
    log.debug("remove: ro_options: " + repr(ro_options))
    # Find RO root directory
    ro_dir = ro_root_directory("%s %s" % (progname, args[1]), ro_config, ro_options['rodir'])
    if not ro_dir: return 1
    if options.verbose:
        print "%(rocmd)s remove -d %(rodir)s %(wild)s%(rofile)s" % (ro_options)
    # Read and update manifest and annotations
    rometa = ro_metadata(ro_config, ro_dir)
    if options.wildcard:
        try:
            rofilepattern = re.compile(ro_options['rofile'])
        except re.error as e:
            ro_options["err"] = str(e)
            print '''%(rocmd)s remove -w "%(rofile)s" <...> : %(err)s''' % ro_options
            return 1
        for rofile in [ r for r in rometa.getAggregatedResources() if rofilepattern.search(str(r)) ]:
            rometa.removeAggregatedResource(rofile)
    else:
        rofile = rometa.getComponentUri(ro_options['rofile'])
        rometa.removeAggregatedResource(rofile)
    return 0

def mapmerge(f1, l1, f2, l2):
    """
    Helper function to merge lists of values with different map functions.
    A sorted list is returned containing f1 mapped over the elements of l1 and 
    f2 mapped over the elements ofd l2 that are not in l1; i.e. roughly:

    return sorted([ f1(i1) for i1 in l1 ] + [ f2(i2) for i2 in l2 if i2 not in l1 ])

    The actual code is a little more complex because the final sort is based on the
    original list values rather than the mapped values.
    """    
    def mm(f1, l1, f2, l2, acc):
        if len(l1) == 0: return acc + map(f2, l2)
        if len(l2) == 0: return acc + map(f1, l1)
        if l1[0] < l2[0]: return mm(f1, l1[1:], f2, l2, acc + [f1(l1[0])])
        if l1[0] > l2[0]: return mm(f1, l1, f2, l2[1:], acc + [f2(l2[0])])
        # List heads equal: choose preferentially from l1
        return mm(f1, l1[1:], f2, l2[1:], acc + [f1(l1[0])])
    return mm(f1, sorted(l1), f2, sorted(l2), [])

def prepend_f(pref):
    """
    Returns a function that prepends prefix 'pref' to a supplied string
    """
    return lambda s:pref + s

def testMap():
    l1 = ["a", "b", "d", "e"]
    l2 = ["a", "c"]
    assert mapmerge(prepend_f("1:"), l1, prepend_f("2:"), l2) == ["1:a", "1:b", "2:c", "1:d", "1:e"]
    l1 = ["d", "a"]
    l2 = ["f", "e", "c", "a"]
    assert mapmerge(prepend_f("1:"), l1, prepend_f("2:"), l2) == ["1:a", "2:c", "1:d", "2:e", "2:f"]

def list(progname, configbase, options, args):
    """
    List contents of a designated research object
    
    -a displays files present in directory as well as aggregated resources
    -h includes hidden files in display

    ro list [ -a ] [ -h ] [ -d dir | uri ]
    ro ls   [ -a ] [ -h ] [ -d dir | uri ]
    """
    # Check command arguments
    rouri      = (args[2] if len(args) >= 3 else "")
    ro_config  = getroconfig(configbase, options, rouri)
    ro_options = {
        "rouri":   rouri,
        "rodir":   options.rodir or "",
        "all":     " -a" if options.all    else "",
        "hidden":  " -h" if options.hidden else "",
        }
    log.debug("ro_options: " + repr(ro_options))
    cmdname = progname + " list"
    if rouri:
        rouri = ro_root_reference(cmdname, ro_config, ro_options['rodir'], rouri)
        if not rouri: return 1
        if options.verbose:
            print cmdname + (" \"%(rouri)s\" " % ro_options)
        ro_dir = ""
    else:
        ro_dir = ro_root_directory(cmdname, ro_config, ro_options['rodir'], restricted=False)
        if not ro_dir: return 1
        if options.verbose:
            print cmdname + ("%(all)s%(hidden)s -d \"%(rodir)s\" " % ro_options)
        rouri  = ro_dir

    # Prepare to display aggregated resources
    prep_f = ""
    prep_a = ""
    rofiles = []
    if options.all:
        if not ro_dir:
            print ("%s: '--all' option is valid only with RO directory, not URI" % (cmdname))
            return 1
        prep_f = "f: "
        prep_a = "a: "
        rofiles = MiscUtils.ScanDirectories.CollectDirectoryContents(
                    ro_dir, baseDir=os.path.abspath(ro_dir),
                    listDirs=False, listFiles=True, recursive=True, appendSep=False)
        if not options.hidden:
            def notHidden(f):
                return re.match("\.|.*/\.", f) == None
            rofiles = filter(notHidden, rofiles)
    # Scan RO and collect aggregated resources
    try:
        rometa = ro_metadata(ro_config, rouri)
    except ROSRS_Error, e:
        print str(e)
        return 2
    roaggs = [ str(rometa.getComponentUriRel(a)) for a in rometa.getAggregatedResources() ]
    # Assemble and output listing
    print "\n".join(mapmerge(prepend_f(prep_a), roaggs, prepend_f(prep_f), rofiles))
    return 0

def annotate(progname, configbase, options, args):
    """
    Annotate a specified research object component

    ro annotate file attribute-name [ attribute-value ]
    ro link file attribute-name [ attribute-value ]
    """
    ro_config = getroconfig(configbase, options)
    rodir = options.rodir or (not options.wildcard and os.path.dirname(args[2]))
    if len(args) == 3:
        # Using graph form
        ro_options = {
            # Usding graph annotation form
            "rofile":       args[2],
            "rodir":        rodir,
            "wildcard":     options.wildcard,
            "wild":         "-w " if options.wildcard else "",
            "graph":        options.graph or None,
            "defaultType":  "resource" if args[1] == "link" else "string",
            "rocmd":        progname,
            "anncmd":       args[1]
            }
    else:
        ro_options = {
            # Usding explicit annotation form
            "rofile":       args[2],
            "rodir":        rodir,
            "wildcard":     options.wildcard,
            "wild":         "-w " if options.wildcard else "",
            "roattribute":  args[3],
            "rovalue":      args[4] if len(args) == 5 else None,
            "defaultType":  "resource" if args[1] == "link" else "string",
            "rocmd":        progname,
            "anncmd":       args[1]
            }
    log.debug("ro_options: " + repr(ro_options))
    # Find RO root directory
    ro_dir = ro_root_directory("%s %s" % (progname, args[1]), ro_config, ro_options['rodir'])
    if not ro_dir: return 1
    if options.verbose:
        if len(args) == 3:
            print "%(rocmd)s %(anncmd)s -d %(rodir)s %(wild)s%(rofile)s -g %(graph)s " % (ro_options)
        else:
            print "%(rocmd)s %(anncmd)s -d %(rodir)s %(wild)s%(rofile)s %(roattribute)s \"%(rovalue)s\"" % ro_options
    # Read and update manifest and annotations
    # ---- local function to annotate a single entry ----
    def annotate_single(rofile):
        if len(args) == 3:
            # Add existing graph as annotation
            rometa.addGraphAnnotation(rofile, ro_options['graph'])
        else:
            # Create new annotation graph
            rometa.addSimpleAnnotation(rofile,
                ro_options['roattribute'], ro_options['rovalue'],
                ro_options['defaultType'])
    # ----
    rometa = ro_metadata(ro_config, ro_dir)
    if options.wildcard:
        try:
            rofilepattern = re.compile(ro_options['rofile'])
        except re.error as e:
            ro_options["err"] = str(e)
            print '''%(rocmd)s %(anncmd)s -w "%(rofile)s" <...> : %(err)s''' % ro_options
            return 1
        for rofile in [ str(r) for r in rometa.getAggregatedResources() if rofilepattern.search(str(r)) ]:
            annotate_single(rofile)
    else:
        rofile = ro_uriutils.resolveFileAsUri(ro_options['rofile'])  # Relative to CWD
        annotate_single(rofile)
    return 0

def annotations(progname, configbase, options, args):
    """
    Display annotations

    ro annotations [ file | -d dir ]
    """
    # @@TODO: although a URI is accepted on the command line, the actual display logic assumes
    #         a local file when displaying annotations.
    log.debug("annotations: progname %s, configbase %s, args %s" % 
              (progname, configbase, repr(args)))
    ro_config = getroconfig(configbase, options)
    ro_file = (args[2] if len(args) >= 3 else "")
    ro_options = {
        "rofile":       ro_file,
        "rodir":        options.rodir or os.path.dirname(ro_file)
        }
    log.debug("ro_options: " + repr(ro_options))
    cmdname = progname + " annotations"
    rouri = ro_root_reference(cmdname, ro_config, ro_options['rodir'])
    if not rouri: return 1
    if options.verbose:
        print cmdname + " -d \"%(rodir)s\" %(rofile)s " % ro_options
    # Enumerate and display annotations
    log.debug("- displaying annotations for %s"%(rouri))
    rometa = ro_metadata(ro_config, rouri)
    if ro_options['rofile']:
        rofile = ro_uriutils.resolveFileAsUri(ro_options['rofile'])  # Relative to CWD
        log.debug("Annotations for %s" % str(rofile))
        annotations = rometa.getFileAnnotations(rofile)
    else:
        annotations = rometa.getAllAnnotations()
    if options.debug:
        log.debug("---- Annotations:")
        for a in annotations:
            log.debug("  %s" % repr(a))
        log.debug("----")
    rometa.showAnnotations(annotations, sys.stdout)
    return 0

def snapshot(progname, configbase, options, args):
    """
    Prepare a snapshot of live research object
    snapshot <live-RO> <snapshot-id> [ --asynchronous ] [ --freeze ] [ -t <token> ]
    """
    ro_config = getroconfig(configbase, options)
    ro_options = {
        "rodir":          options.rodir or "",
        "rosrs_uri":          ro_config['rosrs_uri'],
        "rosrs_access_token": ro_config['rosrs_access_token'],
    }
    if options.verbose:
        to_print = "ro snapshot %(copy-from)s %(target)s -r %(rosrs_uri)s -t %(rosrs_access_token)s" % dict(ro_options.items() + {'copy-from':args[2], 'target':args[3]}.items())
        if options.asynchronous:
            to_print+=" --asynchronous"
        if options.freeze:
            to_print+=" --freeze"
        print to_print
    return ro_evo.copy_operation(dict(vars(options).items() + ro_options.items()), args,"SNAPSHOT")

def archive(progname, configbase, options, args):
    """
    Prepare an archive of live research object
    archive <live-RO> <archive-id> [ --asynchronous ] [ --freeze ] [ -t <token> ]
    """
    ro_config = getroconfig(configbase, options)
    ro_options = {
        "rosrs_uri":          ro_config['rosrs_uri'],
        "rosrs_access_token": ro_config['rosrs_access_token'],
    }
    if options.verbose:
        to_print = "ro archive %(copy-from)s %(target)s -t %(rosrs_access_token)s" % dict(ro_options.items() + {'copy-from':args[2], 'target':args[3]}.items())
        if options.asynchronous:
            to_print+=" --asynchronous"
        if options.freeze:
            to_print+=" --freeze"
        print to_print
    return ro_evo.copy_operation(dict(vars(options).items() + ro_options.items()), args, "ARCHIVE")

def freeze(progname, configbase, options, args):
    """
    Freeze snapshot or archive
    freeze <RO-id>
    """
    ro_config = getroconfig(configbase, options)
    ro_options = {
        "rosrs_uri":          ro_config['rosrs_uri'],
        "rosrs_access_token": ro_config['rosrs_access_token'],
    }
    return ro_evo.freeze(dict(vars(options).items() + ro_options.items()), args)
    
def push_zip(progname, configbase, options, args):
    """
    push RO in zip format
    
    ro push <zip> | -d <dir> [ -f ] [-- new ] [ -r <rosrs_uri> ] [ -t <access_token> [ --asynchronous ] ]    
    """
    ro_config = getroconfig(configbase, options)
    ro_options = {
        "zip": args[2],
        "rosrs_uri":          ro_config['rosrs_uri'],
        "rosrs_access_token": ro_config['rosrs_access_token'],
        "force":          options.force,
        "roId": args[2].replace(".zip", "").split("/")[-1]
        }

    if options.roident:
        ro_options["roId"] = options.roident
    if options.verbose:
        echo = "ro push %(zip)s -r %(rosrs_uri)s -t %(rosrs_access_token)s -i %(roId)s" % dict(ro_options.items() + {'zip':args[2], 'roId':ro_options["roId"]}.items())
        if options.asynchronous:
         echo+=" --asynchronous"
        if options.new:
            echo+=" --new"
        print echo
    rosrs = ROSRS_Session(ro_options["rosrs_uri"], ro_options["rosrs_access_token"])
    if options.new:
        (status, reason, headers, data) = ro_remote_metadata.sendZipRO(rosrs, ro_options["rosrs_uri"], ro_options["roId"], open(args[2], 'rb').read(),"zip/create")
    else:
        (status, reason, headers, data) = ro_remote_metadata.sendZipRO(rosrs, ro_options["rosrs_uri"], ro_options["roId"], open(args[2], 'rb').read())
    jobUri = headers["location"]
    (job_status, target_id, processed_resources, submitted_resources) = ro_utils.parse_job(rosrs, headers["location"])
    print "Your Research Object %s is already processed" % target_id
    print "Job URI: %s" % jobUri
    if options.asynchronous:
        return  handle_asynchronous_zip_push(rosrs, headers["location"])
    #with esc option
    print   "If you don't want to wait until the operation is finished press [ENTER]"
    while printZipJob(ro_utils.parse_job(rosrs, jobUri),jobUri):
        i, o, e = select.select( [sys.stdin], [], [], 2 )
        if (i) and "" == sys.stdin.readline().strip():
            print "You can check the process status using job URI: %s" % jobUri
            return
    if options.verbose:
        print "Status: %s" % status
        print "Reason: %s" % reason
        print "Headers: %s" % headers
        print "Data: %s" % data
    log.debug("Status: %s" % status)
    log.debug("Reason: %s" % reason)
    log.debug("Headers: %s" % headers)
    log.debug("Data: %s" % data)
    return 0

def handle_asynchronous_zip_push(rosrs,location):
    status = "RUNNING"
    while (status == "RUNNING"):
        (status, target_id, processed_resources, submitted_resources) = ro_utils.parse_job(rosrs, location)
        print "RO URI: % s" % target_id
        return 0

def handle_synchronous_zip_push(rosrs,location):
    status = "RUNNING"
    first = True
    while (status == "RUNNING"):
        (status, target_id, processed_resources, submitted_resources) = ro_utils.parse_job(rosrs, location)
        if(first):
            #print "Job Status: %s" % status
            print "RO URI: % s" % target_id
            first = False
        if submitted_resources != "0":
            print "Prcessed resources/Submitted resources: %s/%s" %(processed_resources, submitted_resources)
        time.sleep(2)
    if (status == "DONE"):
        print "Operation finised successfully"
        return 0
    else: 
        print "Oparation failed, check details: %s" % location
        return 0

# @@NOTE Fixing this typo introduces a bug.  I think the function should be removed.
# "handle_asynchronous_zip_push" is defined prioperly later
def hendle_asynchronous_zip_push():
    None

def printZipJob(parseJobResult, jobUri):
    (job_status, target_id, processed_resources, submitted_resources) = parseJobResult
    if submitted_resources != "0":
        print "Prcessed resources/Submitted resources: %s/%s" %(processed_resources, submitted_resources)
    if job_status != "RUNNING":
        print "Job Status: %s" % job_status
        print "RO URI: % s" % target_id
        if job_status != "DONE":
            print "You can check the process status using job URI: %s" % jobUri
        return False
    return True

def push(progname, configbase, options, args):
    """
    Push all or selected ROs and their resources to ROSRS

    ro push <zip> | -d <dir> [ -f ] [ -r <rosrs_uri> ] [ -t <access_token> ]
    """
    ro_config = getroconfig(configbase, options)
    ro_options = {
        "rodir":          options.rodir,
        "rosrs_uri":          ro_config['rosrs_uri'],
        "rosrs_access_token": ro_config['rosrs_access_token'],
        "force":          options.force
        }
    log.debug("ro_options: " + repr(ro_options))
    
    if len(args) == 3:
        return push_zip(progname, configbase, options, args)
    if options.verbose:
        print "ro push -d %(rodir)s -r %(rosrs_uri)s -t %(rosrs_access_token)s" % ro_options
    ro_dir = ro_root_directory(progname + " push", ro_config, ro_options['rodir'])
    if not ro_dir: return 1
    localRo = ro_metadata(ro_config, ro_dir)
    roId = ro_dir.replace(ro_config["robase"], "", 1)
    if roId.startswith("/"): 
        roId = roId.replace("/", "", 1)
    rosrs = ROSRS_Session(ro_options["rosrs_uri"], ro_options["rosrs_access_token"])
    (status, _, rouri, _) = ro_remote_metadata.createRO(rosrs, roId)
    if status == 201:
        print "Created RO: %s" % (rouri)
    elif status == 409:
        rouri = urlparse.urljoin(ro_options["rosrs_uri"], roId + "/")
        print "RO already exists: %s" % (rouri)
    remoteRo = ro_remote_metadata.ro_remote_metadata(ro_config, rosrs, rouri)
    pushedResCnt = 0
    pushedAnnCnt = 0
    deletedResCnt = 0
    deletedAnnCnt = 0
    for (action, resuri) in ro_rosrs_sync.pushResearchObject(localRo, remoteRo):
        if action == ro_rosrs_sync.ACTION_AGGREGATE_INTERNAL:
            print "Resource uploaded: %s" % (resuri)
            log.debug("Resource uploaded: %s" % (resuri))
            pushedResCnt += 1
        elif action == ro_rosrs_sync.ACTION_AGGREGATE_EXTERNAL:
            print "External resource pushed: %s" % (resuri)
            log.debug("External resource pushed: %s" % (resuri))
            pushedResCnt += 1
        elif action == ro_rosrs_sync.ACTION_AGGREGATE_ANNOTATION:
            if options.verbose:
                print "Annotation pushed: %s" % (resuri)
            log.debug("Annotation pushed: %s" % (resuri))
            pushedAnnCnt += 1
        elif action == ro_rosrs_sync.ACTION_UPDATE_OVERWRITE:
            # TODO ask user for confirmation
            print "Resource uploaded (WARNING: it has overwritten changes in RODL): %s" % (resuri)
            log.debug("Resource uploaded (WARNING: it has overwritten changes in RODL): %s" % (resuri))
            pushedResCnt += 1
        elif action == ro_rosrs_sync.ACTION_UPDATE:
            print "Resource uploaded: %s" % (resuri)
            log.debug("Resource uploaded: %s" % (resuri))
            pushedResCnt += 1
        elif action == ro_rosrs_sync.ACTION_UPDATE_ANNOTATION:
            if options.verbose:
                print "Annotation updated: %s" % (resuri)
            log.debug("Annotation updated: %s" % (resuri))
            pushedAnnCnt += 1
        elif action == ro_rosrs_sync.ACTION_SKIP:
            print "Resource skipped: %s" % (resuri)
            log.debug("Resource skipped: %s" % (resuri))
        elif action == ro_rosrs_sync.ACTION_DELETE:
            # TODO ask user for confirmation
            print "Resource deleted in ROSRS: %s" % (resuri)
            log.debug("Resource deleted in ROSRS: %s" % (resuri))
            deletedResCnt += 1
        elif action == ro_rosrs_sync.ACTION_DELETE_ANNOTATION:
            if options.verbose:
                print "Annotation deleted in ROSRS: %s" % (resuri)
            log.debug("Annotation deleted in ROSRS: %s" % (resuri))
            deletedAnnCnt += 1
        elif action == ro_rosrs_sync.ACTION_ERROR:
            print resuri
    print "%d resources pushed, %d annotations pushed, %d resources deleted, %d annotations deleted" \
        % (pushedResCnt, pushedAnnCnt, deletedResCnt, deletedAnnCnt)
    return 0

def checkout(progname, configbase, options, args):
    """
    Checkout a RO from ROSRS

    ro checkout <RO-identifier> [-d <dir> ] [ -r <rosrs_uri> ] [ -t <access_token> ]
    """
    ro_config = getroconfig(configbase, options)
    ro_options = {
        "roident":        args[2],
        "rodir":          options.rodir or "",
        "rosrs_uri":          ro_config['rosrs_uri'],
        "rosrs_access_token": ro_config['rosrs_access_token'],
        }
    log.debug("ro_options: " + repr(ro_options))
    if options.verbose:
        print "ro checkout %(roident)s %(rodir)s %(rosrs_uri)s %(rosrs_access_token)s" % ro_options
    ro_dir = os.path.join(ro_options['rodir'], ro_options["roident"])
    if not ro_dir: return 1
    rouri = urlparse.urljoin(ro_options["rosrs_uri"], ro_options["roident"])
    try:
        zipdata = ro_remote_metadata.getAsZip(rouri)
        __unpackZip(zipdata, ro_dir, options.verbose)
    except urllib2.URLError as e:
        print "Could not checkout %s: %s" % (rouri, e)
    return 0

def __unpackZip(verzip, rodir, verbose):
    zipfile = ZipFile(verzip)

    if verbose:
        for l in zipfile.namelist():
            print os.path.join(rodir, l)

    if not os.path.exists(rodir) or not os.path.isdir(rodir):
        os.mkdir(rodir)
    zipfile.extractall(rodir)

    print "%d files checked out" % len(zipfile.namelist())
    return 0

def evaluate(progname, configbase, options, args):
    """
    Evaluate RO

    ro evaluate checklist [ -d <dir> ] <minim> <purpose> [ <target> ]"
    """
    log.debug("evaluate: progname %s, configbase %s, args %s" % 
              (progname, configbase, repr(args)))
    ro_config = getroconfig(configbase, options)
    ro_options = (
        { "rodir":        options.rodir or ""
        , "function":     args[2]
        })
    log.debug("ro_options: " + repr(ro_options))
    ro_ref = ro_root_reference(progname + " annotations", ro_config, None, ro_options['rodir'])
    if not ro_ref: return 1
    # Evaluate...
    if ro_options["function"] == "checklist":
        if len(args) not in [5, 6]:
            print ("%s evaluate checklist: wrong number of arguments provided" % (progname))
            print ("Usage: %s evaluate checklist [ -d <dir> ] [ -a | -l <level> ] <minim> <purpose> [ <target> ]" % (progname))
            return 1
        levels = ["summary", "must", "should", "may", "full"]
        if options.level not in ["summary", "must", "should", "may", "full"]:
            print ("%s evaluate checklist: invalid reporting level %s, must be one of %s" % 
                    (progname, options.level, repr(levels)))
            return 1
        ro_options["minim"]   = ((len(args) > 3) and args[3]) or "minim.rdf"
        ro_options["purpose"] = ((len(args) > 4) and args[4]) or "create"
        ro_options["target"]  = ((len(args) > 5) and args[5]) or "."
        if options.verbose:
            print "ro evaluate %(function)s -d \"%(rodir)s\" %(minim)s %(purpose)s %(target)s" % ro_options
        rometa = ro_metadata(ro_config, ro_ref)
        (minimgraph, evalresult) = ro_eval_minim.evaluate(rometa,
            ro_options["minim"], ro_options["target"], ro_options["purpose"])
        if options.verbose:
            print "== Evaluation result =="
            print json.dumps(evalresult, indent=2)
        if options.outformat and options.outformat.upper() in RDFTYPSERIALIZERMAP:
            # RDF output
            graph = ro_eval_minim.evalResultGraph(minimgraph, evalresult)
            graph.serialize(destination=sys.stdout,
                format=RDFTYPSERIALIZERMAP[options.outformat.upper()])
        else:
            ro_eval_minim.format(evalresult,
                { "detail" : "full" if options.all else options.level },
                sys.stdout)
    # elif ... other functions here
    else:
        print ("%s evaluate: unrecognized function provided (%s)" % (progname, ro_options["function"]))
        print ("Usage:")
        print ("  %s evaluate checklist [ -d <dir> ] [ -a | -l <level> ] <minim> <purpose> [ <target> ]" % (progname))
        return 1
    return 0

def dump(progname, configbase, options, args):
    """
    Dump RDF of annotations
    """
    log.debug("dump: progname %s, configbase %s, args %s" % 
              (progname, configbase, repr(args)))
    rouri      = (args[2] if len(args) >= 3 else "")
    ro_config  = getroconfig(configbase, options, rouri)
    ro_options = {
        "rouri":        rouri,
        "rodir":        options.rodir or ""
        }
    cmdname = progname + " dump"
    rouri = ro_root_reference(cmdname, ro_config, ro_options['rodir'], rouri)
    if not rouri: return 1
    if options.verbose:
        if ro_options['rouri']:
            print cmdname + (" \"%(rouri)s\" " % ro_options)
        else:
            print cmdname + (" -d \"%(rodir)s\" " % ro_options)
    # Enumerate and display annotations
    rometa = ro_metadata(ro_config, rouri)
    format = "RDFXML"
    if options.outformat and options.outformat.upper() in RDFTYPSERIALIZERMAP:
        format = options.outformat.upper()
    graph = rometa.getAnnotationGraph()
    graph.serialize(destination=sys.stdout, format=RDFTYPSERIALIZERMAP[format])
    return 0

def manifest(progname, configbase, options, args):
    """
    Dump RDF of manifest
    """
    log.debug("manifest: progname %s, configbase %s, args %s" % 
              (progname, configbase, repr(args)))
    rouri      = (args[2] if len(args) >= 3 else "")
    ro_config  = getroconfig(configbase, options, rouri)
    ro_options = {
        "rouri":        rouri,
        "rodir":        options.rodir or ""
        }
    cmdname = progname + " manifest"
    rouri = ro_root_reference(cmdname, ro_config, ro_options['rodir'], rouri)
    if not rouri: return 1
    if options.verbose:
        if ro_options['rouri']:
            print cmdname + (" \"%(rouri)s\" " % ro_options)
        else:
            print cmdname + (" -d \"%(rodir)s\" " % ro_options)
    # Enumerate and display annotations
    rometa = ro_metadata(ro_config, rouri)
    format = "RDFXML"
    if options.outformat and options.outformat.upper() in RDFTYPSERIALIZERMAP:
        format = options.outformat.upper()
    graph = rometa.getManifestGraph()
    graph.serialize(destination=sys.stdout, format=RDFTYPSERIALIZERMAP[format])
    return 0

# End.
