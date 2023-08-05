#!coding:utf-8

"""
This software is licensed under Apache License v2.
For more information see LICENSE file.
"""

from pyparsing import (
    Word, alphanums, Forward, OneOrMore, ZeroOrMore, Literal, nums, LineEnd,
    oneOf, printables
)
__all__ = ('TokensList', 'RtfParseError', 'merge_structure_libreoffice',
           'merge_structure_word', 'create_structure', 'make_rtf_tokens'
           'normalize_rtf', )


class TokensList(list):
    def __init__(self, iterable=None):
        if iterable is None:
            iterable = []
        super(TokensList, self).__init__(iterable)
        self.parent = None


class RtfParseError(Exception):
    pass

RTLCH_KEY_ORDER = ['\\rtlch \\ltrch\\loch']
temp_key = ['\\rtlch \\ltrch\\loch', '\n', '#']
INSRSID = '\\insrsid'
FCS1 = ['\\rtlch\\fcs1', '\\af0', '\\ltrch\\fcs0']

insrsid_codes = ((
    Literal('\\lang') + Word(nums, exact=4) +
    Literal('\\langfe') + Word(nums, exact=4) +
    Literal('\\langnp') + Word(nums, exact=4) +
    Literal('\\insrsid') + Word(nums, exact=7)
) | (
    Literal('\\insrsid') + Word(nums, exact=7)
))

control_codes = ZeroOrMore(LineEnd()) + (
    Literal('\\rtlch \\ltrch\\loch') +
    LineEnd() +
    oneOf(list(printables)+[' ']).leaveWhitespace() +
    ZeroOrMore(Word(alphanums + ' \\\'#;*'))
) | (
    #'\\rtlch\\fcs1', '\\af0', '\\ltrch\\fcs0'
    Literal(FCS1) +
    ZeroOrMore(LineEnd()) +
    insrsid_codes +
    ZeroOrMore(LineEnd()) +
    oneOf(list(printables)+[' ']).leaveWhitespace() +
    ZeroOrMore(Word(alphanums + ' \\\'#;*'))
) | (Word('\\', alphanums + '*;\\\'') + ZeroOrMore(LineEnd()))

inner_properties = OneOrMore(control_codes)
start = Literal('{')
end = Literal('}') | (Literal(';') + Literal('}'))
paragraph = Literal('\\par') + Word(alphanums + '\\\'#;*')
paragraph.setName('paragraph')
paragraph.setDebug()
text_ = ZeroOrMore(Word(alphanums + '\\\'#;* \n().,:/!?'))
text_.setName('text_')
document = Forward()
header = OneOrMore(control_codes | document)
header.setName('header')
document <<= (
    start +
    header +
    ZeroOrMore(Literal('\\par')) +
    text_ +
    ZeroOrMore(document) | end
)


def merge_structure_libreoffice(structure):
    result = TokensList()
    first_rtlch_node = None
    counter = 0
    for c, v in enumerate(structure):
        if isinstance(v, TokensList):
            flag = True
            a = v[:1]
            if v[:1] == RTLCH_KEY_ORDER:
                flag = False
                if first_rtlch_node is None:
                    first_rtlch_node = v
                    result.append(v)
                else:
                    first_rtlch_node[-1] = first_rtlch_node[-1] + v[2]
                    first_rtlch_node.extend(v[3:])
                    # Не добавляем в result значение
                    #tree_ = tree_[:counter] + tree_[counter + 1:]
                    #del tree_[counter + 1]
                    counter -= 1
            else:
                first_rtlch_node = None
            if flag:
                result.append(merge_structure_libreoffice(v))
        else:
            first_rtlch_node = None
            result.append(v)
        counter += 1
    return result


def merge_structure_word(structure):
    result = TokensList()
    first_fsc1_node = None
    counter = 0
    insrsid_index = 3
    for c, v in enumerate(structure):
        if isinstance(v, TokensList):
            flag = True
            a = v[:1]
            if v[:3] == FCS1:
                ii = insrsid_index
                if v[3] == '\n':
                    ii = 4
                if INSRSID not in v[ii]:
                    counter += 1
                    continue
                flag = False
                if first_fsc1_node is None:
                    first_fsc1_node = TokensList(v[4:])
                    result.append(first_fsc1_node)
                else:
                    first_fsc1_node.extend(v[insrsid_index + 1:])
                    # no append to result
                    counter -= 1
            else:
                first_fsc1_node = None
            if flag:
                result.append(merge_structure_word(v))
        else:
            first_fsc1_node = None
            result.append(v)
        counter += 1
    return result


def create_structure(parse_results):
    start_tree = TokensList()
    tree = start_tree
    for counter, token in enumerate(parse_results):
        if token == '{':
            parent = tree
            tree = TokensList()
            tree.parent = parent
            parent.append(tree)
        elif token == '}':
            up_tree = tree.parent
            tree = up_tree
        else:
            tree.append(token)

    return start_tree


def make_rtf_tokens(tree, list_tokens=None):
    if list_tokens is None:
        list_tokens = []
    first = True
    for v in tree:
        if isinstance(v, TokensList):
            list_tokens.append('{')
            make_rtf_tokens(v, list_tokens)
            list_tokens.append('}')
        else:
            list_tokens.append((' ' if not first else '') + v)
        first = False
    return list_tokens


def normalize_rtf(filepath):
    with open(filepath) as rtf_file_read:
        rtf_read_string = rtf_file_read.read()
    if not rtf_read_string.startswith('{\\rtf1'):
        raise RtfParseError('This is not an RTF file')
    parse_results = document.parseString(rtf_read_string, parseAll=True)
    structure = create_structure(parse_results)
    structure = merge_structure_libreoffice(structure)
    structure = merge_structure_word(structure)
    return ''.join(make_rtf_tokens(structure))

if __name__ == '__main__':
    print normalize_rtf('../tests/test_data/test_libreoffice.rtf')
    print normalize_rtf('../tests/test_data/test_word2003.rtf')