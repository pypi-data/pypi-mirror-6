#!python
# EASY-INSTALL-ENTRY-SCRIPT: 'Doorstop==0.0.16-beta.4','console_scripts','doorstop-gui'
__requires__ = 'Doorstop==0.0.16-beta.4'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('Doorstop==0.0.16-beta.4', 'console_scripts', 'doorstop-gui')()
    )
