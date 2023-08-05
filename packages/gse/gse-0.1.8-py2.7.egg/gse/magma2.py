
from __init__ import *

import sys
import csv
import json

from pprint import pprint

from config import Configurator

log_levels = {'DEB': logging.DEBUG,
              'INF': logging.INFO,
              'WAR': logging.WARN,
              'ERR': logging.ERROR,
              'CRI': logging.CRITICAL,
              'FAT': logging.FATAL,
              }

from matricks import *
from cPickle import *

default_cfg = """\
# These correspond to columns of same name in magma2.datasets table
dataset_handle                 = lambda go: go.metadata.geo_accession
dataset_fullname               = lambda go: go.metadata.title
dataset_version                = lambda go: '1.0'
dataset_description            = lambda go: '\\n'.join(go.metadata.summary) if isinstance(go.metadata.summary, list) else go.metadata.summary
dataset_platform_type          = lambda go: 'microarray'    # CHANGE!! if this isn't a microarray dataset!
dataset_platform_details       = lambda go: ''
dataset_pubmed_id = lambda go: go.metadata.pubmed_id if hasattr(go.metadata, 'pubmed_id') else ''
dataset_excluded               = lambda go: 0      # 1 -> excluded;  0 -> included
dataset_species_id             = lambda go: 1      # HEADS-UP!!  defafults to mouse 
dataset_storage_type           = lambda go: 'hdf5'  

# These correspond roughly to columns of the same name in magma2.dataset_metadata
dataset_metadata_axis          = lambda go: 1      # 1 for column (sample), 0 for row (gene/probe)
dataset_metadata_level         = lambda go: ''     # this isn't typically used
dataset_metadata_repository_id = lambda: -1        # -1 indicates there is no corresponding dataset_metadat for this
dataset_metadata_name          = lambda go: ''        
dataset_metadata_description   = lambda go: ''

# These correspond roughly to columns of the same name in magma2.sample_metadata
sample_metadata_sample_id      = lambda s: s.sample_id
sample_metadata_level          = lambda s: ''      # For now, these are calc'd by gse-magma directly.
sample_metadata_name           = lambda s: ''      #    "
sample_metadata_value          = lambda s: ''      #    "

"""

def getHandleAndVersion(gseObj, opts):
    """\
Return strings containing a dataset identifier (or *handle*) and version.   Value
is derived from ``--handle=`` (``--version``) value, if present.  Otherwise, 
`dataset_handle` and `dataset_version` functions are invoked.  If these are empty strings,
the hard defaults are ``dataset`` and ``1.0``.
"""
    handle = opts.handle if opts.handle else (opts.dataset_handle(gseObj) if opts.dataset_handle(gseObj) else 'dataset')
    version = opts.version if opts.version else (opts.dataset_version(gseObj) if opts.dataset_version(gseObj) else '1.0')
    return handle, version


def configure(cfgObj):
    """\
Addes configuration elements to an existing *ConfigParser* object `cfgObj`.
"""
    cfgObj.add_option('dataset_handle')
    cfgObj.add_option('dataset_fullname')
    cfgObj.add_option('dataset_version')
    cfgObj.add_option('dataset_description')
    cfgObj.add_option('dataset_platform_type')
    cfgObj.add_option('dataset_platform_details')
    cfgObj.add_option('dataset_pubmed_id')
    cfgObj.add_option('dataset_excluded')
    cfgObj.add_option('dataset_species_id')
    cfgObj.add_option('dataset_storage_type')

    cfgObj.add_option('dataset_metadata_axis')
    cfgObj.add_option('dataset_metadata_level')
    cfgObj.add_option('dataset_metadata_repository_id')
    cfgObj.add_option('dataset_metadata_name')
    cfgObj.add_option('dataset_metadata_description')

    cfgObj.add_option('sample_metadata_sample_id')
    cfgObj.add_option('sample_metadata_level')
    cfgObj.add_option('sample_metadata_name')
    cfgObj.add_option('sample_metadata_value')

    cfgObj.add_file(content=default_cfg, type='py')


def createMatricksPickles(gseObj, opts, ctLevel=1, sampleLevel=0):
    """\
Creates the *SampleSignalProfiles* and *CelltypeSignalProfiles* pickled `Matricks`
files used by `Guide`. 

The files will be named ``SampleSignalProfile.``*handle*``.pickled`` and
``CelltypeSignalProfile.``*handle*``.pickled``.   The grouping used for the
celltype file is determined by ctLevel.  Samples are "grouped" by level 0, but this can
be changed by specifying `sampleLevel`.   
"""
    samples = gseObj.mean(level=sampleLevel)
    celltypes = gseObj.mean(level=ctLevel)

    s_list = list(samples.itertuples()) 
    s_list.insert(0, [ 'probeId' ] + list(samples.columns))

    c_list = list(celltypes.itertuples())
    c_list.insert(0, ['probeId' ] + list(celltypes.columns))

    sm = Matricks(s_list)
    cm = Matricks(c_list)

    handle, version = getHandleAndVersion(gseObj, opts)

    cPickle.dump(sm, open('SampleSignalProfiles.{0}.{1}.pickled'.format(handle, version), 'w'), -1)
    cPickle.dump(cm, open('CelltypeSignalProfiles.{0}.{1}.pickled'.format(handle, version), 'w'), -1)


