# -*- coding: utf-8 -*-

import os
from optparse import OptionParser

import instructions

__version__ = '0.1.0'

CWD = ''


def do_build(location):
    """
    Configures a server based on a dockerfile repo.

    Args:
        location (string): directory that the dockerfile exists in.
    """
    filename = os.path.join(location, 'Dockerfile')
    with open(filename, 'rU') as f:
        # switch to the dockerfile directory before we do anything, folks
        # ususally use relative directory paths in dockerfiles. If they use
        # CHDIR, it'll change it again.
        os.chdir(location)

        # keep track of the step
        step = 0

        # buffer multi-line commands
        buf = ''
        buf_instruction = None

        for line in f:
            line = line.strip()
            # if there's a line separator at the end of the line, store it, and
            # the instruction, and move on.
            if line[-1:] == '\\':
                if buf != '':
                    buf += line + "\n"
                else:
                    buf = ' '.join(line.split(' ')[1:]) + "\n"

                if not buf_instruction:
                    buf_instruction = line.split(' ')[0].lower()
                continue

            if buf:
                # if there are buffered commands,
                arguments = buf + line
                instruction = buf_instruction
                buf = ''
                buf_instruction = None
            else:
                parts = line.split(' ')
                instruction = parts[0].lower()
                arguments = ' '.join(parts[1:])

            if instruction.strip() in ['', '#']:
                # pass by newlines and comments, don't even bother looking them
                # up.
                continue

            method = getattr(instructions, 'instruction_%s' % instruction,
                             False)
            if not method:
                print '# Skipping unknown instruction %s\n' % instruction
                continue

            step += 1
            print 'Step %s : %s %s\n' % (step, instruction, arguments)
            result = method(arguments)
            if not result:
                print '---> failed.'

        print 'Successfully built %s\n' % 'Server'


def main():
    usage = 'usage: dockerstack [options] path_to_dockerfile'
    parser = OptionParser(usage)

    parser.add_option('-d', '--debug', dest='debug', action='store_true')

    options, args = parser.parse_args()

    do_build(args[0])


if __name__ == '__main__':
    main()
