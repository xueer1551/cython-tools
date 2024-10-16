from __future__ import annotations
import re, sys, os
import time

import pyximport
pyximport.install(language_level=3)
import cut
import warnings, copy

# 忽略所有的 SyntaxWarning 警告
warnings.filterwarnings('ignore', category=SyntaxWarning)

def get_cython_include_path() ->str:
    p = sys.executable
    install_path = os.path.dirname(p)
    path=os.path.join(install_path, r'Lib\site-packages\Cython\Includes')
    return path
def open_utf8(path):
    return open(path,'r',encoding='utf8')

func_args_and_suffix=r'\((?P<args>[^()]*)\)(?P<suffix>[^:]*:)'
cdef_block=re.compile(r'\s*cdef(\s+(?P<public>public|private|readonly))?\s*:', re.DOTALL)
cdef_line=re.compile(r'\s*cdef\s+(?P<content>.+)', re.DOTALL)
cdef_attr_line=re.compile(r'\s*cdef\s+(?P<public>public|private|readonly)?\s*(?P<content>[^()]+)')
cdef_struct_union_enum_fused=re.compile(r'\s*(?:cdef|ctypedef)\s+(?:.+?)?(?P<type>struct|union|enum|fused)\s+(?P<name>[^:]+)\s*:', re.DOTALL)
cdef_class=re.compile(r'\s*(?P<cdef>cdef|ctypedef)?\s*(?P<cppclass>cpplass|class)\s+(?P<name>[_\w]+)(?P<jicheng>\s*\([^()]+\)\s*)?:', re.DOTALL)
extern_class=re.compile(r'\s*(?:cdef|ctypedef)\s+(?:extern\s+)?(?P<cppclass>cpplass|class)\s+(?P<name>[_\w.]+\s*)(?P<c_struct>\[[_\w.\s]+\]\s*)?(?P<maohao>:)?', re.DOTALL)
extern_struct_union_enum_fused=re.compile(r'\s*(?:ctypedef)\s+(?:.+?)?(?P<type>struct|union|enum|fused)\s+(?P<name>[^:\s]+)', re.DOTALL)
cdef_extern_from=re.compile(r'\s*cdef\s+(?P<public>public\s+)?extern\s+from\s+(?P<name>[^:]+):', re.DOTALL)
ctypedef_bieming=re.compile(r'\s*ctypedef\s+(?P<content>[^()\'"]+)(?:\s*[\'"][^\'"]*[\'"])?',re.DOTALL)
from_import=re.compile(r'\s*from\s+(.+?)\s+(c?import)(?P<content>.+)', re.DOTALL)
with_=re.compile(r'\s*with\s+(?P<content>.+):', re.DOTALL)
with_nogil=re.compile(r'\s*with\s+nogil\s*:')
import_=re.compile(r'\s*(c?import)\s+(?P<content>.+)', re.DOTALL)
func_name_and_arg_and_suffix=rf'(?P<type_and_name>[^()]+){func_args_and_suffix}'
modifiers_=r'(?:(?:public\s+)?(?:api\s+)?(?:inline\s+)?(?P<volatile_const>volatile\s+const\s+|const\s+volatile\s+)?)'
func=modifiers_+func_name_and_arg_and_suffix
extern_func=re.compile(r'\s*'+modifiers_+r'(?P<type_and_name>[^()]+)\s*\((?P<args>[^()]*)\)(?P<suffix>.*)', re.DOTALL)
cdef_func=re.compile(fr'\s*(?:async\s+)?(?P<cpdef>c?p?def)\s+{func}', re.DOTALL)
async_func=re.compile(rf'\s*(?:async\s+)?(?:def)\s+{func_name_and_arg_and_suffix}', re.DOTALL)
ctypedef_func0=re.compile(rf'\s*ctypedef\s+'+modifiers_+r'(?P<type_and_name>[^()]+)\s*\((?P<args>[^()]*)\)(?P<suffix>.*)', re.DOTALL)
ctypedef_func1=re.compile(rf'\s*ctypedef\s+{modifiers_}(?P<type>(?:[_\w]+\s+)+)(?:\(\s*\**(?P<name>[_\w]+)\s*\))'+r'\((?P<args>[^()]*)\)(?P<suffix>.*)', re.DOTALL)
include=re.compile(r'\s*include\s*[\'"]{1,3}(?P<name>[^\'"]+)[\'"]{1,3}', re.DOTALL)
global_=re.compile(r'\s*global\s+(?P<name>[\w_]+)', re.DOTALL)
for_=re.compile(r'\s*for\s+(?P<content>.+)?\s+(in|from)\s+', re.DOTALL)
except_=re.compile(r'\s*except(?P<content>(?:\s+)[\w_]+)?((?:\s+as\s+)([\w_]+)\s*)?:', re.DOTALL)
other_keywords=re.compile(r'\s*(?:[#@]|(if|elif|else|wihle|continue|try|raise|finally|match|case|return|await)|pass|break)', re.DOTALL)
need_keywords=re.compile(r'\s*(cdef|cpdef|ctypedef|def|with|for|from|cimport|include|async|global|class|except)\s', re.DOTALL)
comment_block=re.compile(r'\s*(if|elif|else|while|try|finally|match|case|with|for|except).*?:', re.DOTALL)
no_used=re.compile(r'(?:\s*[#@\'"\n])', re.DOTALL)
all_kongbai=re.compile(r'\s+')
extern_keyword=re.compile('(ctypedef|cdef)')
jinghaozhushi=re.compile(r'\s*#')
left_value_express=re.compile(r'\s*([^=+\-/:]+)\s*[<>+\-*/:=]?=\s*(.+)', re.DOTALL)
left_value_fuzhi_express=re.compile(r'\s*([^=+\-/:<>]+)\s*[:=]\s*(.+)', re.DOTALL)
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
    cpdef, modifier_text, type_and_name_text, args_text, suffix_text = rr.groups()
    modifier = tuple(sorted(words_.findall(modifier_text))) if modifier_text else tuple()
    return_type, func_name = get_func_return_type_and_name(type_and_name_text, modifier)
    func = Func(func_name, return_type, args_text, suffix_text, cpdef, rr.group())
    parent_vars_symbol_table[func_name] = func
    return func


