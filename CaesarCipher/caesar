def encrypt(key,plaintext):
    ciphertext=""
    for i in range (len(plaintext)):
        char = plaintext[i]
        ciphertext+=chr((ord(char)-65+key)%26+65)
    return ciphertext

def decrypt(key,ciphertext):
    plaintext=""
    for i in range (len(ciphertext)):
        char = ciphertext[i]
        plaintext+=chr((ord(char)-65-key+26)%26+65)
    return plaintext
