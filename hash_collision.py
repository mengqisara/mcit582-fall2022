import hashlib
import os

def hash_collision(k):
    if not isinstance(k,int):
        print( "hash_collision expects an integer" )
        return( b'\x00',b'\x00' )
    if k < 0:
        print( "Specify a positive number of bits" )
        return( b'\x00',b'\x00' )
   
    #Collision finding code goes here
    size=64
    dic={}
    seen=set()
    s=os.urandom(size) #byte
    s1=hashlib.sha256(s).hexdigest() #hexdecimal
    sbit=bin( int( s1, 16 ) )[2:]  #binary string
    seen.add(s)
    dic[sbit[0:k]] = s
    while(True):
      x=os.urandom(size)
      if x in seen:
          continue
      x1 = hashlib.sha256(x).hexdigest()
      xbit=bin( int( x1, 16 ) )[2:]
      if xbit[0:k] in dic:
          return (x,dic.get(xbit[0:k]))
      seen.add(x)
      dic[xbit[0:k]] = x
    