class Func(M):
    __slots__ = ('name', 'return_type', 'args_text', 'suffix_text', 'nogil', 'c_declare_vars', 'vars', 'cpdef', 'text')
    def __init__(self, name:str, return_type: str, args_text: str, suffix_text:str, cpdef: str, text):
        self.name, self.return_type, self.args_text, self.suffix_text = name, return_type, args_text, suffix_text
        self.cpdef = cpdef
        self.text=text
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
    __slots__ = ('path', 'from_cython_model', )
    def __str__(self):
        return str((self.path, self.from_cython_model))
    def __init__(self, path:tuple[str], from_cython_model:bool):
        self.path , self.from_cython_model= path, from_cython_model

class Ctype:
    __slots__ = ( 'name','base_type_name', 'modifiers', 'ptr_levels', 'memoryview')  # 指针和数组都被视为ptr_level，只不过指针是运行期变长
    def __init__(self, base_type_name:tuple, modifier, ptr_level: list, memoriview:bool):
        self.base_type_name, self.modifiers, self.ptr_levels = base_type_name, modifier, ptr_level
        self.memoryview = memoriview
    def __hash__(self):
        return hash(self.base_type_name)
    def __str__(self):
        return str(self.base_type_name)
    def __add__(self, ptr_level: list) :
        assert not self.memoryview
        return Ctype( self.base_type_name, self.modifiers, ptr_level+self.ptr_levels, False)
    def __eq__(self, other):
        return self.base_type_name == other.base_type_name and eq_modifiers(self.modifiers, other.modifiers) and self.ptr_levels == other.ptr_levels and self.memoryview==other.memoryview

def eq_modifiers(m0, m1):
    any0, any1 =not any(m0), not any(m1)
    if any0 == any1:
        return True
    else:
        return m0==m1
class CClass(M):
    __slots__ = ('name', 'type', 'public_attrs', 'private_attrs', 'readonly_attrs', 'funcs' )
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
    __slots__ = ('name', 'var_mapping_type', 'lines' )
    def __init__(self, name: str):
        self.name = name
        self.var_mapping_type={}
        self.lines=[]
    def line_func(self, line:str, model:Model):
        decode_cdef_line(line, self.var_mapping_type)
        self.lines.append(line)
        return False
    def get_enter(self):
        if self.var_mapping_type: #(明确了成员)
            pass
    def get_show_class_name_and_func_name(self, symbols:set,  ):
        name = self.name.title()
        cls_name = get_name(name, symbols)
        func_name = get_name(f'show_{name}', symbols)
        return cls_name, func_name
    @property
    def defined(self):
        return self.var_mapping_type
    def get_show_text(self, ):


class Union(M):
    __slots__ = ('name', 'type_mapping_type', 'lines')
    def __init__(self, name: str):
        self.name = name
        self.type_mapping_type={}
        self.lines=[]
    def line_func(self, line:str, model:Model):
        decode_cdef_line(line, self.type_mapping_type)
        self.lines.append(line)
        return False
    def get_show_func_name(self, symbols:set,  ):
        name = self.name.title()
        cls_name = get_name(name, symbols)
        func_name = get_name(f'show_{name}', symbols)
        return cls_name, func_name
    @property
    def defined(self):
        return self.var_mapping_type

class Enum(M):
    __slots__ = ('name', 'vars')
    def __init__(self, name: str):
        self.name = name
        self.vars=[]
        self.lines = []
    def line_func(self, line:str, model:Model):
        words=words_.findall(line)
        assert len(words)==1
        self.vars.append(words[0])
        return False
    def get_show_func_name(self, symbols:set,  ):
        name = self.name.title()
        cls_name = get_name(name, symbols)
        func_name = get_name(f'show_{name}', symbols)
        return cls_name, func_name

    @property
    def defined(self):
        return self.vars

