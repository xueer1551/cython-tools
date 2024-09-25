import re, sys, os
import pyximport
pyximport.install(language_level=3)
import cut
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

func_args_and_suffix=r'(?P<args>\([^()]+\))(.*)'
cdef_block=re.compile(r'cdef(\s+(?P<public>public|private|readonly))?\s*:', re.DOTALL)
cdef_line=re.compile(r'cdef\s+(?P<content>.+)',re.DOTALL)
struct_union_enum_fused_class=re.compile(r'(?:cdef|ctypedef)\s+(?:.+?)?(?P<type>struct|union|enum|fused|cpplass|class)\s+(?P<name>[^:]+)\s*:', re.DOTALL)
extend_struct_union_enum_fused_class=struct_union_enum_fused_class
cdef_extend_from=re.compile(r'cdef\s+(?P<public>public\s+)?extend\s+from(?P<name>.+?):', re.DOTALL)
ctypedef_bieming=re.compile(r'ctypedef\s+(?P<content>[^()]+)',re.DOTALL)
from_cimport=re.compile(r'from\s+(.+?)\s+(c?import)(.+)', re.DOTALL)
with_=re.compile(r'with\s+(?P<nogil>nogil|.+):', re.DOTALL)
cimport_=re.compile(r'cimport\s+(?P<name>.+)', re.DOTALL)
func_name_and_arg_and_suffix=rf'(?P<type_and_name>[^()]+){func_args_and_suffix}'
func=rf'(public\s+)?(api\s+)?(inline\s+)?{func_name_and_arg_and_suffix}'
extend_func=re.compile(func, re.DOTALL)
cdef_func=re.compile(fr'(c?p?def)\s+{func}')
async_func=re.compile(rf'(async\s+)?(?P<cpdef>def)\s+{func_name_and_arg_and_suffix}', re.DOTALL)
ctypedef_func0=re.compile(rf'ctypedef\s+{func}', re.DOTALL)
ctypedef_func1=re.compile(rf'ctypedef\s+(?P<type_and_name>[^()]+){func_args_and_suffix}')
include=re.compile(r'include\s*[\'"]{1,3}(?P<name>[^\'"]+)[\'"]{1,3}', re.DOTALL)
global_=re.compile(r'global\s+(?P<name>[\w_]+)', re.DOTALL)
for_=re.compile(r'for\s+(?P<names>.+)?\s+(in|from)\s+', re.DOTALL)
except_=re.compile(r'except(?P<name>(?:\s+)[\w_]+)?((?:\s+as\s+)([\w_]+)\s*)?:', re.DOTALL)
other_keywords=re.compile(r'(?:[#@]|(if|elif|else|wihle|continue|try|raise|finally|match|case|return|await)[\s(:]|pass|break)', re.DOTALL)
need_keywords=re.compile(r'(cdef|cpdef|ctypedef|def|with|for|from|cimport|include|async|global|class|except)\s', re.DOTALL)
extend_no_used=re.compile('(?:[#@\'"\n])')
extend_keyword=re.compile('(ctypedef|cdef)')
all_kongbai=re.compile(r'(?:\s+)')
left_value_express=re.compile(r'(.+)\s*[+\-*/:=]?=', re.DOTALL)
memoryview_=re.compile('\[[^:]*:[^\]]*\]', re.DOTALL)
shuzu=re.compile('\[\s*([0-9]*)\s*\]',re.DOTALL)
name_=re.compile('[_\w]+',re.DOTALL)
fanxing=re.compile('\[.+\]',re.DOTALL)
#
model_enter_block_keywords=set(['cdef','cpdef','def'])
class_keywords=set(['class', 'cppclass'])
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
_class='class'
_cppclass='cppclass'
_ctypedef='ctypedef'
_volatile='volatile'
_const='const'
_as='as'
_maohao=':'
_array='array'
_memoryview='memoryview'
class Ctype:
    __slots__ = ( 'base_type_name', 'modifiers', 'ptr_levels')  # 指针和数组都被视为ptr_level，只不过指针是运行期变长
    def __init__(self, base_type_name:tuple, modifier, ptr_level: list, ):
        self.base_type_name, self.modifiers, self.ptr_levels, self.belong_model_name = base_type_name, modifier, ptr_level
    def __hash__(self):
        return hash(self.name)

