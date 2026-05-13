import os
import shutil
import argparse

parser = argparse.ArgumentParser(description="Batch rename files using two list files.")
parser.add_argument("before_file", help="File containing original paths")
parser.add_argument("after_file", help="File containing new paths")
parser.add_argument("--dry-run", action="store_true", help="Print moves without executing")
args = parser.parse_args()

with open(args.before_file) as f:
    lines_before = f.read().splitlines()

with open(args.after_file) as f:
    lines_after = f.read().splitlines()

if len(lines_before) != len(lines_after):
    raise ValueError(f"Length mismatch: {len(lines_before)} vs {len(lines_after)}")

print(f"{'[dry-run] ' if args.dry_run else ''}{len(lines_before)} renames: {args.before_file} -> {args.after_file}")

for src, dst in zip(lines_before, lines_after):
    if not os.path.exists(src):
        print(f"SKIP (src not found): {src}")
        continue
    if os.path.exists(dst):
        print(f"SKIP (dst already exists): {dst}")
        continue
    dst_dir = os.path.dirname(dst)
    if dst_dir and not os.path.isdir(dst_dir):
        print(f"SKIP (dst dir missing): {dst_dir}")
        continue
    print(f"move: {src} -> {dst}")
    if not args.dry_run:
        try:
            shutil.move(src, dst)
        except OSError as e:
            print(f"ERROR: {e}")
