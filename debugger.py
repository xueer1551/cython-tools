import re, sys, os
import time

import pyximport
pyximport.install(language_level=3)
import cut
import warnings, copy
# 忽略所有的 SyntaxWarning 警告
warnings.filterwarnings('ignore', category=SyntaxWarning)

内置类型=r'\s*(int|short|long|long long|double|float|char|list|tuple|dict|str|bytes|object|bytearray|Py_UCS4|struct|union|enum|class|cppclass|fused)'

def get_cython_include_path() ->str:
    p = sys.executable
    install_path = os.path.dirname(p)
    path=os.path.join(install_path, r'\Lib\site-packages\Cython\Includes')
    return path
def open_utf8(path):
    return open(path,'r',encoding='utf8')

func_args_and_suffix=r'\((?P<args>[^()]+)\)(?P<suffix>.*)'
cdef_block=re.compile(r'\s*cdef(\s+(?P<public>public|private|readonly))?\s*:', re.DOTALL)
cdef_line=re.compile(r'\s*cdef\s+(?P<content>.+)',re.DOTALL)
cdef_attr_line=re.compile(r'\s*cdef\s+(?P<public>public|private|readonly)?\s*(?P<content>[^()]+)')
cdef_struct_union_enum_fused=re.compile(r'\s*(?:cdef|ctypedef)\s+(?:.+?)?(?P<type>struct|union|enum|fused)\s+(?P<name>[^:]+)\s*:', re.DOTALL)
cdef_class=re.compile(r'\s*(?P<cdef>cdef|ctypedef)?\s*(?P<cppclass>cpplass|class)\s+(?P<name>[_\w]+):')
extend_class=re.compile(r'\s*(?:cdef|ctypedef)\s+(?:extern\s+)?(?P<cppclass>cpplass|class)\s+(?P<name>[_\w.]+\s*)(?P<c_struct>\[[_\w.\s]+\]\s*)?(?P<maohao>:)?', re.DOTALL)
extend_struct_union_enum_fused=cdef_struct_union_enum_fused
cdef_extend_from=re.compile(r'\s*cdef\s+(?P<public>public\s+)?extend\s+from(?P<name>.+?):', re.DOTALL)
ctypedef_bieming=re.compile(r'\s*ctypedef\s+(?P<content>[^()]+)',re.DOTALL)
from_import=re.compile(r'\s*from\s+(.+?)\s+(c?import)(?P<content>.+)', re.DOTALL)
with_=re.compile(r'\s*with\s+(.+):', re.DOTALL)
with_nogil=re.compile(r'\s*with\s+nogil\s*:')
import_=re.compile(r'\s*(c?import)\s+(?P<content>.+)', re.DOTALL)
func_name_and_arg_and_suffix=rf'(?P<type_and_name>[^()]+){func_args_and_suffix}'
modifiers_=r'(?P<modifier>(?:public\s+)?(?:api\s+)?(?:inline\s+)?(?:volatile\s+|const\s+){0,2})'
func=modifiers_+func_name_and_arg_and_suffix
extend_func=re.compile(r'\s*'+func, re.DOTALL)
cdef_func=re.compile(fr'\s*(?:async\s+)?(?:c?p?def)\s+{func}', re.DOTALL)
async_func=re.compile(rf'\s*(?:async\s+)?(?:def)\s+{func_name_and_arg_and_suffix}', re.DOTALL)
ctypedef_func0=re.compile(rf'\s*ctypedef\s+{func}', re.DOTALL)
ctypedef_func1=re.compile(rf'\s*ctypedef\s+{modifiers_}(?P<type>(?:[_\w]+\s+)+)(?:\(\s*\**(?P<name>[_\w]+)\s*\)){func_args_and_suffix}', re.DOTALL)
include=re.compile(r'\s*include\s*[\'"]{1,3}(?P<name>[^\'"]+)[\'"]{1,3}', re.DOTALL)
global_=re.compile(r'\s*global\s+(?P<name>[\w_]+)', re.DOTALL)
for_=re.compile(r'\s*for\s+(?P<content>.+)?\s+(in|from)\s+', re.DOTALL)
except_=re.compile(r'\s*except(?P<content>(?:\s+)[\w_]+)?((?:\s+as\s+)([\w_]+)\s*)?:', re.DOTALL)
other_keywords=re.compile(r'(?:[#@]|(if|elif|else|wihle|continue|try|raise|finally|match|case|return|await)[\s(:]|pass|break)', re.DOTALL)
need_keywords=re.compile(r'(cdef|cpdef|ctypedef|def|with|for|from|cimport|include|async|global|class|except)\s', re.DOTALL)
no_used=re.compile('(?:\s*[#@\'"\n])')
extend_keyword=re.compile('(ctypedef|cdef)')
all_kongbai=re.compile(r'(?:\s+)')
left_value_express=re.compile(r'([_\w,]+)\s*[+\-*/:=]{1,2}\s*(.+)', re.DOTALL)
declare_var=re.compile('([^=]+)(=.+)?',re.DOTALL)
memoryview_=re.compile(r'\[[^:]*:[^\]]*\]', re.DOTALL)
shuzu=re.compile(r'\[\s*([0-9]*)\s*\]',re.DOTALL)
name_=re.compile(r'[_\w]+',re.DOTALL)
fanxing=re.compile(r'\[.+\]',re.DOTALL)
words_=re.compile(r'[\w_]+')
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
_nogil='nogil'