class Fused(M):
    __slots__ = ('name', 'define_types')
    def __init__(self,name: str):
        self.name=name
        self.define_struct_union_enum_fuseds=[]
    def line_func(self, line: str, model:Model):
        words = words_.findall(line)
        assert len(words) == 1
        self.define_struct_union_enum_fuseds.append(words[0])
        return False
    def enter(self, code_lines:list, start_i:int, l:int, lines:list, model:Model, line_func ):
        for i in range(start_i, l):
            line = code_lines[i]
            code_line, suojin_len, start_lineno, end_lineno = line
            if suojin_len > 0:  # 仍在块中
                lines[i] = (line, line_func(line, model), model)
    def get_show_func_name(self, symbols:set,  ):
        name = self.name.title()
        func_name = get_name(f'show_{name}', symbols)
        return func_name
    @property
    def defined(self):
        return self.define_types


    
class FinalCtype(M):
    def __init__(self, t: Struct|Union|Enum|Fused|FuncSignature|object|str, modifiers, ptr_levels):
        self.type, self.modifiers, self.ptr_levels = t, modifiers, ptr_levels
    def get_call_show_text(self, var_name:str, show_funcs: dict, show_ptr_func_name:str, show_func_ptr_func_name: str):
        if self.type is object:
            return var_name
        elif self.type is FuncSignature:
            return f'{show_func_ptr_func_name}(&{var_name})'
        else:
            if not self.ptr_levels:
                show_func_name = show_funcs[self.type]
            else:
                show_func_name = show_ptr_func_name
            return f'{show_func_name}(&{var_name})'


