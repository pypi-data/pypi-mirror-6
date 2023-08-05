"""Miscellaneous tools."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"


def indented(string, level=1, size=4):
# TODO: (Python 3)
#def indented(string, level=1, *, size=4):
    """Indent a string.

    :param int level:
        The number of indents to apply.

    :param int size:
        The size of each indent.

    :rtype: :obj:`str`

    :raise ValueError:
        Raised if *level* or *size* is negative.

    """
    if level < 0:
        raise ValueError('level must be nonnegative')
    if size < 0:
        raise ValueError('size must be nonnegative')
    if level == 0 or size == 0:
        return string[:]
    return '\n'.join(' ' * size * level + line
                     for line in string.split('\n'))


def split_blocks(string, joinlines=True):
    """Split a string into blocks.

    If *joinlines* is true, then the lines within each block are joined with
    :func:`strip_and_cleanjoin`.

    :param str string:
        A string.

    :param bool joinlines:
        Whether to join the lines within each block.

    :rtype: [:obj:`str`]

    """
    blocks = []
    lines = string.split('\n')
    joinfunc = strip_and_cleanjoin if joinlines else '\n'.join
    blocklines = []
    for line in lines:
        line = line.strip()
        if line:
            blocklines.append(line)
        else:
            if blocklines:
                blocks.append(joinfunc(*blocklines))
                blocklines = []
    if blocklines:
        blocks.append(joinfunc(*blocklines))
    return blocks


def strip_and_cleanjoin(*strings):
    """
    Strip some strings and join them with numbers of spaces that respect
    punctuation.

    .. note:: **TODOC:**
        example

    :param strings:
        Strings.
    :type strings: ~[:obj:`str`]

    :rtype: :obj:`str`

    """
    strings_new = []
    punctuation_by_spaces = {(0, 0): ['--', '---'],
                             (0, 1): [',', ';', ':'],
                             (0, 2): ['.', '!', '?'],
                             (1, 1): ['=', '+', '-', '*', '/', '&', '|', '<',
                                      '>', '~', '\\'],
                             }
    prevstring_endspaces = 0
    for i, string in enumerate(strings):
        string = string.strip()

        # prepend spaces if previous string didn't have enough
        if i == 0:
            pass
        else:
            for startspaces, endspaces in sorted(punctuation_by_spaces.keys()):
                if prevstring_endspaces < startspaces \
                       and any(string.startswith(mark)
                               for mark
                               in punctuation_by_spaces[(startspaces,
                                                         endspaces)]):
                    string = ' ' * (startspaces - prevstring_endspaces) \
                             + string

        # append spaces if string is terminated by a punctuation mark that
        #     demands them
        if i == len(strings) - 1:
            prevstring_endspaces = 0
        else:
            for startspaces, endspaces in sorted(punctuation_by_spaces.keys()):
                if any(string.endswith(mark)
                       for mark in punctuation_by_spaces[(startspaces,
                                                          endspaces)]):
                    prevstring_endspaces = endspaces
                    string += ' ' * endspaces

        strings_new.append(string)
    return ''.join(strings_new)


def stripped_lines(string, chars=' \t', tabsize=8):
    """
    Strip the greatest amount of leading characters that is present in all
    lines of a string.

    In other words, move the left margin as close as possible to the
    non-*chars* content of *string*.

    For example, if *chars* contains the space character, then this
    *string* ::

        '''
            Fancy Heading

            data:
                function: foo
                widgets: 42
        '''

    will be returned like this::

        '''
        Fancy Heading

        data:
            function: foo
            widgets: 42
        '''

    .. note:: **TODO:**
        implement this:
            Tab characters are interpreted as having a size of *tabsize*.
            If the number of characters to strip is not a multiple of
            *tabsize*, then tabs that span the new margin are converted to
            spaces and stripped accordingly.

    :param str string:
        A string to be stripped.

    :param str chars:
        A string of characters to strip.

    :param int tabsize:
        The size of a tab character.

    :rtype: :obj:`str`

    """
    lines = string.split('\n')
    strip_count = None
    def chars_count(line):
        for i, char in enumerate(line):
            if char not in chars:
                return i
    for line in lines:
        count = chars_count(line)
        if strip_count is None:
            strip_count = count
        else:
            strip_count = min(strip_count, count)
        if strip_count == 0:
            return lines[:]
    return '\n'.join(line[strip_count:] for line in lines)
