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
    if a==1:
        return pow(c1,-1,p)
    if a%2==1:
        return pow(c1,-1,p)*inverseModular(c1,a-1,p)%p
    d = pow(c1,-1,p)*pow(c1,-1,p)%p
    a = (int)(a/2)
    while(a>1):
        d = d*d%p
        a = (int)(a/2)
    return d


def keygen():
    sk = random.randrange(2, p)
    pk=power(g,sk,p)
    return pk,sk


def encrypt(pk,m):
    c1=0
    c2=0
    return [c1,c2]


def decrypt(sk,c):
    m=0
    return m
