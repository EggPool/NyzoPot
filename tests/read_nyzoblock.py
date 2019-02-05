"""
Read .nyzoblock file from ../data directory and convert to a list of native blocks objects.
No sanity check / validation yet, but checked to match nyzo website for first files.
"""

import sys
sys.path.append('../')
from pynyzo.block import Block

blocks = Block.from_nyzoblock('../data/000000.nyzoblock', verbose=False)

for block in blocks:
    print(block.to_string())
    # print(block.to_json())
