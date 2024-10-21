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
with_nogil=re.compile(r'\s*with\s+(nogil|gil)\s*:')
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
_gil='gil'

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
    __slots__ = ('name', 'return_type', 'args_text', 'suffix_text', 'nogil', 'c_declare_vars', 'args', 'vars', 'cpdef', 'text')
    def __init__(self, name:str, return_type: str, args_text: str, suffix_text:str, cpdef: str, text):
        self.name, self.return_type, self.args_text, self.suffix_text = name, return_type, args_text, suffix_text
        self.cpdef = cpdef
        self.text=text
        self.args={}
        if args_text:
            args = {}
            get_cdef_func_args(self.args_text, args)
            self.c_declare_vars, self.vars, self.args = args,  list(args.keys()), copy.deepcopy(args)
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
    def have_fused_arg(self, ctype_mapping_final_type: dict):
        for arg in self.args.values():
            if isinstance(arg, Ctype):
                final_t: FinalCtype = ctype_mapping_final_type[arg]
                ft = final_t.type
                if isinstance(ft , Fused):
                    return True
        return False
    def get_all_symbol(self):
        return set(self.vars).union(set(self.c_declare_vars.keys()))

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

start_with_keyword=re.compile(r'(?:\s*)(public|readonly|private)')
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
    def block_line_func(self, line:str, model):
        line0 = start_with_keyword.match(line)
        if line0:
            g = line0.groups()[0]
            line0=start_with_keyword.sub('',line)
            if g=='readonly':
                return self.readonly_line_func(line0, model)
            elif g=='public':
                return self.public_line_func(line0, model)
            else:
                return self.private_line_func(line0, model)
    def get_all_symbol(self):
        return set(self.public_attrs.keys()).union(self.readonly_attrs.keys()).union(self.funcs.keys()).union(self.private_attrs.keys())



class Struct(M):
    __slots__ = ('name', 'var_mapping_type', 'lines' )
    def __init__(self, name: str):
        self.name = name
        self.var_mapping_type={}
        self.lines=[]
    def line_func(self, line:str, model:Model):
        decode_cdef_line(line, self.var_mapping_type)
        self.lines.append(line)
        return None
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
    @property
    def appeared_types(self, ):
        return self.var_mapping_type.values()


class Union(M):
    __slots__ = ('name', 'type_mapping_type', 'lines')
    def __init__(self, name: str):
        self.name = name
        self.type_mapping_type={}
        self.lines=[]
    def line_func(self, line:str, model:Model):
        decode_cdef_line(line, self.type_mapping_type)
        self.lines.append(line)
        return None
    def get_show_func_name(self, symbols:set,  ):
        name = self.name.title()
        cls_name = get_name(name, symbols)
        func_name = get_name(f'show_{name}', symbols)
        return cls_name, func_name
    @property
    def defined(self):
        return self.var_mapping_type

    @property
    def appeared_types(self, ):
        return self.var_mapping_type.values()

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
    __slots__ = ('name', 'define_struct_union_enum_fuseds')
    def __init__(self,name: str):
        self.name=name
        self.define_struct_union_enum_fuseds=[]
    def line_func(self, line: str, model:Model):
        words_xinghaocount_xinghaos_fangkuohao_stat_s = cut.split_by_fangkuohao_and_del_yuan_kuohao(line)
        assert len(words_xinghaocount_xinghaos_fangkuohao_stat_s)==1
        words, xinghaocount, _, fangkuohao, stat = words_xinghaocount_xinghaos_fangkuohao_stat_s[0]
        if xinghaocount!=0: raise NotImplementedError
        if not fangkuohao: raise NotImplementedError
        words=tuple([x.strip() for x in words] )
        t = Ctype( tuple(words), (None,None), [], False)
        self.define_struct_union_enum_fuseds.append(t)
        return None
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
        return self.define_struct_union_enum_fuseds
    @property
    def appeared_types(self, ):
        return self.define_struct_union_enum_fuseds


    
