from __future__ import annotations
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
    path=os.path.join(install_path, r'Lib\site-packages\Cython\Includes')
    return path
def open_utf8(path):
    return open(path,'r',encoding='utf8')

func_args_and_suffix=r'\((?P<args>[^()]*)\)(?P<suffix>.*)'
cdef_block=re.compile(r'\s*cdef(\s+(?P<public>public|private|readonly))?\s*:', re.DOTALL)
cdef_line=re.compile(r'\s*cdef\s+(?P<content>.+)',re.DOTALL)
cdef_attr_line=re.compile(r'\s*cdef\s+(?P<public>public|private|readonly)?\s*(?P<content>[^()]+)')
cdef_struct_union_enum_fused=re.compile(r'\s*(?:cdef|ctypedef)\s+(?:.+?)?(?P<type>struct|union|enum|fused)\s+(?P<name>[^:]+)\s*:', re.DOTALL)
cdef_class=re.compile(r'\s*(?P<cdef>cdef|ctypedef)?\s*(?P<cppclass>cpplass|class)\s+(?P<name>[_\w]+)(?P<jicheng>\s*\([^()]+\)\s*)?:', re.DOTALL)
extend_class=re.compile(r'\s*(?:cdef|ctypedef)\s+(?:extern\s+)?(?P<cppclass>cpplass|class)\s+(?P<name>[_\w.]+\s*)(?P<c_struct>\[[_\w.\s]+\]\s*)?(?P<maohao>:)?', re.DOTALL)
extend_struct_union_enum_fused=cdef_struct_union_enum_fused
cdef_extend_from=re.compile(r'\s*cdef\s+(?P<public>public\s+)?extend\s+from(?P<name>.+?):', re.DOTALL)
ctypedef_bieming=re.compile(r'\s*ctypedef\s+(?P<content>[^()]+)',re.DOTALL)
from_import=re.compile(r'\s*from\s+(.+?)\s+(c?import)(?P<content>.+)', re.DOTALL)
with_=re.compile(r'\s*with\s+(?P<content>.+):', re.DOTALL)
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
other_keywords=re.compile(r'\s*(?:[#@]|(if|elif|else|wihle|continue|try|raise|finally|match|case|return|await)|pass|break)', re.DOTALL)
need_keywords=re.compile(r'\s*(cdef|cpdef|ctypedef|def|with|for|from|cimport|include|async|global|class|except)\s', re.DOTALL)
comment_block=re.compile(r'\s*(if|elif|else|while|try|finally|match|case|with|for|except).*?:', re.DOTALL)
no_used=re.compile(r'(?:\s*[#@\'"\n])', re.DOTALL)
all_kongbai=re.compile(r'\s+')
extend_keyword=re.compile('(ctypedef|cdef)')
jinghaozhushi=re.compile(r'\s*#')
left_value_express=re.compile(r'\s*([^=+\-/:]+)\s*[+\-*/:=]?=\s*(.+)', re.DOTALL)
left_value_fuzhi_express=re.compile(r'\s*([^=+\-/:]+)\s*[:=]\s*(.+)', re.DOTALL)
declare_var=re.compile('([^=]+)(=.+)?',re.DOTALL)
memoryview_=re.compile(r'\[[^:]*:[^\]]*\]', re.DOTALL)
shuzu=re.compile(r'\[\s*([0-9]*)\s*\]',re.DOTALL)
name_=re.compile(r'[_\w]+',re.DOTALL)
fanxing=re.compile(r'\[.+\]',re.DOTALL)
words_=re.compile(r'[\w_]+',re.DOTALL)
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
class M:
    def __str__(self):
        return f'{self.name}: {type(self).__name__}'
    def __repr__(self):
        return self.__str__()
    def __hash__(self):
        return hash(self.name)


def create_func(rr:re.Match, parent_vars_symbol_table: dict) :
    modifier_text, type_and_name_text, args_text, suffix_text = rr.groups()
    modifier = tuple(words_.findall(modifier_text))
    return_type, func_name = get_func_return_type_and_name(type_and_name_text, modifier)
    func = Func(func_name, return_type, args_text, suffix_text)
    parent_vars_symbol_table[func_name] = func
    return func


