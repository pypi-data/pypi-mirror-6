#!/usr/bin/env python
'''
See help(Pipeline) for details on configuring a Pipeline.

This software is released under an MIT/X11 open source license.

Copyright 2012-2013 Diffeo, Inc.

usage:
    python -m streamcorpus_pipeline.run ...
'''
from __future__ import absolute_import
import os
import sys
import copy
import json
import time
import importlib
from streamcorpus_pipeline._exceptions import ConfigurationError
from streamcorpus_pipeline._pipeline import Pipeline
from streamcorpus_pipeline._logging import logger, reset_log_level

from streamcorpus_pipeline.config import load_layered_configs, config_to_string

def make_absolute_paths( config ):
    if not 'streamcorpus_pipeline' in config:
        logger.critical('bad config: %r', config)
        raise ConfigurationError('missing "streamcorpus_pipeline" from config')
    ## remove the root_path, so it does not get extended itself
    root_path = config['streamcorpus_pipeline'].pop('root_path', None)
    if not root_path:
        root_path = os.getcwd()

    if not root_path.startswith('/'):
        root_path = os.path.join( os.getcwd(), root_path )

    def recursive_abs_path( sub_config, root_path ):
        for key, val in sub_config.items():
            if isinstance(val, basestring):
                if key.endswith('path'):
                    ## we have a path... is it already absolute?
                    if not val.startswith('/'):
                        ## make the path absolute
                        sub_config[key] = os.path.join(root_path, val)

            elif isinstance(val, dict):
                recursive_abs_path( val, root_path )

    recursive_abs_path( config, root_path )

    ## put the root_path back
    config['root_path'] = root_path

def make_hash(obj):
    '''
    Makes a hash from a dictionary, list, tuple or set to any level,
    that contains only other hashable types (including any lists,
    tuples, sets, and dictionaries).  See second answer (not the
    accepted answer):
    http://stackoverflow.com/questions/5884066/hashing-a-python-dictionary
    '''
    if isinstance(obj, (set, tuple, list)):
        return tuple([make_hash(e) for e in obj])
    elif not isinstance(obj, dict):
        return hash(obj)

    new_obj = copy.deepcopy(obj)
    for k, v in new_obj.items():
        ## call self recursively
        new_obj[k] = make_hash(v)

    return hash(tuple(frozenset(new_obj.items())))

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description=Pipeline.__doc__,
        usage='python -m streamcorpus.pipeline.run config.yaml')
    parser.add_argument('-i', '--input', action='append', 
                        help='file paths to input instead of reading from stdin')
    parser.add_argument('config', metavar='config.yaml', nargs='+',
                        help='configuration parameters for a pipeline run. many config yaml files may be specified, later values win.')
    args = parser.parse_args()

    config = load_layered_configs(args.config)
    if len(args.config) > 1:
        print '# net config:'
        print config_to_string(config)

    make_absolute_paths(config)

    pipeline_config = config['streamcorpus_pipeline']

    tq_name = pipeline_config.get('task_queue', 'no-task-queue')
    tq_conf = pipeline_config.get(tq_name)
    if tq_conf is None:
        tq_conf = {}
    ## put info about the whole config in the extractor's config
    tq_conf['config_hash'] = make_hash(config)
    tq_conf['config_json'] = json.dumps(config)
    pipeline_config[tq_name] = tq_conf

    ## setup loggers
    reset_log_level( pipeline_config.get('log_level', 'DEBUG') )

    logger.warn('running config: %s = %s' % (
            tq_conf['config_hash'], args.config))

    logger.info(json.dumps(config, indent=4, sort_keys=True))

    ## Load modules
    # This is a method of using settings in yaml configs to load plugins.
    die = False
    for pathstr in pipeline_config.get('pythonpath', {}).itervalues():
        if pathstr not in sys.path:
            sys.path.append(pathstr)
    for modname in pipeline_config.get('setup_modules', {}).itervalues():
        try:
            m = importlib.import_module(modname)
            if not m:
                logger.error('could not load module %r', modname)
                die = True
                continue
            if hasattr(m, 'setup'):
                m.setup()
                logger.debug('loaded and setup %r', modname)
            else:
                logger.debug('loaded %r', modname)
        except:
            logger.error('error loading and initting module %r', modname, exc_info=True)
            die = True
    if die:
        sys.exit(1)
        return

    pipeline = Pipeline(config)

    if args.input:
        input_paths = args.input
    else:
        input_paths = sys.stdin

    for i_str in input_paths:
        work_unit = SimpleWorkUnit(i_str.strip())
        work_unit.data['start_chunk_time'] = time.time()
        work_unit.data['start_count'] = 0
        pipeline._process_task(work_unit)

class SimpleWorkUnit(object):
    '''partially duck-typed rejester.WorkUnit that wraps strings from
    stdin and provides only the methods used by the Pipeline

    '''
    def __init__(self, i_str):
        self.key = i_str
        self.data = dict()

    def update(self):
        ## a real WorkUnit would send self.data to the registry and
        ## renew the lease time
        pass

    def terminate(self):
        pass



if __name__ == '__main__':
    main()