class FinalCtype(M):
    def __init__(self, t: Struct|Union|Enum|Fused|FuncSignature|object|tuple, modifiers, ptr_levels):
        self.type, self.modifiers, self.ptr_levels = t, modifiers, ptr_levels
    def __repr__(self):
        return f'{self.type}: FinalCtype'
    def get_call_show_text(self, var_name:str, model:Model):
        if self.type is object:
            return var_name
        else:
            if self.ptr_levels:
                if not self.type is FuncSignature: #不是函数指针
                    if isinstance(self.type, tuple):#内置类型指针
                        type_name=self.type[0]
                        if not type_name=='void' and not type_name=='Py_buffer': #已知类型指针
                            show_base_type_func_name:str = model.show_func_names[self.type]
                        else: #void指针
                            assert len(self.ptr_levels) > 1
                            show_base_type_func_name: str = model.show_no_define_type_func_name
                        base_type_name = ' '.join(self.type)
                        return f'{model.ptr_class_name}().set(&{var_name}, {self.ptr_levels}, &{show_base_type_func_name}, sizeof({base_type_name}))'
                    else: #Struct or Union or Enum or Fused
                        if not isinstance(self.type , Fused):
                            base_type_name = self.type.name
                            show_base_type_func_name:str = model.show_func_names[base_type_name]
                            return f'{model.ptr_class_name}().set(&{var_name}, {self.ptr_levels}, &{show_base_type_func_name}, sizeof({base_type_name}))'
                        else:
                            show_base_type_func_name: str = model.fused_ptr_show_func_names[self.type]
                            return f'{show_base_type_func_name}(&{var_name}, {self.ptr_levels})'
                        #

                else: #函数指针
                    if len(self.ptr_levels)==1:
                        return f'{model.show_func_ptr_name}({var_name})'
                    else:
                        show_base_type_func_name:str = model.show_func_ptr_name
                        return f'{model.ptr_class_name}().set(&{var_name}, {self.ptr_levels}, &{show_base_type_func_name}, sizeof(void*))'
            else:
                if not self.type is FuncSignature:
                    show_func_name = model.show_func_names[self.type]
                    if not isinstance(self.type, Fused):
                        return f'{show_func_name}(&{var_name})'
                    else:
                        return f'{show_func_name}({var_name})'
                else: # 省略了*的函数指针
                    return f'{model.show_func_ptr_name}({var_name})'

