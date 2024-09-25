from cpython.unicode cimport Py_UCS1, Py_UCS2, PyUnicode_1BYTE_DATA, PyUnicode_2BYTE_DATA, PyUnicode_4BYTE_DATA, PyUnicode_KIND, PyUnicode_Substring
from libc.string cimport memset
cdef int k

cdef fused pyucs:
    Py_UCS1
    Py_UCS2
    Py_UCS4

ctypedef unsigned int uint

def get_type_and_bieming_or_vars(unicode text):
    pass

def cut_line(unicode text) ->list[tuple[str, int, int, int]]:
    cdef :
        uint k=PyUnicode_KIND (text)
        pyucs t
    if k==2:
        return _cut_line(text, PyUnicode_2BYTE_DATA(text), len(text))
    elif k==1:
        return _cut_line(text, PyUnicode_1BYTE_DATA(text), len(text))
    else:
        return _cut_line(text, PyUnicode_4BYTE_DATA(text), len(text))

def cut_douhao_and_strip(unicode text) ->list[str]:
    cdef:
        uint k = PyUnicode_KIND(text)
        pyucs t
    if k == 2:
        return _cut_douhao_and_strip(text, PyUnicode_2BYTE_DATA(text), len(text))
    elif k == 1:
        return _cut_douhao_and_strip(text, PyUnicode_1BYTE_DATA(text), len(text))
    else:
        return _cut_douhao_and_strip(text, PyUnicode_4BYTE_DATA(text), len(text))

def split_by_fangkuohao_and_del_kongbai(unicode text) ->list[str]:
    cdef:
        uint k = PyUnicode_KIND(text)
        pyucs t
    if k == 2:
        return _split_by_fangkuohao_and_del_kongbai(text, PyUnicode_2BYTE_DATA(text), len(text))
    elif k == 1:
        return _split_by_fangkuohao_and_del_kongbai(text, PyUnicode_1BYTE_DATA(text), len(text))
    else:
        return _split_by_fangkuohao_and_del_kongbai(text, PyUnicode_4BYTE_DATA(text), len(text))


cdef :
    uint normal=0, kuohao=1, string=2, string3=3
    Py_UCS4 left_kuohao0=c'(', left_kuohao1=c'[', left_kuohao2=c'{', right_kuohao0=c')', right_kuohao1=c']', right_kuohao2=c'}', dyh=c"'", \
        syh=c'"', xhx=c'\\', hh=c'\n', kongge=c' ', tab=c'\t', kongbai0=c'\r', fenhao=c';', douhao=c',', jinghao=c'#',\
        xinghao=c'*'
    Py_UCS4[255] sp_chars
#print(PyUnicode_Substring('aaa',0,0), '---')
cdef  init_sp_chars():
    memset(sp_chars, 0, sizeof(Py_UCS4)*255)
    sp_chars[left_kuohao0]=1
    sp_chars[left_kuohao1]=1
    sp_chars[left_kuohao2]=1
    sp_chars[right_kuohao0]=2
    sp_chars[right_kuohao1]=2
    sp_chars[right_kuohao2]=2
    sp_chars[dyh]=3
    sp_chars[syh]=3
    sp_chars[xhx]=xhx
    sp_chars[xhx]=douhao
    sp_chars[hh]=5
    sp_chars[kongge]=4
    sp_chars[kongbai0]=4
    sp_chars[tab]=tab
    sp_chars[fenhao]=fenhao
    sp_chars[douhao]=douhao
    sp_chars[jinghao]=jinghao
    sp_chars[xinghao]=xinghao
init_sp_chars()
assert left_kuohao2>left_kuohao1>left_kuohao0
assert right_kuohao0<right_kuohao1<right_kuohao2

cdef _split_by_fangkuohao_and_del_kongbai(unicode text, pyucs* t, uint l):
    cdef:
        uint _ = 0, i = 0, start = 0, end, xinghao_count
        pyucs c
        list ll = []
        list lll=[]
    i=break_kongbai(t,0,l)
    while(i<l):
        c = t[i]
        if c != left_kuohao0 and c != left_kuohao1 and c != left_kuohao2:
            pass
        else:
            start = i
            stat = find_fangkuohao_and_identify_type(t, i+1, l, &end)
            s = [sub_text_del_yuan_kuohao(text, start, end), stat]
            lll.append((tuple(ll), (s, stat)))
            ll=[]
            i = end
            start=end
            continue
        #
        if c != dyh and c != syh:
            pass
        else:
            i = find_yh_str(t, i + 1, l, c, &_)
            continue
        #
        if c!=xinghao:
            pass
        else:
            #找到连续的*（空白分隔）
            xinghao_count=1
            start=i
            i+=1
            while(i<l):
                c=t[i]
                if c==xinghao:
                    xinghao_count+=1
                    i+=1
                    continue
                elif c==kongge or c==tab:
                    i+=1
                    continue
                else:
                    break
            end=i
            start=end
            s = sub_text_del_yuan_kuohao(text, start, end)
            ll.append((s, xinghao_count))
            continue
        #
        if c != kongge and c != tab:
            pass
        else:  #遇见空白，跳过并分割中间的文本，i是逗号的位置
            end=i
            i+=1
            s = sub_text_del_yuan_kuohao(text, start, end)
            ll.append(s)
            #
            i = break_kongbai(t, i, l)
            start = i
            continue
        i += 1
    if ll:
        lll.append((ll, None))
    return lll