def createDDL(gseObj, opts):
    """\
Emit DDL for populating the ``dataset``, ``dataset_metadata`` and ``sample_metadata`` tables in the *guide* database.
"""
    handle, version = getHandleAndVersion(gseObj, opts)

    ddl_file = open('{0}.{1}.DDL.sql'.format(handle, version), 'w')
    
    ddl_file.write("-- dataset --\n")
    # handle TEXT NOT NULL, 
    # fullname TEXT, 
    # varsion TEXT, 
    # description TEXT NOT NULL, 
    # platform_type TEXT NOT NULL CHECK (platform_type in ('microarray', 'rnaseq', 'ngs')),
    # platform_details TEXT NOT NULL, 
    # pubmed_id TEXT, 
    # excluded BOOLEAN, 
    # species_id INTEGER, 
    # storage_type TEXT CHECK (storage_type in ('hdf5', 'h5', 'matricks', 'txt', 'tsv', 'csv', 'xl', 'xlxs')), 
    ddl_file.write("""INSERT INTO datasets VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', {8}, '{9}');\n\n""".format(
    	handle,
	opts.dataset_fullname(gseObj).replace("'", "''"),
	version,
	opts.dataset_description(gseObj).replace("'", "''"),
	opts.dataset_platform_type(gseObj),
	opts.dataset_platform_details(gseObj).replace("'", "''"),
	opts.dataset_pubmed_id(gseObj),
	opts.dataset_excluded(gseObj),
	opts.dataset_species_id(gseObj), 
	opts.dataset_storage_type(gseObj)))


    ddl_file.write("-- dataset_metadata --\n")

    for lev, vals in sorted(gseObj.level_map.items(), key=lambda x: x[1]['level']):
        ddl_file.write("""INSERT INTO dataset_metadata VALUES ('{0}', 1, {1}, null, '{2}', '');\n""".format(
            opts.dataset_handle(gseObj), vals['level'], lev))

    ddl_file.write("-- sample_metadata --\n")
    all_samples = list(gseObj.metadata.samples)
    for samp in all_samples:
        ddl_file.write("""INSERT INTO sample_metadata VALUES ('{0}', '{1}', {2}, '{3}', '{4}');\n""".format(
                handle, opts.sample_metadata_sample_id(samp), 0, 'sample_id', opts.sample_metadata_sample_id(samp)))
        for k, v in samp.metadata_levels.items():
            ddl_file.write("""INSERT INTO sample_metadata VALUES ('{0}', '{1}', {2}, '{3}', '{4}');\n""".format(
                handle, opts.sample_metadata_sample_id(samp), gseObj.level_map[k]['level'], k, v))

    ddl_file.close()
              
    
def main():
    config = Configurator(use_msg="usage: %prog [options] [pickled_GSESeries_file]",
                          config_files=('--magma2-config',))

    config.add_option("--input", "-i", action='store', type='string', default='',
                      help="Input file containing the pickled GEOSeries object, created with gse")

    config.add_option("--output", "-o", action='store', type='string', default='',
                      help="Output file in TSV format.")

    config.add_option("--group-by", "-g", action='store', type='string', default='1',
                      help="group columns at the specified index level")

    config.add_option('--handle', '-H', action='store', type='string', default='',
                       help='name of dataset to use in naming the output files, and in the DDL for magma2 metadata')

    config.add_option('--template', '-t', action='store_true', default=False,
                       help='prints out a template for a configuration file.')

    config.add_option('--version', action='store', type='string', default='',
                       help='name of dataset to use in naming the output files, and in the DDL for magma2 metadata')

    config.add_option('--verbose', '-v', action='store_true', help='turn on verbose logging', default=False)
    config.add_option('--debug', '-d', default='WARN', help='debug level (DEBUG, INFO, [WARN], ERROR, CRITICAL, FATAL)')

    # Add config file params:
    configure(config)

    opts, args = config()

    log.setLevel(log_levels.get(opts.debug[:3].upper(), logging.WARN))

    log.debug('configuration processed:  opts={0}, args={1}'.format(opts, args))

    # Print a template?
    if opts.template:

        if opts.handle:
            print default_cfg.replace('go.metadata.geo_accession', "'{0}'".format(opts.handle))
        else:
            print default_cfg
        sys.exit(0)

    # Open and read in the series matrix file
    # Pickle and save the resulting object.
    if opts.input != '':
        gmd = cPickle.load(opts.input)

    elif len(args) == 0 :
        config.print_help()
        sys.exit(1)

    elif args[0] == '-':
        gmd = cPickle.load(sys.stdin)

    else:
        gmd = cPickle.load(open(args[0]))

    # Figure out which column index level will be used for "celltype" grouping.
    try:
        lev = int(opts.group_by)
    except:
        lev = opts.group_by
            
    if lev not in gmd.column_index_levels and lev not in range(len(gmd.column_index_levels)):
        raise ValueError('Invalid column index level specified: "{0}"'.format(lev))

    # Emit the pickled matricks files
    #createMatricksPickles(gmd, opts, ctLevel=lev)   # REPLACE THIS WITH createPandasHDF5
    createDDL(gmd, opts)



if __name__ == '__main__':  main()
