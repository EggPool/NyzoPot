"""
Read .nyzoblock file from ../data directory and convert to a list of native blocks objects.
No sanity check / validation yet, but checked to match nyzo website for first files.
"""

import sys
import json
from os import path, makedirs
sys.path.append('../')
from pynyzo.block import Block
from modules.nyzodb import NyzoDB

NYZOBLOCK_PATH = '../data/'

DB_PATH = '../data/db'

if __name__ == "__main__":
    if not path.isdir(DB_PATH):
        makedirs(DB_PATH, exist_ok=True)
    nyzodb = NyzoDB(db_path=DB_PATH)
    i = 0
    while path.isfile(f'{NYZOBLOCK_PATH}/{i:06}.nyzoblock'):
        filename = f'{NYZOBLOCK_PATH}/{i:06}.nyzoblock'
        print(f"Importing {filename}")
        blocks = Block.from_nyzoblock(filename, verbose=False)
        for block in blocks:
            # TODO: evolve block and transactions getter to avoid messing with private props.
            height = block._height
            print(f"Height {height}")
            nyzodb.insert_block(block)
        with open(f"{NYZOBLOCK_PATH}/import.json", 'w') as f:
            json.dump({'last': i}, f)
        i+= 1


