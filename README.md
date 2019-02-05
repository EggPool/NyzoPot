# NyzoPot
Nyzo - Proof of transactions.    
An attempt to fetch, rebuild, validate then keep in sync the whole Nyzo transactions history. 

Interactive query interface (explorer) is planned.

Relies on PyNyzo python package https://github.com/EggPool/PyNyzo

## PoC
 
See tests/read_nyzoblocks.py

```
from pynyzo.block import Block

blocks = Block.from_nyzoblock('../data/000000.nyzoblock', verbose=False)

for block in blocks:
    print(block.to_string())
```

## DB Storage

See tests/import_nyzoblock.py

Still very early attempt for an explorer feature, do not expect much atm except for dev and test purposes.