class Func(M):
    __slots__ = ('name', 'return_type', 'args_text', 'suffix_text', 'nogil', 'c_declare_vars', 'vars')
    def __init__(self, name:str, return_type: str, args_text: str, suffix_text:str):
        self.name, self.return_type, self.args_text, self.suffix_text = name, return_type, args_text, suffix_text
        if args_text:
            args = {}
            get_cdef_func_args(self.args_text, args)
            self.c_declare_vars, self.vars= args,  list(args.keys())
        else:
            self.c_declare_vars, self.vars = {}, []
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

class FuncSignature(M):
    __slots__ = ('name', 'return_type', 'args_text', 'suffix_text', 'nogil')
    def __init__(self, name:str, return_type: str, args_text: str, suffix_text:str):
        self.name, self.return_type, self.args_text, self.suffix_text = name, return_type, args_text, suffix_text
        if nogil_.search(suffix_text):
            self.nogil=True
        else:
            self.nogil=False


class CimportModel(M):
    __slots__ = ('path','from_cython_model')
    def __init__(self, path:tuple[str], from_cython_model:bool):
        self.path , self.from_cython_model= path, from_cython_model

class Ctype:
    __slots__ = ( 'name','base_type_name', 'modifiers', 'ptr_levels', 'memoryview')  # 指针和数组都被视为ptr_level，只不过指针是运行期变长
    def __init__(self, base_type_name:tuple, modifier, ptr_level: list, memoriview:bool):
        self.base_type_name, self.modifiers, self.ptr_levels = base_type_name, modifier, ptr_level
        self.memoryview = memoriview
    def __hash__(self):
        return hash(self.name)
    def __str__(self):
        return str(self.base_type_name)
    def __add__(self, ptr_level: list) :
        assert not self.memoryview
        return Ctype( self.base_type_name, self.modifiers, ptr_level+self.ptr_levels, False)


class CClass(M):
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


class Struct(M):
    __slots__ = ('name', 'var_mapping_type')
    def __init__(self, name: str):
        self.name = name
        self.var_mapping_type={}
    def line_func(self, line:str, model:Model):
        decode_cdef_line(line, self.var_mapping_type)
        return False

class Union(M):
    __slots__ = ('name', 'type_mapping_type')
    def __init__(self, name: str):
        self.name = name
        self.type_mapping_type={}
    def line_func(self, line:str, model:Model):
        decode_cdef_line(line, self.type_mapping_type)
        return False

class Enum(M):
    __slots__ = ('name', 'vars')
    def __init__(self, name: str):
        self.name = name
        self.vars=[]
    def line_func(self, line:str, model:Model):
        words=words_.findall(line)
        assert len(words)==1
        self.vars.append(words[0])
        return False

class Fused(M):
    __slots__ = ('name', 'defind_types')
    def __init__(self,name: str):
        self.name=name
        self.defind_types=[]
    def line_func(self, line: str, model:Model):
        words = words_.findall(line)
        assert len(words) == 1
        self.defind_types.append(words[0])
        return False
    def enter(self, code_lines:list, start_i:int, l:int, lines:list, model:Model, line_func ):
        for i in range(start_i, l):
            line = code_lines[i]
            code_line, suojin_len, start_lineno, end_lineno = line
            if suojin_len > 0:  # 仍在块中
                lines[i] = (line, line_func(line, model), model)

