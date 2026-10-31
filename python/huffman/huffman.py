import bisect
import itertools
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import override


def scan_freq(source: str) -> dict[str,int]:
    freq: dict[str, int] = {}
    for chr in source:
        if not chr in freq:
            freq[chr] = 1
        else:
            freq[chr] = freq[chr] + 1
    return freq


@dataclass
class NodeLeaf:
    char: str
    freq: int

type Node = "NodeLeaf | NodeComposite"

class NodeComposite:
    _id_seq : Iterator[int] =  itertools.count(1)
    id: int
    freq: int
    left: Node
    right: Node

    def __init__(self, freq: int, left: Node, right: Node):
        self.id = next(NodeComposite._id_seq)
        self.freq = freq
        self.left = left
        self.right = right

    def __iter__(self):
        yield [self.left]
        yield [self.right]

    @override
    def __repr__(self):
        return f"#{self.id}:freq={self.freq} -> {self.left.freq} + {self.right.freq}"


def recurse(node: Node) -> Iterable[Node]:
    yield node
    if type(node) == NodeComposite:
        for kid in recurse(node.left):
            yield kid
        for kid in recurse(node.right):
            yield kid

def build_huffman_tree(freq: dict[str,int]) -> NodeComposite:
    ordered_nodes : list[Node] = [
        NodeLeaf(c, f) for (c, f) in sorted(freq.items(), key=lambda x: (x[1], x[0]))
    ]
    start_size = len(ordered_nodes)

    round: int = 0
    while len(ordered_nodes) > 1:
        b0 = ordered_nodes.pop(0)
        b1 = ordered_nodes.pop(0)
        combine = NodeComposite(b0.freq + b0.freq, b0, b1)
        bisect.insort(ordered_nodes, combine, key=lambda x:x.freq)
        round += 1
        if round > start_size:
            raise AssertionError("too long")

    # TODO: I need a EOF/EOT End-Of-File/Transmission
    # node_EOF = # bottom on tree

    root = ordered_nodes[0]

    if type(root) != NodeComposite:
        raise AssertionError("Must be composite")

    return root


def write_graphvis(root : NodeComposite) -> None:
    def dot_name(node: Node) -> str:
        if isinstance(node, NodeComposite):
            return f"n{node.id}"
        else:
            return f"leaf{ord(node.char)}"

    def dot_label(node: Node) -> str:
        if isinstance(node, NodeComposite):
            return f"{node.freq}"
        else:
            if not node.char.isalpha():
                return f"{ord(node.char)}"
            return f"{ord(node.char)} {node.char}"

    with open("huffman-tree.dot", "w") as f:
        _ = f.write("digraph huffman {\n")
        for n in recurse(root):
            if isinstance(n, NodeComposite):
                _ = f.write(f'  {dot_name(n)} [label="{n.freq}"];\n')
                _ = f.write(f'  {dot_name(n)} -> {dot_name(n.left)} [label="0"];\n')
                _ = f.write(f'  {dot_name(n)} -> {dot_name(n.right)} [label="1"];\n')
            else:
                _ = f.write(f'  {dot_name(n)} [shape=box, label="{dot_label(n)}"];\n')
        _ = f.write("}\n")

class BitStream:
    stream: bytearray
    bit_idx: int

    def __init__(self):
        self.stream = bytearray()
        self.bit_idx = -1

    def add(self, bit: bool):
        if self.bit_idx < 0 or self.bit_idx > 7:
            self.stream.append(0)
            self.bit_idx = 0

        if bit:
            self.stream[-1] |= 0x80 >> self.bit_idx
        self.bit_idx += 1


def build_lookup(root: NodeComposite) -> dict[str, list[bool]]:
    """ find each leaf, then generate the Left/Right or 0/1 path to node """
    raise NotImplementedError()

def compress(target: BitStream, lookup: dict[str, list[bool]], source: str) -> None:
    raise NotImplementedError()

if __name__ == "__main__":

    all = sys.stdin.read()
    freq = scan_freq(all)
    huff_root = build_huffman_tree(freq)
    huff_lookup = build_lookup(huff_root)

    compressed = BitStream()
    compress(compressed, huff_lookup, all)

    if "--svg" in sys.argv:
        write_graphvis(huff_root)
        print("see huffman-tree.dot")
