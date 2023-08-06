# fsq -- a python library for manipulating and introspecting FSQ queues
# @author: Matthew Story <matt.story@axial.net>
#
# fsq/construct.py -- provides name construction functions: construct,
#                     deconstruct, encode, decode
#
#     fsq is all unicode internally, if you pass in strings,
#     they will be explicitly coerced to unicode.
#
# This software is for POSIX compliant systems only.
import errno

from . import FSQMalformedEntryError, constants as _c, encode, decode
from .internal import coerce_unicode, delimiter_encodeseq

####### EXPOSED METHODS #######
def construct(args):
    '''Construct a queue-name from a set of arguments and a delimiter'''
    # make everything unicode
    name = u''
    delimiter, encodeseq = delimiter_encodeseq(_c.FSQ_DELIMITER,
                                               _c.FSQ_ENCODE, _c.FSQ_CHARSET)
    if len(args) == 0:
        return delimiter
    for arg in args:
        name = delimiter.join([ name,
                                encode(coerce_unicode(arg, _c.FSQ_CHARSET),
                                delimiter=delimiter, encodeseq=encodeseq)])

    return name

def deconstruct(name):
    '''Deconstruct a queue-name to a set of arguments'''
    name = coerce_unicode(name, _c.FSQ_CHARSET)
    new_arg = sep = u''
    args = []
    # can't get delimiter, if string is empty
    if 1 > len(name):
        raise FSQMalformedEntryError(errno.EINVAL, u'cannot derive delimiter'\
                                     u'from: {0}'.format(name))

    delimiter, encodeseq = delimiter_encodeseq(name[0], _c.FSQ_ENCODE,
                                               _c.FSQ_CHARSET)
    # edge case, no args
    if 1 == len(name):
        return delimiter, args

    # normal case
    encoding_trg = sep
    for c in name[1:]:
        if 3 == len(encoding_trg):
            encoding_trg = sep
        if c == encodeseq or len(encoding_trg):
            encoding_trg = sep.join([encoding_trg, c])
        elif c == delimiter:
            # at delimiter, append and reset working arg
            args.append(decode(new_arg, delimiter=delimiter,
                               encodeseq=encodeseq))
            new_arg = sep
            continue

        new_arg = sep.join([new_arg, c])

    # append our last arg
    args.append(decode(new_arg, delimiter=delimiter, encodeseq=encodeseq))
    return delimiter, args
