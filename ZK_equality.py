from zksk import Secret, DLRep
from zksk import utils
import zksk
import random

def ZK_equality(G,H):

    #Generate two El-Gamal ciphertexts (C1,C2) and (D1,D2)
    r_c = Secret()
    r_d = Secret()
    m = Secret(Bn(42))
    C1 = r_c*G
    C2 = m * G + r_c * H
    D1 = r_d*G
    D2 = m * G + r_d * H

    #Generate a NIZK proving equality of the plaintexts
    stmt = DLRep(C1,r_c*G) & DLRep(C2,r_c*H+m*G) & DLRep(D1,r_d*G) & DLRep(D2,r_d*H+m*G)
    zk_proof = stmt.prove()

    #Return two ciphertexts and the proof
    return (C1,C2), (D1,D2), zk_proof