PyObject=('PyObject',)
class Model(M):
    def __init__(self, name:str, path:str, suffix:str ):
        self.name, self.path, self.suffix = name, path, suffix
        self.funcs, self.vars, self.from_cimport, self.includes = {},[],{},[]
        self.classes={}
        self.cimport_biemings={}
        self.define_struct_union_enum_fuseds={}
        self.c_declare_vars={}
        self.includes_models: set=set()
        self.all_appeared_base_type: set=None
        self.all_define_ctype: set=None
        self.appeared_base_type: dict={}
        self.all_include_models: set=None
        self.all_cimport_types: dict=None
        self.all_cimport_biemings: dict=None
        self.all_from_cimports: dict=None
        self.ctypedef_biemings: dict={}
        self.all_ctypedef_biemings: dict=None
        self.ctypedef_func_ptr: dict={}
        self.all_ctypedef_func_ptr: dict=None
        self.all_ctypedef_bieming_final_type: dict=None
        self.all_appeared_type_final_types: dict = None
        self.all_symbol: set=None
    def cdef_line_func(self, line: str,  model):
        return decode_cdef_line(line, self.c_declare_vars)
    def get_define_ctype_show_class_and_show_func_text(self):
        symbols=self.get_all_symbol()
        for t in self.all_define_ctype:pass


    def get_all_symbol(self) ->set[str]:
        if not self.all_symbol:
            s= set().union(builtin_ctypes).union([x[0] for x in builtin_cpy_types]).union( [x[0] for x in self.all_define_ctype])
            s = s.union(self.all_funcs).union( [x[0] for x in self.all_classes]).union( [x[0] for x in self.all_ctypedef_biemings])
            s = s.union([x[0] for x in self.all_ctypedef_func_ptr]).union(self.all_from_cimports).union(self.all_vars)
            s = s.union(self.all_c_declare_vars)
            for x in s:
                assert isinstance(x, str)
            self.all_symbol = s
        return self.all_symbol

    def get_all_include_models(self):
        if not self.all_include_models:
            model: Model
            all_include_models=self.includes_models
            for model in self.includes_models:
                m_a_i_m = model.get_all_include_models()
                all_include_models=all_include_models.union(m_a_i_m)
            self.all_include_models=all_include_models
        return self.all_include_models
    def pxd_get_cdef_classes_name(self):
        d={}
        for name, cls in self.classes.items():
            names=name.split('.')
            d[(names[-1],)]=cls
        self.classes =d
    def pxd_get_define_final_type(self, t: Ctype):
        symbol: str = t.base_type_name
        while(symbol in self.ctypedef_biemings):
            tt=self.ctypedef_biemings[symbol]
            tt += t.ptr_levels
            symbol=tt.base_type_name
            t=tt
        if symbol in self.define_struct_union_enum_fuseds:
            return FinalCtype(self.define_struct_union_enum_fuseds[symbol], t.modifiers, t.ptr_levels)
        elif symbol in builtin_types or symbol in builtin_cpy_types:
            return FinalCtype(symbol, t.modifiers, t.ptr_levels)
        elif symbol in self.classes:
            assert not( any(t.modifiers) or t.ptr_levels)
            return FinalCtype(object, None, None)
        elif symbol in self.ctypedef_func_ptr:
            return FinalCtype(FuncSignature, t.modifiers, t.ptr_levels)
        else:
            raise KeyError
    def get_all_appeared_type_final_type_and_struct_union_enum_fuse_show_class_and_func(self):
        t: Ctype=None
        all_appeared_type_final_type={}
        for ts in self.all_appeared_base_type.values():
            for t in ts:
                final_t = self.get_define_final_type_from_ctype(t)
                all_appeared_type_final_type[t]=final_t
        self.all_appeared_type_final_type=all_appeared_type_final_type

    def get_define_final_type_from_ctype(self, t: Ctype|object|FuncSignature, ):
        if t is object:
            return FinalCtype(object, None,None)
        else:
            pxd_model: Model = None
            assert isinstance(t, Ctype)
            #
            if t.memoryview:
                return FinalCtype(object, None,None)
            #
            name, tt = t.base_type_name, t
            while (name in self.all_ctypedef_biemings):
                tt: Ctype = self.all_ctypedef_biemings[name]
                tt += t.ptr_levels
                name = tt.base_type_name
            t=tt
            #
            if name in self.all_classes:
                return FinalCtype(object, None, None)
            elif name in builtin_cpy_types:
                return FinalCtype(object, None, None)
            elif name in builtin_types:
                return FinalCtype(name, t.modifiers, t.ptr_levels)
            #
            elif name in self.all_define_ctype:
                ctype = self.all_define_ctype[name]
                return FinalCtype(ctype, t.modifiers, tt.ptr_levels)
            #
            elif name in self.all_cimport_types:
                pxd_and_type_name = self.all_cimport_types[name]
                pxd_model, type_name = pxd_and_type_name
                t.base_type_name = (type_name,)
                final_t = pxd_model.pxd_get_define_final_type(t)
                return final_t
            #
            elif name in self.all_ctypedef_func_ptr:
                return FinalCtype(FuncSignature, tt.modifiers, tt.ptr_levels)
            else:
                raise AssertionError

    def get_all_ctypedef_bieming_final_type(self):
        all_ctypedef_bieming_final_type={}
        for name, t in self.all_ctypedef_biemings.items():
            while(t.base_type_name in self.ctypedef_biemings):
                name = t.base_type_name
                tt = self.all_ctypedef_biemings[name]
                t = tt+t.ptr_levels
            all_ctypedef_bieming_final_type[name]=t
        self.all_ctypedef_bieming_final_type=all_ctypedef_bieming_final_type
    def get_all(self):
        all_classes = copy.deepcopy(self.classes)
        all_funcs = copy.deepcopy(self.funcs)
        all_from_cimports = copy.deepcopy(self.from_cimport)
        all_cimport_biemings = copy.deepcopy(self.cimport_biemings)
        all_define_ctype = copy.deepcopy(self.define_struct_union_enum_fuseds)
        all_ctypedef_biemings = copy.deepcopy(self.ctypedef_biemings)
        all_ctypedef_func_ptr = copy.deepcopy(self.ctypedef_func_ptr)
        all_appeared_base_type_names = self.get_appeared_base_type()
        all_vars=self.vars.copy()
        all_include_models = self.get_all_include_models()
        all_c_declare_vars = copy.deepcopy(self.c_declare_vars)
        for model in self.includes_models:
            model.get_all()
            all_classes.update(model.all_classes)
            all_funcs.update(model.all_funcs)
            all_appeared_base_type_names = merge_dict(all_appeared_base_type_names, model.all_appeared_base_type, merge_set)
            all_define_ctype.update(model.all_define_ctype)
            all_ctypedef_biemings.update(model.all_ctypedef_biemings)
            all_ctypedef_func_ptr.update(model.all_ctypedef_func_ptr)
            all_cimport_biemings.update(model.all_cimport_biemings)
            all_from_cimports.update(model.all_from_cimports)
            all_vars += model.all_vars
            all_cimport_biemings.update(model.all_cimport_biemings)
        self.all_from_cimports = all_from_cimports
        self.all_cimport_biemings = all_cimport_biemings
        self.all_define_ctype = all_define_ctype
        self.all_appeared_base_type = all_appeared_base_type_names
        self.all_funcs = all_funcs
        self.all_classes = all_classes
        self.all_define_ctype = all_define_ctype
        self.all_ctypedef_biemings = all_ctypedef_biemings
        self.all_ctypedef_func_ptr = all_ctypedef_func_ptr
        self.all_vars = all_vars
        self.all_c_declare_vars = all_c_declare_vars
        self.all_cimport_pxd_models: dict=None
        #
        self.get_all_ctypedef_bieming_final_type()
        #
        all_define_base_type = copy.deepcopy(all_define_ctype)
        for ts in ( all_classes, all_ctypedef_func_ptr, self.all_ctypedef_bieming_final_type):
            all_define_base_type.update(ts)
        self.all_define_base_type = all_define_base_type
        #
        s = set().union(builtin_ctypes).union([x[0] for x in builtin_cpy_types]).union(
            [x[0] for x in self.all_define_ctype])
        s = s.union(self.all_funcs).union([x[0] for x in self.all_classes]).union(
            [x[0] for x in self.all_ctypedef_biemings])
        s = s.union([x[0] for x in self.all_ctypedef_func_ptr]).union(self.all_from_cimports).union(self.all_vars)
        s = s.union(self.all_c_declare_vars)
        for x in s:
            assert isinstance(x, str)
        self.all_symbol = s
    def get_appeared_base_type(self):
        if not self.appeared_base_type:
            appeared_base_type={}
            for func in self.funcs.values():
                get_all_c_declare_var_types(func.c_declare_vars.values(), appeared_base_type)
                rt = func.return_type
                if isinstance(rt, Ctype) and rt.base_type_name not in appeared_base_type:
                    appeared_base_type[rt.base_type_name] = set((rt,))
            get_all_c_declare_var_types(self.c_declare_vars.values(), appeared_base_type)
            get_all_c_declare_var_types(self.ctypedef_biemings.values(), appeared_base_type)
            self.appeared_base_type=appeared_base_type
        return self.appeared_base_type

    def get_all_cimport_types(self, cache_cimport_model: dict, cache_pxd_model: dict):
        if not self.all_cimport_types:
            if self.suffix=='.pyx':
                define_types:dict =self.all_define_base_type
                appeared_types:dict =self.all_appeared_base_type
                s={}
                for name, v in appeared_types.items():
                    if name not in builtin_types and name not in self.all_define_base_type :
                        s[name]=v
                #
                all_cimport_biemings=self.all_cimport_biemings
                all_from_cimports = self.all_from_cimports
                all_cimport_types={}
                #all_cimport_ptr_level_lens={}
                for bieming, _ in s.items():
                    assert len(bieming) == 1
                    bm: str=tuple(bieming[0].split('.'))
                    bm0=(bm[0],)
                    type_name = all_cimport_biemings[bm0]
                    from_text = all_from_cimports[type_name]
                    path = '.'.join((from_text, bieming[0]))
                    pxd_path=get_cimport(path, cache_cimport_model)
                    cimport_name = path.split('.')[-1]
                    all_cimport_types[bieming]=(pxd_path, type_name)
                self.all_cimport_types=all_cimport_types
            elif self.suffix=='.pxd':
                all_cimport_types = {}
                for bieming, from_text in self.from_cimport.items():
                    bm: str = tuple(bieming[0].split('.'))
                    bm0 = (bieming,)
                    type_name = self.cimport_biemings[bm0]
                    path = '.'.join((from_text, type_name))
                    pxd_path = get_cimport(path, cache_cimport_model)
                    all_cimport_types[bieming] = pxd_path
                    cimport_name = path.split('.')[-1]
                    all_cimport_types[bieming] = (pxd_path, type_name)
                self.all_cimport_types=all_cimport_types
            else:
                raise AssertionError
            #
            if self.suffix=='.pyx':
                for bieming, path_and_type_name in self.all_cimport_types.items():
                    path, type_name = path_and_type_name
                    cimport_model: CimportModel = cache_cimport_model[path]
                    if not cimport_model.from_cython_model:
                        try:
                            pxd_model:Model = cache_pxd_model[path]
                        except KeyError:
                            folder, filename = get_folder_and_filename(path)
                            pxd_model = enter_pxd(folder, filename)
                            pxd_model.pxd_get_cdef_classes_name()
                        cache_pxd_model[path] = pxd_model
                        self.all_cimport_types[bieming] = (pxd_model, type_name)
                    else:
                        raise NotImplementedError

        #
        return self.all_cimport_types
    def get_all_symbols_and_show_names(self):
        symbols = self.get_all_symbol()
        self.ptr_class_name = get_name('Ptr', symbols)
        self.struct_class_name = get_name('Struct', symbols)
        self.union_class_name = get_name('Union', symbols)
        self.enum_class_name = get_name('Enum', symbols)
        self.funcs_name = get_name('funcs', symbols)
        #
        self.show_type_ptr_name=get_name('show_ptr', symbols)
        self.show_func_ptr_name = get_name('show_func', symbols)
        self.show_class_names= {}
        self.show_func_names={}
        #
        self.show_struct_names={}
        self.show_union_names={}
        self.show_enum_names={}
        self.show_fused_names={}
        self.show_no_define_type_func_name = get_name('show_no_define_type', symbols)
        symbols.union((self.ptr_class_name, self.struct_class_name, self.union_class_name, self.enum_class_name,
                       self.show_type_ptr_name, self.show_no_define_type_func_name, self.funcs_name))
        #
        final_type: FinalCtype=None
        for final_type in self.all_appeared_type_final_type.values():
            t : Struct|Union|Enum|Fused = final_type.type
            #
            if t is object or isinstance(t, str) or isinstance(t, FuncSignature):
                continue
            else:
                if t.defined:
                    cls_name = get_name(t.name, symbols)
                    if not isinstance(t, Fused): self.show_class_names[t] = cls_name
                    show_func_name = get_name(f'show_{t.name}', symbols)
                    self.show_func_names[t] = show_func_name
                else:
                    self.show_struct_names[t] = self.show_no_define_type_func_name
        #
        for final_type in self.all_appeared_type_final_type.values():
            if isinstance(t, Struct):
            elif isinstance(t, Union):
            elif isinstance(t, Enum):
            elif isinstance(t, Fused):

        return symbols
    def get_show_func_text(self):
        text = f'''
        ctypedef {self.show_type_ptr_name}(void* ptr)
        
        cdef {self.show_func_ptr_name}(void* ptr):
            raise ValueError('该类型仅声明，未定义/Not define the type, only declared')

        cdef class {self.ptr_class_name}:
            cdef char* ptr
            cdef readonly list ptr_levels
            cdef readonly address
            cdef readonly len
            cdef readonly unsigned int itemsize
            cdef show_func* func
            def __init__(self):pass
            def __getattr__(self, i: int):
                cdef char** ptr
                if isinstance(i, int):
                    if self.len:
                        if i< self.len:
                            if len(self.ptr_levels)==1:
                                return self.func(self.ptr + self.itemsize*i)
                            else:
                                assert len(self.ptr_levels)>1
                                ptr=<char**>(self.ptr + self.itemsize*i)
                                return Ptr().set(self.ptr, self.ptr_levels[:-1], self.show_func, self.itemsize)
                        else:
                            raise IndexError
                    else:
                        raise ValueError("请先调用set_len方法设置元素个数/please call set_len method set item count")
                else:
                    raise KeyError

            def set_len(self, l: int):
                if isinstance(l, int):
                    self.len=l
                else:
                    raise TypeError

            cdef set(self, void** ptr, list ptr_levels, show_func* func, unsigned int itemsize ):
                self.ptr=<char**>ptr[0]
                self.address=<unsigned int>ptr
                self.len  = ptr_levels[-1]
                self.ptr_levels=ptr_levels
                self.itemsize=itemsize
                self.func=func
                return self

        class {self.struct_class_name}:
            def __repr__(self):
                return self.__name__+': struct'

        class {self.union_class_name}:
            def __repr__(self):
                return self.__name__+': union'

        class {self.enum_class_name}:
            def __init__(self, name, value):
                self.name=name
                self.value=value
            def __repr__(self):
                return self.__name__+'.self.name'+': enum'
        '''
        func: Func=None
        funcs_text=[]
        for func in self.all_funcs:
            if func.cpdef != _def:
                funcs_text.append(f'<unsigned int><void*>&{func.name}:{func.name}')
        text += '\n{'+''.join(funcs_text)+'}\n'
        return text





