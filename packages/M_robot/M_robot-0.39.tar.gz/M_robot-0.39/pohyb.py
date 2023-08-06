from numpy import array, asarray, sin, cos, dot
def rotmat(alpha):                    # angle in radians!
    ca, sa = cos(alpha), sin(alpha)
    return array([[ca, -sa],[sa, ca]])

def rotate(X, Y, alpha, C=(0,0)):
    """
    X,Y - coordinates of points, C - center of rotation, default (0,0)
    
    """
    #Ca = asarray(C)
    Ca = asarray([[C[0]]*len(X), [C[1]]*len(X)])
    XY = asarray([X,Y])
    Xr,Yr = Ca + dot(rotmat(alpha), XY-Ca)
    return Xr,Yr

def translate(X, Y, V): # posunutie o vektor V, predpoklada np. polia X,Y,V
    return X+V[0], Y+V[1] 