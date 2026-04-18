#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Huffman Adaptatif (Algorithme de Vitter)
TP2: Compression de données - Huffman adaptatif
Ismaïl ABLOUA
"""

import os
import sys
import math
from pathlib import Path

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
M = len(ALPHABET)
E = int(math.floor(math.log2(M)))  # 5 (2^5 = 32)
R = M - 2**E  # 4 (36-32)


class Node:
    """Nœud de l'arbre de Huffman adaptatif"""
    node_counter = 0
    
    def __init__(self, char=None, weight=0, is_nyt=False):
        self.char = char  # caractère ou None pour nœud interne
        self.weight = weight
        self.parent = None
        self.left = None
        self.right = None
        self.is_nyt = is_nyt
        self.node_id = Node.node_counter
        Node.node_counter += 1
    
    def __repr__(self):
        if self.is_nyt:
            return f"NYT({self.weight})"
        elif self.char:
            return f"{self.char}({self.weight})"
        else:
            return f"Internal({self.weight})"


class AdaptiveHuffman:
    """Implémentation du Huffman adaptatif (Vitter)"""
    
    def __init__(self):
        self.root = Node(is_nyt=True)  # Nœud NYT racine
        self.alphabet = ALPHABET
        self.char_nodes = {}  # Mapping char -> nœud feuille
        self.tree_history = []  # Pour afficher l'évolution
        self.swap_count = 0
        
    def find_nyt(self):
        """Trouve le nœud NYT actuel"""
        def search(node):
            if node is None:
                return None
            if node.is_nyt:
                return node
            left_result = search(node.left)
            if left_result:
                return left_result
            return search(node.right)
        
        return search(self.root)
    
    def is_leaf(self, node):
        """Vérifie si un nœud est une feuille"""
        return node.left is None and node.right is None
    
    def get_code_for_node(self, node):
        """Obtient le code Huffman pour un nœud"""
        code = ""
        current = node
        
        while current.parent is not None:
            if current.parent.left == current:
                code = "0" + code
            else:
                code = "1" + code
            current = current.parent
        
        return code
    
    def get_nyt_code(self):
        """Obtient le code Huffman du nœud NYT"""
        nyt_node = self.find_nyt()
        return self.get_code_for_node(nyt_node)
    
    def encode_fixed_code(self, char):
        """Encode un caractère avec le code fixe"""
        k = self.alphabet.index(char) + 1
        
        if 0 <= k <= 2 * R:
            # (k-1) sur (e+1) bits
            bits = E + 1
            value = k - 1
        else:
            # (k - r - 1) sur e bits
            bits = E
            value = k - R - 1
        
        return format(value, f'0{bits}b')
    
    def decode_fixed_code(self, bits):
        """Décode un code fixe pour obtenir le caractère"""
        # Lire e bits
        e_bits = bits[:E]
        e_value = int(e_bits, 2)
        
        if e_value < R:
            # Lire e+1 bits
            full_bits = bits[:E+1]
            k = int(full_bits, 2) + 1
            remaining = bits[E+1:]
        else:
            # Lire e bits supplémentaires
            full_bits = bits[:E]
            k = int(full_bits, 2) + R + 1
            remaining = bits[E:]
        
        char = self.alphabet[k - 1]
        return char, remaining
    
    def add_char_to_tree(self, char):
        """Ajoute un caractère à l'arbre (première occurrence)"""
        nyt_node = self.find_nyt()
        
        # Créer les deux enfants du NYT
        new_nyt = Node(is_nyt=True)
        new_char_node = Node(char=char, weight=1)
        
        # Remplacer le NYT par un nœud interne
        nyt_node.is_nyt = False
        nyt_node.left = new_nyt
        nyt_node.right = new_char_node
        # Le poids interne doit être la somme exacte des enfants: 0 + 1 = 1
        nyt_node.weight = 1
        new_nyt.parent = nyt_node
        new_char_node.parent = nyt_node
        
        self.char_nodes[char] = new_char_node
        
        # Mettre à jour les ancêtres
        self.update_ancestors(nyt_node)
    
    def update_ancestors(self, node):
        """Met à jour les poids des ancêtres et fait les swaps"""
        current = node
        while current is not None:
            if not self.is_leaf(current):
                # Vérifier si swap nécessaire au niveau du nœud courant
                if current.left and current.right and current.left.weight > current.right.weight:
                    current.left, current.right = current.right, current.left
                    self.swap_count += 1

                # Le poids interne est la somme exacte des enfants
                left_weight = current.left.weight if current.left else 0
                right_weight = current.right.weight if current.right else 0
                current.weight = left_weight + right_weight

            current = current.parent
    
    def increment_char_weight(self, char):
        """Incrémente le poids d'un caractère existant"""
        if char not in self.char_nodes:
            return
        
        node = self.char_nodes[char]
        node.weight += 1
        
        # Mettre à jour les ancêtres
        self.update_ancestors(node.parent)
    
    def encode_message(self, message, verbose=True):
        """Encode un message avec Huffman adaptatif"""
        encoded_codes = []
        encoded_with_nyt = []
        step = 0
        
        if verbose:
            print("\n" + "=" * 60)
            print("ÉTAPES DE L'ENCODAGE")
            print("=" * 60)
        
        for i, char in enumerate(message):
            if char not in self.alphabet:
                continue
            
            step += 1
            if verbose:
                print(f"\nÉtape {step}: Caractère '{char}'")
            
            if char not in self.char_nodes:
                # Nouvelle caractère
                nyt_code = self.get_nyt_code()
                fixed_code = self.encode_fixed_code(char)
                full_code = nyt_code + fixed_code
                
                encoded_codes.append(full_code)
                encoded_with_nyt.append(f"NYT")
                
                if verbose:
                    print(f"  → Nouvelle lettre")
                    print(f"  → Code NYT: {nyt_code}")
                    print(f"  → Code fixe: {fixed_code}")
                    print(f"  → Code complet: {full_code}")
                
                # Ajouter le caractère à l'arbre
                self.add_char_to_tree(char)
                
                if verbose:
                    print(f"  → Arbre mis à jour")
                    self.print_tree()
                    if self.swap_count > 0:
                        print(f"  → ⚡ Swap effectué! (Total swaps: {self.swap_count})")
            else:
                # Caractère connu
                char_code = self.get_code_for_node(self.char_nodes[char])
                encoded_codes.append(char_code)
                encoded_with_nyt.append(char)
                
                if verbose:
                    print(f"  → Caractère déjà rencontré")
                    print(f"  → Code Huffman: {char_code}")
                
                # Incrémenter le poids
                old_weight = self.char_nodes[char].weight
                self.increment_char_weight(char)
                
                if verbose:
                    print(f"  → Poids incrémenté: {old_weight} → {self.char_nodes[char].weight}")
                    print("  → Arbre après mise à jour:")
                    self.print_tree()
        
        binary_code = ''.join(encoded_codes)
        if verbose:
            print("\n" + "=" * 60)
        return binary_code, encoded_with_nyt
    
    def decode_message(self, binary_code, verbose=True):
        """Décode un message Huffman adaptatif"""
        decoded_chars = []
        decoded_with_nyt = []
        index = 0
        step = 0

        if verbose:
            print("\n" + "=" * 60)
            print("ÉTAPES DU DÉCODAGE")
            print("=" * 60)
        
        while index < len(binary_code):
            # Traverser l'arbre pour trouver un symbole
            node = self.root
            
            while not self.is_leaf(node):
                if index >= len(binary_code):
                    break
                
                bit = binary_code[index]
                index += 1
                
                if bit == '0':
                    if node.left:
                        node = node.left
                    else:
                        break
                else:
                    if node.right:
                        node = node.right
                    else:
                        break
            
            if self.is_leaf(node) and index <= len(binary_code):
                step += 1
                if node.is_nyt:
                    # Décoder le caractère avec code fixe
                    remaining_bits = binary_code[index:]
                    
                    # Lire E bits d'abord
                    if len(remaining_bits) < E:
                        break
                    
                    e_bits = remaining_bits[:E]
                    e_value = int(e_bits, 2)
                    index += E
                    
                    if e_value < R:
                        # Lire 1 bit supplémentaire (total E+1 bits)
                        if len(binary_code) < index + 1:
                            break
                        extra_bit = binary_code[index]
                        index += 1
                        value = (e_value << 1) | int(extra_bit)
                        k = value + 1
                    else:
                        # Les E bits suffisent
                        k = e_value + R + 1
                    
                    if k <= len(self.alphabet):
                        char = self.alphabet[k - 1]
                        decoded_chars.append(char)
                        decoded_with_nyt.append("NYT")

                        if verbose:
                            print(f"\nÉtape {step}: NYT -> '{char}'")
                            print(f"  → Index courant: {index}")
                            print("  → Arbre après insertion:")
                        
                        # Ajouter à l'arbre
                        self.add_char_to_tree(char)

                        if verbose:
                            self.print_tree()
                    else:
                        break
                        
                elif node.char:
                    decoded_chars.append(node.char)
                    decoded_with_nyt.append(node.char)

                    if verbose:
                        print(f"\nÉtape {step}: symbole existant '{node.char}'")
                        print(f"  → Index courant: {index}")
                        print("  → Arbre après mise à jour:")
                    
                    # Incrémenter le poids
                    self.increment_char_weight(node.char)

                    if verbose:
                        self.print_tree()
            else:
                break

        if verbose:
            print("\n" + "=" * 60)
        
        return ''.join(decoded_chars), decoded_with_nyt
    
    def print_tree(self):
        """Affiche l'arbre de Huffman adaptatif"""
        def print_node(node, prefix="", is_left=None):
            if node is None:
                return
            
            if is_left is None:
                print(prefix + repr(node))
            else:
                print(prefix + ("├── L: " if is_left else "└── R: ") + repr(node))
            
            if not self.is_leaf(node):
                if node.left:
                    print_node(node.left, prefix + ("│   " if is_left else "    "), True)
                if node.right:
                    print_node(node.right, prefix + ("│   " if is_left else "    "), False)
        
        print_node(self.root)


