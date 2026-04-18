# TP-Adaptive-Huffman

Implementation of Adaptive Huffman coding (FGK) in Python.

## Supported alphabet

`abcdefghijklmnopqrstuvwxyz0123456789`

## Run

```bash
python huffman.py "darkvador2026"
```

This command writes files in `output/`:

- `output/input.txt`
- `output/encoded.txt`
- `output/decoded.txt`
- `output/summary.json`

You can change the folder:

```bash
python huffman.py "darkvador2026" --output-dir output
```

## Tests

```bash
pytest -q
```