"""Synchronize existing question blocks from the master; do not alter membership."""
from pathlib import Path
import argparse, json, re

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r'(^### (Q\d{3})[^\n]*\n.*?)(?=^### |^## |\Z)', re.M | re.S)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Update existing blocks in the four topic files.')
    args = parser.parse_args()
    config = json.loads((ROOT/'maintenance/catalog.json').read_text(encoding='utf-8'))
    master = (ROOT/config['master']).read_text(encoding='utf-8')
    blocks = {m.group(2): m.group(1).strip() for m in PATTERN.finditer(master)}
    differences = []
    for item in config['documents']:
        if item['file'] == config['master']:
            continue
        path = ROOT/item['file']
        text = path.read_text(encoding='utf-8')
        def replace(m):
            key=m.group(2)
            if key not in blocks:
                raise ValueError(f'{path.name}: {key} is missing from master')
            if m.group(1).strip()!=blocks[key]:
                differences.append(f'{path.name}: {key}')
            return blocks[key]+'\n\n'
        updated=PATTERN.sub(replace,text)
        if args.write and updated!=text:
            path.write_text(updated,encoding='utf-8')
    print(json.dumps({'changed_questions':differences,'mode':'write' if args.write else 'check'},ensure_ascii=False,indent=2))
    if differences and not args.write:
        raise SystemExit(1)

if __name__=='__main__':
    main()
