"""
Read .nyzoblock file from ../data directory and convert to a list of native blocks objects.
No sanity check / validation yet, but checked to match nyzo website for first files.
"""

import sys
from os import path, makedirs
sys.path.append('../')
from pynyzo.block import Block
from modules.nyzodb import NyzoDB


if __name__ == "__main__":
    if not path.isdir('../data/db'):
        makedirs('../data/db', exist_ok=True)
    nyzodb = NyzoDB(db_path='../data/db/')
    i = 0
    while path.isfile(f'../data/{i:06}.nyzoblock'):
        filename = f'../data/{i:06}.nyzoblock'
        print(f"Importing {filename}")
        blocks = Block.from_nyzoblock(filename, verbose=False)
        for block in blocks:
            # TODO: evolve block and transactions getter to avoid messing with private props.
            height = block._height
            print(f"Height {height}")
            nyzodb.insert_block(block)

        i+= 1