builtin_ctypes=['void', 'bint', 'char', 'signed char', 'unsigned char', 'short', 'unsigned short', 'signed short','int', 'unsigned int','signed int',
                'long', 'unsigned long', 'signed long', 'long long', 'unsigned long long', 'signed long long','float', 'double', 'long double',
                'float complex', 'double complex', 'long double complex', 'size_t', 'Py_ssize_t', 'Py_hash_t', 'Py_UCS4','Py_Unicode']
builtin_cpy_types=['list','set','tuple','dict','str','unicode','bytes','bytearray','object']
kongbais=re.compile(r'\s+')
builtin_types= set()
for cts in (builtin_ctypes,builtin_cpy_types):
    for ct in cts:
        builtin_types.add(tuple(kongbais.split(ct)))
builtin_cpy_types = set([(x,) for x in builtin_cpy_types])


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

def get_cimport(text, cache_cimport_models:dict):
    levels = text.strip('.').split('.')
    assert len(levels)>1
    path='/'.join(levels[:-1])
    #
    from_cython_model = False
    p, is_pxd = try_get_pxd(path)
    if is_pxd: # p是pxd的路径
        if p not in cache_cimport_models.keys():
            cm=CimportModel(p, from_cython_model)
            cache_cimport_models[p]=cm
        else:
            pass
        return p
    else:
        froms = text.split('.')
        if froms[0] == 'cython':
            p = 'cython'
            from_cython_model=True
            cm = CimportModel(p, from_cython_model)
            cache_cimport_models[p]=cm
            return p
        else:
            raise FileNotFoundError

