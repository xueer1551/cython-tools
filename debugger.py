import re, sys, os
import pyximport
pyximport.install(language_level=3)
import cut
import warnings, copy
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
from_import=re.compile(r'\s*from\s+(.+?)\s+(c?import)(?P<content>.+)', re.DOTALL)
with_=re.compile(r'\s*with\s+(?P<nogil>nogil|.+):', re.DOTALL)
import_=re.compile(r'c?import\s+(?P<content>.+)', re.DOTALL)
func_name_and_arg_and_suffix=rf'(?P<type_and_name>[^()]+){func_args_and_suffix}'
modifiers_=r'(?P<modifier>(?:public\s+)?(?:api\s+)?(?:inline\s+)?(?:volatile\s+|const\s+){0,2})'
func=modifiers_+func_name_and_arg_and_suffix
extend_func=re.compile(func, re.DOTALL)
cdef_func=re.compile(fr'(c?p?def)\s+{func}', re.DOTALL)
async_func=re.compile(rf'(async\s+)?(?P<cpdef>def)\s+{func_name_and_arg_and_suffix}', re.DOTALL)
ctypedef_func0=re.compile(rf'ctypedef\s+{func}', re.DOTALL)
ctypedef_func1=re.compile(rf'ctypedef\s+{modifiers_}(?P<type>(?:[_\w]+\s+)+)(?:\(\s*\**(?P<name>[_\w]+)\s*\)){func_args_and_suffix}', re.DOTALL)
include=re.compile(r'include\s*[\'"]{1,3}(?P<name>[^\'"]+)[\'"]{1,3}', re.DOTALL)
global_=re.compile(r'\s*global\s+(?P<name>[\w_]+)', re.DOTALL)
for_=re.compile(r'\s*for\s+(?P<content>.+)?\s+(in|from)\s+', re.DOTALL)
except_=re.compile(r'\s*except(?P<content>(?:\s+)[\w_]+)?((?:\s+as\s+)([\w_]+)\s*)?:', re.DOTALL)
other_keywords=re.compile(r'(?:[#@]|(if|elif|else|wihle|continue|try|raise|finally|match|case|return|await)[\s(:]|pass|break)', re.DOTALL)
need_keywords=re.compile(r'(cdef|cpdef|ctypedef|def|with|for|from|cimport|include|async|global|class|except)\s', re.DOTALL)
extend_no_used=re.compile('(?:[#@\'"\n])')
extend_keyword=re.compile('(ctypedef|cdef)')
all_kongbai=re.compile(r'(?:\s+)')
left_value_express=re.compile(r'([_\w,]+)\s*[+\-*/:=]?=\s*(.+)', re.DOTALL)
declare_var=re.compile('([^=]+)(=.+)?',re.DOTALL)
memoryview_=re.compile(r'\[[^:]*:[^\]]*\]', re.DOTALL)
shuzu=re.compile(r'\[\s*([0-9]*)\s*\]',re.DOTALL)
name_=re.compile(r'[_\w]+',re.DOTALL)
fanxing=re.compile(r'\[.+\]',re.DOTALL)
words_=re.compile(r'[_\w]+')
nogil_=re.compile('nogil')
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
class Model:
    __slots__ = ('name', 'path', 'suffix', 'classes', 'funcs', 'vars')

class FuncSignature:
    __slots__ = ('name', 'return_type', 'args_text', 'suffix_text', 'nogil')
    def __init__(self, name:str, return_type: str, args_text: str, suffix_text:str):
        self.name, self.return_type, self.args_text, self.suffix_text = name, return_type, args_text, suffix_text
        if nogil_.search(suffix_text):
            self.nogil=True
        else:
            self.nogil=False

class Func:
    __slots__ = ('name', 'return_type', 'args_text', 'suffix_text', 'nogil', 'c_declare_vars', 'vars')
    def __init__(self, name:str, return_type: str, args_text: str, args: dict, suffix_text:str):
        self.name, self.return_type, self.args_text, self.suffix_text = name, return_type, args_text, suffix_text
        self.c_declare_vars, self.vars= args,  copy.deepcopy(args)
        if nogil_.search(suffix_text):
            self.nogil=True
        else:
            self.nogil=False
    def cdef_block_line_func(self, line: str):
        var_names = decode_cdef_line(line, self.c_declare_vars)
        return var_names
    def line_func(self, line:str):
        r=cdef_line.match(line)
        if r:
            content=r.groups()[0]
            var_names=decode_cdef_line(content, self.c_declare_vars)
            return var_names
        #
        r=left_value_express.match(line)
        if r:
            get_left_express(r, self.vars)