PyObject=('PyObject',)
class Model(M):
    def __init__(self, name:str, folder:str, suffix:str ):
        self.name, self.folder, self.suffix = name, folder, suffix
        self.funcs, self.vars, self.from_cimport, self.includes = {},[],{},[]
        self.classes={}
        self.cimport_biemings={}
        self.define_struct_union_enum_fuseds={}
        self.c_declare_vars={}
        self.includes_models: set=set()
        self.all_appeared_base_type: set=None
        self.all_define_ctype: set=None
        self.appeared_base_type: dict={}
        self.all_include_models: list=[]
        self.all_cimport_types: dict=None
        self.all_cimport_biemings: dict=None
        self.all_from_cimports: dict=None
        self.ctypedef_biemings: dict={}
        self.all_ctypedef_biemings: dict=None
        self.ctypedef_func_ptr: dict={}
        self.all_ctypedef_func_ptr: dict=None
        self.all_ctypedef_bieming_final_type: dict=None
        self.all_appeared_type_final_type: dict = None
        self.all_symbol: set=None
        self.cimport_lines: list=[]
        self.all_cimport_lines: list=[]

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

    def get_all_include_models(self, all_include_models):
        if not self.includes_models:
            folder = self.folder
            for filepath in self.includes:
                pyx_model=enter_pyx(folder, filepath)
                self.includes_models.add(pyx_model)
        #
        model: Model
        #all_include_models=list(self.includes_models)
        #s= self.includes_models
        for model in self.includes_models:
            model.get_all_include_models(all_include_models)
        all_include_models += list(self.includes_models)
        return all_include_models
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
                ttt = Ctype((type_name,), t.modifiers, t.ptr_levels, t.memoryview)
                final_t = pxd_model.pxd_get_define_final_type(ttt)
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
        self.get_all_include_models(self.all_include_models)
        all_classes = copy.deepcopy(self.classes)
        all_funcs = copy.deepcopy(self.funcs)
        all_from_cimports = copy.deepcopy(self.from_cimport)
        all_cimport_biemings = copy.deepcopy(self.cimport_biemings)
        all_define_ctype = copy.deepcopy(self.define_struct_union_enum_fuseds)
        all_ctypedef_biemings = copy.deepcopy(self.ctypedef_biemings)
        all_ctypedef_func_ptr = copy.deepcopy(self.ctypedef_func_ptr)
        all_vars=self.vars.copy()
        all_c_declare_vars = copy.deepcopy(self.c_declare_vars)
        self.all_cimport_lines=self.cimport_lines.copy()
        for model in self.includes_models:
            model.get_all()
            all_classes.update(model.all_classes)
            all_funcs.update(model.all_funcs)
            #all_appeared_base_type_names = merge_dict(all_appeared_base_type_names, model.all_appeared_base_type, merge_set)
            all_define_ctype.update(model.all_define_ctype)
            all_ctypedef_biemings.update(model.all_ctypedef_biemings)
            all_ctypedef_func_ptr.update(model.all_ctypedef_func_ptr)
            all_cimport_biemings.update(model.all_cimport_biemings)
            all_from_cimports.update(model.all_from_cimports)
            all_c_declare_vars.update(model.all_c_declare_vars)
            all_vars += model.all_vars
            all_cimport_biemings.update(model.all_cimport_biemings)
            self.all_cimport_lines += model.all_cimport_lines
        self.all_from_cimports = all_from_cimports
        self.all_cimport_biemings = all_cimport_biemings
        self.all_define_ctype = all_define_ctype
        #self.all_appeared_base_type = all_appeared_base_type_names
        self.all_funcs = all_funcs
        self.all_classes = all_classes
        self.all_define_ctype = all_define_ctype
        self.all_ctypedef_biemings = all_ctypedef_biemings
        self.all_ctypedef_func_ptr = all_ctypedef_func_ptr
        self.all_vars = all_vars
        self.all_c_declare_vars = all_c_declare_vars
        self.all_cimport_pxd_models: dict=None
        #
        self.get_all_appeared_base_type()
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

    def get_all_final_type(self):
        #
        all_appeared_type_final_type = {}
        for ts in self.all_appeared_base_type.values():
            for t in ts:
                final_t = self.get_define_final_type_from_ctype(t)
                all_appeared_type_final_type[t] = final_t
        self.all_appeared_type_final_type = all_appeared_type_final_type
    def get_all_appeared_base_type(self):
        if not self.appeared_base_type:
            appeared_base_type={}
            cls: CClass=None
            for cls in self.all_classes.values():
                get_funcs_appeared_base_types(cls.funcs.values(), appeared_base_type)
                get_all_c_declare_var_types(cls.public_attrs.values(), appeared_base_type)
                get_all_c_declare_var_types(cls.readonly_attrs.values(), appeared_base_type)
                get_all_c_declare_var_types(cls.private_attrs.values(), appeared_base_type)
            for t in self.all_define_ctype.values():
                if not isinstance(t, Enum):
                    get_all_c_declare_var_types(t.appeared_types, appeared_base_type)
            get_funcs_appeared_base_types(self.all_funcs.values(), appeared_base_type)
            get_all_c_declare_var_types(self.all_c_declare_vars.values(), appeared_base_type)
            get_all_c_declare_var_types(self.all_ctypedef_biemings.values(), appeared_base_type)
            self.all_appeared_base_type=appeared_base_type
        return self.all_appeared_base_type

    def get_all_cimport_types(self, cache_cimport_model: dict, cache_pxd_model: dict):
        if not self.all_cimport_types:
            if self.suffix=='.pyx':
                define_struct_union_enum_fuseds:dict =self.all_define_base_type
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

    def get_builtin_type_show_text(self):
        it = iter(builtin_types)
        next(it) #舍弃void
        for name in it:
            words = name.split(' ')
            cls_name=''
            for word in words:
                cls_name += word.title()

    def get_no_cimport_code_lines(self):
        l=[]
        for i in range(len(self.lines)):
            x=self.lines[i]
            if x:
                flag=x[1]
                if not flag is _cimport:
                    assert flag is None or isinstance(flag, list) or flag is _cdef or flag is _nogil
                    line = x[2]
                    assert isinstance(line, tuple)
                    l.append(line[0])
                else:
                    continue
        return l
    def get_all_cimport_text(self):
        t=''.join(self.all_cimport_lines)
        return t
    def get_no_cimport_text(self):
        t=''.join(self.get_no_cimport_code_lines())
        return t
    def get_all_text(self):
        text = self.get_all_cimport_text()
        text += f'\n{'#'*50}\n' + f'\n{'#'*50}\n'.join([model.get_no_cimport_text() for model in self.all_include_models])
        text += f'\n{'#'*50}\n'+self.get_no_cimport_text()
        return text
    def get_model_dbg_code(self, model:Model, folder:str, dbg_file):
        symbols = self.get_all_symbol()
        dbg_model_name: str = get_name(model.name, symbols)
        #
        enter_symbols = set(model.all_funcs.keys()).union(model.classes.keys())
        global_vars_names = get_name('global_vars', enter_symbols)
        py_enter_lines = [f'{global_vars_names}=dict()\n']
        #
        py_enter_name: str = None
        pre_block = model
        lines: list = model.lines
        dbg_lines = [f'import {dbg_model_name}']
        gil_stack = [(_gil, '', 0)]
        cur_func, cur_func_sj_len = None, None
        cur_cls = None
        i, l = 0, len(lines)
        while (i < l):
            line = lines[i]
            if line:
                block, flag, code_lines = line
                code_line, sj_len, start_lineno, end_lineno = code_lines
                sj_text = f'{code_line[:sj_len]}{gil_text}'
                #
                if isinstance(block, Func):
                    cur_func, cur_func_sj_len = block, sj_len
                    if block is pre_block:
                        pass
                    else:  # 这行是函数头
                        # 找到下一行的缩进
                        offset = i + 1
                        next_line = lines[offset]
                        while (not next_line):
                            offset += 1
                            next_line = lines[offset]
                        next_block, _, code_lines = line[2]
                        next_sj_len = code_lines[1]
                        # 查看是否是nogil函数
                        if block.nogil:
                            gil_stat, gil_text, gil_sj_len = _nogil, 'with nogil: ', sj_len
                            gil_stack.append((_nogil, gil_text, gil_sj_len))
                        #
                        sj_text = f'{code_line[:next_sj_len]}{gil_text}'
                        assert next_block is block
                        #
                        py_enter_name = get_name(block.name, symbols)
                        start_enter_text = f'{sj_text}{py_enter_name} = {dbg_model_name}_{block.name}()\n{sj_text}next({py_enter_name})'
                        dbg_lines.append(start_enter_text)
                        var_names = block.args.values()
                        show_text = self.get_show_vars_text(var_names, sj_text, py_enter_name, cur_func, model,
                                                            global_vars_names)
                        dbg_lines.append(show_text)
                        #
                        enter_text = get_enter_text(var_names, code_line, next_sj_len, start_lineno, end_lineno)
                        py_enter_lines.append(enter_text)
                        i = offset
                        continue
                elif isinstance(block, Model):
                    cur_func, py_enter_name = None, None
                    if cur_cls:  # 刚出class块
                        assert cls_min_sj_text
                        cls_symbols = cur_cls.get_all_symbol()
                        for private_attr_name, private_attr_ctype in cur_cls.private_attrs.keys():
                            show_func_name = get_name(f'show_{private_attr_name}', cls_symbols)
                            final_t: FinalCtype = model.all_appeared_type_final_type[private_attr_ctype]
                            show_text = final_t.get_call_show_text(f'self.{private_attr_name}', model)
                            method_text = f'{cls_min_sj_text}cdef {show_func_name}(self):  return {show_text}\n'
                            dbg_lines.append(method_text)
                        cls_min_sj_text = None
                    cur_cls = None
                elif isinstance(block, CClass):
                    if block is pre_block:
                        pass
                    else:
                        if isinstance(pre_block, Func):
                            cur_func, py_enter_name = None, None
                        else:
                            assert isinstance(pre_block, Model)
                            cur_cls, cls_min_sj_text = block, code_line[:sj_len]
                else:
                    raise AssertionError
                # 查询并更新当前gil状态
                if not gil_stack:
                    pass
                else:
                    while (gil_stack):
                        gil_stat, gil_text, gil_sj_len = gil_stack.pop()
                        if gil_sj_len > sj_len:
                            break
                        else:
                            continue
                    gil_stack.append((gil_stat, gil_text, gil_sj_len))
                # 生成暴露给python空间的代码
                if isinstance(flag, list):
                    var_names = flag
                    show_text = self.get_show_vars_text(var_names, sj_text, py_enter_name, cur_func, model,
                                                        global_vars_names)
                    dbg_lines.append(code_line)
                    dbg_lines.append(show_text)
                    #
                    py_enter_lines.append(get_enter_text(var_names, code_line, sj_len, start_lineno, end_lineno))
                elif flag == _cdef:  # cdef: 块 要改写成一个个cdef ……行
                    cdef_block_sj_len = sj_len
                    sj_kongbai_text = code_line[:sj_len]  # 当前cdef所在的缩进
                    # 进入cdef 块直到跳出(缩进长度小于等于块头缩进长度)
                    i += 1
                    while (i < l):
                        line = lines[i]
                        if line:
                            block, flag, code_lines = line
                            code_line, sj_len, start_lineno, end_lineno = code_lines
                            if sj_len > cdef_block_sj_len:
                                assert isinstance(flag, list)
                                var_names = flag
                                new_line = f'{sj_kongbai_text}cdef {code_line}'
                                sj_text = f'{sj_kongbai_text}{gil_text}'
                                show_text = self.get_show_vars_text(var_names, sj_text, py_enter_name, cur_func, model,
                                                                    global_vars_names)
                                dbg_lines.append(new_line)
                                dbg_lines.append(show_text)
                                #
                                enter_text = get_enter_text(var_names, new_line, sj_len, start_lineno, end_lineno)
                                py_enter_lines.append(enter_text)
                                i += 1
                            else:
                                break
                    continue
                elif flag == _nogil:
                    nogil_text = 'with gil: '
                    gil_stack.append((_nogil, nogil_text, sj_len))
                    dbg_lines.append(code_line)
                elif flag == _gil:
                    assert gil_stat == _nogil
                    gil_stack.append((_gil, '', sj_len))
                    dbg_lines.append(code_line)
                else:
                    dbg_lines.append(code_line)
            else:
                py_enter_lines.append('\n')
                dbg_lines.append('\n')
        #
        text = ''.join(dbg_lines)
        dbg_file.write(text)
        #
        enter_filename = os.path.join(folder, dbg_model_name, '.py')
        with open(enter_filename, 'w+', encoding='utf-8') as f:
            text0 = ''.join(py_enter_lines)
            f.write(text0)
    def rewrite_code_to_show(self, folder: str):
        dbg_filename = os.path.join(folder, self.name, '_dbg.pyx')
        dbg_file=open(dbg_filename, 'w+', encoding='utf-8')
        header_text = self.get_show_text()
        dbg_file.write(header_text)
        for model in self.all_include_models:
            self.get_model_dbg_code(model, folder, dbg_file)
        self.get_model_dbg_code(self, folder, dbg_file)




    def get_show_vars_text(self, var_names: list[str], sj_text:str, py_enter_name: str, cur_func:Func, model:Model, global_vars_name:str ):
        fts = []
        for var_name in var_names:
            final_t: FinalCtype = get_var_final_type(var_name, cur_func, model)
            fts.append(final_t.get_call_show_text(var_name, self))
            show_vars = ', '.join(fts)
        if cur_func:
            show_text = f'\n{sj_text}{py_enter_name}.send({show_vars})'
        else:
            assert py_enter_name is None
            new_vars= [f"{global_vars_name}['{x}']" for x in var_names]
            names = ', '.join(new_vars)
            show_text = f'\n{sj_text}{names} = {show_vars}'
        return show_text
    def get_show_text(self):
        symbols = self.get_all_symbol()
        self.ptr_class_name = get_name('Ptr', symbols)
        self.show_type_ptr_name = get_name('show_ptr', symbols)
        self.show_func_ptr_name = get_name('show_func', symbols)
        self.show_no_define_type_func_name = get_name('show_no_define_type', symbols)
        text = f'''
ctypedef {self.show_type_ptr_name}(volatile const void* ptr)

cdef {self.show_no_define_type_func_name}(volatile const void* ptr):
    raise ValueError('该类型仅声明，未定义/Not define the type, only declared')

cdef class {self.ptr_class_name}:
    cdef char* ptr
    cdef readonly list ptr_levels
    cdef readonly address
    cdef readonly len
    cdef readonly unsigned int itemsize
    cdef {self.show_type_ptr_name}* func
    def __init__(self):pass
    def __getattr__(self, i: int):
        cdef :
            char* ptr
            unsigned int offset
        if isinstance(i, int):
            if self.len:
                if i< self.len:
                    if len(self.ptr_levels)==1:
                        offset = self.itemsize*<unsigned int>i
                        return self.func(self.ptr + offset)
                    else:
                        offset = self.itemsize*<unsigned int>i
                        assert len(self.ptr_levels)>1
                        ptr=self.ptr + offset
                        return Ptr().set(<volatile const void**>ptr, self.ptr_levels[:-1], self.func, self.itemsize)
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

    cdef set(self, volatile const void** ptr, list ptr_levels, {self.show_type_ptr_name}* func, unsigned int itemsize ):
        self.ptr=<char*>ptr[0]
        self.address=<unsigned int>ptr
        self.len  = ptr_levels[-1]
        self.ptr_levels=ptr_levels[:-1]
        self.itemsize=itemsize
        self.func=func
        return self'''
        self.show_func_names=show_func_names= {}
        fused_ptr_show_func_names={}

        # 内置类型的show_func
        for name in builtin_ctypes[2:]:
            tuple_name = tuple(name.split(' '))
            class_name = get_name(get_class_name_from_tuple_name(tuple_name), symbols)
            func_name = get_name(f'show_{'_'.join(tuple_name)}', symbols)
            tt = get_builtin_type_show_text(class_name, func_name, name)
            text += tt
            show_func_names[tuple_name] = func_name
        # 定义类型的show_func
        final_t: FinalCtype =None
        s=set([Struct, Union, Enum, Fused])
        fina_ts = list(self.all_appeared_type_final_type.values())
        for final_t in fina_ts:
            t = final_t.type
            tt=type(t)
            if tt in s:
                if t.defined:
                    type_name = (t.name,)
                    func_name = get_name(f'show_{t.name}', symbols)
                    show_func_names[type_name] = func_name
                else: #未定义的struct
                    type_name = (t.name,)
                    show_func_names[type_name] = self.show_no_define_type_func_name
        #
        showed =set()
        for final_t in fina_ts:
            t = final_t.type
            tp = type(t)
            if tp in s :
                if tp not in showed:
                    if isinstance(t, Fused):
                        type_name = t.name
                        func_name =show_func_names[(type_name,)]
                        parts = t.define_struct_union_enum_fuseds
                        ptr_func_name = get_name(f'show_{type_name}_ptr', symbols)
                        tt = get_fused_show_text(type_name, func_name, parts, self)
                        ttt = call_fused_choose_base_type_show_func(type_name, ptr_func_name, parts, self)
                        text += tt+ttt
                        fused_ptr_show_func_names[type_name] = ptr_func_name
                    elif isinstance(t, Enum):
                        type_name = t.name
                        func_name = show_func_names[(type_name,)]
                        class_name = get_name(type_name.title(), symbols)
                        parts = t.vars
                        tt=get_enum_show_text(class_name, type_name, func_name, parts)
                        text += tt
                    elif isinstance(t,Struct) or isinstance(t, Union): # Struct or Union
                        type_name = t.name
                        func_name = show_func_names[(type_name,)]
                        class_name = get_name(type_name, symbols)
                        parts = t.var_mapping_type.items()
                        if parts:
                            tt=get_struct_or_union_show_text(class_name, type_name, func_name, parts, self.all_appeared_type_final_type, self)
                            text += tt
                        else:
                            assert final_t.ptr_levels
                    showed.add(tp)
                    show_func_names[type_name] = func_name
                else:
                    continue
            #
        #
        self.fused_ptr_show_func_names=fused_ptr_show_func_names
        # 函数指针的show_func
        func: Func = None
        funcs_text = []
        d_funcs_name = get_name('d_funcs', symbols)
        for func in self.all_funcs.values():
            if func.cpdef != _def:
                if not func.have_fused_arg(self.all_appeared_type_final_type):
                    funcs_text.append(f"<unsigned int><void*>&{func.name}:'''{func.text}'''")
                else:
                    continue
        text += f'\n{d_funcs_name}=' + '{' + ', '.join(funcs_text) + '}\n'
        text += f'''
cdef {self.show_func_ptr_name}(volatile const void* ptr):
    try:
        return {d_funcs_name}[<unsigned int>ptr]
    except KeyError:
        return None
        '''

        return text

