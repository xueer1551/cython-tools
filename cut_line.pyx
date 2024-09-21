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


cdef :
    uint normal=0, kh=1, string=2, string3=3
    Py_UCS4 left_kh0=c'(', left_kh1=c'[', left_kh2=c'{', right_kh0=c')', right_kh1=c']', right_kh2=c'}', dyh=c"'", \
        syh=c'"', xhx=c'\\', hh=c'\n', kg=c' ', tab='\t', kb0='\r',kb1='\v', kb2='\f', fh=';'
    Py_UCS4[255] sp_chars
#print(PyUnicode_Substring('aaa',0,0), '---')
cdef init_sp_chars():
    memset(sp_chars, 0, sizeof(Py_UCS4)*255)
    sp_chars[left_kh0]=1
    sp_chars[left_kh1]=1
    sp_chars[left_kh2]=1
    sp_chars[right_kh0]=2
    sp_chars[right_kh1]=2
    sp_chars[right_kh2]=2
    sp_chars[dyh]=3
    sp_chars[syh]=3
    sp_chars[xhx]=xhx
    sp_chars[hh]=4
    sp_chars[kg]=4
    sp_chars[kb0]=4
    sp_chars[kb1]=4
    sp_chars[kb2]=4
    sp_chars[tab]=tab
    sp_chars[fh]=fh
init_sp_chars()
assert left_kh2>left_kh1>left_kh0
assert right_kh0<right_kh1<right_kh2
cdef list _cut_line(unicode text, pyucs* t, uint l):
    cdef:
        uint i=0, start=0, ii, sj=0
        pyucs c
        list ll=[]
    while(i<l):
        c=t[i]
        if c!=left_kh0 and c!=left_kh1 and c!=left_kh2:
            pass
        else:
            i = find_kh(t, i + 1, l)
            continue
        #
        if c!=dyh and c!=syh:
            pass
        else:
            i=find_yh_str(t, i+1, l, c)
            continue
        #
        if c!=hh:
            if c!=fh:
                pass
            else: #c is ;
                ll.append((PyUnicode_Substring(text, start, i+1), sj))
                start=i+1
        else: # c is \n
            if want_hh(t, i, l):
                ll.append((PyUnicode_Substring(text, start, i+1), sj))
                i+=1
                start = i
                sj=find_sj(t, i, l)
                i += sj
                continue
            else:
                ll.append('')
        i+=1
    return ll


cdef bint want_hh(pyucs* t, uint i, uint l):
    cdef uint c, ii
    while(0<i):
        c=t[i]
        #if c==kg or c==tab or c==kb0 or c==kb1 or c==kb2
        if c<255:
            pass
        else:
            return True
        #
        if sp_chars[c]==4:
            i-=1
        elif sp_chars[c]==xhx:
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
    elif sp_chars[c] == xhx:
        return False
    else:
        return True

cdef uint find_sj(pyucs* t, uint i, uint l):
    cdef :
        pyucs c, start_char
        uint count=0
    c=t[i]
    if c==kg or c==tab:
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


cdef uint find_kh(pyucs* t, uint i, uint l):
    cdef :
        uint ii, left_kh_count=1
        pyucs c
    while(i<l):
        c=t[i]
        if c!=left_kh0 and c!=left_kh1 and c!=left_kh2:
            if c!=right_kh0 and c!=right_kh1 and c!=right_kh2:
                if c!=dyh and c!=syh:
                    pass
                else:
                    i=find_yh_str(t, i+1, l, c)
                    continue
            else:
                left_kh_count-=1
                if left_kh_count==0:
                    return i+1
        else:
            left_kh_count +=1
        i+=1

cdef uint find_yh_str(pyucs* t, uint i, uint l, pyucs left_yh):
    cdef:
        pyucs c
    if l-i>2:
        if t[i]!=left_yh:
            return find_no_multi_line_kh_str(t, i+1, l, left_yh)
        else:
            i+=1
            if t[i]!=left_yh:
                return find_no_multi_line_kh_str(t, i + 1, l, left_yh)
            else: #三引号'''
                while(i<l):
                    c=t[i]
                    if c!=left_yh:
                        pass
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

cdef uint find_no_multi_line_kh_str(pyucs* t, uint i, uint l, pyucs left_yh):
    cdef:
        pyucs c
    while (i < l):
        c = t[i]
        if c != left_yh:
            pass
        elif t[i - 1] != xhx:
            return i + 1
        else:
            pass
        i+=1
    return l