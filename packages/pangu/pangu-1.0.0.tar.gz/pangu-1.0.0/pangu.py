# coding: utf-8

import re


__version__ = '1.0.0'
__all__ = ['spacing', ]


# def build_re(source):
#     L = []
#     for i in source:
#         if isinstance(i, list):
#             f, t = i
#             try:
#                 f = unichr(f)
#                 t = unichr(t)
#                 L.append('%s-%s' % (f, t))
#             except:
#                 pass # A narrow python build, so can't use chars > 65535 without surrogate pairs!

#         else:
#             try:
#                 L.append(unichr(i))
#             except:
#                 pass

#     re_str = '[%s]' % ''.join(L)

#     print 're:', RE.encode('utf-8')

#     return re.compile(re_str, flags=re.IGNORECASE|re.UNICODE)


CJK_QUOTE_L_RE = re.compile(ur'([\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])(["\'])', flags=re.IGNORECASE)
CJK_QUOTE_R_RE = re.compile(ur'(["\'])([\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])', flags=re.IGNORECASE)
CJK_QUOTE_FIX_RE = re.compile(ur'(["\']+)(\s*)(.+?)(\s*)(["\']+)', flags=re.IGNORECASE)

CJK_BRACKET_RE = re.compile(ur'([\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([<\[\{\(]+(.*?)[>\]\}\)]+)([\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])', flags=re.IGNORECASE)
CJK_BRACKETFIX_RE = re.compile(ur'([<\[\{\(]+)(\s*)(.+?)(\s*)([>\]\}\)]+)', flags=re.IGNORECASE)
CJK_BRACKET_L_RE = re.compile(ur'([\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([<>\[\]\{\}\(\)])', flags=re.IGNORECASE)
CJK_BRACKET_R_RE = re.compile(ur'([<>\[\]\{\}\(\)])([\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])', flags=re.IGNORECASE)

CJK_HASH_L_RE = re.compile(ur'([\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])(#(\S+))', flags=re.IGNORECASE)
CJK_HASH_R_RE = re.compile(ur'((\S+)#)([\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])', flags=re.IGNORECASE)

CJK_L_RE = re.compile(ur'([\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([a-z0-9`@&%=\$\^\*\-\+\|\/\\])', flags=re.IGNORECASE)
CJK_R_RE = re.compile(ur'([a-z0-9`~!%&=;\|\,\.\:\?\$\^\*\-\+\/\\])([\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])', flags=re.IGNORECASE)


def spacing(text):
    text = CJK_QUOTE_L_RE.sub(r'\1 \2', text)
    text = CJK_QUOTE_R_RE.sub(r'\1 \2', text)
    text = CJK_QUOTE_FIX_RE.sub(r'\1\3\5', text)

    old_text = text
    new_text = CJK_BRACKET_RE.sub(r'\1 \2 \4', old_text)
    text = new_text
    if (old_text == new_text):
        text = CJK_BRACKET_L_RE.sub(r'\1 \2', text)
        text = CJK_BRACKET_R_RE.sub(r'\1 \2', text)
    text = CJK_BRACKETFIX_RE.sub(r'\1\3\5', text)

    text = CJK_HASH_L_RE.sub(r'\1 \2', text)
    text = CJK_HASH_R_RE.sub(r'\1 \3', text)

    text = CJK_L_RE.sub(r'\1 \2', text)
    text = CJK_R_RE.sub(r'\1 \2', text)

    return text
