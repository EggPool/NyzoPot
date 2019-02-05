"""
Tries to get a missing block by scraping nyzo.co

Deprecated
"""

import sys
sys.path.append('../')
from pynyzo.block import Block


with open('314.html') as f:
    html = f.read()

block = Block.from_nyzo_html(html)
print(block.to_json())