def run_encode_then_decode(message, verbose, output_dir):
    print("=" * 60)
    print("HUFFMAN ADAPTATIF - ENCODAGE")
    print("=" * 60)
    print(f"Message: {message}")
    print(f"Paramètres: M={M}, E={E}, R={R}")

    huffman = AdaptiveHuffman()
    binary_code, with_nyt = huffman.encode_message(message, verbose=verbose)

    title = "Résumé de l'encodage:"
    print(f"\n{title:^60}")
    print(f"Message avec NYT: {' '.join(with_nyt)}")
    print(f"Code binaire: {binary_code}")
    print(f"Longueur du code: {len(binary_code)} bits")
    print(f"Nombre de swaps: {huffman.swap_count}")
    print()

    with open(output_dir / "input.txt", "w") as f:
        f.write(message)

    with open(output_dir / "encoded.txt", "w") as f:
        f.write(binary_code)

    with open(output_dir / "encoded_NYT.txt", "w") as f:
        f.write(' '.join(with_nyt))

    print("=" * 60)
    print("HUFFMAN ADAPTATIF - DÉCODAGE")
    print("=" * 60)

    huffman2 = AdaptiveHuffman()
    decoded_message, decoded_with_nyt = huffman2.decode_message(binary_code, verbose=verbose)

    print(f"Message décodé avec NYT: {' '.join(decoded_with_nyt)}")
    print(f"Message décodé: {decoded_message}")
    print()

    with open(output_dir / "decoded.txt", "w") as f:
        f.write(decoded_message)

    if decoded_message == message:
        print("✓ Encodage/Décodage réussi!")
    else:
        print(f"✗ Erreur: {decoded_message} != {message}")

    print()
    print(f"Fichiers sauvegardés dans: {output_dir.absolute()}")


