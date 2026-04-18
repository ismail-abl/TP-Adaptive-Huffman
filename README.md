# Huffman Adaptatif - TP2

Implémentation du codage Huffman adaptatif (Algorithme de Vitter) en Python.


Ismaïl ABLOUA


18.04.2026

## Alphabet supporté

`abcdefghijklmnopqrstuvwxyz0123456789` (M=36, E=5, R=4)

## Exécution

### Encodage du message "darkvador"

```bash
python3 huffman.py darkvador
```

**Résultats générés dans `output/`:**
- `input.txt` → message original : `darkvador`
- `encoded.txt` → code binaire : `00001100000001001101110001101110100011001111001010110`
- `encoded_NYT.txt` → message avec NYT : `NYT NYT NYT NYT NYT a d NYT r`
- `decoded.txt` → message décodé : `darkvador`

### Décodage du code binaire

Le programme encode automatiquement et décode le résultat pour vérification.

Pour décoder `00001100000001001101110001101110100011001111001010110` :
- Ce code a été généré par l'encodage de "darkvador"
- Le décodage produit : `darkvador`

**Exemple de sortie:**
```
Message avec NYT: NYT NYT NYT NYT NYT a d NYT r
Code binaire: 00001100000001001101110001101110100011001111001010110
Longueur du code: 53 bits
Nombre de swaps: 5
✓ Encodage/Décodage réussi!
```

## Mode silencieux

Pour exécuter sans afficher les étapes :
```bash
python3 huffman.py darkvador --quiet
```

## Fichiers de sortie

Les résultats sont toujours sauvegardés dans le dossier `output/` :
- `input.txt` - Message d'entrée
- `encoded.txt` - Code binaire produit
- `encoded_NYT.txt` - Message avec symboles NYT
- `decoded.txt` - Message décodé
