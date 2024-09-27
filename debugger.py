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

func_args_and_suffix=r'\((?P<args>[^()]+)\)(?P<suffix>.*)'
cdef_block=re.compile(r'cdef(\s+(?P<public>public|private|readonly))?\s*:', re.DOTALL)
cdef_line=re.compile(r'cdef\s+(?P<content>.+)',re.DOTALL)
struct_union_enum_fused_class=re.compile(r'(?:cdef|ctypedef)\s+(?:.+?)?(?P<type>struct|union|enum|fused|cpplass|class)\s+(?P<name>[^:]+)\s*:', re.DOTALL)
#cdef_class=re.compile('(?:cdef|ctypedef)\s+(?:.+?)?(cpplass|class)\s+(?P<name>[_\w.]+)(?P<c_struct>\s+\[[_\w.\s]+\])?(?P<maohao>\s+:)?', re.DOTALL)
extend_struct_union_enum_fused_class=struct_union_enum_fused_class
cdef_extend_from=re.compile(r'cdef\s+(?P<public>public\s+)?extend\s+from(?P<name>.+?):', re.DOTALL)
ctypedef_bieming=re.compile(r'ctypedef\s+(?P<content>[^()]+)',re.DOTALL)
from_cimport=re.compile(r'from\s+(.+?)\s+(c?import)(.+)', re.DOTALL)
with_=re.compile(r'with\s+(?P<nogil>nogil|.+):', re.DOTALL)
cimport_=re.compile(r'cimport\s+(?P<name>.+)', re.DOTALL)
func_name_and_arg_and_suffix=rf'(?P<type_and_name>[^()]+){func_args_and_suffix}'
modifiers_=r'(?P<modifier>(?:public\s+)?(?:api\s+)?(?:inline\s+)?(?:volatile\s+|const\s+){0,2})'
func=modifiers_+func_name_and_arg_and_suffix
extend_func=re.compile(func, re.DOTALL)
cdef_func=re.compile(fr'(c?p?def)\s+{func}', re.DOTALL)
async_func=re.compile(rf'(async\s+)?(?P<cpdef>def)\s+{func_name_and_arg_and_suffix}', re.DOTALL)
ctypedef_func0=re.compile(rf'ctypedef\s+{func}', re.DOTALL)
ctypedef_func1=re.compile(rf'ctypedef\s+{modifiers_}(?P<type>(?:[_\w]+\s+)+)(?:\(\s*\**(?P<name>[_\w]+)\s*\)){func_args_and_suffix}', re.DOTALL)
include=re.compile(r'include\s*[\'"]{1,3}(?P<name>[^\'"]+)[\'"]{1,3}', re.DOTALL)
global_=re.compile(r'global\s+(?P<name>[\w_]+)', re.DOTALL)
for_=re.compile(r'for\s+(?P<names>.+)?\s+(in|from)\s+', re.DOTALL)
except_=re.compile(r'except(?P<name>(?:\s+)[\w_]+)?((?:\s+as\s+)([\w_]+)\s*)?:', re.DOTALL)
other_keywords=re.compile(r'(?:[#@]|(if|elif|else|wihle|continue|try|raise|finally|match|case|return|await)[\s(:]|pass|break)', re.DOTALL)
need_keywords=re.compile(r'(cdef|cpdef|ctypedef|def|with|for|from|cimport|include|async|global|class|except)\s', re.DOTALL)
extend_no_used=re.compile('(?:[#@\'"\n])')
extend_keyword=re.compile('(ctypedef|cdef)')
all_kongbai=re.compile(r'(?:\s+)')
left_value_express=re.compile(r'(.+)\s*[+\-*/:=]?=\s*(.+)', re.DOTALL)
memoryview_=re.compile(r'\[[^:]*:[^\]]*\]', re.DOTALL)
shuzu=re.compile(r'\[\s*([0-9]*)\s*\]',re.DOTALL)
name_=re.compile(r'[_\w]+',re.DOTALL)
fanxing=re.compile(r'\[.+\]',re.DOTALL)
words_=re.compile(r'[_\w]+')
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
class CFunc:
    __slots__ = ('name', 'return_type', 'args_text', 'args_type','suffix_text')
    def __init__(self, name:str, return_type: str, args_text: str, suffix_text:str):
        self.name, self.return_type, self.args_text, self.suffix_text = name, return_type, args_text, suffix_text

class Ctype:
    __slots__ = ( 'base_type_name', 'modifiers', 'ptr_levels', 'memoryview')  # 指针和数组都被视为ptr_level，只不过指针是运行期变长
    def __init__(self, base_type_name:tuple, modifier, ptr_level: list):
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
    d[name]=Ctype(name, t, )

