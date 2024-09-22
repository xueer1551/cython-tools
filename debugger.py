import re, sys, os
import pyximport
pyximport.install(language_level=3)
import cut_line
import warnings
# 忽略所有的 SyntaxWarning 警告
warnings.filterwarnings('ignore', category=SyntaxWarning)

内置类型=r'\s*(int|short|long|long long|double|float|char|list|tuple|dict|str|bytes|object|bytearray|Py_UCS4|struct|union|enum|class|cppclass|fused)'

def get_cytho_include_path():
    p = sys.executable
    install_path = os.path.dirname(p)
    path=os.path.join(install_path, r'\Lib\site-packages\Cython\Includes')
def open_utf8(path):
    return open(path,'r',encoding='utf8')


cdef_block=re.compile(r'cdef(\s+(?P<public>public|private|readonly))?\s*:', re.DOTALL)
cdef_line=re.compile(r'cdef\s+(?P<names>.+)',re.DOTALL)
cdef_struct_union_enum_fused_class=re.compile(r'cdef\s+(?P<public>public\s+)?(?P<type>struct|union|enum|fused|cpplass|class)\s+(?P<name>[^:]+):', re.DOTALL)
cdef_extend_from=re.compile(r'cdef\s+(?P<public>public\s+)?extend\s+from(?P<name>.+?):', re.DOTALL)
from_cimport=re.compile(r'from\s+(.+?)\s+(c?import)(.+)', re.DOTALL)
with_=re.compile(r'with\s+(?P<nogil>nogil|.+):', re.DOTALL)
cimport_=re.compile(r'cimport\s+(?P<name>.+)', re.DOTALL)
func=r'(public\s+)?(api\s+)?(inline\s+)?(?P<name>[^()]+)(?P<args>\([^()]+\))(.+)?(?P<nogil>nogil?).*'
pxd_func=re.compile(fr'\s*{func}', re.DOTALL)
cpdef_func=re.compile(rf'(async\s+)?(?P<cpdef>c?p?def)\s+{func}', re.DOTALL)
include=re.compile(r'include\s*[\'"]{1,3}(?P<name>[^\'"]+)[\'"]{1,3}',re.DOTALL)
global_=re.compile(r'global\s+(?P<name>[\w_]+)',re.DOTALL)
for_=re.compile('for\s+(?P<names>.+)?\s+(in|from)\s+',re.DOTALL)
except_=re.compile('except\s+(?P<name>[\w]+)((?=as\s+)?([\w_]+))',re.DOTALL)
other_keywords=re.compile('([#@]|(if|elif|else|wihle|try|raise|finally|match|case|return|await)[\s(:]|pass|break)',re.DOTALL)
need_keywords=re.compile('(cdef|cpdef|def|with|for|from|cimport|include|async|global|class|except)\s',re.DOTALL)
left_value_express=re.compile('(.+)\s*[+\-*/:=]=',re.DOTALL)
#
_cdef='cdef'
_cpdef='cpdef'
_def='def'
_for='for'
_from='from'
_with='with'
_cimport='cimport'
_include='include'
_async='async'
_global='global'

def check_line_need_process(code_line: str, suojin_len: int):
    if other_keywords.match(code_line, suojin_len):
        return False
    #
    r=need_keywords.match(code_line, suojin_len)
    if r:
        return r
    #
    r=left_value_express.match(code_line, suojin_len)
    if r:
        return r
    #
    return False

def identify_code_lines(code_lines):
    class_dict, func_dict={},{}
    it=iter(code_lines)
    while(True):

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

def enter_cdef_class_namespace(name: str, code_lines: iter, sj_len: int, parent_namespace: tuple, start_i: int, l: int,  lines: list):
    vars, funcs=[],[]
    namespace=NameSpace('class', name, vars, funcs, sj_len, parent_namespace, start_i)
    i=start_i+1
    while(i<l):
        cl=code_lines[i]
        code_line, suojin_len, start_lineno, end_lino = cl
        if suojin_len>sj_len: #仍在块中
            r=cdef_line.match(code_line, suojin_len)
            if r:
                lines[i]=(cl, r, namespace)
                i+=1
                continue
            #
            r=cdef_block.match(code_line, suojin_len)
            if r:
                i, block_vars=find_cdef_block_vars(code_lines, sj_len, parent_namespace, i+1, l)
                continue
            #
            r=cpdef_func.match(code_line, suojin_len)
            if r:

        else:
            return i
    return l

def find_cdef_block_vars( namespace: type, code_lines: iter, sj_len: int,  start_i: int, l: int, lines: list ):
    for i in range(start_i, l):
        line = code_lines[i]
        code_line, suojin_len, start_lineno, end_lino = line
        if suojin_len<sj_len:
            lines[i]=(line, line, namespace)
        else:
            return i
    return l

def find_func_vars( name:str, parent_namespace: type, code_lines: iter, sj_len: int,  start_i: int, l: int, lines: list ):
    namespace=NameSpace('func', name, [], parent_namespace, start_i)
    i=start_i
    while(i<l):
        line = code_lines[i]
        code_line, suojin_len, start_lineno, end_lino = line
        if suojin_len<sj_len:

            lines[i]=(line, line, namespace)
        else:
            return i
    return l

class NameSpace:
    __slots__ = ('type', 'name', 'vars', 'funcs', 'sj_len', 'parent', 'start_i', 'end_i')
    def __init__(self, t:str, name:str, vars:list, sj_len:int, parent:type, start_i:int):
        self.name, self.vars, self.sj_len, self.parent, self.start_i, = name, vars, sj_len, parent, start_i
        self.type=t



def define_func_code_line(code_line):
    r = cpdef_func.match(code_line)
    if r:
        r = cdef_block.match(code_line)
    if r:
        r = cdef_struct_union_enum_fused_class.match(code_line)
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