def get_enter_text(var_names, code_line:str, sj_len:int, start_lineno:int, end_lineno:int):
    names_text = ', '.join(var_names)
    code_content = code_line[sj_len:]
    if end_lineno - start_lineno == 1:
        text = f'{names_text} = yield None #{code_content}'

    else:
        text = f"{names_text} = yield None #'''{code_content}'''"
    return text
final_object = FinalCtype(object, None, None)
def get_var_final_type(var_name:str, func:Func, model:Model) ->FinalCtype:
    name=(var_name,)
    if not func is None:
        try:
            t:Ctype = func.c_declare_vars[name]
            final_t = model.all_appeared_type_final_type[t]
            return final_t
        except KeyError:
            try:
                t:Ctype = model.all_c_declare_vars[name]
                final_t = model.all_appeared_type_final_type[t]
                return final_t
            except KeyError:
                return final_object

def get_class_name_from_tuple_name(tuple_name: tuple):
    text=''
    for word in tuple_name:
        text +=word.title()
    return text

def get_funcs_appeared_base_types(funcs, appeared_base_type):
    func: Func=None
    for func in funcs:
        get_all_c_declare_var_types(func.c_declare_vars.values(), appeared_base_type)
        rt = func.return_type
        if isinstance(rt, Ctype) and rt.base_type_name not in appeared_base_type:
            appeared_base_type[rt.base_type_name] = set((rt,))

