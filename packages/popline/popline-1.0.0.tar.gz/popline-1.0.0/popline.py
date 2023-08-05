"""Popline pops the first line off a file."""

import sys


def main():
    """Main method."""
    if len(sys.argv) != 2:
        raise Exception

    filename = sys.argv[1]
    with open(filename, 'r') as fp:
        lines = fp.read()

    lines = lines.split("\n")

    if len(lines) > 0:
        first, rest = lines[0], lines[1:]

        with open(filename, 'w') as fp:
            fp.write("\n".join(rest))

        print first

if __name__ == '__main__':
    main()
