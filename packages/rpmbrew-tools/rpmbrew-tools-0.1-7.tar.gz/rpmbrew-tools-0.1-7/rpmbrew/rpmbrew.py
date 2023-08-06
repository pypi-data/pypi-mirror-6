"""
RpmBrew Tools 

usage:
     rpmbrew tar2rpm <filename> [--source=SOURCE] [--prefix=PREFIX] 
     rpmbrew createrepo
     rpmbrew search [srpm name]
"""

from __future__ import print_function
from brewlib import get_fedora_list
from brewlib import tar2rpm
from brewlib import createrepo_rpmbuild
import hashlib
import os.path
from docopt import docopt



def main():
    
    arguments = docopt(__doc__, version='RPMBrew Tool 0.1')

        
if __name__ == "__main__":
    
    main()
    
        
