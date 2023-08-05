#!python
# EASY-INSTALL-ENTRY-SCRIPT: 'sumy==0.2.0','console_scripts','sumy-2.6'
__requires__ = 'sumy==0.2.0'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('sumy==0.2.0', 'console_scripts', 'sumy-2.6')()
    )
