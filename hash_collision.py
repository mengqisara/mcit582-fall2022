import hashlib
import os

def hash_collision(k):
    size=64
    dic={}
    seen=set()
    s=os.urandom(size) #byte
    s1=hashlib.sha256(s).hexdigest() #hexdecimal
    sbit=bin( int( s1, 16 ) )[2:]  #binary string
    seen.add(s)
    dic[sbit[len(sbit)-k:len(sbit)]] = s
    while(True):
      x=os.urandom(size)
      if x in seen:
          continue
      x1 = hashlib.sha256(x).hexdigest()
      xbit=bin( int( x1, 16 ) )[2:]
      if xbit[len(xbit)-k:len(xbit)] in dic:
          return (x,dic.get(xbit[len(xbit)-k:len(xbit)]))
      seen.add(x)
      dic[xbit[len(xbit)-k:len(xbit)]] = x
    




