import re
import pyximport
pyximport.install(language_level=3)
import cut_line
import warnings
# 忽略所有的 SyntaxWarning 警告
warnings.filterwarnings('ignore', category=SyntaxWarning)

内置类型=r'\s*(int|short|long|long long|double|float|char|list|tuple|dict|str|bytes|object|bytearray|Py_UCS4|struct|union|class|cppclass|fused)'

def open_utf8(path):
    return open(path,'r',encoding='utf8')


cdef_block=re.compile(r'cdef\s+(public|private|readonly)?\s*:', re.DOTALL)
cdef_line=re.compile(r'cdef\s+(.+)')
cdef_struct_union_fused_class=re.compile(r'cdef\s+(public\s+)?(struct|union|fused|cpplass|class)\s+', re.DOTALL)
cdef_extend_from=re.compile(r'cdef\s+(public\s+)?extend\s+from.+?:', re.DOTALL)
from_cimport=re.compile(r'from\s+(.+?)\s+cimport(.+)', re.DOTALL)
with_=re.compile(r'with\s+(nogil|.+):', re.DOTALL)
cimport_=re.compile(r'cimport\s+(.+)', re.DOTALL)
cpdef_func=re.compile(r'c?p?def\s+(public\s+)?(api\s+)?(inline\s+)?([^()]+)(\([^()]+\))', re.DOTALL)
include=re.compile(r'include\s*[\'"]{1,3}([^\'"]+)[\'"]{1,3}')
for_=re.compile('for\s+(.+)?\s+(in|from)\s+')
async_def=re.compile('async\s+def\s+(.+)([^()]+)(\([^()]+\))')
#
cdef_for_with_from_cimport_include=re.compile('(cdef|cpdef|def|with|for|from|cimport|include|async)\s')
_cdef='cdef'
_cpdef='cpdef'
_def='def'
_for='for'
_from='from'
_with='with'
_cimport='cimport'
include='include'
_async='async'
def identify_code_lines(code_lines):
    for code_line, suojin_len, start_lineno, end_lino in code_lines:
        kt=cdef_for_with_from_cimport_include.match(code_line)
        if kt:
            ktg=kt.groups()[0]
            if ktg==_cdef:
                r=cpdef_func.match(code_line)
                if r:
                r= cdef_block.match(code_line)
                if r:
                r= cdef_struct_union_fused_class.match(code_line)
                if r:
                r= cdef_line.match(code_line)
                if r:
                raise AssertionError
            elif ktg==_cpdef or ktg==_def:
                r = cpdef_func.match(code_line)
                assert r
            elif ktg==_for:
                r=for_.match(code_line)
                assert r
            elif ktg==_from:
                r=from_cimport.match(code_line)
                if r:
                else: #是from……import
                    pass
            elif ktg==_cimport:
                r=cimport_.match(code_line)
                assert r
            elif ktg== _with:
                r = cimport_.match(code_line)
                assert r
            elif ktg==_include:

def define_func_code_line(code_line):
    r = cpdef_func.match(code_line)
    if r:
        r = cdef_block.match(code_line)
    if r:
        r = cdef_struct_union_fused_class.match(code_line)
    if r:
        r = cdef_line.match(code_line)
    if r:
        raise AssertionError

def split_func_args(args_text: str):
    pass

if __name__ == '__main__':
    p='D:/xrdb/PyUnicode.pyx'
    text=open_utf8(p).read()
    #it=cfunc.finditer(text)
    code_lines=cut_line.cut_line(text)
    pass
    #find_line(code_lines)

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
