import hashlib
import os

def hash_preimage(target_string):
    if not all( [x in '01' for x in target_string ] ):
        print( "Input should be a string of bits" )
        return
    nonce = b'\x00'
    seen = set()
    len_input = len(target_string)
    while(True):
        nonce=os.urandom(64)
        if nonce in seen:
            continue
        x1 = hashlib.sha256(nonce).hexdigest()
        xbit = bin(int(x1, 16))[2:]
        if xbit[len(xbit)-len_input:len(xbit)]==target_string:
            return (nonce)
        seen.add(nonce)