#-----------------------------------------------------------------------------------------------------------------------

class Model:
    __slots__ = ('name', 'path', 'suffix', 'classes', 'funcs', 'vars', 'c_declare_vars','types', 'cimport', 'from_cimport', 'includes')
    def __init__(self, name:str, path:str, suffix:str, ):
        self.name, self.path, self.suffix = name, path, suffix
        self.funcs, self.vars, self.cimport, self.from_cimport, self.includes = {},{},{},{},[]
        self.types={}
        self.c_declare_vars={}

def create_func(rr:re.Match, parent_vars_symbol_table: dict) :
    modifier_text, type_and_name_text, args_text, suffix_text = rr.groups()
    modifier = tuple(words_.findall(modifier_text))
    return_type, func_name = get_func_return_type_and_name(type_and_name_text, modifier)
    args_text_ = cut.cut_douhao_and_strip(args_text)
    func = Func(func_name, return_type, args_text, suffix_text)
    parent_vars_symbol_table[func_name] = func
    for arg_text in args_text_:
        tt, var_name, _ = get_type_and_name(arg_text)
        if var_name:  # 不是(a,b,*,c,d)中的*
            func.vars[var_name] = tt
    return func


class Func:
    __slots__ = ('name', 'return_type', 'args_text', 'suffix_text', 'nogil', 'c_declare_vars', 'vars')
    def __init__(self, name:str, return_type: str, args_text: str, suffix_text:str):
        self.name, self.return_type, self.args_text, self.suffix_text = name, return_type, args_text, suffix_text
        args = {}
        get_cdef_func_args(self.args_text, args)
        self.c_declare_vars, self.vars= args,  copy.deepcopy(args)
        if nogil_.search(suffix_text):
            self.nogil=True
        else:
            self.nogil=False
    def cdef_block_line_func(self, line: str, model:Model):
        var_names = decode_cdef_line(line, self.c_declare_vars)
        return var_names
    def line_func(self, code_line:str, model:Model):
        r=cdef_line.match(code_line)
        if r:
            content=r.groups()[0]
            var_names=decode_cdef_line(content, self.c_declare_vars)
            return var_names
        #
        r=left_value_express.match(code_line)
        if r:
            get_left_express(r, self.vars)

class FuncSignature:
    __slots__ = ('name', 'return_type', 'args_text', 'suffix_text', 'nogil')
    def __init__(self, name:str, return_type: str, args_text: str, suffix_text:str):
        self.name, self.return_type, self.args_text, self.suffix_text = name, return_type, args_text, suffix_text
        if nogil_.search(suffix_text):
            self.nogil=True
        else:
            self.nogil=False


