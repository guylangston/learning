import sys

def is_stdin() -> bool:
    return not sys.stdin.isatty()

def build_frequency(text: str) -> dict[str, int]:
    res: dict[str, int] = {}
    for chr in text:
        if chr in res:
            c = res[chr]
            c += 1
            res[chr] = c
        else:
            res[chr] = 1
    return res

# https://en.wikipedia.org/wiki/Huffman_coding
class HuffmanTreeNode:
    char: str
    freq: int
    parent: HuffmanTreeNode | None
    left: HuffmanTreeNode | None
    right: HuffmanTreeNode | None

    def __init__(self, char:str, freq:int, parent: HuffmanTreeNode | None):
        self.char = char
        self.freq = freq
        self.parent = parent
        self.left = None
        self.right = None

    def is_root(self):
        return self.freq == -1

    def path(self) -> list[int]:
        res = []
        curr = self
        while not curr.is_root():
           res.append( (1 if curr == curr.parent.right else 0) )
           curr = curr.parent
        return res

    def char_display(self) -> str:
        if self.char == " ":
            return "<SPACE>"

        if self.char == "\n":
            return "<LF>"

        return self.char

    def __str__(self):
        return f"[{self.char_display()}:{self.freq}] <- {self.left.char_display()} -> {self.right.char_display()}"

class HuffmanTree:
    root: HuffmanTreeNode

    def __init__(self, root:HuffmanTreeNode):
        self.root = root


    def _insert_rec(self, curr: HuffmanTreeNode, char:str, freq:int) -> HuffmanTreeNode:
        if freq > curr.freq:
            if curr.right is None:
                new = HuffmanTreeNode(char, freq, curr)
                curr.right = new
                return new
            else:
                return self._insert_rec(curr.right, char, freq)
        else:
            if curr.left is None:
                new = HuffmanTreeNode(char, freq, curr)
                curr.left = new
                return new
            else:
                return self._insert_rec(curr.left, char, freq)


    def insert(self, char:str, freq:int) -> HuffmanTreeNode:
        return self._insert_rec(self.root, char, freq)




    def _itter(self, curr: HuffmanTreeNode, res: list[HuffmanTreeNode]):
        res.append(curr)
        if curr.right:
            self._itter(curr.right, res)
        if curr.left:
            self._itter(curr.left, res)

    def iter(self):
        res = []
        self._itter(self.root.right, res)
        self._itter(self.root.left, res)
        return res

def main():
    # if stdin not available load default
    text = ""
    def_file = "./alice_in_wonderland.txt"
    print("using: ", def_file)
    with open(def_file, "r") as f:
        text = f.read()
    # if not is_stdin():
    #     def_file = "./alice_in_wonderland.txt"
    #     print("using: ", def_file)
    #     with open(def_file, "r") as f:
    #         text = f.read()
    # else:
    #     print("using: stdin")
    #     text = sys.stdin.read()

    # ln = 0
    # for line in text.splitlines():
    #     print(f"| {ln} | {line}")
    #     ln += 1

    freq = build_frequency(text)

    sorted_by_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    tree = HuffmanTree(HuffmanTreeNode("_SKIP_", -1, None))
    tree.root.right = HuffmanTreeNode(sorted_by_freq[0][0], sorted_by_freq[0][1], tree.root)
    tree.root.left = HuffmanTreeNode(sorted_by_freq[1][0], sorted_by_freq[1][1], tree.root)

    for char, freq in sorted_by_freq[2:]:
        tree.insert(char, freq)


    print("list")
    for node in tree.iter():
        print(f"{node.char}:{node.freq} -> {node.path()}")




if __name__ == "__main__":
    print("----------------------")
    main()
    print("--[done]--------------------")
