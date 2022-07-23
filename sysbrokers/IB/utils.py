import re
import os
from pathlib import Path
from datetime import datetime
from syscore.fileutils import get_filename_for_package

def write_ibkr_rebalance_file(name, weights: dict, leverage=1, path='private.data.rebalance'):
    weights = { k:v*leverage for k,v in weights.items()}
    linkPath = get_filename_for_package(f'{path}.{name}.rebalance')
    dir, file = os.path.split(linkPath)
    fullPath = Path(dir,'archive',f'{name}-{datetime.now()}.rebalance')
    write_portfolio_weights(weights, fullPath)
    write_portfolio_weights(weights, linkPath)

def write_portfolio_weights(weights, path):
    dir, file = os.path.split(path)
    os.makedirs(dir, exist_ok=True)
    lines = []
    with open(path, "w") as f:
        for k,v in weights.items():
            symbol = k
            route = 'SMART/AMEX'

            match = re.match(r'.*\.TRT$', k)
            if match:
                symbol = k[:-4].replace('-','.',1)
                route = 'SMART/TSE'

            if len(symbol) == 5:
                route = 'SMART/OTCLNKECN'

            line = 'DES,{},STK,{},,,,,,{:.2f}\n'.format(symbol,route,v*100)
            lines.append(line)
            f.write(line)
    return "".join(lines)


if __name__ == '__main__':
    write_ibkr_rebalance_file('test', dict(test1=0.5, test2=0.5), leverage=0.5)