class Model(M):
    __slots__ = ('name', 'path', 'suffix', 'classes', 'funcs', 'vars', 'c_declare_vars','defind_types', 'cimport_bieming',
                 'from_cimport', 'includes', 'includes_models','all_include_models', 'appeared_base_type',
                 'all_appeared_base_type','all_defind_base_type','log','lines')
    def __init__(self, name:str, path:str, suffix:str ):
        self.name, self.path, self.suffix = name, path, suffix
        self.funcs, self.vars, self.from_cimport, self.includes = {},[],{},[]
        self.classes={}
        self.cimport_bieming={}
        self.defind_types={}
        self.c_declare_vars={}
        self.all_appeared_base_type: set=None
        self.all_defind_base_type: set=None
        self.appeared_base_type: set=None
        self.all_include_models: set=None
    def cdef_line_func(self, line: str,  model):
        return decode_cdef_line(line, self.c_declare_vars)
    def get_all_include_models(self):
        if not self.all_include_models:
            model: Model
            all_include_models=self.includes_models
            for model in self.includes_models:
                m_a_i_m = model.get_all_include_models()
                all_include_models=all_include_models.union(m_a_i_m)
            self.all_include_models=all_include_models
        return self.all_include_models
    def get_defind_type_names(self):
        ctype_names = set(self.defind_types.keys())
        cclass_names = set([(x,) for x in self.classes.keys()])
        return ctype_names.union(cclass_names)
    def get_appeared_base_type(self):
        if not self.appeared_base_type:
            appeared_base_type = set()
            self.appeared_base_type = get_all_func_c_decalre_var_types(self.funcs.values(), appeared_base_type)
            self.appeared_base_type=appeared_base_type
        return self.appeared_base_type
    def get_all_appeared_base_type(self, ):
        if not self.all_appeared_base_type:
            all_base_type_names: set = set()
            get_all_func_c_decalre_var_types(self.funcs.values(), all_base_type_names)
            self.all_appeared_base_type=all_base_type_names
        return self.all_appeared_base_type
    def get_all_defind_base_type(self, ):
        if not self.all_defind_base_type:
            all_defind_base_type = self.get_defind_type_names()
            all_include_models = self.get_all_include_models()
            model: Model
            for model in all_include_models:
                all_defind_base_type= all_defind_base_type.union(model.get_defind_type_names())
            self.all_defind_base_type=all_defind_base_type
        return self.all_defind_base_type
    def get_cimport_types(self):
        defind_types=self.get_all_defind_base_type()
        appeard_types=self.get_appeared_base_type()
        s=appeard_types - builtin_types
        s -= defind_types
        return s
        
    def check_define_type(self, type_name:str):
        if type_name in self.defind_types.keys():
            return True
        else:
            for model in self.includes_models:
                if type_name in model.defind_types.keys():
                    return True
            return False

    def get_total_cimports(self, entered_): #本pyx的和递归include的
        total=set()
        for model in self.includes_models:
            total += model.get_all_appeared_base_type








builtin_ctypes=['void','bint', 'char', 'signed char', 'unsigned char', 'short', 'unsigned short', 'int', 'unsigned int', 'long', 'unsigned long', 'long long', 'unsigned long long', 'float', 'double', 'long double', 'float complex', 'double complex', 'long double complex', 'size_t', 'Py_ssize_t', 'Py_hash_t', 'Py_UCS4','Py_Unicode']
builtin_cpy_types=['list','set','tuple','dict','str','unicode','bytes','bytearray','object']
kongbais=re.compile('\s+')
builtin_types= set()
for cts in (builtin_ctypes,builtin_cpy_types):
    for ct in cts:
        builtin_types.add(tuple(kongbais.split(ct)))


#-----------------------------------------------------------------------------------------------------------------------
timeout=3*10**10


def check_cimport_model_exists( path):
    if os.path.isdir(path):
        p = path
        is_pxd = False
        return p, is_pxd
    else:
        pxd = path + '.pxd'
        if os.path.exists(pxd):
            p = pxd
            is_pxd = True
            return p, is_pxd
        else:
            return None, False

def try_get_pxd(path:str):
    for folder in ('', get_cython_include_path()):
        path = os.path.join(folder, path)
        p, is_pxd = check_cimport_model_exists(path)
        if is_pxd:
            return p, is_pxd
    return None, False

def get_cimport(text, cimport_models:dict, cache_pxds:dict):
    levels = text.replace('.', '/')
    assert len(levels)>1
    path=levels[:-1]
    name=levels[-1]
    #
    from_cython_model = False
    p, is_pxd = try_get_pxd(path)
    if is_pxd: # from_text是某个pxd文件，name是pxd里面的东西
        if p not in cache_pxds.keys():
            cm=CimportModel(p, from_cython_model)
            cimport_models[name]=cm
            cache_pxds[path]=cm
        else:
            pass
    else:
        froms = text.split('.')
        if froms[0] == 'cython':
            p = 'cython'
            from_cython_model=True
            cm = CimportModel(p, from_cython_model)
            cimport_models[name] = cm
            cache_pxds[path] = cm
        else:
            raise FileNotFoundError


def get_all_func_c_decalre_var_types(funcs, all_base_type_names: set):
    func: Func
    for func in funcs:
        get_all_c_declare_var_types(func.c_declare_vars.values(), all_base_type_names)
def get_all_c_declare_var_types(defind_types, all_base_type_names:set):
    t: Ctype
    for t in defind_types: # t: Ctype
        if isinstance(t, Ctype):
            all_base_type_names.add(t.base_type_name)