builtin_ctypes=['void', 'Py_buffer','bint', 'char', 'signed char', 'unsigned char', 'short', 'unsigned short', 'signed short','int', 'unsigned int','signed int',
                'long', 'unsigned long', 'signed long', 'long long', 'unsigned long long', 'signed long long','float', 'double', 'long double',
                'float complex', 'double complex', 'long double complex', 'size_t', 'Py_ssize_t', 'Py_hash_t', 'Py_UCS4',]
builtin_cpy_types=['list','set','tuple','dict','str','unicode','bytes','bytearray','object']
kongbais=re.compile(r'\s+')
builtin_types= set()
for cts in (builtin_ctypes,builtin_cpy_types):
    for ct in cts:
        builtin_types.add(tuple(kongbais.split(ct)))
builtin_cpy_types = set([(x,) for x in builtin_cpy_types])

def get_builtin_type_show_text(class_name: str, func_name:str,type_name: str):
    text = f'''
    
cdef class {class_name}:
    cdef :
        volatile {type_name}* ptr
    cdef set(self, volatile const void* ptr):
        self.ptr=<volatile {type_name}*>ptr
        return self
    def set_from_address(self, address):
        return self.set(<volatile const void*><unsigned int>address)
    def set_from_object(self, obj):
        self.ptr[0]=<{type_name}>obj
    @property
    def ptr(self):
        return <unsigned int>self.ptr
    @property
    def v(self):
        return self.ptr[0]
'''
    text +='''
    def __repr__(self):
        return f"address in hex({self.ptr[0]}), value is {self.v}"
        '''
    text +=f'''
    
cdef {func_name}(volatile const void* ptr):
    return {class_name}().set(ptr)'''
    return text

