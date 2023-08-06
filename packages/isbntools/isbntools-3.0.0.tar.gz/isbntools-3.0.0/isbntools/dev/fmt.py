# -*- coding: utf-8 -*-

import re
import uuid
from string import Template


bibtex = r"""@book{$ISBN,
  title={$Title},
  author={$AUTHORS},
  isbn={$ISBN},
  year={$Year},
  publisher={$Publisher}
}"""

endnote = r"""%0 Book
%T $Title
%A $AUTHORS
%@ $ISBN
%D $Year
%I $Publisher """

refworks = r"""TY  - BOOK
T1  - $Title
A1  - $AUTHORS
SN  - $ISBN
UR  -
Y1  - $Year
PB  - $Publisher
ER """

msword = r'''<b:Source xmlns:b="http://schemas.microsoft.com/office/'''\
         r'''word/2004/10/bibliography">
<b:Tag>$uid</b:Tag>
<b:SourceType>Book</b:SourceType>
<b:Author>
<b:NameList>$AUTHORS
</b:NameList>
</b:Author>
<b:Title>$Title</b:Title>
<b:Year>$Year</b:Year>
<b:City></b:City>
<b:Publisher>$Publisher</b:Publisher>
</b:Source>'''

labels = r"""Type:      BOOK
Title:     $Title
Author:    $AUTHORS
ISBN:      $ISBN
Year:      $Year
Publisher: $Publisher"""

templates = {'labels': labels, 'bibtex': bibtex,
             'endnote': endnote, 'refworks': refworks,
             'msword': msword}

fmts = templates.keys()


def _gen_proc(name, canonical):
    if 'ISBN-13' in canonical:
        canonical['ISBN'] = canonical.pop('ISBN-13')
    tpl = templates[name]
    return Template(tpl).safe_substitute(canonical)


def _last_first(author):
    if ',' in author:
        tokens = author.split(',')
        last = tokens[0].strip()
        first = ' '.join(tokens[1:]).strip()
    else:
        tokens = author.split(' ')
        last = tokens[-1].strip()
        first = ' '.join(tokens[:-1]).strip()
    return {'last': last, 'first': first}


def _spec_proc(name, fmtrec, authors):
    """
    Fixes the Authors records (TODO: refator this!)
    """
    if name not in ('labels', 'bibtex',
                    'refworks', 'endnote', 'msword'):
        return
    if name == 'labels':
        AUTHORS = '\nAuthor:    '.join(authors)
    if name == 'bibtex':
        AUTHORS = ' and '.join(authors)
    if name == 'refworks':
        AUTHORS = '\nA1  - '.join(authors)
    if name == 'endnote':
        AUTHORS = '\n%A '.join(authors)
    if name == 'msword':
        uid = str(uuid.uuid4())
        fmtrec = Template(fmtrec).safe_substitute(uid=uid)
        person = r"\n<b:Person><b:Last>$last</b:Last>"\
                 r"<b:First>$first</b:First></b:Person>"
        AUTHORS = ''
        for a in authors:
            AUTHORS += Template(person).safe_substitute(_last_first(a))

    return re.sub(r'\$AUTHORS', AUTHORS, fmtrec)


def fmtbib(fmtname, canonical):
    """
    Returns a canonical record in the selected format
    """
    return _spec_proc(fmtname, _gen_proc(fmtname, canonical),
                      canonical['Authors'])