class CimportModel:
    __slots__ = ('from_text', 'name', 'path', 'from_text_is_pxd')
    def __init__(self, from_text:str, name:str):
        self.from_text, self.name = from_text, name
        levels = from_text.replace('.', '/')
        if os.path.exists(levels):
            path = levels
        else:
            pp = get_cython_include_path()
            path = os.path.join(pp, levels)
            if os.path.exists(levels):
                pass
            else:
                raise FileNotFoundError
        if os.path.isdir(path):
            self.path=path
            self.from_text_is_pxd=False
        else:
            pxd =path+'.pxd'
            if os.path.exists(pxd):
                self.path=pxd
                self.from_text_is_pxd=True
            else:
                raise FileNotFoundError


class Ctype:
    __slots__ = ( 'base_type_name', 'modifiers', 'ptr_levels', 'memoryview')  # 指针和数组都被视为ptr_level，只不过指针是运行期变长
    def __init__(self, base_type_name:tuple, modifier, ptr_level: list, memoriview:bool):
        self.base_type_name, self.modifiers, self.ptr_levels = base_type_name, modifier, ptr_level
        self.memoryview = memoriview
    def __hash__(self):
        return hash(self.name)
    def __add__(self, ptr_level: list) :
        assert not self.memoryview
        return Ctype(self.base_type_name, self.modifiers, ptr_level+self.ptr_levels, False)


class CClass:
    __slots__ = ('name', 'type', 'public_attrs','private_attrs','readonly_attrs', 'funcs' )
    def __init__(self, name:str, type:str,):
        #type -> class or cppclass
        self.name, self.type = name, type
        self.public_attrs, self.readonly_attrs, self.private_attrs = {}, {}, {}
        self.funcs={}
    def public_line_func(self, line:str, model:Model):
        var_names = decode_cdef_line(line, self.public_attrs)
        return var_names
    def readonly_line_func(self, line:str, model:Model):
        var_names = decode_cdef_line(line, self.readonly_attrs)
        return var_names
    def private_line_func(self, line:str, model:Model):
        var_names = decode_cdef_line(line, self.private_attrs)
        return var_names


class Struct:
    __slots__ = ('name', 'var_mapping_type')
    def __init__(self, name: str):
        self.name = name
        self.var_mapping_type={}
    def line_func(self, line:str, model:Model):
        decode_cdef_line(line, self.var_mapping_type)
        return False

class Union:
    __slots__ = ('name', 'type_mapping_type')
    def __init__(self, name: str):
        self.name = name
        self.type_mapping_type={}
    def line_func(self, line:str, model:Model):
        decode_cdef_line(line, self.type_mapping_type)
        return False

class Enum:
    __slots__ = ('name', 'vars')
    def __init__(self, name: str):
        self.name = name
        self.vars=[]
    def line_func(self, line:str, model:Model):
        words=words_.findall(line)
        assert len(words)==1
        self.vars.append(words[0])
        return False

class Fused:
    __slots__ = ('name', 'types')
    def __init__(self,name: str):
        self.name=name
        self.types=[]
    def line_func(self, line: str, model:Model):
        words = words_.findall(line)
        assert len(words) == 1
        self.types.append(words[0])
        return False
    def enter(self, code_lines:list, start_i:int, l:int, lines:list, model:Model, line_func ):
        for i in range(start_i, l):
            line = code_lines[i]
            code_line, suojin_len, start_lineno, end_lino = line
            if suojin_len > 0:  # 仍在块中
                lines[i] = (line, line_func(line, model), model)

#-----------------------------------------------------------------------------------------------------------------------
timeout=5000
def enter_pyx(folder:str, filename:str):
    assert filename[-4:]=='.pyx'
    name=filename[:-4]
    path=os.path.join(folder, filename)
    model=Model(name, path, '.pyx')
    f=open_utf8(path)
    text=f.read()
    code_lines=cut.cut_line(text)
    lines=enter_model_block(code_lines, model)
    return lines

