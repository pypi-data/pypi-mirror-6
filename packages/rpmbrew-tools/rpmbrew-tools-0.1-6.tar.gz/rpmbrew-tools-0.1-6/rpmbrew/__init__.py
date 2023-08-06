"""
RpmBrew Tools 

usage:
     rpmbrew tar2rpm <filename> [--source=SOURCE] [--prefix=PREFIX] 
     rpmbrew createrepo
     rpmbrew makerepo
     rpmbrew search [srpm name]
"""

from __future__ import print_function
from rpmbrew.brewlib import get_fedora_list
from rpmbrew.brewlib import tar2rpm
from rpmbrew.brewlib import createrepo_rpmbuild
from rpmbrew.brewlib import make_repo 

import hashlib
import os.path
from docopt import docopt



def main():
    
    arguments = docopt(__doc__, version='RPMBrew Tool 0.1')
    print(arguments)

    if arguments.get("tar2rpm",None):
        filename = arguments.get("<filename>")
        source = arguments.get("--source")
        prefix= arguments.get("--prefix")
       
        tar2rpm(filename=filename, prefix=prefix,
                        source=source)
    if arguments.get("createrepo",None):
        createrepo_rpmbuild()        

    if arguments.get("makerepo", None):
        make_repo()
if __name__ == "__main__":
    
    main()
    
        
