#!/usr/bin/env python

"""
Usage:
    doctpl -t <template> <file>...
    doctpl -l|--list
    doctpl -p|--position

Options:
    -t <template>   init files with template.
    -l --list       list all avaliable templates.
    -p --position   print absolute path of where templates exists.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from docopt import docopt
from doctpl.bussiness import ToolSet


def main():
    arguments = docopt(
        __doc__,
        version='0.1.1',
    )

    toolset = ToolSet()

    if arguments['<file>']:
        # copy template
        template_name = arguments['-t']
        targets = arguments['<file>']
        for target in targets:
            try:
                toolset.make_copy(target, template_name)
            except Exception as e:
                info = str(e)
                print(info)

    elif arguments['--list']:
        templates = list(toolset.avaliable_templates)
        if not templates:
            print('No Template Exist, Place Your Templates In ~/.doctpl')
        else:
            print('\t'.join(templates))

    elif arguments['--position']:
        print(toolset.dir_abs_path)


if __name__ == '__main__':
    main()