class CClass:
    __slots__ = ('name', 'type', 'base_type' )
    def __init__(self, name:str, type:str, base_type):
        #base_type当type是memoryview时才有效
        #type -> class or memoryview or cppclass
        self.name, self.type, self.base_type= name, type, base_type


def get_struct_union_enum_fused_class_type_and_name(rr: re.Match, d: dict):
    g=rr.groups()
    t, name = g
    d[name]=type

def get_func_signature(rr: re.Match, d):
    pass
def get_import_with_for_vars_biemings(content: str, d) ->list[str]:
    codens=cut.cut_douhao_and_strip(content)
    for coden in codens:
        tokens=cut.cut_kongbai(coden)
        if len(tokens)==1:
            name=tokens[0]
            d[name]=name
        else:
            assert len(tokens)==3
            assert tokens[1]==_as
            name, bieming= tokens[0], tokens[2]
            d[bieming]=name
    return d



def get_ctypedef_type_bieming(rr: re.Match, d: dict):
    content=rr.groups()
    codens_and_fangkuohaos = cut.split_by_fangkuohao_and_del_kongbai(content)


def get_type_or_name(codens: list):
    t, i = find_type_and_other_in_text(codens)


def get_type_from_codens_and_fangkuohao(codens: list, fangkuohao):
    text, stat=fangkuohao
    if stat is cut.arr:
        modifiers, start_i=get_const_volatile(codens)
        l=len(codens)
        benming=[]
        for i in range(start_i, l):
            c=codens[i]
            if type(c) is str:
                benming.append(c)
            elif type(c) is tuple:
                text, xinghao_count= c
                ptr_level=[None]*xinghao_count
                while(i<l):
                    if type(c) is tuple:
                        text, xinghao_count = c
                        ptr_level = [None] * xinghao_count
                        i+=1
                    else:
                        raise AssertionError
                return Ctype(benming, modifiers, ptr_level)
            else:
                raise AssertionError
        return Ctype(benming, modifiers, [])
    elif stat is cut.typed_memoryview:
        name=tuple(codens)
        t=CClass(name, stat, text)
    elif stat is cut.cppclass:
        name=tuple(codens)
        t=CClass(name, stat, text)
    else:
        raise AssertionError

def get_const_volatile(codens:str, ):
    coden=codens[0]
    if coden==_const:
        if codens[1]==_volatile:
            return (_const,_volatile), 2
        else:
            return (_const,None), 1
    elif coden==_volatile:
        if codens[1]==_const:
            return (_const,_volatile), 2
        else:
            return (None, _volatile), 1
    else:
        return (None, None), 0

def break_block(code_lines:list, sj_len:int, start_i:int, l:int, ):
    for i in range(start_i,l):
        code_line, suojin_len, _,  __ = code_lines[i]
        if suojin_len<sj_len:
            continue
        else:
            return i

class NameSpace:
    __slots__ = ('type', 'name', 'vars', 'funcs', 'sj_len', 'parent', 'children', 'start_i', 'end_i', 'cdef_blocks_start_end')
    def __init__(self, t:str, name:str, vars:list, sj_len:int, parent, start_i:int):
        if parent:
            parent.children.append(self)
        self.name, self.vars, self.sj_len, self.parent, self.start_i, = name, vars, sj_len, parent, start_i
        self.cdef_blocks_start_end=[]
        self.children=[]
        self.type=t


