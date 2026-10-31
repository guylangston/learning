INPUT ?= alice_in_wonderland.txt

.PHONY: lint fix open clean

lint:
	uv run ruff check .
	uv run basedpyright

fix:
	uv run ruff check --fix .

open: huffman-tree.svg
	open huffman-tree.svg

huffman-tree.svg: huffman-tree.dot
	dot -Tsvg $< -o $@

huffman-tree.dot: huffman.py $(INPUT)
	uv run python huffman.py --svg < $(INPUT) > /dev/null

clean:
	rm -f huffman-tree.dot huffman-tree.svg
