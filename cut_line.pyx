from cpython.unicode cimport Py_UCS1, Py_UCS2, PyUnicode_1BYTE_DATA, PyUnicode_2BYTE_DATA, PyUnicode_4BYTE_DATA, PyUnicode_KIND, PyUnicode_Substring
from libc.string cimport memset
cdef fused pyucs:
    Py_UCS1
    Py_UCS2
    Py_UCS4
ctypedef unsigned int uint
cpdef cut_line(unicode text):
    cdef :
        uint k=PyUnicode_KIND (text)
        pyucs t
    if k==2:
        return _cut_line(text, PyUnicode_2BYTE_DATA(text), len(text))
    elif k==1:
        return _cut_line(text, PyUnicode_1BYTE_DATA(text), len(text))
    else:
        return _cut_line(text, PyUnicode_4BYTE_DATA(text), len(text))

cpdef cut_douhao(unicode text):
    cdef:
        uint k = PyUnicode_KIND(text)
        pyucs t
    if k == 2:
        return _cut_douhao(text, PyUnicode_2BYTE_DATA(text), len(text))
    elif k == 1:
        return _cut_douhao(text, PyUnicode_1BYTE_DATA(text), len(text))
    else:
        return _cut_douhao(text, PyUnicode_4BYTE_DATA(text), len(text))

cdef :
    uint normal=0, kuohao=1, string=2, string3=3
    Py_UCS4 left_kuohao0=c'(', left_kuohao1=c'[', left_kuohao2=c'{', right_kuohao0=c')', right_kuohao1=c']', right_kuohao2=c'}', dyh=c"'", \
        syh=c'"', xhx=c'\\', hh=c'\n', kongge=c' ', tab=c'\t', kongbai0=c'\r',kongbai1=c'\v', kongbai2=c'\f', fenhao=c';', douhao=c','
    Py_UCS4[255] sp_chars
#print(PyUnicode_Substring('aaa',0,0), '---')
cdef init_sp_chars():
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
    sp_chars[kongbai1]=4
    sp_chars[kongbai2]=4
    sp_chars[tab]=tab
    sp_chars[fenhao]=fenhao
init_sp_chars()
assert left_kuohao2>left_kuohao1>left_kuohao0
assert right_kuohao0<right_kuohao1<right_kuohao2

cdef _cut_douhao(unicode text, pyucs* t, uint l, ):
    cdef :
        uint _=0, i=0, start=0
        list ll=[]
    while (i < l): # \s*
        i=find_kongbai(t,i,l)
        #
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
        else:
            s=PyUnicode_Substring(text, start, i)
            ll.append(s)
            start=i+1
        i+=1
    if
    return l

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


cdef bint want_hh(pyucs* t, uint i, uint l):
    cdef uint c, ii
    while(0<i):
        c=t[i]
        #if c==kongge or c==tab or c==kongbai0 or c==kongbai1 or c==kongbai2
        if c<255:
            pass
        else:
            return True
        #
        if sp_chars[c]==4:
            i-=1
        elif c==xhx:
            return False
        else:
            return True
    if c < 255:
        pass
    else:
        return True
    #
    c = t[0]
    if sp_chars[c] == 4:
        return True
    elif c == xhx:
        return False
    else:
        return True

cdef uint find_suojin(pyucs* t, uint i, uint l):
    cdef :
        pyucs c, start_char
        uint count=0
    c=t[i]
    if c==kongge or c==tab:
        start_char=c
        i-=1
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


cdef inline void line_text_try_add_1(pyucs c, uint* line_text):
    if c!=hh:
        pass
    else:
        line_text[0] +=1
#-----------------------------------------------------------------------------------------------------------------------

