struct_union='''
class {name}:
    def __init__(self, d, struct_or_union):
        self.__dict__ = d
        self.struct = struct_or_union
    '''

init_enum='''
def init_enum_{name}():
    cdef name tem 
'''