def enter_pyx(folder:str, filename:str):
    return enter_model_file(folder, filename, '.pyx')

def enter_pxd(folder:str, filename:str):
    return enter_model_file(folder, filename, '.pxd')

def enter_model_file(folder:str, filename:str, suffix:str):
    assert filename[-4:] == suffix
    name = filename[:-4]
    path = os.path.join(folder, filename)
    model = Model(name, path, suffix)
    f = open_utf8(path)
    text = f.read()
    code_lines = cut.cut_line(text)
    lines = enter_model_block(code_lines, model)
    model.lines = lines
    model.get_all_appeared_base_type()
    return model

def enter_model_block( code_lines: iter,  model:Model )->int:
    i=0
    l=len(code_lines)
    lines = [None] * l
    log=lines.copy()
    model.log=log
    t0=time.time()
    pre_i, pre_enter = 0, None
    while (i<l):
        #print(i)
        line = code_lines[i]
        code_line, suojin_len, start_lineno, end_lineno = line
        if suojin_len==0:
            #
            t1 = time.time()
            if t1 - t0 > timeout: raise TimeoutError
            #
            r=no_used.match(code_line)
            if r:
                i+=1
                continue
            #
            r = cdef_class.match(code_line)
            if r:
                _, type, name, __ = r.groups()
                lines[i]=(model, None, line)
                log[i]=1
                name=name.strip()
                cls=CClass(name, type)
                model.classes[name]=cls
                i=enter_class_block(code_lines, suojin_len, i+1, l, lines, cls, model, start_lineno, end_lineno, log)
                assert pre_i < i
                pre_i, pre_enter = i, 1
                continue
            #
            r=cdef_func.match(code_line)
            if r:
                lines[i] = (model, None, line)
                log[i]=0
                func=create_func(r, model.funcs)
                i=enter_func_block(code_lines, suojin_len, i+1, l, lines, func, model)
                assert pre_i < i
                pre_i, pre_enter = i, 0
                continue
            #
            r=cdef_struct_union_enum_fused.match(code_line)
            if r:
                log[i] = 2
                i=enter_struct_union_enum_fused_block(r, code_lines, suojin_len, i+1, l, lines, model, log, 20)
                assert pre_i < i
                pre_i, pre_enter = i, 2
                continue
            #
            r=cdef_extend_from.match(code_line)
            if r:
                log[i] = 3
                lines[i] = (model, None, line)
                i=enter_extend_block(code_lines, suojin_len, i+1, l, lines, model, log)
                assert pre_i < i
                pre_i, pre_enter = i, 3
                continue
            #
            r=cdef_block.match(code_line)
            if r:
                log[i] = 4
                lines[i] = (model, None, line)
                i=enter_block(code_lines, suojin_len,  model.cdef_line_func, i+1, l, lines, model,  model, log, 40)
                pre_i, pre_enter = i, 4
                continue
            #
            r=comment_block.match(code_line)
            if r:
                log[i] = 5
                rr=new_var_line_or_nogil(code_line, model.c_declare_vars, model.vars)
                lines[i] = (model, rr, line)
                i=model_enter_comment_block(code_lines, suojin_len, i+1, l, lines, model)
                pre_i, pre_enter = i, 5
                continue
            #
            r = ctypedef_bieming.match(code_line)
            if r:
                log[i] = 10
                get_ctypede_type_bieming(r, model.defind_types)
                lines[i] = (model, None, line)
                pre_i, pre_enter = i, 10
                i += 1
                continue
            #
            r = cdef_line.match(code_line)
            if r:
                log[i] = 6
                content = r.groups()[0]
                var_names = decode_cdef_line(content, model.c_declare_vars)
                model.vars += var_names
                lines[i]=(model, var_names, line)
                pre_i, pre_enter = i, 6
                i+=1
                continue
            #
            r = left_value_express.match(code_line)
            if r:
                log[i] = 13
                names = get_left_express(r)
                model.vars += names
                lines[i]=(model, names, line)
                pre_i, pre_enter = i, 13
                i+=1
                continue
            #
            r = ctypedef_func0.match(code_line)
            if r:
                log[i] = 11
                get_ctypedef_func0_signature(r, model.defind_types)
                pre_i, pre_enter = i, 11
                i += 1
                continue
            #
            r = ctypedef_func1.match(code_line)
            if r:
                log[i] = 12
                get_ctypedef_func1_signature(r, model.defind_types)
                pre_i, pre_enter = i, 12
                i += 1
                continue
            #
            r = import_.match(code_line)
            if r:
                log[i] = 7
                cimport, names_text = r.groups()
                if cimport == _cimport:
                    names = get_as_biemings(names_text)
                    ns=[]
                    for bieming, name in names:
                        model.cimport_bieming[bieming]=name
                        model.from_cimport[name] = ''
                        ns.append(name)
                lines[i] = (model, None, line)
                pre_i, pre_enter = i, 7
                i += 1
                continue
            #
            r = from_import.match(code_line)
            if r:
                log[i] = 8
                from_text, cimport, names_text = r.groups()
                if cimport == _cimport:
                    names = get_as_biemings(names_text)
                    ns=[]
                    for bieming, name in names:
                        model.cimport_bieming[bieming] = name
                        model.from_cimport[name] = from_text
                        ns.append(name)
                lines[i] = (model, None, line)
                pre_i, pre_enter = i, 8
                i += 1
                continue
            #
            r = include.match(code_line)
            if r:
                log[i] = 9
                name = r.groups()[0]
                model.includes.append(name)
                lines[i]=(model, None, line)
                pre_i, pre_enter = i, 9
                i += 1
                continue
            #
            if not code_line or all_kongbai.fullmatch(code_line):
                pass
            else:
                print(f'该行认为无需管， 物理行开始和结束[{start_lineno},{end_lineno}), 内容：{code_line}，逻辑行号:{i}' )
            i+=1
        else:
            if not check_code_line_have_content(code_line):
                i+=1
            else:
                raise AssertionError
    model
    return lines


