# -*- coding: utf-8 -*-
"""
http://www.pbc.gov.cn/rhwg/971601f7.htm
"""

import re

__author__ = 'Kang Li<eastern.fence@gmail.com>'
__version__ = '0.0.1'


def wrapper(digits=u'零壹贰叁肆伍陆柒捌玖', words=u'亿万仟佰拾元角分整'):
    digits = list(digits) + ['']
    yi, wan, qian, bai, shi, yuan, jiao, fen, zheng = list(words)

    valid = re.compile(r'^\d{1,16}(\.\d+)?$')

    def integers(number, postfix=yuan):
        vs = number[-4:]
        result = list(reversed(zip(reversed(vs), [postfix] + [shi, bai, qian])))
        result = combine_zeros(result, postfix)

        if len(number) > 8:
            result[:0] = integers(number[:-8], yi)+integers(number[-8:-4], wan)
        elif len(number) > 4:
            result[:0] = integers(number[:-4], wan)

        return result

    def fractions(number):
        return zip(number, ('' if number.startswith('0') else jiao, fen))

    def combine_zeros(chips, postfix):
        result = []
        for i in range(len(chips)):
            if chips[i][0] == '0':
                if i != 0 and chips[i-1][0] == '0':
                    continue
                result.append(('0', ''))
            else:
                result.append(chips[i])
        if result and result[-1][0] == '0':
            if len(result) == 1 and postfix == wan:
                return []
            result[-1] = ('-1', postfix)
        return result

    def concat(chips):
        return ''.join([digits[int(v)]+n for v, n in chips])

    def upper_case(number):
        number = str(number)
        if valid.match(number):
            return ''

        integer, fraction = (number+'.').split('.')[:2]

        integer_part = concat(integers(integer.lstrip('0')))
        fraction_part = concat(fractions(fraction.rstrip('0')))
        if not integer_part:
            if not fraction_part:
                return digits[0] + yuan + zheng
            else:
                return fraction_part.lstrip(digits[0])

        result = integer_part + fraction_part
        if result.endswith(yuan):
            result += zheng
        return result

    return upper_case

upper = wrapper()