def merge_item(v0, v1): raise AssertionError
def merge_dict(d0:dict, d1:dict, func):
    if len(d0)>len(d1):
        d_long, d_short = d0, d1
    else:
        d_long, d_short = d1, d0
    d=copy.deepcopy(d_long)
    for k,v in d_short.items():
        try:
            vv=d[k]
            d[k]=func( v, vv)
        except KeyError:
            d[k]=v
    return d


def merge_list(v0:list, v1:list):
    return v0+v1
def merge_set(v0:set, v1:set):
    return v0|v1

def get_all_c_declare_var_types(define_types, all_base_type_names:dict):
    t: Ctype
    for t in define_types: # t: Ctype
        if isinstance(t, Ctype):
            tbn=t.base_type_name
            if tbn in all_base_type_names.keys():
                s=all_base_type_names[t.base_type_name]
                s.add(t)
            else:
                s=set()
                s.add(t)
                all_base_type_names[t.base_type_name]=s
        else:
            assert t is object



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
                model.classes[(name,)]=cls
                i=enter_class_block(code_lines, suojin_len, i+1, l, lines, cls, model, start_lineno, end_lineno, log)
                assert pre_i < i
                pre_i, pre_enter = i, 1
                continue
            #
            r = ctypedef_func0.match(code_line)
            if r:
                log[i] = 11
                get_ctypedef_func0_signature(r, model.ctypedef_func_ptr)
                pre_i, pre_enter = i, 11
                i += 1
                continue
            #
            r = ctypedef_func1.match(code_line)
            if r:
                log[i] = 12
                get_ctypedef_func1_signature(r, model.ctypedef_func_ptr)
                pre_i, pre_enter = i, 12
                i += 1
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
            r=cdef_extern_from.match(code_line)
            if r:
                log[i] = 3
                lines[i] = (model, None, line)
                i=enter_extern_block(code_lines, suojin_len, i+1, l, lines, model, log)
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
                get_ctypede_type_bieming(r, model.ctypedef_biemings)
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
            r = import_.match(code_line)
            if r:
                log[i] = 7
                cimport, names_text = r.groups()
                if cimport == _cimport:
                    names = get_as_biemings(names_text)
                    ns=[]
                    for bieming, name in names:
                        model.cimport_biemings[(bieming,)]=name
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
                        model.cimport_biemings[(bieming,)] = name
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
                i += 1
            else:
                raise AssertionError
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
    block=get_struct_union_enum_fused_block(rr, model.define_struct_union_enum_fuseds)
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