def model_enter_comment_block( code_lines: iter, sj_len: int, start_i: int, l: int, lines:list, model:Model):
    i =start_i
    while (i < l):
        line = code_lines[i]
        code_line, suojin_len, start_lineno, end_lineno = line
        if suojin_len>sj_len:
            r=new_var_line_or_nogil(code_line, model.c_declare_vars, model.vars)
            lines[i]=(model, r, line)
            i+=1
        else:
            return i

def enter_func_block( code_lines: iter, sj_len: int, start_i: int, l: int, lines:list, func:Func, model:Model):
    i=start_i
    t0 = time.time()
    while(i<l):
        line=code_lines[i]
        #print(i, line)
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
                rr=new_var_line_or_nogil(code_line, func.c_declare_vars, func.vars)
                lines[i]=(func, rr, line)
                #comment_line_func(code_line, func.c_declare_vars, func.vars, model)
                i+=1
        else:
            return i
    return l

def enter_class_block( code_lines: iter, sj_len: int, start_i: int, l: int, lines:list, cls:CClass, model:Model, s_lineno:int, e_lineno:int, log:list )->int:
    i = start_i
    t0 = time.time()
    pre_i, pre_enter=0, None
    while (i < l):
        #print(i)
        line = code_lines[i]
        code_line, suojin_len, start_lineno, end_lineno = line
        t1 = time.time()
        if t1 - t0 > timeout:
            raise TimeoutError
        if suojin_len > sj_len:
            #
            r=cdef_block.match(code_line)
            if r:
                public=r.groups()[0]
                log[i] = 10
                if public == 'readonly':
                    i=enter_block(code_lines, suojin_len, cls.readonly_line_func, i+1,l, lines, cls, model)
                elif public == 'public':
                    i=enter_block(code_lines, suojin_len, cls.public_line_func, i+1,l, lines, cls, model)
                else:
                    i=enter_block(code_lines, suojin_len, cls.private_line_func, i+1,l, lines, cls, model, log, 100)
                assert pre_i < i
                pre_i, pre_enter=i, 0
                continue
            #
            r=cdef_func.match(code_line)
            if r:
                log[i] = 11
                func=create_func(r, cls.funcs)
                i=enter_func_block(code_lines, suojin_len, i+1, l, lines, func, model)
                assert pre_i < i
                pre_i, pre_enter = i, 1
                continue
            #
            r = cdef_attr_line.match(code_line)
            if r:
                log[i] = 12
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
                log[i] = 13
                i+=1
                assert pre_i < i
                pre_i, pre_enter = i, 3
                continue
            #
            r= not check_code_line_have_content(code_line)
            if r:
                log[i] = 14
                i+=1
                assert pre_i < i
                pre_i, pre_enter = i, 4
                continue
            raise AssertionError
        else:
            if jinghaozhushi.match(code_line):
                log[i] = 16
                i+=1
                continue
            else:
                log[i] = 15
                return i
    return l


