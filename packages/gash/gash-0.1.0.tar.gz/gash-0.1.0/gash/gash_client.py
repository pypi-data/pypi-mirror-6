# -*- coding: utf-8 -*-

import logging
import base64
from hashlib import sha1
import copy

import requests
from crypt3des import Crypt3Des
from .utils import dict2xml, xml2dict

logger = logging.getLogger('gash')


class GashClient(object):
    """
    一个gash的client
    """

    password = None
    key = None
    iv = None

    def __init__(self, password, key, iv):
        """
        key
        """

        self.password = password
        self.key = key
        self.iv = iv

    def post(self, url, input_dict, **kwargs):
        """
        调用接口
        """
        if not isinstance(input_dict, dict):
            logger.fatal('input_dict is not dict. %s', input_dict)
            return None, 'invalid input_dict'

        input_dict = copy.deepcopy(input_dict)

        # 就算有也不能存
        input_dict.pop('ERQC', None)

        input_dict['ERQC'] = self.make_erqc(
            input_dict['CID'],
            input_dict['COID'],
            input_dict['CUID'],
            input_dict['AMOUNT'],
        )

        trans_dict = dict(
            TRANS=input_dict
        )

        rsp = requests.post(url, self.make_req(trans_dict), **kwargs)

        if rsp.status_code != 200:
            logger.fatal('status_code: %s, input_dict:%s', rsp.status_code, input_dict)
            return None, 'status_code is %s' % rsp.status_code

        try:
            result_dict = self.parse_rsp(rsp.text)
            return result_dict['TRANS'], None
        except Exception, e:
            logger.fatal('e: %s, input_dict: %s', e, input_dict, exc_info=True)
            return None, str(e)

    def make_req(self, data):
        return base64.encodestring(dict2xml(data))

    def parse_rsp(self, data):
        return xml2dict(base64.decodestring(data))

    def make_erqc(self, cid, coid, cuid, amt):
        """
        生成ERQC
        """

        # 因为担心可能只能用一次
        des = Crypt3Des(self.key, self.iv)

        src = '%s%s%s%s%s' % (cid, coid, cuid, amt, self.password)

        result = des.encrypt(src)
        # 20字符的2进制
        result = sha1(result).digest()

        result = base64.encodestring(result)

        return result