extern_const_var_define=re.compile(r'[_\w.\s]')
ctypedef_class=re.compile(r'\s*ctypedef\s+(cppclass|class)\s+(?P<name>[_\w.]+)\s+(\[.+?\])?(:)?', re.DOTALL)
def enter_extern_block(  code_lines: iter, sj_len: int,  start_i: int, l: int, lines:list, model:Model, log:list ):
    i=start_i
    t0 = time.time()
    while(i<l):
        #print(i)
        t1 = time.time()
        if t1 - t0 > timeout: raise TimeoutError
        line=code_lines[i]
        code_line, suojin_len, start_lineno, end_lineno = line
        if suojin_len>sj_len:
            if no_used.match(code_line):
                i+=1
                continue
            #
            r=cdef_struct_union_enum_fused.match(code_line)
            if r:
                i=enter_struct_union_enum_fused_block(r, code_lines, suojin_len, i+1, l, lines, model, log, 1000)
                lines[i]=(model, r, code_line)
                log[i] = 100
                continue
            #
            r = extern_struct_union_enum_fused.match(code_line)
            if r:
                # name, type= r.groups()
                t=get_struct_union_enum_fused_block(r, model.define_struct_union_enum_fuseds)
                i += 1
                log[i] = 100
                continue
            #
            r = ctypedef_func0.match(code_line)
            if r:
                log[i] = 11
                get_ctypedef_func0_signature(r, model.ctypedef_func_ptr)
                i += 1
                continue
            #
            r = ctypedef_func1.match(code_line)
            if r:
                log[i] = 12
                get_ctypedef_func1_signature(r, model.ctypedef_func_ptr)
                i += 1
                continue
            #
            r=extern_func.match(code_line)
            if r:
                get_extern_func_signature(r, model.funcs)
                lines[i]=(model, r, code_line)
                log[i]=101
                i+=1
                continue
            #
            r = ctypedef_class.match(code_line)
            if r:
                type, name,_, __ = r.groups()
                lines[i] = (model, None, line)
                log[i] = 1
                name = name.strip()
                cls = CClass(name, type)
                model.classes[name] = cls
                i = enter_class_block(code_lines, suojin_len, i + 1, l, lines, cls, model, start_lineno, end_lineno,
                                      log)
                continue
            #
            r=cdef_func.match(code_line)
            if r:
                get_extern_func_signature(r, model.funcs)
                lines[i]=(model, r, code_line)
                i=break_block(code_lines, sj_len, i+1, l)
                log[i] = 102
                continue
            #
            r = ctypedef_bieming.match(code_line)
            if r:
                log[i] = 10
                get_ctypede_type_bieming(r, model.ctypedef_biemings)
                lines[i] = (model, None, line)
                i += 1
                continue
            #
            i+=1
            '''if not check_code_line_have_content(code_line):
                i+=1
                continue
            raise AssertionError'''
        else:
            if not check_code_line_have_content(code_line):
                i+=1
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
    modifier = tuple(sorted(words_.findall(modifier_text))) if modifier_text else tuple()
    return_type, name = get_func_return_type_and_name(type_and_name_text, modifier)
    name = (name.strip(),)
    if return_type is object: assert not modifier
    t=FuncSignature(name, return_type, args_text, suffix_text)
    type_symbol_table[name]=t
    #
get_extern_func_signature=get_ctypedef_func0_signature

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
    modifier_text, type_and_name_text, args_text, suffix_text=rr.groups()
    get_func(modifier_text, type_and_name_text, args_text, suffix_text, parent_vars_symbol_table)

def get_func(modifier_text, type_and_name_text, args_text, suffix_text, parent_vars_symbol_table: dict, self_vars_symbol_table: dict):
    modifier = tuple(sorted(words_.findall(modifier_text))) if modifier_text else tuple()
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
    return_type, name, _ = get_1_fangkuohao(words_xinghaocount_xinghaos_fangkuohao_stat_s)
    if isinstance(return_type, Ctype):
        return_type.modifiers=modifier
    else:
        assert not modifier
    return return_type, name

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
        t=CClass(tname, cut.cppclass)
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
    ptr_level += [None] * xinghao_count
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
    
