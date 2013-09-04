# parable
# Copyright (c) 2012, 2013, Charles Childers
# ==========================================

#
# Dependencies
#

from math import floor

#
# Memory Configuration
#

MAX_SLICES = 64000
SLICE_LEN = 1000


#
# Constants for data types
#

TYPE_NUMBER = 100
TYPE_STRING = 200
TYPE_CHARACTER= 300
TYPE_FUNCTION = 400
TYPE_FLAG = 500


#
# Constants for byte codes
# These are loosely grouped by type
#

BC_PUSH_N = 100
BC_PUSH_S = 101
BC_PUSH_C = 102
BC_PUSH_F = 103
BC_PUSH_COMMENT = 104
BC_TYPE_N = 110
BC_TYPE_S = 111
BC_TYPE_C = 112
BC_TYPE_F = 113
BC_TYPE_FLAG = 114
BC_GET_TYPE = 120
BC_ADD = 200
BC_SUBTRACT = 201
BC_MULTIPLY = 202
BC_DIVIDE = 203
BC_REMAINDER = 204
BC_FLOOR = 205
BC_BITWISE_SHIFT = 210
BC_BITWISE_AND = 211
BC_BITWISE_OR = 212
BC_BITWISE_XOR = 213
BC_COMPARE_LT = 220
BC_COMPARE_GT = 221
BC_COMPARE_LTEQ = 222
BC_COMPARE_GTEQ = 223
BC_COMPARE_EQ = 224
BC_COMPARE_NEQ = 225
BC_FLOW_IF = 300
BC_FLOW_WHILE = 301
BC_FLOW_UNTIL = 302
BC_FLOW_TIMES = 303
BC_FLOW_CALL = 304
BC_FLOW_CALL_F = 305
BC_FLOW_DIP = 306
BC_FLOW_SIP = 307
BC_FLOW_BI = 308
BC_FLOW_TRI = 309
BC_FLOW_RETURN = 399
BC_MEM_COPY = 400
BC_MEM_FETCH = 401
BC_MEM_STORE = 402
BC_MEM_REQUEST = 403
BC_MEM_RELEASE = 404
BC_MEM_COLLECT = 405
BC_STACK_DUP = 500
BC_STACK_DROP = 501
BC_STACK_SWAP = 502
BC_STACK_OVER = 503
BC_STACK_TUCK = 504
BC_STACK_NIP = 505
BC_STACK_DEPTH = 506
BC_STACK_CLEAR = 507
BC_QUOTE_NAME = 600
BC_STRING_SEEK = 700
BC_STRING_SUBSTR = 701
BC_STRING_NUMERIC= 702
BC_TO_LOWER = 800
BC_TO_UPPER = 801
BC_LENGTH = 802
BC_REPORT_ERROR = 900


#
# Support code
#

def is_number(s):
    """return True if s is a number, or False otherwise"""
    try:
        float(s)
        return True
    except ValueError:
        return False


#
# logging of errors
#
# errors are stored in an array, with helper functions to
# record and clear them
#

errors = []

def clear_errors():
    """remove all errors from the error log"""
    global errors
    i = 0
    while i < len(errors):
        errors.pop()
        i += 1


def report_error(text):
    """report an error"""
    global errors
    errors.append(text)


def check_depth(cells):
    """returns True if the stack has at least *cells* number of items, or"""
    """False otherwise. If False, reports an underflow error."""
    global stack
    if len(stack) < cells:
        report_error('Stack underflow: ' + str(cells) + ' values required')
        return False
    else:
        return True


#
# Byte code interpreter
#

