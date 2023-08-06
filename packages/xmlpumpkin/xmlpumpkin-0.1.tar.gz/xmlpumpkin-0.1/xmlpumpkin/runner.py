# encoding: utf-8

import subprocess


CABOCHA_ENCODING = 'utf-8'
CABOCHA_FORMAT_TREE = '0'
CABOCHA_FORMAT_XML = '3'


class CaboCha(object):
    """CaboCha subprocess runner."""

    def as_xml(self, text):
        if not self._filtertext(text):
            return u'<sentence />'
        xml = self._cabocha(
            text,
            arguments=['-f', CABOCHA_FORMAT_XML],
        )
        return xml.decode(CABOCHA_ENCODING)

    def _filtertext(self, text):
        return not (text == u'')

    def txttree(self, text):
        text_tree = self._cabocha(
            text,
            arguments=['-f', CABOCHA_FORMAT_TREE],
        )
        return text_tree.decode(CABOCHA_ENCODING)

    def _cabocha(self, text, arguments=tuple()):
        cabocha_process = subprocess.Popen(
            ['cabocha'] + list(arguments),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        out, err = cabocha_process.communicate(
            input=text.encode(CABOCHA_ENCODING),
        )
        return out


cabocha = CaboCha()