def get_ctypedef_func0_signature(rr: re.Match, type_symbol_table: dict):
    modifier_text, type_and_name_text, args_text, suffix_args= rr.groups()
    modifier = tuple(words_.findall(modifier_text))
    return_type, name = get_func_return_type_and_name(type_and_name_text, modifier)
    if return_type is object: assert not modifier
    t=CFunc(name, return_type, args_text, suffix_args)
    type_symbol_table[name]=t
    #

def get_ctypedef_func1_signature(rr: re.Match, type_symbol_table: dict):
    modifier_text, type_text, name_text, args_text, suffix_args = rr.groups()
    modifier = tuple(words_.findall(modifier_text))
    #
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_kongbai(text)
    base_type, name, ptr_level = get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    t = Ctype(base_type, modifier, name, ptr_level)
    #
    name = name_text.strip()
    #
    type_symbol_table[name]=t

def get_func_args(text: str, vars_symbol_table: dict):
    type_and_names = cut.cut_douhao_and_strip(text)
    return [get_type_or_var(text) for text in type_and_names]

def get_func_return_type_and_name(text: str, modifier):
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_kongbai(text)
    base_type, name, ptr_level = get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    if base_type is object:
        assert not ptr_level
        return object, name
    else:
        return Ctype(base_type, modifier, name, ptr_level), name

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

def get_type_or_var(content: str) ->tuple[Ctype|object|None, str, list|None]:
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_kongbai(content)
    l=len(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    if l==1:
        words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
        assert stat is None or type(stat) is int
        r=get_1_fangkuohao(words, xinghaocount, fangkuohao, stat)
        assert all(r)
        return r
    else:
        assert l==2
        return get_2_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)


def get_ctypede_type_bieming(content: str):
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_kongbai(content)
    l = len(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    if l==2:
        return get_2_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    else:
        assert l==1
        words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
        r = get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
        assert all(r)
        return r

def get_2_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s):
    l=len(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
    assert type(stat) is int
    modifier, base_type =get_modifier_and_base_type(words)
    shared_ptr_level=get_ptr_level(xinghaocount, fangkuohao, stat)
    #
    words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[1]
    assert len(words)==1
    ptr_level1=get_ptr_level(xinghaocount, fangkuohao, stat)
    name=words[0]
    ptr_level = ptr_level1+shared_ptr_level
    t=Ctype(base_type, modifier, ptr_level)
    return t, name, shared_ptr_level


def get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s):
    words, xinghaocount, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
    shared_ptr_level=[]
    ptr_level = get_ptr_level(xinghaocount, fangkuohao, stat)
    l=len(words)
    if l>1:
        name, words = words[-1], words[:-1]
        modifier, base_type = get_modifier_and_base_type(words)
        t = Ctype(base_type, modifier, ptr_level)
        return t, name, shared_ptr_level
    elif l==1: # *args, **, name only
        assert stat is None
        assert xinghaocount>0
        name=words[0]
        return object, name, None
    else: #函数参数里(a,b,*,c,d)
        assert xinghaocount==1
        return None, None, None


def get_ptr_level(xinghao_count:int, fangkuohao:str, stat: int) -> list[int | None]:
    if not stat is None:
        assert fangkuohao
        pl = shuzu.findall(fangkuohao)
        assert len(pl) == stat
        ptr_level=[]
        for v in pl:
            if v:
                ptr_level.append(int(v))
            else:
                ptr_level.append(None)
    else:
        ptr_level = []
    ptr_level + [None] * xinghao_count
    return ptr_level

def get_modifier_and_base_type(words):
    modifier, start_i = get_const_volatile(words)
    assert start_i < len(words)
    base_type = words[start_i:]
    return modifier, base_type

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
                    keyword, name = rr.groups()
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
                #

                unknows.append((line, r, namespace))
            elif keyword==_ctypedef:
                #
                rr = struct_union_enum_fused_class.match(code_line)
                if rr:
                    g=rr.groups()
                    namespace=NameSpace()
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
                pass
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
                pass
            elif keyword == _with:
                pass
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

def enter_struct_union_enum_fused_namespace(name: str, type_, line_func,  code_lines: iter, sj_len: int, parent_namespace: tuple, start_i: int, l: int, lines: list):
    namespace = NameSpace(type_, name, [], sj_len, parent_namespace, start_i)
    for i in range(start_i+1, l):
        line = code_lines[i]
        code_line, suojin_len, start_lineno, end_lino = line
        if suojin_len > sj_len:  # 仍在块中
            lines[i]=(line, line_func(line), namespace)

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
