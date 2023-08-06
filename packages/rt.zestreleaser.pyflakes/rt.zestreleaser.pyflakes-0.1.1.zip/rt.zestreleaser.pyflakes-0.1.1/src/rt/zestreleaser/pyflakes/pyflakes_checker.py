# -*- coding: utf-8 -*-

import os
import sys
import fnmatch
import zest.releaser.utils
from StringIO import StringIO

from pyflakes.api import checkPath
from pyflakes.reporter import Reporter


def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def check(data):
    # data is {'tag_already_exists': False, 'version': ..., 'workingdir': ..., 'name': ...},

    python_sources = find('*.py', data['workingdir'])
    if not python_sources:
        return

    reporter = Reporter(StringIO(), StringIO())
    
    for source in python_sources:
        checkPath(source, reporter)

    output = reporter._stdout.getvalue()

    if not output or not zest.releaser.utils.ask('You have Pyflakes warning. Do you want to see them?'):
        return

    print '\n'
    print output
    
    if not zest.releaser.utils.ask('Do you want to continue anyway?', default=False):
        print "Fix your warnings and retry"
        sys.exit(0)
