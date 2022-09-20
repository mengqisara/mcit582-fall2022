import random
import hashlib
from fastecdsa.curve import secp256k1
from fastecdsa.keys import export_key, gen_keypair

from fastecdsa import curve, ecdsa, keys, point
from hashlib import sha256

def sign(m):
	#generate public key
	#Your code here
	G = curve.secp256k1.G
	n = curve.secp256k1.q
	sk = random.randrange(1, n)
	public_key = sk*G

	# generate signature
	# Your code here
	k = random.randrange(1, 2**127)
	T= k*G
	r = T.x%n
	hash = hashlib.sha256(m.encode("utf8")).digest()
	z = int.from_bytes(hash, byteorder="big")
	s = ((z+r*sk%n)%n*pow(k,-1,n))%n

	assert isinstance( public_key, point.Point )
	assert isinstance( r, int )
	assert isinstance( s, int )
	return( public_key, [r,s] )
