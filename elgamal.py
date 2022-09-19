import random

from params import p
from params import g

def power(g,a,p):
    x = g
    res = 1
    while (a > 0):
        if a% 2 == 1:
            res = res * x % p
        x = x * x % p
        a = (int)(a / 2)
    return res


def inverseModular(c1,a,p):
    res=1
    while(a>0):
        if a%2==1:
            res=res*pow(c1,-1,p)
        c1=pow(c1*c1,-1,p)
        a=(int)(a/2)
    return res


def keygen():
    sk = random.randrange(1, p)
    pk=power(g,sk,p)
    return pk,sk


def encrypt(pk,m):
    r=random.randrange(1, p)
    c1 = power(g,r,p)
    c2 = (power(pk,r,p)*power(m,1,p))%p
    return [c1,c2]


def decrypt(sk,c):
    d = inverseModular(c[0],sk,p)
    m = (c[1]*d)%p
    return m