def enter_model_block( code_lines: iter,  model:Model )->int:
    i=0
    l=len(code_lines)
    lines = [None] * l
    t0=time.time()
    pre_i, pre_enter = 0, None
    while (i<l):
        print(i)
        line = code_lines[i]
        code_line, suojin_len, _, __ = line
        assert suojin_len==0
        r=cdef_func.match(code_line)
        t1 = time.time()
        if t1 - t0 > timeout: raise TimeoutError
        if r:
            lines[i] = (model, None, line)
            func=create_func(r, model.funcs)
            i=enter_func_block(code_lines, suojin_len, i+1, l, lines, func, model)
            assert pre_i < i
            pre_i, pre_enter = i, 0
            continue
        #
        r=cdef_class.match(code_line)
        if r:
            _, type, name = r.groups()
            lines[i]=(model, None, line)
            cls=CClass(name, type)
            i=enter_class_block(code_lines, suojin_len, i+1, l, lines, cls, model)
            assert pre_i < i
            pre_i, pre_enter = i, 1
            continue
        r=cdef_struct_union_enum_fused.match(code_line)
        if r:
            i=enter_struct_union_enum_fused_block(r, code_lines, suojin_len, i+1, l, lines, model)
            assert pre_i < i
            pre_i, pre_enter = i, 2
            continue
        #
        r=cdef_extend_from.match(code_line)
        if r:
            lines[i] = (model, None, line)
            i=enter_extend_block(code_lines, suojin_len, i+1, l, lines, model)
            assert pre_i < i
            pre_i, pre_enter = i, 3
            continue
        #
        comment_line_func(code_line, model.c_declare_vars, model.vars, model)
        i+=1
        assert pre_i<i
        pre_i, pre_enter = i, 4
    return lines



def enter_func_block( code_lines: iter, sj_len: int, start_i: int, l: int, lines:list, func:Func, model:Model ):
    i=start_i
    t0 = time.time()
    while(i<l):
        line=code_lines[i]
        code_line, suojin_len, _, __ = line
        if suojin_len>sj_len:
            t1 = time.time()
            if t1 - t0 > timeout: raise TimeoutError
            cdef_sj_len=suojin_len
            r = cdef_block.match(code_line)
            if r:
                lines[i]=(func, None, '')
                for ii in range(i+1, l):
                    line = code_lines[i]
                    code_line, suojin_len, _, __ = line
                    if suojin_len > cdef_sj_len:
                        lines[ii] = (func, func.cdef_block_line_func(code_line, model), code_line[:cdef_sj_len]+_cdef+code_line)
                    else:
                        i=ii
                        break
                continue

            else:
                comment_line_func(code_line, func.c_declare_vars, func.vars, model)
                i+=1
        else:
            return i
    return l

def enter_class_block( code_lines: iter, sj_len: int, start_i: int, l: int, lines:list, cls:CClass, model:Model )->int:
    i = start_i
    t0 = time.time()
    pre_i, pre_enter=0, None
    while (i < l):
        #print(i)
        line = code_lines[i]
        code_line, suojin_len, _, __ = line
        t1 = time.time()
        if t1 - t0 > timeout:
            raise TimeoutError
        if suojin_len > sj_len:
            #
            r=cdef_block.match(code_line)
            if r:
                public=r.groups()[0]
                if public == 'readonly':
                    i=enter_block(code_lines, suojin_len, cls.readonly_line_func, i+1,l, lines, cls, model)
                elif public == 'public':
                    i=enter_block(code_lines, suojin_len, cls.public_line_func, i+1,l, lines, cls, model)
                else:
                    i=enter_block(code_lines, suojin_len, cls.private_line_func, i+1,l, lines, cls, model)
                assert pre_i < i
                pre_i, pre_enter=i, 0
                continue
            #
            r=cdef_func.match(code_line)
            if r:
                func=create_func(r, cls.funcs)
                i=enter_func_block(code_lines, suojin_len, i+1, l, lines, func, model)
                assert pre_i < i
                pre_i, pre_enter = i, 1
                continue
            #
            r = cdef_attr_line.match(code_line)
            if r:
                public, content = r.groups()
                if public == 'readonly':
                    attr_names = cls.readonly_line_func(code_line, model)
                elif public == 'public':
                    attr_names = cls.public_line_func(code_line, model)
                else:
                    attr_names = cls.private_line_func(code_line, model)
                lines[i] = (cls, attr_names, code_line)
                i += 1
                assert pre_i < i
                pre_i, pre_enter = i, 2
                continue
            #
            r=no_used.match(code_line)
            if r:
                i+=1
                assert pre_i < i
                pre_i, pre_enter = i, 3
                continue
            raise AssertionError
        else:
            return i
    return l


