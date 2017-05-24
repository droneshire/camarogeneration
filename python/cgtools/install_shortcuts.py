import os
import sys
import config

def main():
    if sys.platform != 'win32':
        print 'Desktop shortcuts are only available for Windows'
        exit(1)

    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    with open(os.path.join(desktop, 'cg_tools.cmd'), 'w') as f:
        f.write('python -m cgtools.cg_ui.py\n')
        f.close()

if __name__ == '__main__':
    main()