def get_struct_or_union_show_text(class_name:str, type_name:str, func_name:str, parts, ctype_mapping_final_type:dict, model):
    text=f'''
    
cdef class {class_name}:
    cdef :
        volatile {type_name}* ptr
        dict __dict__
    cdef set(self, volatile const void* ptr):
        self.ptr=<volatile {type_name}*>ptr
        self.__dict__ = {"{"}'''
    assert parts
    for part_name, part_type in parts:
        assert isinstance(part_type, Ctype) and not part_type.memoryview
        final_t: FinalCtype = ctype_mapping_final_type[part_type]
        var_name = f'self.ptr.{part_name}'
        call_show_text = final_t.get_call_show_text(var_name, model)
        text += f' "{part_name}": {call_show_text}, '
    #
    text += '''}
        return self
        
    cpdef set_from_address(self, address):
        return self.set(<volatile const void*><unsigned int>address)
        '''
    #
    text += f'''
    
cdef {func_name}(volatile const void* ptr):
    return {class_name}().set(ptr)'''

    return text

def get_enum_show_text(class_name:str, type_name:str, func_name:str, parts,):
    text=f'''
    
cdef class {class_name}:
    cdef :
        volatile {type_name}* ptr
    cdef readonly:
        str text
        object value
    cdef set(self, volatile const void* ptr):
        self.ptr=<volatile {type_name}*>ptr
        cdef {type_name} v=self.ptr[0]
        '''
    assert parts
    it=iter(parts)
    part = next(it)
    text += f'\n        if v=={type_name}.{part}: self.v, self.text = <unsinged int>v, "{part}" '
    for part in it:
        text += f'\n        elif v=={type_name}.{part}: self.v, self.text = <unsinged int>v, "{part}" '
    text +='\n        else: raise AssertionError\n        return self'
    text +=f'''
    
cdef {func_name}(volatile const void* ptr):
    return {class_name}().set(ptr)'''

