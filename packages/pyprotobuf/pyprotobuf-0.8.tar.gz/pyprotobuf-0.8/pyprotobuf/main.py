#!/bin/python
import sys
import pkg_resources
import os
import logging
import argparse
from pyprotobuf.compiler import Compiler


ENTRYPOINT = 'pyprotobuf.generators'

GENERATORS = {
    'closure': 'pyprotobuf.generators.closurelib',
    'go': 'pyprotobuf.generators.go',
    'python': 'pyprotobuf.generators.protorpc',
    'externs':  'pyprotobuf.generators.externs'
}

def import_generator(module_name):
    try:
        module = __import__(module_name, globals(), locals(), ['__generator__'], -1)
        return module.__generator__
    except ImportError:
        return None

def main(args=None):
    
    generators = {}

    # include default generators
    for name, module in GENERATORS.items():
        generators[name] = getattr(module, '__generator__', None)

    # search for entrypoints defined in setup.py or extended with plugins
    # generator modules are defined in [pyprotobuf.generators]
    # generator module must have a __generator__ symbol pointing to a generator class
    for entrypoint in pkg_resources.iter_entry_points(ENTRYPOINT):
         module = entrypoint.load()
         generators[entrypoint.name] = getattr(module, '__generator__', None)

    generator_names = generators.keys()
    
    if args is None:
        parser = argparse.ArgumentParser()
        parser.add_argument('--format', '-f', choices=generator_names, dest='format')
        parser.add_argument('--debug', '-d', default=False, action='store_true')
        parser.add_argument('--generator', default=None, help="Manually specify a generator module.")
        parser.add_argument('paths', nargs="+")
        args = parser.parse_args()

    level = logging.INFO

    if getattr(args, 'debug'):
        level = logging.DEBUG

    logging.basicConfig(level=level)


    overrride_generator_name = getattr(args, 'generator', None)

    if overrride_generator_name is not None:
        generator_name = overrride_generator_name
    else:
        # check built-in generators
        generator_name = args.format

        if generator_name not in GENERATORS:
            print ('Wrong format! Expected  {0} Got:'.format(', '.join(generator_names)))
            sys.exit(-1)

        generator_name = GENERATORS[generator_name]

    generator_class = import_generator(generator_name)

    if generator_class is None:
        raise Exception("Invalid generator: %s" % generator_name)

    out = []
    for path in args.paths:
       path = os.path.abspath(path)
       string = open(path).read()

       compiler = Compiler(generator_class)
       compiler.generate_header = True
       out.append(compiler.compile_string(path, string))
    
    return ''.join(out)
    
def parse_and_generate(string, path, generator_class):
    compiler = Compiler(generator_class)
    return compiler.compile_string(path, string)

 
def _main():
    sys.stdout.write(main())
    
if __name__ == '__main__':
    _main()