def enter_struct_union_enum_fused_block( rr: re.Match, code_lines: iter, sj_len: int, start_i: int, l: int, lines:list, model:Model, log:list, log_v:list )->int:
    block=get_struct_union_enum_fused_block(rr, model.defind_types)
    return enter_block(code_lines, sj_len, block.line_func, start_i, l, lines, block, model, log, log_v)

def new_var_line_or_nogil(code_line: str, c_declare_vars: dict, vars: dict ):
    r = cdef_line.match(code_line)
    if r:
        content = r.groups()[0]
        var_names = decode_cdef_line(content, c_declare_vars)
        vars += var_names
        return var_names
    #
    r = left_value_express.match(code_line)
    if r:
        names = get_left_express(r)
        vars += names
        return names
    #
    r = with_nogil.match(code_line)
    if r:
        return _nogil
    #
    for keyword_re in (for_, with_, except_):
        r = keyword_re.match(code_line)
        if r:
            d = r.groupdict()
            names = get_as_biemings(d['content'])
            vars += names
            return [x[0] for x in names]
    #
    return None

d0={'struct':Struct, 'union': Union, 'enum':Enum, 'fused':Fused}
def get_struct_union_enum_fused_block(rr: re.Match, type_symbol_table: dict):
    g=rr.groups()
    t, name = g
    cls=d0[t]
    block=cls(name)
    type_symbol_table[(name,)] =block
    return block

def enter_block( code_lines: iter, sj_len: int, line_func:callable,  start_i: int, l: int, lines:list, block, model, log:list, log_v ) ->int:
    for i in range(start_i, l):
        line = code_lines[i]
        code_line, suojin_len, start_lineno, end_lineno = line
        if suojin_len > sj_len:
            if check_code_line_have_content(code_line):
                lines[i]=(block, line_func(code_line, model), code_line)
                log[i]=log_v
        else:
            return i
    return l

def check_code_line_have_content(code_line:str):
    if all_kongbai.fullmatch(code_line) or jinghaozhushi.match(code_line):
        return False
    else:
        return True

def enter_extend_block(  code_lines: iter, sj_len: int,  start_i: int, l: int, lines:list, model:Model, log:list ):
    i=start_i
    t0 = time.time()
    while(i<l):
        t1 = time.time()
        if t1 - t0 > timeout: raise TimeoutError
        line=code_lines[i]
        code_line, suojin_len, _, __ = line
        if suojin_len>sj_len:
            if no_used.match(code_line):continue
            #
            r=extend_struct_union_enum_fused.match(code_line)
            if r:
                i=enter_struct_union_enum_fused_block(r, code_lines, sj_len, start_i, l, lines, model)
                lines[i]=(model, r, code_line)
                log[i] = 100
                continue
            #
            r=extend_func.match(code_line)
            if r:
                get_extend_func_signature(r, model.funcs)
                #get_cdef_func_signature(r, model.funcs, {})
                lines[i]=(model, r, code_line)
                log[i]=101
                i+=1
                continue
            #
            r=cdef_func.match(code_line)
            if r:
                get_extend_func_signature(r, model.funcs)
                lines[i]=(model, r, code_line)
                i=break_block(code_lines, sj_len, i+1, l)
                log[i] = 102
                continue
        else:
            return i
    return l