def get_fused_ctypedef_one_word(parts, symbols):
    text = ''
    part: Ctype = None
    d_words = {}
    for part in parts:
        if len(part.base_type_name) > 1:
            many_word = ' '.join(part.base_type_name)
            one_word = get_name('_'.join(part.base_type_name), symbols)
            d_words[part] = one_word
            text += f'ctypedef {many_word} {one_word}'
    return text, d_words

def get_fused_show_text(type_name:str, func_name:str, parts, model):
    text, d_words=get_fused_ctypedef_one_word(parts, model.all_symbol)
    text+=f'''
    
cdef {func_name}(volatile const {type_name}* ptr):'''
    for part in parts:
        try:
            one_word = d_words[part]
        except KeyError:
            one_word = part.base_type_name[0]
        final_t :FinalCtype=model.all_appeared_type_final_type[part] # show变量
        call_show_text = final_t.get_call_show_text('ptr', model)
        text += f'\n    if {type_name}=={one_word}: return {call_show_text}'
    return text

def call_fused_choose_base_type_show_func( type_name:str, func_name:str, parts, model ):
    text, d_words = get_fused_ctypedef_one_word(parts, model.all_symbol)
    text += f'''
    
cdef {func_name}(volatile const {type_name}* ptr, ptr_levels):'''
    for part in parts:
        try:
            one_word = d_words[part]
        except KeyError:
            one_word = part.base_type_name[0]
        final_t :FinalCtype=model.all_appeared_type_final_type[part]#show变量指针
        show_base_type_func_name = model.show_func_names[final_t.type]
        # cdef set(self, volatile const void** ptr, list ptr_levels, show_func* func, unsigned int itemsize )
        text += f'\n    if {type_name}=={one_word}: return {model.ptr_class_name}().set(<volatile const void**>&ptr, ptr_levels, &{show_base_type_func_name}, sizeof({one_word}))'
    text += '\n    raise AssertionError'
    return text
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

