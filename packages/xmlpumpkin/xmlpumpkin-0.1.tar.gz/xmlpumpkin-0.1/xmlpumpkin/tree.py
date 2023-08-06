# encoding: utf-8

from lxml import etree
from .utils import cacheonceproperty


XML_ENCODING = 'utf-8'


class Tree(object):
    """Tree accessor for CaboCha xml."""

    def __init__(self, cabocha_xml):
        self._element = etree.fromstring(
            cabocha_xml.encode(XML_ENCODING),
        )

    @cacheonceproperty
    def chunks(self):
        chunk_elems = self._element.findall('.//chunk')
        chunks = tuple([Chunk(elem, self) for elem in chunk_elems])
        return chunks

    @cacheonceproperty
    def root(self):
        for chunk in self.chunks:
            if chunk.link_to_id == -1:
                return chunk
        return None

    def chunk_by_id(self, chunk_id):
        for chunk in self.chunks:
            if chunk.id == chunk_id:
                return chunk
        return None


class Chunk(object):
    """CaboCha chunk object representation."""

    def __init__(self, element, parent):
        self._element = element
        self._parent = parent

    def __eq__(self, other):
        return self._element == other._element

    @cacheonceproperty
    def id(self):
        return int(self._element.attrib['id'])

    @cacheonceproperty
    def link_to_id(self):
        return int(self._element.attrib['link'])

    @cacheonceproperty
    def linked_from_ids(self):
        return tuple([chunk.id for chunk in self.linked])

    @cacheonceproperty
    def func_id(self):
        return int(self._element.attrib['func'])

    @cacheonceproperty
    def dep(self):
        return self._parent.chunk_by_id(self.link_to_id)

    @cacheonceproperty
    def linked(self):
        to_id = self.id
        return [
            chunk for chunk
            in self._parent.chunks
            if chunk.link_to_id == to_id
        ]

    @cacheonceproperty
    def surface(self):
        tokens = self._tokens()
        texts = [t.text for t in tokens]
        return u''.join(texts)

    @cacheonceproperty
    def func_surface(self):
        tid = self.func_id
        tokens = self._tokens()
        for tok in tokens:
            if int(tok.attrib['id']) == tid:
                return tok.text

    def _tokens(self):
        return self._element.findall('.//tok')
