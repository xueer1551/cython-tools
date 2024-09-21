import re
import pyximport
pyximport.install(language_level=3)
import cut_line
import warnings
# 忽略所有的 SyntaxWarning 警告
warnings.filterwarnings('ignore', category=SyntaxWarning)

sj_re=re.compile(r'(?=\n)\s+')

变量名='\s*[_\w][_\w\d]*'
变量名s=f'{变量名}(\s*,)?'
变量别名=f'{变量名}\s*(as\s{变量名})?'
变量别名s=f'{变量别名}(\s*,)'
类型修饰符='\s+(public|private|readonly|volatile|const|unsigned)'
vars_len=f'{类型修饰符}*{变量名s}'
指针修饰符='\s*(\*)*\s*'
变量后缀修饰符=f'\[_\w\d:\]'
类型注解='\s*:.+?='
内置类型='\s*(int|short|long|long long|double|float|char|list|tuple|dict|str|bytes|object|bytearray|Py_UCS4|struct|union|class|cppclass|fused)'
include='include [\'\"](.+?)[\'\"]'
from_cimport=f'from\s+(\S+)\s+cimport{变量别名s}'
cimport=f'cimport\s+{变量别名}\s*'
cdef_vars_line=f'cdef(类型修饰符)?((指针修饰符)?\s+{变量名},?)+'
cdef_vars_block='cdef(类型修饰符)?:'
ctypedef_vars=f'ctypedef{变量名}{变量名}'
cdef_func=f'cdef{内置类型}?{变量名}\(({变量名}\s*,?)*\).+?(nogil)?'
ctypedef_func=f'ctypedef{内置类型}?{变量名}\(({变量名}\s*,?)*\)'
for_vars=f'for{变量别名s}?\s+in'
vars解包=f'{变量名s}\s*='
vars_decalre='变量名s'
with_nogil='with\s+nogil'
with_var='with.+?as\s+{变量名}'
{1,2,34,5}
def find_sj_from_lines(lines):
    for line in lines:
        r=re.match(sj_re, line)
        if r:
            return r.group()
    return '\n' #代表这个line没有缩进， lines不可能以\n开头



multi_line_str=r"[rFfbu]{0,2}'''.*?\n.*?'''"
signal_line_str=r'[rRFfbBuUCc]{0,2}"[^"]+"|[rFfbu]{0,2}\'[^\']+\''
#multi_line_content='\[[^\[\]]*?\n[^\[\]]*?\]|\([^()]*?\n[^()]*\)|{[^{}]*?\n[^{}]*}|\\\s*\n'
kh_left='[\[\({]'
kh_right='[\])}]'
kh_no_right='[^\])}]'
kh_sigal=r'[\[({][^\])}]*[\])}]'
kh_multi=rf'({kh_left})(({kh_no_right})*{kh_left}))*(.*?{kh_right})'
multi_line_content=r'\[[^\[\]]*?\]|\([^()]*?\)|{[^{}]*?\n}|\\\s*\n'
multi_line_re=re.compile(multi_line_content)
split='|'.join([multi_line_str, signal_line_str, multi_line_content])
first=f'({split})'
first_re=re.compile(first, re.DOTALL)
def open_utf8(path):
    return open(path,'r',encoding='utf8')

def split_code_lines(text: str) ->list[list[str]]:
    splits=first_re.finditer(text)
    lines0 = lines1 = 0
    code_lines=[[]]
    s = 0
    for t in splits:
        t0=text[s:t.start()]
        t1=t.group() #t1是一段多行代码
        t0_code_lines=t0.split('\n') #t0是
        #
        last_line=code_lines[-1]
        it = iter(t0_code_lines)
        last_line.append(next(it))
        #
        for t0_code_line in it:
            code_lines.append([t0_code_line])
        #
        last_line=code_lines[-1]
        last_line.append(t1)
        s=t.end()
    print(code_lines)
    return code_lines

coden='[\w_][\w\d_]+'
space_and_first_word_and_other=re.compile(r'(\s*)([\w_][\w\d_]+(?=\s+))?(.+)')
func=f'(\S+\s+)*({coden})\(.+?\)'
cfunc=re.compile(f'(\s+inline)?((\s+(volatile|const|unsigned)){0,3}\s+{coden})\s+{coden}')

from_cimport=re.compile(r'\s+(\S+)\s+cimport(.+)', re.DOTALL)
cimport=re.compile(r'\s+(.+)', re.DOTALL)
cdef_block=re.compile(r'\s+(public|private|readonly)?\s+:')
struct_union_fused='struct|union|fused'
extend_from=re.compile(r'extend\s+from.+?:')
def find_line(code_lines: list[list[str]]):
    for code_line in code_lines:
        cl=''.join(code_line)
        sfo=space_and_first_word_and_other.match(cl)
        if sfo:
            sj, word, other = sfo.groups()
            identify_first_word(word, other)
            #print(sfo.groups())
        else:
            assert cl==''
from_='from'
cimport_='cimport'
cdef_='cdef'
cpdef_='cpdef'
def_='def'
include_='include'

def identify_first_word(word, other):
    if word==cdef_:
        print(word,other)
    elif word==cpdef_:
        print(word,other)
    elif word==def_:
        print(word,other)
    elif word==cimport:
        print(word,other)
    elif word==from_:
        print(word,other)
    elif word==include_:
        print(word, other)
fkh='\[.+?\]'
def split_func_args(args_text: str):
    pass

if __name__ == '__main__':
    p='D:/xrdb/PyUnicode.pyx'
    text=open_utf8(p).read()
    #it=cfunc.finditer(text)
    code_lines=cut_line.cut_line(text)
    print('\n-----'.join(code_lines))
    #find_line(code_lines)

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
