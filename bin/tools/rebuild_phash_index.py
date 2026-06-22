#!/usr/bin/env python3
# -*-coding:UTF-8 -*

"""
Rebuild Phash BK-Tree Index
=============================

This script rebuilds the BK-tree index for all existing phash objects.

Use this when:
- Importing old data that had phashes but no index
- Recovering from index corruption
- Migrating to the BK-tree implementation

"""

import os
import sys

sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
from lib.objects import Phashs


def main():
    """
    Rebuild the BK-tree index from all existing phash objects.
    """
    print('Rebuilding Phash BK-tree index...')
    
    count = Phashs.rebuild_bktree_index()
    
    print(f'BK-tree index rebuilt successfully.')
    print(f'Total phashes indexed: {count}')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
