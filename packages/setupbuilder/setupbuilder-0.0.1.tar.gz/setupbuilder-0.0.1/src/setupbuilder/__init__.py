# -*- coding: utf-8 -*-
import os
import sys
import zlib
import base64
import argparse

__version__ = '0.0.1'

__templates = {
    'setup.py': [
        b'eNplksGO3CAMhu88BVJVQVaZzB6rkXLYwx723GNVISYhGXYJUONUG6367iU4mTYt'
        b'ORDszz829id+ejjxLvTWjxc+43D6slqYnWIA5GlJ+29IjA0QJp4MzhFDcInv1Gqp'
        b'+WB9r6Lu3vRoErEEOHvdUdrUFPrZGcZYbwbu9WRkdWE8L8hS4Ln4LCOEV9OhWr1V'
        b'Ehv700Cywe94uVn1FnibE2yixluTT0VxP+trWnep1GCdUaqqKBS6fwJfg/Xyrlhz'
        b'kRFRMaKXDbI+GUD5WO8CpIawUEbrouqy8qFaSXUSb947E5G/FOAZIMCf8P0NHpv8'
        b'CcJdMv8Bo0GNCJLkc75Kbc+jlKj3+FwAK0XJEr8R7f0h62Jec2spQTL0JnVgI66s'
        b'+JoLcSb9bWwEcS74UR3gzaFnvAVoxVPZywUHjzKTtu7uj/PV2Y4X48bNkN03xHg5'
        b'n+MSbROXjPomwHi+z0ceDaK3wVtb0n4IcaH2/To4U3uYUUkdJiQ3FrVzCsyP2UJG'
        b'v32vWcV+A3hP/nE='
    ],
    'MANIFEST.in': [],
    'README.txt': [],
    'LICENSE.txt': [],
    'AUTORS.txt': [],
    'docs': {
        'README.txt': []
    },
    'tests': {
        'README.txt': []
    },
    'src': {
        '%(project)s': {
            '__init__.py': [
                b'eNpTVtDV0lVIzk/JzEu3UigtSdO1AIlwccXHl6UWFWfm58XHK9gqqBvoAaE6FwAy'
                b'+Axl'
            ]
        }
    }
}


def ArgumentParser():
    parse = argparse.ArgumentParser()

    parse.add_argument(
        'project'
    )

    parse.add_argument(
        '--with-docs',
        help='',
        dest='with_docs',
        action='store_true'
    )

    parse.add_argument(
        '--with-tests',
        help='',
        dest='with_tests',
        action='store_true'
    )

    return parse


def data_compress():
    if len(sys.argv) > 1:
        for filepath in sys.argv[1:]:
            with open(filepath) as fd:
                data = base64.b64encode(zlib.compress(fd.read().encode(), 9))
                size = len(data)

                for x in range(64, size + 64, 64):
                    print(data[x - 64: x])

    else:
        print('You need specify one file or more for compress')


def generate_file(filepath, template, opts):
    if os.path.exists(filepath) and os.path.isfile(filepath) is False:
        raise Exception('The %s doest not is file.' % filepath)
    elif os.path.exists(filepath) is False:
        with open(filepath, 'w') as fd:
            try:
                data = zlib.decompress(base64.b64decode(b''.join(template)))
            except:
                data = b''
            finally:
                fd.write(data.decode() % opts)


def generate_directory(basepath, template, opts):
    if os.path.exists(basepath) and os.path.isdir(basepath) is False:
        raise Exception('The %s doest not is directory.' % basepath)
    elif os.path.exists(basepath) is False:
        os.mkdir(basepath)

    cdir = os.getcwd()
    os.chdir(basepath)

    for name, tpl in template.items():
        name = name % opts
        path = os.path.join(basepath, name)

        if isinstance(tpl, dict) is True:
            generate_directory(path, tpl, opts)
        else:
            generate_file(path, tpl, opts)

    os.chdir(cdir)


def main():
    parse = ArgumentParser()

    opts = dict(parse.parse_args().__dict__)

    project_dir = os.path.abspath(opts.get('project'))
    project_name = project_dir.split(os.path.sep)[-1]

    opts.update(project_name=project_name)

    tpl = __templates.copy()
    if opts.get('with_docs', False) is False:
        tpl.pop('docs')
    if opts.get('with_tests', False) is False:
        tpl.pop('tests')

    generate_directory(project_dir, tpl, opts)

if __name__ == '__main__':
    main()
