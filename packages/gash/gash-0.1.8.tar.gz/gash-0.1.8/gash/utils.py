# -*- coding: utf-8 -*-

import xmltodict


def dict2xml(d):
    import re
    xml = xmltodict.unparse(d, pretty=True)
    xml = re.sub(r'<\?xml version="1\.0" encoding="utf-8"\?>\n*', '', xml)
    return xml


def xml2dict(xml):
    return xmltodict.parse(xml)