class Ctype:
    __slots__ = ( 'base_type_name', 'modifiers', 'ptr_levels', 'memoryview')  # 指针和数组都被视为ptr_level，只不过指针是运行期变长
    def __init__(self, base_type_name:tuple, modifier, ptr_level: list):
        self.base_type_name, self.modifiers, self.ptr_levels = base_type_name, modifier, ptr_level
    def __hash__(self):
        return hash(self.name)
    def __add__(self, ptr_level: list) :
        return Ctype(self.base_type_name, self.modifiers, ptr_level+self.ptr_levels)

class CClass:
    __slots__ = ('name', 'type', 'attrs' )
    def __init__(self, name:str, type:str,):
        #type -> class or cppclass
        self.name, self.type = name, type
        self.attrs={}


class Variable:
    __slots__ = ('name', 'type', 'set_value')
    def __init__(self, name:str, type: [Ctype|CClass|object], set_value:str):
        self.name, self.type, self.set_value = name, type, set_value

class Struct:
    __slots__ = ('name', 'var_mapping_type')
    def __init__(self, name: str):
        self.name = name
        self.var_mapping_type={}
    def line_func(self, line:str):
        decode_cdef_line(line, self.var_mapping_type)
        return False

class Union:
    __slots__ = ('name', 'type_mapping_type')
    def __init__(self, name: str):
        self.name = name
        self.type_mapping_type={}
    def line_func(self, line:str):
        decode_cdef_line(line, self.type_mapping_type)
        return False

class Enum:
    __slots__ = ('name', 'vars')
    def __init__(self, name: str):
        self.name = name
        self.vars=[]
    def line_func(self, line:str):
        words=words_.findall(line)
        assert len(words)==1
        self.vars.append(words[0])
        return False

class Fused:
    __slots__ = ('name', 'types')
    def __init__(self,name: str):
        self.name=name
        self.types=[]
    def line_func(self, line: str):
        words = words_.findall(line)
        assert len(words) == 1
        self.types.append(words[0])
        return False
    def enter(self, code_lines:list, start_i:int, l:int, lines:list, model:Model, line_func ):
        for i in range(start_i, l):
            line = code_lines[i]
            code_line, suojin_len, start_lineno, end_lino = line
            if suojin_len > 0:  # 仍在块中
                lines[i] = (line, line_func(line), model)

#-----------------------------------------------------------------------------------------------------------------------
d0={'struct':Struct, 'union': Union, 'enum':Enum, 'fused':Fused}

def comment_line_func(line: str, c_declare_vars: dict, vars: dict, model_vars:dict):
    #
    r=other_keywords.match(line)
    if r:
        return False
    #
    r = cdef_line.match(line)
    if r:
        content = r.groups()[0]
        var_names = decode_cdef_line(content, c_declare_vars)
        return var_names
    #
    r = left_value_express.match(line)
    if r:
        names=get_left_express(r, vars)
        return names
    #
    for keyword_re in (for_, with_, except_, import_, from_import):
        r = keyword_re.match(line)
        if r:
            d=r.groupdict()
            names = get_as_biemings(d['content'])
            return [x[0] for x in names]
    #
    r=global_.match(line)
    if r:
        name=r.groups()[0]
        return [name]
    #
    for kw in (import_, from_import):pass


    

def enter_struct_union_enum_fused_class_type_and_name(rr: re.Match, type_symbol_table: dict, vars_symbol_table: dict, mode:Model):
    g=rr.groups()
    t, name = g
    cls=d0[t]
    type_symbol_table[name] =cls(name)
    return