def enter_struct_union_enum_fused_block( rr: re.Match, code_lines: iter, sj_len: int, start_i: int, l: int, lines:list, model:Model )->int:
    block=get_struct_union_enum_fused_block(rr, model.types)
    return enter_block(code_lines, sj_len, block.line_func, start_i, l, lines, block, model)


def comment_line_func(code_line: str, c_declare_vars: dict, vars: dict, model:Model):
    #
    r=other_keywords.match(code_line)
    if r:
        return False
    #
    r = cdef_line.match(code_line)
    if r:
        content = r.groups()[0]
        var_names = decode_cdef_line(content, c_declare_vars)
        return var_names
    #
    r = left_value_express.match(code_line)
    if r:
        names=get_left_express(r, vars)
        return names
    r=with_nogil.match(code_line)
    if r:
        return _nogil
    #
    for keyword_re in (for_, with_, except_):
        r = keyword_re.match(code_line)
        if r:
            d=r.groupdict()
            names = get_as_biemings(d['content'])
            return [x[0] for x in names]
    #
    r=import_.match(code_line)
    if r:
        cimport, names_text=r.groups()
        if cimport:
            names = get_as_biemings(names_text)
            for bieming, name in names:
                model.from_cimport[bieming]=CimportModel('', name, )
            model.cimport.update(names)
            return False
    #
    r=from_import.match(code_line)
    if r:
        from_text, cimport, names_text = r.groups()
        if cimport:
            names=get_as_biemings(names_text)
            for bieming, name in names:
                model.from_cimport[bieming]=CimportModel(from_text, name )
            return False
    #
    r=global_.match(code_line)
    if r:
        name=r.groups()[0]
        return [name]
    #
    r=include.match(code_line)
    if r:
        name=r.groups()[0]
        model.includes.append(name)
        return False
    return False

d0={'struct':Struct, 'union': Union, 'enum':Enum, 'fused':Fused}
def get_struct_union_enum_fused_block(rr: re.Match, type_symbol_table: dict):
    g=rr.groups()
    t, name = g
    cls=d0[t]
    block=cls(name)
    type_symbol_table[name] =block
    return block

def enter_block( code_lines: iter, sj_len: int, line_func:callable,  start_i: int, l: int, lines:list, block, model ) ->int:
    for i in range(start_i, l):
        line = code_lines[i]
        code_line, suojin_len, _, __ = line
        if suojin_len > sj_len:
            lines[i]=(block, line_func(code_line, model), code_line)
        else:
            return i
    return l

def enter_extend_block(  code_lines: iter, sj_len: int,  start_i: int, l: int, lines:list, model:Model ):
    i=start_i
    t0 = time.time()
    while(i<l):
        t1 = time.time()
        if t1 - t0 > timeout: raise TimeoutError
        line=code_lines[i]
        code_line, suojin_len, _, __ = line
        if suojin_len>sj_len:
            if extend_no_used.match(code_line):continue
            #
            r=extend_struct_union_enum_fused.match(code_line)
            if r:
                enter_struct_union_enum_fused_block(r, code_lines, sj_len, start_i, l, lines, model)
                continue
            #
            r=extend_func.match(code_line)
            if r:
                get_extend_func_signature(r, model.funcs)
                #get_cdef_func_signature(r, model.funcs, {})
                lines[i]=(model, r, code_line)
                continue
            #
            r=cdef_func.match(code_line)
            if r:
                get_extend_func_signature(r, model.funcs)
                lines[i]=(model, r, code_line)
                i=break_block(code_lines, sj_len, i+1, l)
        else:
            return i
    return l

