# import parser
# import builder

# parsed = parser.parse('a[]=1&a[]=2')
# print "Parsed shit", parsed
# print builder.build(parsed)
from timeit import Timer
# global fact

a = "a"
b = False

print "1", not not (a and b)

print "2", (a and b)

print 1 and 2

print None or 23

# def test1(x):
fact = lambda a: reduce(lambda b, c: b * c, range(1, a + 1))

# def funcc(b, c):
#   return b*c
fact2 = lambda a: reduce(lambda b, c: b * c, xrange(1, a + 1))
# def fact2(a):
#     def funcc(b, c):
#         return b * c
#     return reduce(funcc, xrange(1, a + 1))


def fact3(a):
    out = 1
    for i in xrange(1, a + 1):
        out *= i
    return out

import operator
fact4 = lambda a: reduce(operator.__mul__, xrange(1, a + 1), 1)

# print test1(10)
# range(1,0) or [1]

t = Timer("fact(18)", "from __main__ import fact")
print "1", min(t.repeat(23, 10000))

t = Timer("fact2(18)", "from __main__ import fact2")
print "2", min(t.repeat(23, 10000))

t = Timer("fact3(18)", "from __main__ import fact3")
print "3", min(t.repeat(23, 10000))

t = Timer("fact4(18)", "from __main__ import fact4")
print "4", min(t.repeat(23, 10000))