arr='array'
typed_memoryview='memoryview'
cppclass='cppclass'

cdef sub_text_del_yuan_kuohao(unicode text, uint start, uint end):
    cdef :
        unicode s=PyUnicode_Substring(text, start, end)
        uint k = PyUnicode_KIND(s)
        pyucs t
    if k == 2:
        return _text_del_yuan_kuohao(text, PyUnicode_2BYTE_DATA(text), len(text))
    elif k == 1:
        return _text_del_yuan_kuohao(text, PyUnicode_1BYTE_DATA(text), len(text))
    else:
        return _text_del_yuan_kuohao(text, PyUnicode_4BYTE_DATA(text), len(text))

cdef _text_del_yuan_kuohao(unicode s, pyucs* t):
    cdef :
        uint i
        pyucs c
    for i in range(len(s)):
        c=t[i]
        if t[i]!=left_kuohao0:
            pass
        else:
            t[i]=kongge
            continue
        if t[i]!=right_kuohao0:
            pass
        else:
            t[i] = kongge
            continue
    return s

cdef find_fangkuohao_and_identify_type(pyucs* t, uint i, uint l, uint* i_ptr):
    cdef pyucs c
    stat='shuzu'
    while(i<l):
        c=t[i]
        if c!=right_kuohao1:
            if c==c':':
                stat=typed_memoryview
                i+=1
                while(i<l):
                    if t[i] != right_kuohao1:
                        continue
                    else:
                        i_ptr[0] = i + 1
                        return stat
            elif c==douhao:
                stat=cppclass
            else:
                pass
            i+=1
        else:
            i_ptr[0]=i+1
            return stat

cdef uint break_kongbai( pyucs* t, uint i, uint l):
    while(i<l):
        if t[i]==kongge or t[i]==tab:
            i+=1
        else:
            return i

cdef _cut_douhao_and_strip(unicode text, pyucs* t, uint l, ):
    cdef :
        uint _=0, i=0, start=0, end
        list ll=[]
    while (i < l):
        #跳过一段连续空白
        i=find_kongbai(t,i,l)
        start=i
        # i是第一个空白字符的位置
        while(i<l):
            c = t[i]
            if c != left_kuohao0 and c != left_kuohao1 and c != left_kuohao2:
                pass
            else:
                i = find_kuohao(t, i + 1, l, &_)
                continue
            #
            if c != dyh and c != syh:
                pass
            else:
                i = find_yh_str(t, i + 1, l, c, &_)
                continue
            #
            if c!=douhao:
                pass
            else: #遇见逗号，提取两个逗号中间的文本，i是逗号的位置
                end=trace_find_no_kongbai(t, i)
                s=PyUnicode_Substring(text, start, end)
                ll.append(s)
                start=i+1
                break
            i+=1
    #把最后一个逗号到最后一个字符之间的文本给提取
    s = PyUnicode_Substring(text, start, l)
    ll.append(s)
    return ll

cdef uint trace_find_no_kongbai(pyucs* t, uint i,):
    cdef:
        pyucs c
    while(i>0):
        c=t[i]
        if c == kongge or c == tab or c == kongbai0:
            i-=1
        else:
            return i
    c = t[0]
    if c == kongge or c == tab or c == kongbai0:
        raise AssertionError
    else:
        return 0

cdef uint trace_find_kongbai(pyucs* t, uint i,  uint l, ):
    cdef pyucs c
    while(i<l):
        c=t[i]
        if c==kongge or c==tab:
            i-=1
            continue
        else:
            return i

cdef uint find_kongbai(pyucs* t, uint i,  uint l, ):
    cdef pyucs c
    while(i<l):
        c=t[i]
        if c==kongge or c==tab:
            i+=1
            continue
        else:
            return i