def get_all_c_declare_var_types(define_struct_union_enum_fuseds, all_base_type_names:dict):
    t: Ctype
    for t in define_struct_union_enum_fuseds: # t: Ctype
        if isinstance(t, Ctype):
            tbn=t.base_type_name
            if tbn in all_base_type_names:
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
    model = Model(name, folder, suffix)
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
                lines[i] = (model, None, line)
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
                lines[i] = (model, None, line)
                get_ctypedef_func0_signature(r, model.ctypedef_func_ptr)
                pre_i, pre_enter = i, 11
                i += 1
                continue
            #
            r = ctypedef_func1.match(code_line)
            if r:
                log[i] = 12
                lines[i] = (model, None, line)
                get_ctypedef_func1_signature(r, model.ctypedef_func_ptr)
                pre_i, pre_enter = i, 12
                i += 1
                continue
            #
            r=cdef_func.match(code_line)
            if r:
                log[i]=0
                func=create_func(r, model.funcs)
                if not func.nogil:
                    lines[i] = (func, None, line)
                else:
                    lines[i] = (func, _nogil, line)
                i=enter_func_block(code_lines, suojin_len, i+1, l, lines, func, model)
                assert pre_i < i
                pre_i, pre_enter = i, 0
                continue
            #
            r=cdef_struct_union_enum_fused.match(code_line)
            if r:
                log[i] = 2
                lines[i] = (model, None, line)
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
                    model.cimport_lines.append(code_line)
                    names = get_as_biemings(names_text)
                    ns=[]
                    for bieming, name in names:
                        model.cimport_biemings[(bieming,)]=name
                        model.from_cimport[name] = ''
                        ns.append(name)
                    lines[i] = (model, _cimport, line)
                else:
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
                    model.cimport_lines.append(code_line)
                    names = get_as_biemings(names_text)
                    ns=[]
                    for bieming, name in names:
                        model.cimport_biemings[(bieming,)] = name
                        model.from_cimport[name] = from_text
                        ns.append(name)
                    lines[i] = (model, _cimport, line)
                else:
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
                line = (f'#{code_line}', suojin_len, start_lineno, end_lineno )
                lines[i]=(model, None, line)
                pre_i, pre_enter = i, 9
                i += 1
                continue
            #
            if not code_line or all_kongbai.fullmatch(code_line):
                pass
            else:
                print(f'该行认为无需处理， 物理行开始和结束[{start_lineno},{end_lineno}), 内容：{code_line}，逻辑行号:{i}' )
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
                lines[i]=(func, _cdef, line)
                for ii in range(i+1, l):
                    line = code_lines[i]
                    code_line, suojin_len, _, __ = line
                    if suojin_len > cdef_sj_len:
                        lines[ii] = ( func, func.cdef_block_line_func(code_line, model), code_line[:cdef_sj_len] + _cdef + code_line )
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
                lines[i]=(cls, _cdef, line)
                if public == 'readonly':
                    i=enter_block(code_lines, suojin_len, cls.readonly_line_func, i+1,l, lines, cls, model, log, 101)
                elif public == 'public':
                    i=enter_block(code_lines, suojin_len, cls.public_line_func, i+1,l, lines, cls, model, log, 102)
                elif public =='private':
                    i=enter_block(code_lines, suojin_len, cls.private_line_func, i+1,l, lines, cls, model, log, 100)
                else:
                    i=i=enter_block(code_lines, suojin_len, cls.block_line_func, i+1,l, lines, cls, model, log, 100)
                assert pre_i < i
                pre_i, pre_enter=i, 0
                continue
            #
            r=cdef_func.match(code_line)
            if r:
                log[i] = 11
                func = create_func(r, cls.funcs)
                if not func.nogil:
                    lines[i] = (func, None, line)
                else:
                    lines[i] = (func, _nogil, line)
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
                    attr_names = cls.readonly_line_func(content, model)
                elif public == 'public':
                    attr_names = cls.public_line_func(content, model)
                else:
                    attr_names = cls.private_line_func(content, model)
                lines[i] = (cls, attr_names, line)
                i += 1
                assert pre_i < i
                pre_i, pre_enter = i, 2
                continue
            #
            r=no_used.match(code_line)
            if r:
                log[i] = 13
                lines[i] = (cls, None, line)
                i+=1
                assert pre_i < i
                pre_i, pre_enter = i, 3
                continue
            #
            r= not check_code_line_have_content(code_line)
            if r:
                log[i] = 14
                lines[i] = (cls, None, line)
                i+=1
                assert pre_i < i
                pre_i, pre_enter = i, 4
                continue
            raise AssertionError
        else:
            if jinghaozhushi.match(code_line) or all_kongbai.fullmatch(code_line): # #………………
                log[i] = 16
                lines[i] = (cls, None, line)
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
        keyword = r.groups()[0]
        return keyword
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
            if jinghaozhushi.match(code_line):
                lines[i] = (block, None, line)
            elif not all_kongbai.fullmatch(code_line):
                lines[i] = (block, line_func(code_line, model), line)
            else:
                lines[i]=(block, None, line)

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
                lines[i] = (model, None, line)
                i+=1
                continue
            #
            r=cdef_struct_union_enum_fused.match(code_line)
            if r:
                i=enter_struct_union_enum_fused_block(r, code_lines, suojin_len, i+1, l, lines, model, log, 1000)
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
                log[i]=101
                i+=1
                continue
            #
            r = ctypedef_class.match(code_line)
            if r:
                type, name,_, __ = r.groups()
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
                i=break_block(code_lines, sj_len, i+1, l)
                log[i] = 102
                continue
            #
            r = ctypedef_bieming.match(code_line)
            if r:
                log[i] = 10
                get_ctypede_type_bieming(r, model.ctypedef_biemings)
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
_none, _not ='None', 'not'
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
        type_and_name = type_and_name[:-2] if len(type_and_name)>2 and type_and_name[-1]==_none and type_and_name[-2]==_not else type_and_name
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

def get_name(name:str, names:set):
    while(name in names):
        name +='0'
    names.add(name)
    return name


def test_debug_code(pyx_path:str, output_folder:str):
    folder, filename = os.path.split(pyx_path)
    model :Model= enter_pyx(folder, filename)
    model.get_all()
    model.get_all_cimport_types({}, {})
    model.get_all_final_type()
    text = model.get_show_text()
    name, suffix = os.path.splitext(filename)
    new_filename = name + '_dbg'+suffix
    save_filepath = os.path.join(output_folder, new_filename)
    with open(save_filepath, 'w+', encoding='utf-8') as f:
        f.write(model.get_all_text())
        f.write(f'\n{'#'*50}')
        f.write(text)

def rewrite_code(pyx_path:str, output_folder:str):
    folder, filename = os.path.split(pyx_path)
    model: Model = enter_pyx(folder, filename)
    model.get_all()
    model.get_all_cimport_types({}, {})
    model.get_all_final_type()
    model.rewrite_code_to_show(output_folder)

if __name__ == '__main__':
    folder='D:/xrdb'
    test_debug_code(r"D:\xrdb\graph.pyx", 'D:/xrdb/debugger')
    #test_debug_code('D:/xrdb/graph.pyx', 'D:/xrdb/debugger')



# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
