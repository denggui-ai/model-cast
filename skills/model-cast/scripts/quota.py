"""Sum actual generated-image counts, with legacy boolean compatibility."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True)
    args = parser.parse_args()
    ledger = Path(args.run_dir) / 'quota.jsonl'
    used = 0
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            count = row.get('images_generated', int(row.get('counts_quota', False)))
            if type(count) is not int or count < 0:
                parser.error('invalid images_generated')
            used += count
    print(f'used={used} remaining={500-used}')


if __name__ == '__main__':
    main()
