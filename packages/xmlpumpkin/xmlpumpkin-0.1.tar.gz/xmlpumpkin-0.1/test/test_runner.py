# encoding: utf-8

from attest import Tests
from lxml import etree
from xmlpumpkin.runner import cabocha


runner_unit = Tests()


class Fixtures:

    texts = dict(
        fx_msg_cnxn=u'他のサイトも表示できない場合、コンピュータの'
                    u'ネットワーク接続を確認してください。',
        fx_msg_fw=u'ファイアーウォールやプロキシでネットワークが'
                  u'保護されている場合、Firefox による Web アクセスが'
                  u'許可されているか確認してください。',
    )


@runner_unit.test
def noerror():
    """cabocha.as_xml(text), cabocha.txttree(text) witout errors?"""
    for key in Fixtures.texts:
        text = Fixtures.texts[key]
        xml_text = cabocha.as_xml(text)
        txt_tree = cabocha.txttree(text)
        assert isinstance(xml_text, unicode)
        assert isinstance(txt_tree, unicode)
    assert cabocha.as_xml(u'') == u'<sentence />'

@runner_unit.test
def getxml():
    """cabocha.as_xml(text) returns xml?"""
    for key in Fixtures.texts:
        text = Fixtures.texts[key]
        xml_text = cabocha.as_xml(text)
        etree.fromstring(xml_text.encode('utf-8'))

@runner_unit.test
def gettxttree():
    """cabocha.txttree(text) returns text tree?"""
    for key in Fixtures.texts:
        text = Fixtures.texts[key]
        txt_tree = cabocha.txttree(text)
        assert len(txt_tree) > 3
        assert txt_tree.endswith(u'EOS\n')

@runner_unit.test
def correctxml():
    """cabocha.as_xml(text) returns valid xml?"""
    xml_results = []

    for key in Fixtures.texts:
        text = Fixtures.texts[key]
        xml_text = cabocha.as_xml(text)
        xml_results.append(xml_text)

        sentence = etree.fromstring(xml_text.encode('utf-8'))
        assert sentence.tag == 'sentence'
        chunks = sentence.findall('.//chunk')
        assert len(chunks) > 0

    assert len(xml_results) == len(set(xml_results))