cdef list _cut_line(unicode text, pyucs* t, uint l):
    cdef:
        uint i=0, start=0, ii, suojin=0,  line_text=1
        str suojin_text=''
        pyucs c
        list ll=[], lll=[]
        object lts, lte
    lts=lte=1
    while(i<l):
        c=t[i]
        #
        if c!=left_kuohao0 and c!=left_kuohao1 and c!=left_kuohao2:
            pass
        else:
            i = find_kuohao(t, i + 1, l, &line_text)
            continue
        #
        if c!=dyh and c!=syh:
            pass
        else:
            i=find_yh_str(t, i+1, l, c, &line_text)
            continue
        #
        if c!=jinghao:
            pass
        else:
            lte = line_text
            ll.append((PyUnicode_Substring(text, start, i + 1), suojin, lts, lte))
            #
            i=break_jinghao_zhushi(t, i, l, &line_text)
            lts=i
            suojin = find_suojin(t, i, l)
            continue
        #
        if c!=hh:
            if c!=fenhao:
                pass
            else: #c is ;
                lte=line_text
                ll.append((PyUnicode_Substring(text, start, i+1), suojin, lts, lte))
                start=i+1
        else: # c is \n
            line_text += 1
            if want_hh(t, i, l):
                lte = line_text
                ll.append((PyUnicode_Substring(text, start, i+1), suojin, lts, lte))
                lts=lte
                i+=1
                start = i
                suojin=find_suojin(t, i, l)
                #suojin_text=PyUnicode_Substring(text, i, i+suojin)
                i += suojin
                continue
            else:
                pass
        i+=1
    return ll

cdef inline next_line(unicode text, pyucs* t,  uint i, uint l, uint start, uint line_text, lts, uint suojin, list ll, uint* sj, uint* i_ptr):
    lte = line_text
    ll.append((PyUnicode_Substring(text, start, i + 1), suojin, lts, lte))
    lts = lte
    suojin = find_suojin(t, i, l)
    sj[0]=suojin
    i_ptr[0]= i+suojin
    return lts, lte

cdef bint want_hh(pyucs* t, uint i, uint l):
    cdef uint c, ii
    while(0<i):
        c=t[i]
        if c==kongge or c==tab or c==kongbai0:
            i-=1
        elif c==xhx:
            return False
        else:
            return True
    #
    c = t[0]
    if c == xhx:
        return False
    else:
        return True

cdef uint find_suojin(pyucs* t, uint i, uint l):
    cdef :
        pyucs c, start_char
        uint count
    c=t[i]
    if c==kongge or c==tab:
        start_char=c
        count=1
        i+=1
        while (i < l):
            if t[i] == start_char:
                count += 1
                i += 1
            else:
                break
        return count
    else:
        return  0

cdef uint find_kuohao(pyucs* t, uint i, uint l, uint* line_text):
    cdef :
        uint ii, left_kuohao_count=1
        pyucs c
    while(i<l):
        c=t[i]
        if c!=left_kuohao0 and c!=left_kuohao1 and c!=left_kuohao2:
            if c!=right_kuohao0 and c!=right_kuohao1 and c!=right_kuohao2:
                if c!=dyh and c!=syh:
                    line_text_try_add_1(c, line_text)
                else:
                    i=find_yh_str(t, i+1, l, c, line_text)
                    continue
            else:
                left_kuohao_count-=1
                if left_kuohao_count==0:
                    return i+1
        else:
            left_kuohao_count +=1
        i+=1

cdef uint find_yh_str(pyucs* t, uint i, uint l, pyucs left_yh, uint* line_text):
    cdef:
        pyucs c
    if l-i>2:
        if t[i]!=left_yh:
            line_text_try_add_1(t[i], line_text)
            return find_no_multi_line_kuohao_str(t, i+1, l, left_yh, line_text)
        else:
            i+=1
            if t[i]!=left_yh:
                line_text_try_add_1(t[i], line_text)
                return find_no_multi_line_kuohao_str(t, i + 1, l, left_yh, line_text)
            else: #三引号'''
                while(i<l):
                    c=t[i]
                    if c!=left_yh:
                        line_text_try_add_1(c, line_text)
                    elif t[i-1]!=xhx:
                        if t[i+1]==left_yh:
                            if t[i+2]==left_yh: #又一个三引号
                                return i+3
                            else:
                                i=i+3
                                pass
                        else:
                            i=i+2
                            
                    else:
                        pass
                    #
                    i+=1
                return l                   
    else:
        return l
    
cdef uint find_no_multi_line_kuohao_str(pyucs* t, uint i, uint l, pyucs left_yh, uint* line_text):
    cdef:
        pyucs c
    while (i < l):
        c = t[i]
        if c != left_yh:
            line_text_try_add_1(c, line_text)
        elif t[i - 1] != xhx:
            line_text_try_add_1(c, line_text)
            return i + 1
        else:
            line_text_try_add_1(c, line_text)
        i+=1
    return l

cdef uint break_jinghao_zhushi(pyucs* t, uint i, uint l, uint* line_text):
    cdef:
        pyucs c
    while (i < l):
        c = t[i]
        if c != jinghao:
            i+=1
            continue
        else:
            i+=1
            while(i<l):
                c = t[i]
                if c != hh:
                    i+=1
                else:
                    line_text[0]+=1
                    return i+1
            return l
    return l


cdef inline void line_text_try_add_1(pyucs c, uint* line_text):
    if c!=hh:
        pass
    else:
        line_text[0] +=1
#-----------------------------------------------------------------------------------------------------------------------

