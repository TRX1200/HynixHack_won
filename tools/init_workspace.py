#!/usr/bin/env python3
"""Create fresh working templates only; never pretend they are completed results."""
import argparse
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('destination',type=Path)
    a=p.parse_args();dest=a.destination
    if dest.exists() or dest.is_symlink() or any(x.is_symlink() for x in dest.parents):
        p.error('Choose a new non-symlink destination. Existing directories are not overwritten.')
    dest.mkdir(parents=True)
    for name in ['TASK.md','STATE.md','DECISIONS.md','TEST_LOG.csv','SOURCES.csv','REPORT.md']:
        shutil.copyfile(ROOT/'templates'/name,dest/name)
    print('Fresh templates created. Task-required filenames and formats take precedence.')
if __name__=='__main__':main()