def enter_model_namespace(name: str, code_lines: list ):
    namespace=NameSpace('model', name, [], 0, None, 0)
    unknows=[]
    funcs, types, vars, includes=[],[],[],[]
    i, l =0, len(code_lines)
    lines=[None]*l
    while(i<l):
        line=code_lines[i]
        code_line, suojin_len, start_lineno, end_lino = line
        assert suojin_len==0
        r=need_keywords.match(code_line)
        if r:
            keyword=r.groups()[0]
            if keyword==_def or keyword==_cpdef :
                rr=cdef_func.match(code_line)
                lines[i] = (line, rr, namespace)
                i=enter_func_namespace(None, namespace, code_lines, suojin_len, i, l, lines )
                continue
            elif keyword==_cdef:
                rr = cdef_block.match(code_line)
                if rr:
                    lines[i] = (line, rr, namespace)
                    i = enter_cdef_block_vars(namespace, code_lines, suojin_len, i, l, lines)
                    continue
                #
                rr = struct_union_enum_fused_class.match(code_line)
                if rr:
                    lines[i] = (line, rr, namespace)
                    keyword = rr.groups()[0]
                    if keyword == _class or keyword == _cppclass:
                        i = enter_cdef_class_namespace(None, code_lines, suojin_len, namespace, i, l, lines)
                    else:
                        i = enter_cdef_block_vars(namespace, code_lines, suojin_len, i, l, lines)
                    continue
                #
                rr = cdef_func.match(code_line)
                if rr:
                    lines[i] = (line, rr, namespace)
                    i = enter_func_namespace(None, namespace, code_lines, suojin_len, i, l, lines)
                    continue
                #
                rr = cdef_line.match(code_line)
                if rr:
                    lines[i] = (line, rr, namespace)
                    i += 1
                    continue
                #
                rr = cdef_extend_from.match(code_line)
                if rr:
                    lines[i] = (line, rr, namespace)
                    i = enter_extend_block(namespace, code_lines, suojin_len, i, l, lines)
                    continue
                unknows.append((line, r, namespace))
            elif keyword==_ctypedef:
                #
                rr = struct_union_enum_fused_class.match(code_line)
                if rr:
                    lines[i] = (line, rr, namespace)
                    i = enter_cdef_block_vars(namespace, code_lines, suojin_len, i, l, lines)
                    continue
                #
                rr=ctypedef_bieming.match(code_line)
                if rr:
                    lines[i] = (line, rr, namespace)
                    i+=1
                    continue
                #
                rr=ctypedef_func0.match(code_line)
                if rr:
                    lines[i]=(line, rr, namespace)
                    i+=1
                    continue
                #
                rr=ctypedef_func1.match(code_line)
                if rr:
                    lines[i] = (line, rr, namespace)
                    i+=1
                    continue
                #
                unknows.append((line, r, namespace))
                continue
            elif keyword==_class:
                lines[i] = (line, r, namespace)
                i = enter_class_block(namespace, suojin_len, i, l, lines)
                continue
            elif keyword == _async:
                rr=async_func.match(code_line)
                lines[i]=(line, rr, namespace)
                i+=1
                continue
            elif keyword == _from:
            elif keyword == _cimport:
                rr=cimport_.match(code_line)
                assert rr
                content=rr.groups()[0]
                biemings=cut.cut_douhao(rr)

            elif keyword == _include:
                rr=include.match(code_line)
                assert rr
                include_filename=rr.groups()[0]
                includes.append(include_filename)
            elif keyword == _for:
            elif keyword == _with:
            elif keyword ==
            else:
                lines[i] = (line, r, namespace)
                i=enter_block(namespace, suojin_len, i, l, lines)
                continue
        #
        r= left_value_express.match(code_line)
        if r:
            lines[i]=(line, r, namespace)
            i+=1
            continue
        #
        else: #无需处理的
            lines[i] = (line, None, namespace)
            i += 1
            continue
        raise AssertionError
        #
    return namespace

def enter_block(namespace: NameSpace, sj_len:int, start_i: int, l: int, lines: list, ):
    i=start_i+1
    while(i<l):
        line = code_lines[i]
        code_line, suojin_len, start_lineno, end_lino = line
        if suojin_len>sj_len:
            r=check_line_need_process(code_line, suojin_len)
            lines[i]=(line, r, namespace)
            i+=1
        else:
            return i

def enter_class_block(code_lines: list, sj_len: int, parent_namespace: tuple, start_i: int, l: int, lines: list):
    #
    while (i < l):
        line = code_lines[i]
        code_line, suojin_len, start_lineno, end_lino = line
        if suojin_len > sj_len:  # 仍在块中
            #
            r = cdef_func.match(code_line, suojin_len)
            if r:
                i = enter_func_namespace(None, parent_namespace, code_lines, sj_len, i, l, lines)
                continue
            #
            r = async_func.match(code_line, suojin_len)
            if r:
                i = enter_func_namespace(None, parent_namespace, code_lines, sj_len, i, l, lines)
                continue
            #
            lines[i] = check_line_need_process(code_line, suojin_len)
            i += 1
        else:
            return i
        
