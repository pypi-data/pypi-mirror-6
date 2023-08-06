# -*- coding: utf-8 -*-

import xmltodict
import base64


def dict2xml(d):
    import re
    xml = xmltodict.unparse(d, pretty=True)
    xml = re.sub(r'<\?xml version="1\.0" encoding="utf-8"\?>\n*', '', xml)
    return xml


def xml2dict(xml):
    return xmltodict.parse(xml)


def base64_encode_nocr(src):
    """
    返回不带换行的。
    国际标准是每76个字符一个换行符
    """

    return base64.encodestring(src).replace('\n', '')