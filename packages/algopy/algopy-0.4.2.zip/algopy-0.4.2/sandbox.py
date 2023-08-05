import numpy
import numpy.random

from algopy import UTPM, Function, CGraph, sum, zeros, diag, dot, qr
from algopy.linalg import svd



D,P,N,M = 2,1,4,5

X = 2 * numpy.random.rand(D,P,M,N)
Y = 3 * numpy.random.rand(M,N)
AX = UTPM(X)
AX[:,0:2] = 0
# AY1 = Y + AX
# AY2 = Y - AX
# AY3 = Y * AX
# AY4 = Y / AX
# AY5 = AX + Y
# AY6 = AX - Y
# AY7 = AX * Y
# AY8 = AX / Y

print AX

U,s,V = svd(AX)

print s

D,P,M,N = 4,1,4,4

U = UTPM(numpy.random.random((D,P,M,M)))
S = UTPM(numpy.zeros((D,P,M,N)))
V = UTPM(numpy.random.random((D,P,N,N)))

U = qr(U)[0]
V = qr(V)[0]

# zeroth coefficient
S.data[0,0, 0 ,0] = 1.
S.data[0,0, 1, 1] = 1.
S.data[0,0, 2, 2] = 0
S.data[0,0, 3, 3] = 0

# first coefficient
S.data[1,0, 0 ,0] = 1.
S.data[1,0, 1, 1] = -2.
S.data[1,0, 2, 2] = 0
S.data[1,0, 3, 3] = 0


A = dot(U, dot(S,V))

U2,s2,V2 = svd(A)
S2 = zeros((M,N),dtype=A)
S2[:N,:N] = diag(s2)

A2 = dot(dot(U2, S2), V2.T)

# print 'S=', S
# print 'S2=', S2

# print A - A2
# print 'U2=\n', U2
# print 'V2=\n', V2
# print 'dot(U2.T, U2)=\n',dot(U2.T, U2)
# print 'dot(V2.T, V2)=\n',dot(V2.T, V2)


# assert_array_almost_equal( (A2 - A).data, 0.)
# assert_array_almost_equal( (dot(U2.T, U2) - numpy.eye(M)).data, 0.)
# assert_array_almost_equal( (dot(U2, U2.T) - numpy.eye(M)).data, 0.)
# assert_array_almost_equal( (dot(V2.T, V2) - numpy.eye(N)).data, 0.)
# assert_array_almost_equal( (dot(V2, V2.T) - numpy.eye(N)).data, 0.)