def interpret(slice):
    """Interpret the byte codes contained in a slice."""
    global SLICE_LEN
    offset = 0
    while offset < SLICE_LEN:
        opcode = fetch(slice, offset)
        if opcode == BC_PUSH_N:
            offset += 1
            stack_push(fetch(slice, offset), TYPE_NUMBER)
        elif opcode == BC_PUSH_S:
            offset += 1
            stack_push(fetch(slice, offset), TYPE_STRING)
        elif opcode == BC_PUSH_C:
            offset += 1
            stack_push(fetch(slice, offset), TYPE_CHARACTER)
        elif opcode == BC_PUSH_F:
            offset += 1
            stack_push(fetch(slice, offset), TYPE_FUNCTION)
        elif opcode == BC_PUSH_COMMENT:
            offset += 1
        elif opcode == BC_TYPE_N:
            if check_depth(1):
                stack_change_type(TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_TYPE_S:
            if check_depth(1):
                stack_change_type(TYPE_STRING)
            else:
                offset = SLICE_LEN
        elif opcode == BC_TYPE_C:
            if check_depth(1):
                stack_change_type(TYPE_CHARACTER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_TYPE_F:
            if check_depth(1):
                stack_change_type(TYPE_FUNCTION)
            else:
                offset = SLICE_LEN
        elif opcode == BC_TYPE_FLAG:
            if check_depth(1):
                stack_change_type(TYPE_FLAG)
            else:
                offset = SLICE_LEN
        elif opcode == BC_GET_TYPE:
            if check_depth(1):
                stack_push(stack_type(), TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_ADD:
            if check_depth(2):
                x = stack_type()
                a = stack_pop()
                y = stack_type()
                b = stack_pop()
                if x == TYPE_NUMBER and y == TYPE_NUMBER:
                    stack_push(a + b, TYPE_NUMBER)
                elif x == TYPE_STRING and y == TYPE_STRING:
                    a = slice_to_string(a)
                    b = slice_to_string(b)
                    stack_push(string_to_slice(b + a), TYPE_STRING)
                else:
                    offset = SLICE_LEN
                    report_error('BC_ADD only works with NUMBER and STRING types')
            else:
                offset = SLICE_LEN
        elif opcode == BC_SUBTRACT:
            if check_depth(2):
                a = stack_pop()
                b = stack_pop()
                stack_push(b - a, TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_MULTIPLY:
            if check_depth(2):
                a = stack_pop()
                b = stack_pop()
                stack_push(a * b, TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_DIVIDE:
            if check_depth(2):
                a = stack_pop()
                b = stack_pop()
                stack_push(b / a, TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_REMAINDER:
            if check_depth(2):
                a = stack_pop()
                b = stack_pop()
                stack_push(b % a, TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_FLOOR:
            if check_depth(2):
                stack_push(floor(float(stack_pop())), TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_BITWISE_SHIFT:
            if check_depth(2):
                a = int(stack_pop())
                b = int(stack_pop())
                if a < 0:
                    stack_push(b << abs(a), TYPE_NUMBER)
                else:
                    stack_push(b >> a, TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_BITWISE_AND:
            if check_depth(2):
                a = int(stack_pop())
                b = int(stack_pop())
                stack_push(b & a, TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_BITWISE_OR:
            if check_depth(2):
                a = int(stack_pop())
                b = int(stack_pop())
                stack_push(b | a, TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_BITWISE_XOR:
            if check_depth(2):
                a = int(stack_pop())
                b = int(stack_pop())
                stack_push(b ^ a, TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_COMPARE_LT:
            if check_depth(2):
                x = stack_type()
                a = stack_pop()
                y = stack_type()
                b = stack_pop()
                if x == TYPE_NUMBER and y == TYPE_NUMBER:
                    if b < a:
                        stack_push(-1, TYPE_FLAG)
                    else:
                        stack_push(0, TYPE_FLAG)
                else:
                    offset = SLICE_LEN
                    report_error('BC_COMPARE_LT only recognizes NUMBER types')
            else:
                offset = SLICE_LEN
        elif opcode == BC_COMPARE_GT:
            if check_depth(2):
                x = stack_type()
                a = stack_pop()
                y = stack_type()
                b = stack_pop()
                if x == TYPE_NUMBER and y == TYPE_NUMBER:
                    if b > a:
                        stack_push(-1, TYPE_FLAG)
                    else:
                        stack_push(0, TYPE_FLAG)
                else:
                    offset = SLICE_LEN
                    report_error('BC_COMPARE_LT only recognizes NUMBER types')
            else:
                offset = SLICE_LEN
        elif opcode == BC_COMPARE_LTEQ:
            if check_depth(2):
                x = stack_type()
                a = stack_pop()
                y = stack_type()
                b = stack_pop()
                if x == TYPE_NUMBER and y == TYPE_NUMBER:
                    if b <= a:
                        stack_push(-1, TYPE_FLAG)
                    else:
                        stack_push(0, TYPE_FLAG)
                else:
                    offset = SLICE_LEN
                    report_error('BC_COMPARE_LTEQ only recognizes NUMBER types')
            else:
                offset = SLICE_LEN
        elif opcode == BC_COMPARE_GTEQ:
            if check_depth(2):
                x = stack_type()
                a = stack_pop()
                y = stack_type()
                b = stack_pop()
                if x == TYPE_NUMBER and y == TYPE_NUMBER:
                    if b >= a:
                        stack_push(-1, TYPE_FLAG)
                    else:
                        stack_push(0, TYPE_FLAG)
                else:
                    offset = SLICE_LEN
                    report_error('BC_COMPARE_GTEQ only recognizes NUMBER types')
            else:
                offset = SLICE_LEN
        elif opcode == BC_COMPARE_EQ:
            if check_depth(2):
                x = stack_type()
                a = stack_pop()
                y = stack_type()
                b = stack_pop()
                if x == y and x != TYPE_STRING:
                    if b == a:
                        stack_push(-1, TYPE_FLAG)
                    else:
                        stack_push(0, TYPE_FLAG)
                elif x == y and x == TYPE_STRING:
                    if slice_to_string(b) == slice_to_string(a):
                        stack_push(-1, TYPE_FLAG)
                    else:
                        stack_push(0, TYPE_FLAG)
                else:
                    offset = SLICE_LEN
                    report_error('BC_COMPARE_EQ requires matched types')
            else:
                offset = SLICE_LEN
        elif opcode == BC_COMPARE_NEQ:
            if check_depth(2):
                x = stack_type()
                a = stack_pop()
                y = stack_type()
                b = stack_pop()
                if x == y and x != TYPE_STRING:
                    if b != a:
                        stack_push(-1, TYPE_FLAG)
                    else:
                        stack_push(0, TYPE_FLAG)
                elif x == y and x == TYPE_STRING:
                    if slice_to_string(b) != slice_to_string(a):
                        stack_push(-1, TYPE_FLAG)
                    else:
                        stack_push(0, TYPE_FLAG)
                else:
                    offset = SLICE_LEN
                    report_error('BC_COMPARE_NEQ requires matched types')
            else:
                offset = SLICE_LEN
        elif opcode == BC_FLOW_IF:
            if check_depth(3):
                a = stack_pop()
                b = stack_pop()
                c = stack_pop()
                if c == -1:
                    interpret(b)
                else:
                    interpret(a)
            else:
                offset = SLICE_LEN
        elif opcode == BC_FLOW_WHILE:
            if check_depth(1):
                quote = stack_pop()
                a = -1
                while a== -1:
                    interpret(quote)
                    a = stack_pop()
            else:
                offset = SLICE_LEN
        elif opcode == BC_FLOW_UNTIL:
            if check_depth(1):
                quote = stack_pop()
                a = 0
                while a == 0:
                    interpret(quote)
                    a = stack_pop()
            else:
                offset = SLICE_LEN
        elif opcode == BC_FLOW_TIMES:
            if check_depth(2):
                quote = stack_pop()
                count = stack_pop()
                while count > 0:
                    interpret(quote)
                    count -= 1
            else:
                offset = SLICE_LEN
        elif opcode == BC_FLOW_CALL:
            offset += 1
            interpret(int(fetch(slice, offset)))
        elif opcode == BC_FLOW_CALL_F:
            if check_depth(1):
                a = stack_pop()
                interpret(a)
            else:
                offset = SLICE_LEN
        elif opcode == BC_FLOW_DIP:
            if check_depth(2):
                quote = stack_pop()
                vtype = stack_type()
                value = stack_pop()
                interpret(quote)
                stack_push(value, vtype)
            else:
                offset = SLICE_LEN
        elif opcode == BC_FLOW_SIP:
            if check_depth(2):
                quote = stack_pop()
                stack_dup()
                vtype = stack_type()
                value = stack_pop()
                interpret(quote)
                stack_push(value, vtype)
            else:
                offset = SLICE_LEN
        elif opcode == BC_FLOW_BI:
            if check_depth(3):
               a = stack_pop()
               b = stack_pop()
               stack_dup()
               x = stack_type()
               y = stack_pop()
               interpret(b)
               stack_push(y, x)
               interpret(a)
            else:
                offset = SLICE_LEN
        elif opcode == BC_FLOW_TRI:
            if check_depth(4):
                a = stack_pop()
                b = stack_pop()
                c = stack_pop()
                stack_dup()
                x = stack_type()
                y = stack_pop()
                stack_dup()
                m = stack_type()
                q = stack_pop()
                interpret(c)
                stack_push(q, m)
                interpret(b)
                stack_push(y, x)
                interpret(a)
            else:
                offset = SLICE_LEN
        elif opcode == BC_FLOW_RETURN:
            offset = SLICE_LEN
        elif opcode == BC_MEM_COPY:
            if check_depth(2):
                a = stack_pop()
                b = stack_pop()
                copy_slice(b, a)
            else:
                offset = SLICE_LEN
        elif opcode == BC_MEM_FETCH:
            if check_depth(2):
                a = stack_pop()
                b = stack_pop()
                stack_push(fetch(b, a), TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_MEM_STORE:
            if check_depth(3):
                a = stack_pop()
                b = stack_pop()
                c = stack_pop()
                store(c, b, a)
            else:
                offset = SLICE_LEN
        elif opcode == BC_MEM_REQUEST:
            stack_push(request_slice(), TYPE_FUNCTION)
        elif opcode == BC_MEM_RELEASE:
            if check_depth(1):
                release_slice(stack_pop())
            else:
                offset = SLICE_LEN
        elif opcode == BC_MEM_COLLECT:
            collect_unused_slices()
        elif opcode == BC_STACK_DUP:
            if check_depth(1):
                stack_dup()
            else:
                offset = SLICE_LEN
        elif opcode == BC_STACK_DROP:
            if check_depth(1):
                stack_drop()
            else:
                offset = SLICE_LEN
        elif opcode == BC_STACK_SWAP:
            if check_depth(2):
                stack_swap()
            else:
                offset = SLICE_LEN
        elif opcode == BC_STACK_OVER:
            if check_depth(2):
                stack_over()
            else:
                offset = SLICE_LEN
        elif opcode == BC_STACK_TUCK:
            if check_depth(2):
                stack_tuck()
            else:
                offset = SLICE_LEN
        elif opcode == BC_STACK_NIP:
            if check_depth(2):
                stack_swap()
                stack_drop()
            else:
                offset = SLICE_LEN
        elif opcode == BC_STACK_DEPTH:
            stack_push(len(stack), TYPE_NUMBER)
        elif opcode == BC_STACK_CLEAR:
            stack_clear()
        elif opcode == BC_QUOTE_NAME:
            if check_depth(2):
                name = slice_to_string(stack_pop())
                ptr = stack_pop()
                add_definition(name, ptr)
            else:
                offset = SLICE_LEN
        elif opcode == BC_STRING_SEEK:
            if check_depth(2):
                a = slice_to_string(stack_pop())
                b = slice_to_string(stack_pop())
                stack_push(b.find(a), TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_STRING_SUBSTR:
            if check_depth(3):
                a = int(stack_pop())
                b = int(stack_pop())
                c = slice_to_string(stack_pop())
                c = c[b:a]
                stack_push(string_to_slice(c), TYPE_STRING)
            else:
                offset = SLICE_LEN
        elif opcode == BC_STRING_NUMERIC:
            if check_depth(1):
                a = slice_to_string(stack_pop())
                if is_number(a):
                    stack_push(-1, TYPE_FLAG)
                else:
                    stack_push(0, TYPE_FLAG)
            else:
                offset = SLICE_LEN
        elif opcode == BC_TO_UPPER:
            if check_depth(1):
                t = stack_type()
                if t == TYPE_STRING:
                    ptr = stack_pop()
                    a = slice_to_string(ptr).upper()
                    stack_push(string_to_slice(a), TYPE_STRING)
                elif t == TYPE_CHARACTER:
                    a = ''.join(chr(stack_pop()))
                    b = a.upper()
                    stack_push(ord(b[0]), TYPE_CHARACTER)
                else:
                    report_error('ERROR: BC_TO_UPPER requires TYPE_STRING or TYPE_CHARACTER')
            else:
                offset = SLICE_LEN
        elif opcode == BC_TO_LOWER:
            if check_depth(1):
                t = stack_type()
                if t == TYPE_STRING:
                    ptr = stack_pop()
                    a = slice_to_string(ptr).lower()
                    stack_push(string_to_slice(a), TYPE_STRING)
                elif t == TYPE_CHARACTER:
                    a = ''.join(chr(stack_pop()))
                    b = a.lower()
                    stack_push(ord(b[0]), TYPE_CHARACTER)
                else:
                    report_error('ERROR: BC_TO_LOWER requires TYPE_STRING or TYPE_CHARACTER')
            else:
                offset = SLICE_LEN
        elif opcode == BC_LENGTH:
            if check_depth(1):
                if stack_type() == TYPE_STRING:
                    a = slice_to_string(stack_tos())
                    stack_push(len(a), TYPE_NUMBER)
                else:
                    stack_drop()
                    stack_push(0, TYPE_NUMBER)
            else:
                offset = SLICE_LEN
        elif opcode == BC_REPORT_ERROR:
            if check_depth(1):
                if stack_type() == TYPE_STRING:
                    a = slice_to_string(stack_tos())
                    report_error(a)
            offset = SLICE_LEN
        offset += 1


#
# Data stack implementation
#

stack = []
types = []


def stack_clear():
    """remove all values from the stack"""
    global stack, types
    i = 0
    while i < len(stack):
        stack.pop()
        types.pop()


def stack_push(value, type):
    """push a value to the stack"""
    global stack, types
    stack.append(value)
    types.append(type)


def stack_drop():
    """remove a value from the stack"""
    global stack, types
    stack.pop()
    types.pop()


def stack_pop():
    """remove and return a value from the stack"""
    global stack, types
    types.pop()
    return stack.pop()


def tos():
    """return a pointer to the top element in the stack"""
    global stack, types
    return len(stack) - 1


def stack_tos():
    """return the top element on the stack"""
    global stack, types
    return stack[tos()]


def stack_type():
    """return the type identifier for the top item on the stack"""
    global stack, types
    return types[tos()]


def stack_swap():
    """switch the positions of the top items on the stack"""
    at = stack_type()
    av = stack_pop()
    bt = stack_type()
    bv = stack_pop()
    stack_push(av, at)
    stack_push(bv, bt)


def stack_dup():
    """duplicate the top item on the stack"""
    """if the value is a string, makes a copy of it"""
    at = stack_type()
    av = stack_pop()
    stack_push(av, at)
    if at == TYPE_STRING:
        s = request_slice()
        copy_slice(av, s)
        stack_push(s, at)
    else:
        stack_push(av, at)


def stack_over():
    """put a copy of the second item on the stack over the top item"""
    """if the value is a string, makes a copy of it"""
    at = stack_type()
    av = stack_pop()
    bt = stack_type()
    bv = stack_pop()
    stack_push(bv, bt)
    stack_push(av, at)
    if bt == TYPE_STRING:
        s = request_slice()
        copy_slice(bv, s)
        stack_push(s, bt)
    else:
        stack_push(bv, bt)


def stack_tuck():
    """put a copy of the top item under the second item"""
    """if the value is a string, makes a copy of it"""
    stack_swap()
    stack_over()


def stack_change_type(type):
    """convert the type of an item on the stack to a different type"""
    global types, stack
    if type == TYPE_NUMBER:
        if stack_type() == TYPE_STRING:
            if is_number(slice_to_string(stack_tos())):
                stack_push(float(slice_to_string(stack_pop())), TYPE_NUMBER)
            else:
                stack_pop()
                stack_push(0, TYPE_NUMBER)
        else:
            types.pop()
            types.append(TYPE_NUMBER)
    elif type == TYPE_STRING:
        if stack_type() == TYPE_NUMBER:
            stack_push(string_to_slice(str(stack_pop())), TYPE_STRING)
        elif stack_type() == TYPE_CHARACTER:
            stack_push(string_to_slice(''.join(chr(stack_pop()))), TYPE_STRING)
        elif stack_type() == TYPE_FLAG:
            s = stack_pop()
            if s == -1:
                stack_push(string_to_slice('true'), TYPE_STRING)
            elif s == 0:
                stack_push(string_to_slice('false'), TYPE_STRING)
            else:
                stack_push(string_to_slice('malformed flag'), TYPE_STRING)
        elif stack_type() == TYPE_FUNCTION:
            types.pop()
            types.append(TYPE_STRING)
        else:
            return 0
    elif type == TYPE_CHARACTER:
        if stack_type() == TYPE_STRING:
            s = slice_to_string(stack_pop())
            stack_push(ord(s[0]), TYPE_CHARACTER)
        else:
            s = stack_pop()
            stack_push(int(s), TYPE_CHARACTER)
    elif type == TYPE_FUNCTION:
        types.pop()
        types.append(TYPE_FUNCTION)
    elif type == TYPE_FLAG:
        if stack_type() == TYPE_STRING:
            s = slice_to_string(stack_pop())
            if s == 'true':
                stack_push(-1, TYPE_FLAG)
            elif s == 'false':
                stack_push(0, TYPE_FLAG)
            else:
                stack_push(1, TYPE_FLAG)
        else:
            s = stack_pop()
            stack_push(s, TYPE_FLAG)
    else:
        return


#
# Parable's dictionary consists of two related arrays.
# The first contains the names. The second contains pointers
# to the slices for each named item.
#

dictionary_names = []
dictionary_slices = []

def in_dictionary(s):
    global dictionary_names, dictionary_slices
    return s in dictionary_names


def lookup_pointer(name):
    global dictionary_names, dictionary_slices
    name = name.lower()
    if in_dictionary(name) == False:
      return -1
    else:
      return dictionary_slices[dictionary_names.index(name)]


def add_definition(name, slice):
    global dictionary_names, dictionary_slices
    name = name.lower()
    if in_dictionary(name) == False:
      dictionary_names.append(name)
      dictionary_slices.append(slice)
    else:
      target = dictionary_slices[dictionary_names.index(name)]
      copy_slice(slice, target)
    return dictionary_names.index(name)


#
# in parable, memory is divided into regions called slices
# compiled code, strings, and other data are stored in these.
# each slice can contain up to SLICE_LEN values
#

p_slices = []
p_map = []


def request_slice():
    """request a new memory slice"""
    global p_slices, p_map, MAX_SLICES, SLICE_LEN
    i = 0
    while i < MAX_SLICES:
        if p_map[i] == 0:
            p_map[i] = 1
            p_slices[i] = []
            j = 0
            while j < SLICE_LEN:
                p_slices[i].append(0)
                j += 1
            return i
        else:
            i += 1
    return -1


def release_slice(slice):
    """release a slice. the slice should not be used after this is done"""
    global p_map
    p_map[int(slice)] = 0


def copy_slice(source, dest):
    """copy the contents of one slice to another"""
    global p_slices, p_map
    global SLICE_LEN
    i = 0
    while i < SLICE_LEN:
        p_slices[int(dest)][i] = p_slices[int(source)][i]
        i += 1


def prepare_slices():
    """prepare the initial set of slices for use"""
    global p_slices, p_map, MAX_SLICES
    i = 0
    while i < MAX_SLICES:
        p_map.append(0)
        p_slices.append([])
        i += 1


def fetch(slice, offset):
    """obtain a value stored in a slice"""
    global p_slices, p_map
    return p_slices[int(slice)][int(offset)]


def store(value, slice, offset):
    """store a value into a slice"""
    global p_slices, p_map
    p_slices[int(slice)][int(offset)] = value


def string_to_slice(string):
    """convert a string into a slice"""
    s = request_slice()
    i = 0
    for char in list(string):
        store(ord(char), s, i)
        i += 1
    store(0, s, i)
    return s


def slice_to_string(slice):
    """convert a slice into a string"""
    global SLICE_LEN
    s = []
    i = 0
    while i < SLICE_LEN:
        if fetch(slice, i) != 0:
            s.append(chr(fetch(slice, i)))
        else:
            i = SLICE_LEN
        i += 1
    return ''.join(s)


#
# unused slices can be reclaimed either manually using release_slice(),
# or parable can attempt to identify them and reclaim them automatically.
# the code here implements the garbage collector.
#
# note: this does not scan the stack contents. only invoke it if the
#       stack is empty, or problems may arise.
#

def find_references(s):
    """given a slice, return a list of all references in it"""
    global dictionary_slices
    global SLICE_LEN
    ptrs = []
    i = 0
    while i < SLICE_LEN:
        if fetch(s, i) >= 0:
            ptrs.append(int(fetch(s, i)))
        i += 1
    return ptrs


def seek_all_references():
    """return a list of all references in all named slices"""
    global dictionary_slices, p_map
    maybe = []
    deps = []
    refs = []
    for s in dictionary_slices:
        maybe.append(s)
        deps.append(find_references(s))
    maybe += sum(deps, [])
    maybe = list(set(maybe))
    for s in sorted(maybe):
        if p_map[s] == 1:
            refs.append(s)
    return refs


def find_unused():
    """scan memory and return a list of all slices that are not referenced"""
    global p_slices, MAX_SLICES
    i = 0
    map = []
    while i < MAX_SLICES:
        map.append(i)
        i += 1
    refs = seek_all_references()
    unused = list(set(map) ^ set(refs))
    return unused


def collect_unused_slices():
    """scan memory, and collect unused slices"""
    for i in find_unused():
        release_slice(i)


#
# the compiler is pretty trivial.
# we take a string, break it into tokens, then lay down bytecode based on
# single character prefixes.
#
# #  Numbers
# $  Characters
# &  Pointers
# `  Bytecodes
# '  Strings
# "  Comments
#
# the bytecode forms are kept simple:
#
# type           compiled as
# ==========     ===========================
# Functions      BC_FLOW_CALL   pointer
# Strings        BC_PUSH_S      pointer
# Numbers        BC_PUSH_N      VALUE
# Characters     BC_PUSH_C      ASCII_VALUE
# Pointers       BC_PUSH_F      pointer
# Bytecodes      bytecode value
#
# for two functions ([ and ]), new quotes are started or closed. These are
# the only case where the corresponding action is run automatically rather
# than being compiled.
#
# bytecodes get wrapped into named functions. At this point they are not
# inlined. (This hurts performance, but makes decompilation much simpler).
# a recompiler could be added to decompile/recompile an optimized definition
# before running.
#

def compile(str, slice):
    nest = []
    cleaned = ' '.join(str.split())
    tokens = cleaned.split(' ')
    count = len(tokens)
    i = 0
    offset = 0
    while i < count:
        s = ""
        if (tokens[i].startswith('"') or tokens[i] == '"'):
            if (tokens[i].endswith('"') and tokens[i] != '"'):
                s = tokens[i]
            else:
                j = i + 1
                s = tokens[i]
                while j < count:
                    s += " "
                    s += tokens[j]
                    if (tokens[j].endswith('"')):
                        i = j
                        j = count
                    j += 1
            store(BC_PUSH_COMMENT, slice, offset)
            offset += 1
            s = s[1:-1]
            store(string_to_slice(s), slice, offset)
            offset += 1
        elif (tokens[i].startswith('\'') or tokens[i] == '\''):
            if (tokens[i].endswith('\'') and tokens[i] != '\''):
                s = tokens[i]
            else:
                j = i + 1
                s = tokens[i]
                while j < count:
                    s += " "
                    s += tokens[j]
                    if (tokens[j].endswith('\'')):
                        i = j
                        j = count
                    j += 1
            store(BC_PUSH_S, slice, offset)
            offset += 1
            s = s[1:-1]
            store(string_to_slice(s), slice, offset)
            offset += 1
        elif tokens[i].startswith("$"):
            store(BC_PUSH_C, slice, offset)
            offset += 1
            store(ord(tokens[i][1:]), slice, offset)
            offset += 1
        elif tokens[i].startswith("&"):
            store(BC_PUSH_F, slice, offset)
            offset += 1
            if is_number(tokens[i][1:]):
                store(float(tokens[i][1:]), slice, offset)
            else:
                if lookup_pointer(tokens[i][1:]) != -1:
                    store(lookup_pointer(tokens[i][1:]), slice, offset)
                else:
                    store(0, slice, offset)
                    report_error('Unable to map ' + tokens[i] + ' to a pointer')
            offset += 1
        elif tokens[i].startswith("#"):
            store(BC_PUSH_N, slice, offset)
            offset += 1
            if is_number(tokens[i][1:]):
                store(float(tokens[i][1:]), slice, offset)
            else:
                store(0, slice, offset)
                report_error("# prefix expects a valid NUMBER, received " + tokens[i])
            offset += 1
        elif tokens[i].startswith("`"):
            store(float(tokens[i][1:]), slice, offset)
            offset += 1
        elif tokens[i] == "[":
            nest.append(slice)
            nest.append(offset)
            slice = request_slice()
            offset = 0
        elif tokens[i] == "]":
            old = slice
            store(BC_FLOW_RETURN, slice, offset)
            offset = nest.pop()
            slice = nest.pop()
            store(BC_PUSH_F, slice, offset)
            offset += 1
            store(old, slice, offset)
            offset += 1
        else:
            if lookup_pointer(tokens[i]) != -1:
                store(BC_FLOW_CALL, slice, offset)
                offset += 1
                store(lookup_pointer(tokens[i]), slice, offset)
                offset += 1
            else:
                report_error('Unable to find ' + tokens[i] + ' in dictionary')
        i += 1
        store(BC_FLOW_RETURN, slice, offset)
    return slice


def parse_bootstrap(f):
    """compile the bootstrap package it into memory"""
    for line in f:
        if len(line) > 1:
            s = compile(line, request_slice())
            interpret(s)


#
# some parts of the language (prefixes, brackets) are understood as part of
# the parser. but one important bit, the ability to give a name to an item,
# is not. this routine sets up an initial dictionary containing the *define*
# function. with this loaded, all else can be built.
#

def prepare_dictionary():
    """setup the initial dictionary"""
    s = request_slice()
    store(BC_QUOTE_NAME, s, 0)
    store(BC_FLOW_RETURN, s, 1)
    add_definition('define', s)


#
# a decompiler
# since the compiler only uses a small subset of the byte codes, it is
# pretty easy to generate a (mostly) accurate representation of the
# original source.
#

def pointer_to_name(ptr):
    """given a parable pointer, return the corresponding name, or"""
    """an empty string"""
    global dictionary_names, dictionary_slices
    s = ""
    if ptr in dictionary_slices:
        s = dictionary_names[dictionary_slices.index(ptr)]
    return s


def deconstruct(slice):
    """return a string containing the source code for a given slice"""
    global SLICE_LEN
    i = 0
    s = '[ '
    while i < SLICE_LEN:
        o = fetch(slice, i)
        if o == BC_PUSH_N:
            i += 1
            o = fetch(slice, i)
            s += '#' + str(o)
        elif o == BC_PUSH_C:
            i += 1
            o = fetch(slice, i)
            s += '$' + str(chr(o))
        elif o == BC_PUSH_S:
            i += 1
            o = fetch(slice, i)
            s += "'" + slice_to_string(o) + "'"
        elif o == BC_PUSH_COMMENT:
            i += 1
            o = fetch(slice, i)
            s += '"' + slice_to_string(o) + '"'
        elif o == BC_PUSH_F:
            i += 1
            o = fetch(slice, i)
            x = pointer_to_name(o)
            if len(x) == 0:
                s += deconstruct(o)
            else:
                s += '&' + x
        elif o == BC_FLOW_CALL:
            i += 1
            o = fetch(slice, i)
            x = pointer_to_name(o)
            if len(x) == 0:
                s += '&' + str(o) + ' invoke'
            else:
                s += x
        elif o == BC_FLOW_RETURN:
            i = SLICE_LEN
        else:
            s += '`' + str(o)
        s += ' '
        i += 1
    s += ']'
    return s


def generate_source():
    """return a string containing full source code for all named slices and"""
    """their dependencies"""
    global dictionary_names, dictionary_slices
    src = ""
    for s in dictionary_slices:
        src += deconstruct(s)
        src += " '" + pointer_to_name(s)
        src += "' define\n"
    return src + "\n"
