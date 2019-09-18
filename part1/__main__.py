import sys

if "." not in sys.path:
    sys.path.insert(0, ".")

import part1.network as net

if __name__ == '__main__':
    net.main()
