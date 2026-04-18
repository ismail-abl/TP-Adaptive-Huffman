# huffman progressif
# # blocs de meme poids
# noeud interne somme poids enfantas
# noeud externe = 1 + 1 par repetition
# code nyt et code fixe
# k selon valeur nyt dans l'arbre a l'état t
# m = 2^e + r
# exemple "darkvador" alphabet m = 26, e = 4, r = 10
# est ce que 0 <= e <= 2r
# oui
# k-1, sur e+1 bit
# non
# k-r-1, sur e bit


import os
import sys

M = 36
E = 5 # 2^5 = 32
R = 36-32

def find_k(char):
    return ord(char) - ord('a') # fait deja -1

def is_condition(e, r):
    return 0 <= e <= 2 * r

def encode_huffman(msg):
    freq = {}
    for char in msg:
        k = find_k(char)
        

    # construire l'arbre de Huffman
    # TODO

    # générer les codes de Huffman
    # TODO

    # encoder le message
    # TODO

    return -254


def decode_huffman(cyphertext):
    return -254

def run_test():
    assert find_k('d') == 3, f"Expected 3, got {find_k('d')}"
    msg = "darkvador"
    cyphertext = encode_huffman(msg)
    decoded_msg = decode_huffman(cyphertext)
    testing = f"message:{msg}, encoded message: {cyphertext}, decoded message: {decoded_msg}"
    print(testing)
    assert msg == decoded_msg, f"Expected {msg}, got {decoded_msg}"
    print("Test passed!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python huffman.py <message>")
        run_test()
    else:
        pass