def get_ctypede_type_bieming(rr :re.Match, type_symbol_table: dict):
    content = rr.groups()
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_kongbai(content)
    l = len(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    if l==2:
        t, name, _= get_2_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
        type_symbol_table[name] = t
    else:
        assert l==1
        words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
        r = get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
        assert all(r)
        t, name, _ = r
        type_symbol_table[name] = t

def get_ctypedef_func0_signature(rr: re.Match, type_symbol_table: dict):
    modifier_text, type_and_name_text, args_text, suffix_text= rr.groups()
    modifier = tuple(words_.findall(modifier_text))
    return_type, name = get_func_return_type_and_name(type_and_name_text, modifier)
    if return_type is object: assert not modifier
    t=FuncSignature(name, return_type, args_text, suffix_text)
    type_symbol_table[name]=t
    #
get_extend_func_signature=get_ctypedef_func0_signature

def get_ctypedef_func1_signature(rr: re.Match, type_symbol_table: dict):
    modifier_text, type_text, name_text, args_text, suffix_text = rr.groups()
    modifier = tuple(words_.findall(modifier_text))
    #
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_kongbai(type_text)
    t, name, _ = get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    #
    name = name_text.strip()
    #
    type_symbol_table[name]=t

def get_cdef_func_signature(rr: re.Match, parent_vars_symbol_table: dict, self_vars_symbol_table: dict):
    _, modifier_text, type_and_name_text, args_text, suffix_text=rr.groups()
    get_func(modifier_text, type_and_name_text, args_text, suffix_text, parent_vars_symbol_table)

def get_func(modifier_text, type_and_name_text, args_text, suffix_text, parent_vars_symbol_table: dict, self_vars_symbol_table: dict):
    modifier = tuple(words_.findall(modifier_text))
    return_type, func_name = get_func_return_type_and_name(type_and_name_text, modifier)
    #print(modifier_text, type_and_name_text, args_text, suffix_text)
    args_text_ = cut.cut_douhao_and_strip(args_text)
    t = FuncSignature(func_name, return_type, args_text, suffix_text)
    parent_vars_symbol_table[func_name]=t
    for arg_text in args_text_:
        tt, var_name, _ = get_type_and_name(arg_text)
        if var_name: #不是(a,b,*,c,d)中的*
            self_vars_symbol_table[var_name]=tt

strip_type_zhushi=re.compile('')
def get_cdef_func_args(args_text: str, symbol_table:dict): #注意ctypedef的不能用这个
    #print(args_text, '////')
    type_and_names=cut.cut_douhao_and_strip(args_text)
    for type_and_name in type_and_names:
        t, name, _=get_type_and_name(type_and_name)
        symbol_table[name]=t

def get_left_express(rr: re.Match, symbol_table:dict) ->list[str]:
    left, right=rr.groups()
    vars=words_.findall(left)
    return vars

def decode_cdef_line(line: str, symbol_table: dict) ->list[str]:
    var_names=[]
    vars = cut.cut_douhao_and_strip(line)
    l = len(vars)
    first_text = vars[0]
    left, right = declare_var.search(first_text).groups()
    first_var_type, first_var_name, shared_type = get_type_and_name(left)
    symbol_table[first_var_name] = first_var_type
    var_names.append(first_var_name)
    if (type(shared_type) is Ctype and not shared_type.memoryview):
        for i in range(1, l):
            text = vars[i]
            r = left_value_express.search(text)
            if r:
                left, right = r.groups()
            else:
                left = words_.findall(text)
                assert len(left)==1
                left=left[0]
                right=None
            words_xinghaocount_xinghaos_fangkuohao_stat_s=cut.split_by_fangkuohao_and_del_yuan_kuohao(left)
            assert len(words_xinghaocount_xinghaos_fangkuohao_stat_s)==1
            words, xinghao_count, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
            assert len(words)==1
            name=words[0]
            assert stat is None or type(stat) is int
            ptr_level=get_ptr_level(xinghao_count, fangkuohao, stat)
            t = shared_type + ptr_level
            symbol_table[name] = t
            var_names.append(name)
        return var_names
    else: #memoryview 或者 cppclass
        for i in range(1, l):
            text = vars[i]
            left, right = left_value_express.search(text).groups()
            names=words_.findall(left)
            assert len(names)==1
            name=names[0]
            symbol_table[name] = first_var_type
            var_names.append(name)
        return var_names

def get_cdef_line(rr: re.Match, symbol_table: dict):
    text=rr.groups()[0]
    return decode_cdef_line(text, symbol_table)

def get_func_return_type_and_name(text: str, modifier):
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_yuan_kuohao(text)
    t, name, _ = get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    return t, name

def get_as_biemings(content: str) ->list[tuple[str,str]]:
    codens=cut.cut_douhao_and_strip(content)
    l=[]
    for coden in codens:
        tokens=words_.findall(coden)
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
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_yuan_kuohao(content)
    l=len(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    if l==1:
        r=get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
        return r
    else:
        assert l==2
        return get_2_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)

def get_2_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s):
    l=len(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
    assert not stat is None
    tc=type(stat)
    if tc is int:
        modifier, base_type =get_modifier_and_base_type(words)
        shared_ptr_level=get_ptr_level(xinghaocount, fangkuohao, stat)
        shared_type=Ctype(base_type, modifier, shared_ptr_level, False)
        #
        words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[1]
        assert len(words)==1
        ptr_level1=get_ptr_level(xinghaocount, fangkuohao, stat)
        name=words[0]
        ptr_level = ptr_level1+shared_ptr_level
        t=Ctype(base_type, modifier, ptr_level, False)
        return t, name, shared_type
    elif stat is cut.typed_memoryview:
        modifier, base_type = get_modifier_and_base_type(words)
        ptr_level = get_ptr_level(xinghaocount, fangkuohao, stat)
        assert not ptr_level
        t=Ctype(base_type, modifier, ptr_level, True)
        #
        words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[1]
        assert stat is None #无括号
        assert len(words) == 1
        name=words[0]
        return t, name, t
    elif stat is cut.cppclass:
        assert len(words)==1
        tname=words[0]
        t=CClass(tname,cut.cppclass)
        #
        words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[1]
        assert len(words)==1
        assert stat is None
        vname=words[1]
        return t, vname, t

def get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s):
    words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
    assert stat is None or type(stat) is int
    ptr_level = get_ptr_level(xinghaocount, fangkuohao, stat)
    l=len(words)
    if l>1:
        name, words = words[-1], words[:-1]
        modifier, base_type = get_modifier_and_base_type(words)
        t = Ctype(base_type, modifier, ptr_level, False)
        return t, name, t
    elif l==1: # *args, **, name only。 或者是不声明返回类型的cython函数名。 或者是 int *a, *b中的*b
        assert stat is None
        name=words[0]
        return object, name, None
    else: #函数参数里(a,b,*,c,d)
        assert xinghaocount==1
        return None, None, None


def get_ptr_level(xinghao_count:int, fangkuohao:str, stat: int) -> list[int | None]:
    if not stat is None:
        assert fangkuohao
        pl = shuzu.findall(fangkuohao[1])
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

if __name__ == '__main__':
    folder='D:/xrdb'
    filenames= os.listdir(folder)
    for filename in filenames:
        if '.pyx'==filename[-4:]:
            lines=enter_pyx(folder, filename)
            print('ok,', filename)


# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