def enter_cdef_class_namespace(name: str, code_lines: iter, sj_len: int, parent_namespace: tuple, start_i: int, l: int, lines: list):
    namespace=NameSpace('class', name, [], sj_len, parent_namespace, start_i)
    i=start_i+1
    while(i<l):
        line=code_lines[i]
        code_line, suojin_len, start_lineno, end_lino = line
        if suojin_len>sj_len: #仍在块中
            #
            r = cdef_func.match(code_line, suojin_len)
            if r:
                i = enter_func_namespace(name, parent_namespace, code_lines, sj_len, i, l, lines)
                continue
            #
            r=cdef_line.match(code_line, suojin_len)
            if r:
                lines[i]=(line, r, namespace)
                i+=1
                continue
            #
            r=cdef_block.match(code_line, suojin_len)
            if r:
                i=enter_cdef_block_vars(code_lines, sj_len, parent_namespace, i, l, lines)
                continue
            #
            r=async_func.match(code_line, suojin_len)
            if r:
                i=enter_func_namespace(name, parent_namespace, code_lines, sj_len, i, l, lines)
                continue
            #
            lines[i] = check_line_need_process(code_line, suojin_len)
            i += 1
        else:
            return i
    return l

def enter_cdef_block_vars( namespace: NameSpace, code_lines: iter, sj_len: int, start_i: int, l: int, lines: list, ):
    cdef_block_start = start_i
    for i in range(start_i+1, l):
        line = code_lines[i]
        code_line, suojin_len, start_lineno, end_lino = line
        if suojin_len>sj_len:
            first_char=code_line[suojin_len]
            if first_char != '#' and first_char!= '\n':
                lines[i]=(line, line, namespace)
        else:
            cdef_block_end = i
            namespace.cdef_blocks_start_end.append((cdef_block_start, cdef_block_end))
            return i
    cdef_block_end = l
    namespace.cdef_blocks_start_end.append((cdef_block_start, cdef_block_end))
    return l

def enter_func_namespace( name:str, parent_namespace: type, code_lines: iter, sj_len: int,  start_i: int, l: int, lines: list ):
    namespace=NameSpace('func', name, [], sj_len, parent_namespace, start_i)
    i=start_i+1
    while(i<l):
        line = code_lines[i]
        code_line, suojin_len, start_lineno, end_lino = line
        if suojin_len>sj_len:
            r=cdef_block.match(code_line, suojin_len)
            if r:
                i=enter_cdef_block_vars(namespace, code_lines, sj_len, start_i, l, lines)
                continue
            #
            r=cdef_line.match(code_line, suojin_len)
            if r:
                lines[i] = (line, r, namespace)
            else:
                #
                r=check_line_need_process(code_line, suojin_len)
                lines[i] = (line, r, namespace)
            #
            i+=1
        else:
            namespace.end_i=i
            return i
    return l

def enter_extend_block( namespace: NameSpace, code_lines: iter, sj_len: int,  start_i: int, l: int, lines:list ):
    i=start_i
    while(i<l):
        line=code_lines[i]
        code_line, suojin_len, _, __ = line
        if suojin_len>sj_len:
            if extend_no_used.match(code_line, suojin_len):continue
            #
            r=extend_struct_union_enum_fused_class.match(code_line, suojin_len)
            if r:
                enter_cdef_block_vars(namespace, code_lines, sj_len, start_i, l, lines)
                continue
            #
            r=extend_func.match(code_line, suojin_len)
            if r:
                lines[i]=(line, r, namespace)
                continue
            #
            r=cdef_func.match(code_line, suojin_len)
            if r:
                lines[i]=(line, r, namespace)
                i=break_block(code_lines, sj_len, i+1, l)
            #
        else:
            return i
    return l

def check_line_need_process(code_line: str, suojin_len: int):
    r = left_value_express.match(code_line, suojin_len)
    if r:
        return r
    #
    if other_keywords.match(code_line, suojin_len):
        return None
    #
    r=need_keywords.match(code_line, suojin_len)
    if r:
        return r
    #
    return None


if __name__ == '__main__':
    p='D:/xrdb/tools.pyx'
    text=open_utf8(p).read()
    #it=cfunc.finditer(text)
    code_lines=cut.cut(text)
    namespace= enter_model_namespace('tools', code_lines)
    pass
    #find_line(code_lines)

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