def enter_pxds(pxd_paths):
    d={}
    for pxd_path in pxd_paths:
        folder, filename = get_folder_and_filename(pxd_path)
        pxd_model = enter_pxd(folder, filename)
        pxd_model.pxd_get_cdef_classes_name()
        d[pxd_path]=pxd_model
    return d



#-----------------------------------------------------------------------------------------------------------------------
def get_builtin_ctype_class_names_and_show_func_name(model:Model):
    exists_class_names=set(model.get_all_classes().keys())
    exists_func_names=set(model.get_all_funcs().keys())
    type_mapping_class_name={}
    type_mapping_show_func_name={}
    all_base_types=model.get_all_appeared_base_type()
    for name in all_base_types:
        words = name.split(' ')
        class_name = get_name(''.join([x.title() for x in words]), exists_class_names)
        func_name = get_name('show_'+'_'.join(words), exists_func_names)
        type_mapping_class_name[name]=class_name
        type_mapping_show_func_name[name]=func_name

def get_cimport_types_name(cimport_types, pxds:dict, bultin_class_names:dict):
    for bieming, path_and_name in cimport_types:
        pxd_path, type_name = path_and_name
        pxd: Model = pxds[pxd_path]
        #if type_name in pxd

def get_struct_union_class_and_show_func(type_name:str, class_name, jicheng_name:str, type_mapping_show_func: dict):
    class_text = f'''
class {class_name}({jicheng_name}):
    def __init__(self, d):
        self.__dict__ = d
    '''
    func_text = get_struct_union_show_func(type_name, class_name, type_mapping_show_func)
    return class_text+func_text

def get_struct_union_show_func( type_name:str, class_name:str, func_name:str, var_mapping_type, type_mapping_show_func_name: dict, ctype_mapping_final_type:dict):
    text =f'''
cdef {func_name}(volatile {type_name}* vp):
    cdef {type_name} v=vp[0]
    '''
    ts=[]
    att_ctype: Ctype = None
    for att_name, att_ctype in var_mapping_type:
        assert isinstance(att_ctype, Ctype) and not att_ctype.memoryview
        final_t :FinalCtype = ctype_mapping_final_type[att_ctype]
        show_func_name : str = type_mapping_show_func_name[att_ctype]
        ts.append(f'"{att_name}":{show_func_name}(&({type_name}.{att_name}))')

    text += '\n    d= {' + ', '.joi0n(ts) + '}'
    text += f'\n    return {class_name}(d)'
    return text

def get_enum_show_func(type_name:str, jicheng:str, class_name:str, func_name:str, values):
    enum=f'''
class {class_name}({jicheng}):
    def __init__(self, text, value):
        self.text, self.value = text, value
    def __str__(self):
        return self.text
    def __repr__(self):
        return self.value
        
cdef {func_name}(volatile {type_name}* vp):
    cdef {type_name} v=vp[0] '''
    #
    for value in values:
        enum+=f'\n    if v=={type_name}.{value}: return {class_name}("{value}", <unsigned int>v)'
    enum +=f'   raise AssertionError\n   return {class_name}()'
    #
    return enum

def get_fused_show_func(type_name:str, types:list[FinalCtype], func_name:str, symbols:set, type_mapping_show_func_name: dict, ctype_mapping_final_type:dict ):
    t: Ctype=None
    t_mapping_one_word_name = {}
    names=[]
    fused=''
    for t in types:
        tb = t.base_type_name
        if len(tb)==1:
            names.append((t, tb, tb))
        else:
            t_name = get_name('_'.join(tb), symbols)
            many_word_name = " ".join(tb)
            fused += f'\nctypedef {many_word_name} {t_name}'
            names.append((t, tb, t_name))
            t_mapping_one_word_name[tb]=t_name
    #
    fused+=f'''
cdef {func_name}({type_name} v):
        '''
    for t, many_word_name, one_word_name in names:
        final_t :FinalCtype = ctype_mapping_final_type[t.base_type_name]
        fused +=f'\n    if {many_word_name}=={one_word_name}: return {}(&v)'
    fused += '\n   raise AssertionError'

def get_name(name:str, names:set):
    while(name in names):
        name +='0'
    names.add(name)
    return name

def tuple_name_to_str_name(name: tuple[str]):
    return '_'.join(name)

if __name__ == '__main__':
    folder='D:/xrdb'
    entered_pyxs=enter_folder_all_pyx(folder)
    models=list(entered_pyxs.values())
    cache_cimort_models, cache_pxd_models={}, {}
    for model in models:
        model.get_all()
        print(model, model.get_all_cimport_types({},{}))

    for model in models:
        model.get_all_appeared_type_final_type_and_struct_union_enum_fuse_show_class_and_func()
        print(model.all_appeared_type_final_types)
        symbol = model.get_all_symbol()
        print()
    print(models)


# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
