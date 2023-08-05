#!/usr/bin/env python
import os
import sys
try:
    import watson
except:
    dirname, filename = os.path.split(os.path.abspath(__file__))
    watson_root = os.path.join(dirname, '../')
    sys.path.append(os.path.abspath(watson_root))
from watson.framework import applications


if __name__ == '__main__':
    application = applications.Console()
    application()