def get_ctypede_type_bieming(rr :re.Match, type_symbol_table: dict):
    content = rr.groups()[0]
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_yuan_kuohao(content)
    l = len(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    if l==2:
        t, name, _= get_2_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
        name=(name.strip(),)
        type_symbol_table[name] = t
    else:
        assert l==1
        words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
        r = get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
        assert any(r)
        t, name, _ = r
        name = (name.strip(),)
        type_symbol_table[name] = t

def get_ctypedef_func0_signature(rr: re.Match, type_symbol_table: dict):
    modifier_text, type_and_name_text, args_text, suffix_text= rr.groups()
    modifier = tuple(words_.findall(modifier_text))
    return_type, name = get_func_return_type_and_name(type_and_name_text, modifier)
    name = (name.strip(),)
    if return_type is object: assert not modifier
    t=FuncSignature(name, return_type, args_text, suffix_text)
    type_symbol_table[name]=t
    #
get_extend_func_signature=get_ctypedef_func0_signature

def get_ctypedef_func1_signature(rr: re.Match, type_symbol_table: dict):
    modifier_text, type_text, name_text, args_text, suffix_text = rr.groups()
    modifier = tuple(words_.findall(modifier_text))
    #
    words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_yuan_kuohao(type_text)
    return_type, name, _ = get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    #
    name = (name_text.strip(),)
    t=FuncSignature(name, return_type, args_text, suffix_text)
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
    for type_and_name_text in type_and_names:
        r=left_value_fuzhi_express.match(type_and_name_text)
        if r:
            left, right = r.groups()
            type_and_name = left
        else:
            type_and_name=type_and_name_text
        t, name, _=get_type_and_name(type_and_name)
        symbol_table[name]=t


def get_left_express(rr: re.Match) ->list[str]:
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
            if jinghaozhushi.match(text):
                continue
            else:
                r = left_value_fuzhi_express.match(text)
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
            left, right = left_value_express.match(text).groups()
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

bieming_re=re.compile(r'[_\w.]+',re.DOTALL)
def get_as_biemings(content: str) ->list[tuple[str,str]]:
    codens=cut.cut_douhao_and_strip(content)
    l=[]
    for coden in codens:
        tokens=bieming_re.findall(coden)
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
        #
        words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[1]
        assert stat is None #无括号
        assert len(words) == 1
        name=words[0]
        t=Ctype( base_type, modifier, ptr_level, True)
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
        t = Ctype( base_type, modifier, ptr_level, False)
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

def get_folder_and_filename(filepath:str):
    folder, filename = os.path.split(filepath)
    return folder, filename

def enter_folder_all_pyx(folder:str):
    filenames=os.listdir(folder)
    filepaths=[]
    for filename in filenames:
        if filename.endswith('.pyx'):
            filepaths.append(os.path.join(folder, filename))
    return enter_pyxs(filepaths)

def enter_pyxs(file_paths):
    folders={}
    models=[]
    entered_pyxs={}
    for filepath in file_paths:
        if filepath not in entered_pyxs.keys():
            folder, filename = get_folder_and_filename(filepath)
            model = enter_pyx(folder, filename)
            models.append(model)
            entered_pyxs[filepath]=model
    enter_models_include_pyxs(models, entered_pyxs)
    return entered_pyxs

def try_enter_pyx(path:str, entered_pyxs:dict):
    if path not in entered_pyxs:
        f, n = get_folder_and_filename(path)
        model = enter_pyx(f, n)
        entered_pyxs[path] = model
        return model
    else:
        return None
def enter_model_include_pyxs(model:Model, entered_pyxs:dict):
    folder, name = get_folder_and_filename(model.path)
    ps=[]
    new_enter_model=[]
    for include in model.includes:
        path = os.path.join(folder, include)
        m=try_enter_pyx(path, entered_pyxs)
        ps.append(( include, path))
        if m :
            new_enter_model.append(m)
    model.includes=ps
    return new_enter_model
def enter_models_include_pyxs(models:list[Model], entered_pyxs:dict):
    next_enter_models=[]
    for model in models:
        new_enter_models=enter_model_include_pyxs(model, entered_pyxs)
        next_enter_models+=new_enter_models
    while(next_enter_models):
        next_enter_models1=[]
        for model in next_enter_models:
            new_enter_models = enter_model_include_pyxs(model, entered_pyxs)
            next_enter_models1 += new_enter_models
        next_enter_models=next_enter_models1
    #
    for model in models: #把model.includes中的文本都换成Model对象
        includes=[]
        includes_models=set()
        for include, path in model.includes:
            m = entered_pyxs[path]
            includes.append((m, include, path))
            includes_models.add(m)
        model.includes=includes
        model.includes_models=includes_models
    return entered_pyxs
    

def modify_cython_model(pyx_paths):
    enter_pyxs(pyx_paths)

if __name__ == '__main__':
    folder='D:/xrdb'
    entered_pyxs=enter_folder_all_pyx(folder)
    models=list(entered_pyxs.values())
    for model in models:
        #print(model.all_appeared_base_type)
        #print(model.get_all_defind_base_type())
        print(model.get_cimport_types())



# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
