from zksk import Secret, DLRep
from zksk import utils
import zksk
import random
from petlib.bn import Bn

def ZK_equality(G,H):

    #Generate two El-Gamal ciphertexts (C1,C2) and (D1,D2)
    r1 = Secret()
    r2 = Secret()
    m = Secret()
    C1 = r1.value*G
    C2 = m.value * G + r1.value * H
    D1 = r2.value*G
    D2 = m.value * G + r2.value * H

    #Generate a NIZK proving equality of the plaintexts
    stmt = DLRep(C1,r1*G) & DLRep(C2,r1*H+m*G) & DLRep(D1,r2*G) & DLRep(D2,r2*H+m*G)
    zk_proof = stmt.prove()

    #Return two ciphertexts and the proof
    return (C1,C2), (D1,D2), zk_proof

