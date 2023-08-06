# -*- coding: utf-8 -*-

import logging
import base64
from hashlib import sha1
import copy

from crypt3des import Crypt3Des
from .utils import dict2xml, xml2dict, base64_encode_nocr

logger = logging.getLogger('gash')


class GashHelper(object):
    """
    一个gash的client
    """

    password = None
    key = None
    iv = None

    @classmethod
    def dumps(cls, input_dict):
        trans_dict = dict(
            TRANS=input_dict
        )
        return base64_encode_nocr(dict2xml(trans_dict))

    @classmethod
    def loads(cls, raw_data):
        return xml2dict(base64.decodestring(raw_data))['TRANS']

    def __init__(self, password, key, iv):
        """
        key
        """

        self.password = password
        self.key = key
        self.iv = iv

    def pack(self, input_dict):
        """
        传入dict，返回一个可以发送的str
        """
        input_dict = copy.deepcopy(input_dict)

        # 就算有也不能存
        input_dict.pop('ERQC', None)

        input_dict['ERQC'] = self.make_erqc(
            input_dict['CID'],
            input_dict['COID'],
            input_dict['CUID'],
            input_dict['AMOUNT'],
            )

        return self.dumps(input_dict)

    def unpack(self, raw_data):
        """
        传入服务器返回的str，返回dict
        """
        return self.loads(raw_data)

    def make_erqc(self, cid, coid, cuid, amt):
        """
        生成ERQC，生成req时用
        """

        # 因为担心可能只能用一次
        des = Crypt3Des(self.key, self.iv)

        if isinstance(amt, basestring):
            if len(amt) != 14:
                # 说明是忘记转成数字了
                amt = float(amt)

        if not isinstance(amt, basestring):
            amt = '%014d' % (amt * 100)

        src = '%s%s%s%s%s' % (cid, coid, cuid, amt, self.password)

        result = des.encrypt(src)
        # 20字符的2进制
        result = sha1(result).digest()

        result = base64_encode_nocr(result)

        return result

    def make_erpc(self, cid, coid, rrn, cuid, amt, rcode):
        """
        生成ERPC，验证gashserver的回调时用
        """

        # 因为担心可能只能用一次
        des = Crypt3Des(self.key, self.iv)

        if isinstance(amt, basestring):
            if len(amt) != 14:
                # 说明是忘记转成数字了
                amt = float(amt)

        if not isinstance(amt, basestring):
            amt = '%014d' % (amt * 100)

        src = '%s%s%s%s%s%s' % (cid, coid, rrn, cuid, amt, rcode)

        result = des.encrypt(src)
        # 20字符的2进制
        result = sha1(result).digest()

        result = base64_encode_nocr(result)

        return result