def run_decode_only(binary_code, verbose, output_dir):
    if any(bit not in "01" for bit in binary_code):
        print("Erreur: le code à décoder doit contenir uniquement 0 et 1.")
        sys.exit(1)

    print("=" * 60)
    print("HUFFMAN ADAPTATIF - DÉCODAGE (CODE FINAL)")
    print("=" * 60)
    print(f"Code binaire: {binary_code}")
    print(f"Longueur: {len(binary_code)} bits")

    huffman = AdaptiveHuffman()
    decoded_message, decoded_with_nyt = huffman.decode_message(binary_code, verbose=verbose)

    print(f"\nMessage décodé avec NYT: {' '.join(decoded_with_nyt)}")
    print(f"Message décodé: {decoded_message}")

    with open(output_dir / "encoded.txt", "w") as f:
        f.write(binary_code)

    with open(output_dir / "decoded.txt", "w") as f:
        f.write(decoded_message)

    with open(output_dir / "encoded_NYT.txt", "w") as f:
        f.write(' '.join(decoded_with_nyt))

    print()
    print(f"Fichiers sauvegardés dans: {output_dir.absolute()}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 huffman.py <message>")
        print("  python3 huffman.py encode <message> [--quiet]")
        print("  python3 huffman.py decode <code_binaire> [--quiet]")
        sys.exit(1)

    verbose = "--quiet" not in sys.argv
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    mode = sys.argv[1]

    if mode == "encode":
        if len(sys.argv) < 3:
            print("Erreur: message manquant pour le mode encode.")
            sys.exit(1)
        run_encode_then_decode(sys.argv[2], verbose, output_dir)
    elif mode == "decode":
        if len(sys.argv) < 3:
            print("Erreur: code binaire manquant pour le mode decode.")
            sys.exit(1)
        run_decode_only(sys.argv[2], verbose, output_dir)
    else:
        # Compatibilité: comportement historique
        run_encode_then_decode(mode, verbose, output_dir)


if __name__ == "__main__":
    main()