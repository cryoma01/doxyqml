#!/usr/bin/env python
import logging
import os
import sys
from optparse import OptionParser

from qmlclass import QmlClass, fill_qml_class, ParserError
from lexer import Lexer


def coord_for_idx(text, idx):
    head, sep, tail = text[:idx].rpartition("\n")
    if sep == "\n":
        row = head.count("\n") + 2
    else:
        row = 1
        col = len(tail) + 1
        return row, col


def line_for_idx(text, idx):
    bol = text.rfind("\n", 0, idx)
    if bol == -1:
        bol = 0
    eol = text.find("\n", idx)
    return text[bol:eol]


def main():
    parser = OptionParser("usage: %prog [options] <path/to/File.qml>")
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="Log debug info to stderr")
    (options, args) = parser.parse_args()
    name = args[0]

    lexer = Lexer(options)
    text = open(name).read()

    try:
        lexer.tokenize(text)
    except LexerError, exc:
        logging.error("Failed to tokenize %s" % name)
        row, col = coord_for_idx(text, exc.idx)
        line = line_for_idx(text, exc.idx)
        msg = line + "\n" + "-" * (col - 1) + "^"
        logging.error("Lexer error line %d: %s\n%s", row, exc, msg)

    if options.debug:
        for type_, value in lexer.tokens:
            print "#### %s ####" % type_
            print value

    classname = os.path.basename(name).split(".")[0]
    qml_class = QmlClass(classname)

    try:
        fill_qml_class(qml_class, lexer.tokens)
    except ParserError, exc:
        logging.error("Failed to parse %s" % name)
        row, col = coord_for_idx(text, exc.token.idx)
        line = line_for_idx(text, exc.token.idx)
        msg = line + "\n" + "-" * (col - 1) + "^"
        logging.error("Lexer error line %d: %s\n%s", row, exc, msg)
        raise

    print qml_class

    return 0


if __name__ == "__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
