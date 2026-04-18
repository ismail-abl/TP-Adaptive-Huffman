import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
M = len(ALPHABET)
E = int(math.floor(math.log2(M)))
R = M - (2 ** E)

_CHAR_TO_INDEX = {ch: i for i, ch in enumerate(ALPHABET)}


@dataclass
class Node:
    weight: int
    order: int
    symbol: str | None = None
    parent: "Node | None" = None
    left: "Node | None" = None
    right: "Node | None" = None

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


class AdaptiveHuffman:
    def __init__(self) -> None:
        max_nodes = (2 * M) - 1
        self.root = Node(weight=0, order=max_nodes)
        self.nyt = self.root
        self.leaves: dict[str, Node] = {}

    @staticmethod
    def _is_ancestor(ancestor: Node, node: Node) -> bool:
        current = node.parent
        while current is not None:
            if current is ancestor:
                return True
            current = current.parent
        return False

    def _collect_nodes(self, node: Node | None = None) -> list[Node]:
        if node is None:
            node = self.root
        nodes = [node]
        if node.left is not None:
            nodes.extend(self._collect_nodes(node.left))
        if node.right is not None:
            nodes.extend(self._collect_nodes(node.right))
        return nodes

    def _find_block_leader(self, node: Node) -> Node | None:
        candidates = []
        for current in self._collect_nodes():
            if current.weight != node.weight:
                continue
            if current is node:
                continue
            if self._is_ancestor(current, node):
                continue
            candidates.append(current)
        if not candidates:
            return None
        return max(candidates, key=lambda n: n.order)

    @staticmethod
    def _swap_orders(a: Node, b: Node) -> None:
        a.order, b.order = b.order, a.order

    def _swap_nodes(self, a: Node, b: Node) -> None:
        if a is b:
            return
        pa, pb = a.parent, b.parent
        if pa is None or pb is None:
            return

        if pa.left is a:
            pa.left = b
        else:
            pa.right = b

        if pb.left is b:
            pb.left = a
        else:
            pb.right = a

        a.parent, b.parent = pb, pa
        self._swap_orders(a, b)

    def _update(self, node: Node) -> None:
        current = node
        while current is not None:
            leader = self._find_block_leader(current)
            if leader is not None and leader is not current.parent:
                self._swap_nodes(current, leader)
            current.weight += 1
            current = current.parent

    def _code_for_node(self, node: Node) -> str:
        bits: list[str] = []
        current = node
        while current.parent is not None:
            if current.parent.left is current:
                bits.append("0")
            else:
                bits.append("1")
            current = current.parent
        return "".join(reversed(bits))

    def _insert_new_symbol(self, symbol: str) -> Node:
        old_nyt = self.nyt
        internal = Node(weight=0, order=old_nyt.order, parent=old_nyt.parent)
        new_nyt = Node(weight=0, order=old_nyt.order - 2, parent=internal)
        symbol_node = Node(weight=0, order=old_nyt.order - 1, symbol=symbol, parent=internal)
        internal.left = new_nyt
        internal.right = symbol_node

        if old_nyt.parent is None:
            self.root = internal
        else:
            if old_nyt.parent.left is old_nyt:
                old_nyt.parent.left = internal
            else:
                old_nyt.parent.right = internal

        self.nyt = new_nyt
        self.leaves[symbol] = symbol_node
        return symbol_node

    def encode_symbol(self, symbol: str) -> str:
        if symbol in self.leaves:
            node = self.leaves[symbol]
            encoded = self._code_for_node(node)
            self._update(node)
            return encoded

        encoded = self._code_for_node(self.nyt) + encode_fixed(symbol)
        node = self._insert_new_symbol(symbol)
        self._update(node)
        return encoded

    def decode_stream(self, bits: str) -> str:
        out: list[str] = []
        idx = 0
        while idx < len(bits):
            node = self.root
            while not node.is_leaf():
                if idx >= len(bits):
                    raise ValueError("Bitstream ended in the middle of a tree traversal")
                bit = bits[idx]
                idx += 1
                if bit == "0":
                    node = node.left  # type: ignore[assignment]
                elif bit == "1":
                    node = node.right  # type: ignore[assignment]
                else:
                    raise ValueError("Bitstream contains characters other than 0/1")

            if node is self.nyt:
                symbol, consumed = decode_fixed(bits, idx)
                idx += consumed
                out.append(symbol)
                new_node = self._insert_new_symbol(symbol)
                self._update(new_node)
            else:
                if node.symbol is None:
                    raise ValueError("Leaf without symbol encountered")
                out.append(node.symbol)
                self._update(node)

        return "".join(out)


