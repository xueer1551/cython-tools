
def get_struct_union_class( cls_name:str, struct_or_union:str):
    return f'''
class {cls_name}({struct_or_union}):
    def __init__(self, d):
        self.__dict__ = d
    '''
def get_struct_union_name( name:str, func_name:str, cls_name:str, attrs, type_mapping_show_func:dict):
    struct =f'''
cdef {func_name}({name} v):
    '''
    atts=[]
    for att in attrs:
        att_name, show_attr_func = type_mapping_show_func[att]
        atts.append(f'{att_name}:{show_attr_func}({name}.{att})')
    struct += '\n    d= {' + ', '.joi0n(atts) + '}'
    struct += f'\n    return {cls_name}(d)'
    return struct
def get_enum_show_func(name:str, func_name:str, values):
    enum=f'''
cdef {func_name}({name} v):
        cdef {name} tem '''
    for value in values:
        enum+=f'\n    if v=={name}.{value}: return enum.{name}.{value}'
    enum +='   raise AssertionError'
    return enum

def get_fused_show_func(name:str, types, func_name:str, many_word_mapping_one_word: dict):
    fused=f'''
cdef {func_name}({name} v):
        '''
    for t in types:
        type_name, show_type_func_name = many_word_mapping_one_word[t]
        fused +=f'\n    if {name}=={type_name}: return {show_type_func_name}(v)'
    fused +='\n   raise AssertionError'

many_word_builtin_types=['signed char', 'unsigned char', 'short', 'unsigned short', 'signed short','int', 'unsigned int','signed int',
                 'unsigned long', 'signed long', 'long long', 'unsigned long long', 'signed long long', 'long double',
                'float complex', 'double complex', 'long double complex',]

def many_word_to_one_word(words:str):
    one_word=''
    for word in words:
        one_word+=word.title()
    return one_word

def get_default_class_name(name, exists_names, suffix='_'):
    while (name in exists_names):
        name +=suffix
    return name

def get_many_word_builtin_types_biemings(exists_ctype_names):
    text=''
    one_word_names={}
    for name in many_word_builtin_types:
        new_name = name.replace(' ','_')
        new_name = get_default_class_name(new_name, exists_ctype_names, suffix='_')
        one_word_names[name]=new_name
        text+=f'\nctypedef {name} {new_name}'
    return text, one_word_names

def get_ctype_class_name(ctypes, exists_class_names:set):
    builtin_type_class_names={}
    for words, ptr_levels in ctypes:
        new_name = many_word_to_one_word(words)
        nn = get_default_class_name(new_name, exists_class_names)
        builtin_type_class_names[words]=nn # (unsigned,long):UnsignedLong

def create_names(names:dict, exists_names):
    d={}
    for name, new_name in names:
        nn =get_default_class_name(new_name, exists_names)
        d[name]=nn
    return d