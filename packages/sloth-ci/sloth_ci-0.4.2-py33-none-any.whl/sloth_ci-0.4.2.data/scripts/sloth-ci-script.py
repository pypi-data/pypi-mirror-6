#!python
# EASY-INSTALL-ENTRY-SCRIPT: 'sloth-ci==0.4.2','console_scripts','sloth-ci'
__requires__ = 'sloth-ci==0.4.2'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('sloth-ci==0.4.2', 'console_scripts', 'sloth-ci')()
    )