def is_condition(e: int, r: int) -> bool:
    return 0 <= e <= 2 * r


def find_k(char: str) -> int:
    if char not in _CHAR_TO_INDEX:
        raise ValueError(f"Unsupported char '{char}'. Allowed alphabet: {ALPHABET}")
    return _CHAR_TO_INDEX[char]


def encode_fixed(char: str) -> str:
    idx = find_k(char)
    k = idx + 1
    if k <= 2 * R:
        return format(k - 1, f"0{E + 1}b")
    return format(k - R - 1, f"0{E}b")


def decode_fixed(bits: str, start: int) -> tuple[str, int]:
    if start + E > len(bits):
        raise ValueError("Not enough bits to decode fixed-length prefix")

    prefix = int(bits[start : start + E], 2)
    if prefix < R:
        if start + E + 1 > len(bits):
            raise ValueError("Not enough bits to decode extended fixed-length symbol")
        value = int(bits[start : start + E + 1], 2)
        k = value + 1
        consumed = E + 1
    else:
        k = prefix + R + 1
        consumed = E

    idx = k - 1
    if idx < 0 or idx >= M:
        raise ValueError("Decoded symbol index is outside the allowed alphabet")
    return ALPHABET[idx], consumed


def encode_huffman(msg: str) -> str:
    coder = AdaptiveHuffman()
    encoded_parts = []
    for char in msg:
        encoded_parts.append(coder.encode_symbol(char))
    return "".join(encoded_parts)


def decode_huffman(cyphertext: str) -> str:
    coder = AdaptiveHuffman()
    return coder.decode_stream(cyphertext)


def write_output_files(message: str, encoded: str, decoded: str, output_dir: str = "output") -> dict[str, str]:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    input_file = path / "input.txt"
    encoded_file = path / "encoded.txt"
    decoded_file = path / "decoded.txt"
    summary_file = path / "summary.json"

    input_file.write_text(message, encoding="utf-8")
    encoded_file.write_text(encoded, encoding="utf-8")
    decoded_file.write_text(decoded, encoding="utf-8")

    compression_ratio = (len(encoded) / (len(message) * 8)) if message else 0.0
    summary_file.write_text(
        json.dumps(
            {
                "alphabet": ALPHABET,
                "input_length": len(message),
                "encoded_bits": len(encoded),
                "compression_ratio_vs_ascii": compression_ratio,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "input": str(input_file),
        "encoded": str(encoded_file),
        "decoded": str(decoded_file),
        "summary": str(summary_file),
    }


def run_test() -> None:
    assert find_k("d") == 3, f"Expected 3, got {find_k('d')}"
    assert is_condition(E, R)
    msg = "darkvador2026"
    cyphertext = encode_huffman(msg)
    decoded_msg = decode_huffman(cyphertext)
    assert msg == decoded_msg, f"Expected {msg}, got {decoded_msg}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Adaptive Huffman (FGK) encoder/decoder")
    parser.add_argument("message", nargs="?", help=f"Message to encode with alphabet: {ALPHABET}")
    parser.add_argument("--output-dir", default="output", help="Directory where output files are written")
    args = parser.parse_args()

    if not args.message:
        run_test()
        print("Self-test passed. Provide a message to produce files in output/.")
        return

    encoded = encode_huffman(args.message)
    decoded = decode_huffman(encoded)
    files = write_output_files(args.message, encoded, decoded, args.output_dir)
    print(json.dumps(files, indent=2))


if __name__ == "__main__":
    main()
