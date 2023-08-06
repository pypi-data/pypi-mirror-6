# encoding: utf-8

from attest import Tests
from xmlpumpkin.tree import Tree


tree_unit = Tests()


class Fixtures:

    class rain:
        xml = (
            u'<sentence>'
            u' <chunk id="0" link="1" rel="D" score="1.725761" head="0" func="1">'
            u'  <tok id="0" feature="名詞,一般,*,*,*,*,雨,アメ,アメ">雨</tok>'
            u'  <tok id="1" feature="助詞,格助詞,一般,*,*,*,が,ガ,ガ">が</tok>'
            u' </chunk>'
            u' <chunk id="1" link="3" rel="D" score="-1.691271" head="2" func="3">'
            u'  <tok id="2" feature="動詞,自立,*,*,五段・ラ行,基本形,降る,フル,フル">降る</tok>'
            u'  <tok id="3" feature="助詞,接続助詞,*,*,*,*,と,ト,ト">と</tok>'
            u' </chunk>'
            u' <chunk id="2" link="3" rel="D" score="-1.691271" head="4" func="5">'
            u'  <tok id="4" feature="名詞,一般,*,*,*,*,地,チ,チ">地</tok>'
            u'  <tok id="5" feature="助詞,格助詞,一般,*,*,*,が,ガ,ガ">が</tok>'
            u' </chunk>'
            u' <chunk id="3" link="-1" rel="D" score="0.000000" head="6" func="6">'
            u'  <tok id="6" feature="動詞,自立,*,*,五段・ラ行,基本形,固まる,カタマル,カタマル">固まる</tok>'
            u' </chunk>'
            u'</sentence>'
        )
        chunk_ids = [0, 1, 2, 3]
        chunk_links = [1, 3, 3, -1]
        chunk_linked = [tuple(), (0, ), tuple(), (1, 2)]
        num_chunks = 4
        root_id = 3
        chunk_deps = {
            0: 1, 1: 3, 2: 3,
        }
        chunk_dep_from = {
            0: [], 1: [0], 2: [], 3: [1, 2],
        }
        chunk_surfaces = [
            u'雨が', u'降ると', u'地が', u'固まる',
        ]
        func_tok_ids = [1, 3, 5, 6]
        func_surfaces = [
            u'が', u'と', u'が', u'固まる',
        ]

    cases = dict(
        rain=rain,
    )


@tree_unit.test
def maketree():
    """Create a valid Tree instance?"""
    for key in Fixtures.cases:
        case = Fixtures.cases[key]
        tree = Tree(case.xml)

@tree_unit.test
def chunkinfo():
    """Information on chunks?"""
    for key in Fixtures.cases:
        case = Fixtures.cases[key]
        tree = Tree(case.xml)

        assert isinstance(tree.chunks, tuple)
        assert len(tree.chunks) == case.num_chunks

        assert [c.id for c in tree.chunks] == case.chunk_ids
        assert tree.root.id == case.root_id

        for chunk in tree.chunks:
            assert tree.chunk_by_id(chunk.id) == chunk

@tree_unit.test
def chunklinks():
    """Get information on chunk links?"""
    for key in Fixtures.cases:
        case = Fixtures.cases[key]
        tree = Tree(case.xml)

        assert [c.link_to_id for c in tree.chunks] == case.chunk_links
        assert [c.linked_from_ids for c in tree.chunks] == case.chunk_linked

        for chunk in tree.chunks:

            # link to chunk....
            to_id = case.chunk_deps.get(chunk.id, -1)
            dep = chunk.dep
            if to_id == -1:
                assert dep is None
            else:
                assert chunk.dep.id == to_id

            # linked from chunk...
            from_ids = case.chunk_dep_from[chunk.id]
            linked = chunk.linked
            assert set([c.id for c in linked]) == set(from_ids)

@tree_unit.test
def chunksurfaces():
    """Get chunk surfaces?"""
    for key in Fixtures.cases:
        case = Fixtures.cases[key]
        tree = Tree(case.xml)

        assert [c.surface for c in tree.chunks] == case.chunk_surfaces
        assert [c.func_id for c in tree.chunks] == case.func_tok_ids
        assert [c.func_surface for c in tree.chunks] == case.func_surfaces