def get_ctypede_type_bieming(rr :re.Match, type_symbol_table: dict):
    content = rr.groups()
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_kongbai(content)
    l = len(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    if l==2:
        t, name, _= get_2_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
        type_symbol_table[t]=name
    else:
        assert l==1
        words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
        r = get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
        assert all(r)
        t, name, _ = r
        type_symbol_table[t] = name

def get_ctypedef_func0_signature(rr: re.Match, type_symbol_table: dict):
    modifier_text, type_and_name_text, args_text, suffix_text= rr.groups()
    modifier = tuple(words_.findall(modifier_text))
    return_type, name = get_func_return_type_and_name(type_and_name_text, modifier)
    if return_type is object: assert not modifier
    t=FuncSignature(name, return_type, args_text, suffix_text)
    type_symbol_table[name]=t
    #

def get_ctypedef_func1_signature(rr: re.Match, type_symbol_table: dict):
    modifier_text, type_text, name_text, args_text, suffix_text = rr.groups()
    modifier = tuple(words_.findall(modifier_text))
    #
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_kongbai(text)
    base_type, name, ptr_level = get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    t = Ctype(base_type, modifier, name, ptr_level)
    #
    name = name_text.strip()
    #
    type_symbol_table[name]=t

def get_cdef_func_signature(rr: re.Match, parent_vars_symbol_table: dict, self_vars_symbol_table: dict):
    _, modifier_text, type_and_name_text, args_text, suffix_text=rr.groups()
    modifier = tuple(words_.findall(modifier_text))
    return_type, func_name = get_func_return_type_and_name(type_and_name_text, modifier)
    args_text_ = cut.cut_douhao_and_strip(args_text)
    t = FuncSignature(func_name, return_type, args_text, suffix_text)
    parent_vars_symbol_table[func_name]=t
    for arg_text in args_text_:
        tt, var_name, _ = get_type_and_name(arg_text)
        if var_name: #不是(a,b,*,c,d)中的*
            self_vars_symbol_table[var_name]=tt

def get_left_express(rr: re.Match, symbol_table:dict) ->list[str]:
    left, right=rr.groups()
    vars=words_.findall(left)
    return vars

def decode_cdef_line(line: str, symbol_table: dict) ->list[str]:
    var_names=[]
    vars = cut.cut_douhao_and_strip(line)
    l = len(vars)
    first_text = vars[0]
    left, right = declare_var.search(vars[0]).groups()
    first_var_type, first_var_name, shared_type = get_type_and_name(left)
    symbol_table[first_var_name] = first_var_type
    var_names.append(first_var_name)
    for i in range(1, l):
        text = vars[i]
        left, right = declare_var.search(text).groups()
        var_type, var_name, _ = get_type_and_name(left)
        assert var_type is _
        t = shared_type + var_type.ptr_levels
        symbol_table[var_type] = t
        var_names.append(var_name)
    return var_names

def get_cdef_line(rr: re.Match, symbol_table: dict):
    text=rr.groups()[0]
    return decode_cdef_line(text, symbol_table)

def get_func_return_type_and_name(text: str, modifier):
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_kongbai(text)
    base_type, name, ptr_level = get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    if base_type is object:
        assert not ptr_level
        return object, name
    else:
        return Ctype(base_type, modifier, name, ptr_level), name

def get_as_biemings(content: str) ->list[tuple[str,str]]:
    codens=cut.cut_douhao_and_strip(content)
    l=[]
    for coden in codens:
        tokens=cut.cut_kongbai(coden)
        if len(tokens)==1:
            name=tokens[0]
            l.append((name,name))
        else:
            assert len(tokens)==3
            assert tokens[1]==_as
            name, bieming= tokens[0], tokens[2]
            l.append((bieming, name))
    return l

def get_type_and_name(content: str) ->tuple[Ctype|object|None, str|None, Ctype|None]:
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

def get_2_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s):
    l=len(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
    assert type(stat) is int
    modifier, base_type =get_modifier_and_base_type(words)
    shared_ptr_level=get_ptr_level(xinghaocount, fangkuohao, stat)
    shared_type=Ctype(base_type, modifier, shared_ptr_level)
    #
    words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[1]
    assert len(words)==1
    ptr_level1=get_ptr_level(xinghaocount, fangkuohao, stat)
    name=words[0]
    ptr_level = ptr_level1+shared_ptr_level
    t=Ctype(base_type, modifier, ptr_level)
    return t, name, shared_type


def get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s):
    words, xinghaocount, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
    shared_ptr_level=[]
    ptr_level = get_ptr_level(xinghaocount, fangkuohao, stat)
    l=len(words)
    if l>1:
        name, words = words[-1], words[:-1]
        modifier, base_type = get_modifier_and_base_type(words)
        t = Ctype(base_type, modifier, ptr_level)
        return t, name, t
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
                rr=import_.match(code_line)
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
    #it=FuncSignature.finditer(text)
    code_lines=cut.cut(text)
    namespace= enter_model_namespace('tools', code_lines)
    pass
    #find_line(code_lines)

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
