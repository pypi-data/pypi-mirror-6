from __future__  import print_function
from os.path import expanduser
import os.path
import sys
import requests
from bs4 import BeautifulSoup
from shutil import copyfile
import shutil
import sys

from .templates import repo_template, spec_template 
try:
    from sh import rpmbuild
except ImportError as e:
    print("Failed to find rpmbuild command. Please install rpmdevtools.")

import re
EXISTS_AS_DIR = 1
EXISTS_AS_FILE = 2
DOES_NOT_EXIST = 0



def create_path(path):
    import os.path as os_path
    paths_to_create = []
    while not os_path.lexists(path):
        paths_to_create.insert(0, path)
        head,tail = os_path.split(path)
        if len(tail.strip())==0: # Just incase path ends with a / or \
            path = head
            head,tail = os_path.split(path)
        path = head

    for path in paths_to_create:
        os.mkdir(path)

def check_path(path):
    
    """A simple way to check if a path really exists
    and also let us know if its a file or a dir"""

    if not os.path.isdir(path):
        if os.path.exists(path):
            return EXISTS_AS_FILE
        else:
            return DOES_NOT_EXIST
    else:
        return EXISTS_AS_DIR



def setup():

    """Setup the home directory and rpmmacros. 
    Similar to running rpmdev-setuptree"""

    def create_subdirs(rpmbuild_dirs, rpmdir):
        for entry in rpmbuild_dirs:

            entry_path = os.path.join(rpmdir, entry)
            entry_status = check_path(entry_path)

            if entry_status == EXISTS_AS_FILE:
                msg = "Found {} as a file. Removing it."
                print(msg)
                os.remove(entry_path)
                os.mkdir(entry_path)
            elif entry_status == DOES_NOT_EXIST:
                print("Creating {}".format(entry_path))
                os.mkdir(entry_path)

            elif entry_status == EXISTS_AS_DIR:
                print("{} already exists.. Skipping".format(entry_path))

    rpmbuild_dirs = ["BUILD","RPMS","SOURCES","SPECS","SRPMS"]

    home_dir = expanduser("~")
    rpmdir = os.path.join(home_dir,"rpmbuild")

    rpmdir_status = check_path(rpmdir)

    if  rpmdir_status == EXISTS_AS_FILE :
        msg = """File: ~/rpmdir exists. Delete this and try again."""
        print(msg)
        sys.exit(1)    

    elif rpmdir_status == EXISTS_AS_DIR: 

        msg = "~/rpmbuild exists .. Skipping"
        print(msg)

        create_subdirs(rpmbuild_dirs, rpmdir)

    elif rpmdir_status == DOES_NOT_EXIST : 

        print("Creating rpmbuild directories.")
        os.mkdir(rpmdir)
        create_subdirs(rpmbuild_dirs, rpmdir)


    rpmmacros_path = os.path.join(home_dir, ".rpmmacros")
    rpmmacros_path_status =  check_path(rpmmacros_path)

    if rpmmacros_path_status == EXISTS_AS_FILE:
        print("RPM Macros already exist. Not deploying our copy.")

    else: 

        filename = "rpmbrew.rpmmacros"
        print("Deploying files/rpmbrew.rpmmacros")

        BASE_DIR = os.path.dirname(__file__)
        src_file = os.path.join(BASE_DIR, "files", filename)

        shutil.copy2(src_file, os.path.join(home_dir,".rpmmacros"))


def get_fedora_list(url):

    #page = requests.get(url)
    results_list = []

    with open("mock.html", "r") as f:

        text = f.read()

    soup = BeautifulSoup(text)
    #print(soup.prettify())


    hr = soup.find("html")
    body = hr.find("body")
    img = body.findAll("a")

    for i in img:
        results_list.append(i["href"])

    return results_list



def process_output(line, stdin, process):
    print(line)
    #if "ERROR" in line:
    #    process.kill()
    #    return True



def tar2rpm(filename=None, prefix="/opt", 
            source="", 
            summary="No Summary",
            description=None,
            license = "Not Set"):

   

    basename = os.path.basename(filename)
    dirname = os.path.dirname(filename)

    rawstr = r"""(?P<name>[a-z\d_]*)-(?P<major>[\d]*).(?P<minor>[\d]*).tar.gz"""
    matchstr = basename
    match_obj = re.search(rawstr, matchstr)

    if match_obj:

        name = match_obj.group('name')
        major = match_obj.group('major')
        minor = match_obj.group('minor')    

    else:
        print("Failed")
        print("Error: {} must follow the standard name-major.minor.tar.gz naming. Example: foo-1.1.tar.gz".format(basename))
        import sys
        sys.exit(0)


    if description is None:
        msg = "An rpm that packages {} tar.gz file and exapnds it to {}"
        msg = msg.format(basename, prefix)
    license = "Unknown"


    if not source:
        source = basename


    if description is None:

        description = """A simple rpm package built by tar2rpm. 
This package contains {} and expands 
it to  {}/{}-{}.{}\n\n""".format(filename,prefix,name,major,minor)
    url = source    
    spec_contents = spec_template.format(NAME=name, 
                       VERSION="{}.{}".format(major,minor), 
                       RELEASE="ito",
                       SUMMARY=summary,
                       LICENSE=license,
                       URL=url,
                       SOURCE=basename,
                       DESCRIPTION=description,
                       PREFIX=prefix)

    #print(line)

    setup()

    specfile = "{}.spec".format(name)

    home_dir = expanduser("~")
    rpmdir = os.path.join(home_dir,"rpmbuild")    
    rpmdir_sources = os.path.join(rpmdir,"SOURCES")
    rpmdir_specs = os.path.join(rpmdir,"SPECS")
    build_spec = os.path.join(rpmdir_specs,specfile)


    with open(build_spec, "w") as f:        
        f.write(spec_contents)
    fullpath = os.path.join(rpmdir_sources,basename)
    try:
        shutil.copy2(filename, fullpath)
    except IOError as e: 
        print("Error: Could not find tar.gz file: {}".format(fullpath))
        import sys
        sys.exit()

    print("Starting to build!")
    rpmbuild("-ba", build_spec)


def createrepo_rpmbuild():

    from sh import createrepo

    HOME = expanduser("~")
    RPMS = os.path.join(HOME,"rpmbuild/RPMS/")
    REPODATA = os.path.join(RPMS,"repodata")

    if os.path.exists(REPODATA):
        import shutil
        print("{} exists....".format(REPODATA))
        shutil.rmtree(REPODATA)
        print("Deleted {}".format(REPODATA))

    createrepo(RPMS)
    print("Done creating {}".format(REPODATA))


def __load_file__(filename):

    import os.path
    dirname= os.path.dirname(__file__)
    path = os.path.join(dirname, "files",filename)
    with open(path, "r") as f:

        lines = f.read()

    return lines


def make_repo():

    from os.path import expanduser
    HOME= expanduser("~")

    template = repo_template
    NAME="rpmbuild_repo"
    BASEURL="file://{}/rpmbuild/RPMS/".format(HOME)
    repofile =template.format(REPONAME=NAME, DESCRIPTION=NAME, BASEURL=BASEURL)
 
    with open(os.path.join(HOME,"rpmbuild/local.repo"), "w") as f:
        f.write(repofile) 

    source = os.path.join(HOME,"rpmbuild/local.repo")
    dest = "/etc/yum.repos.d/local.repo"
    from sh import sudo
    sudo("/bin/cp",  source, dest)

    print("deployed local.repo to /etc/yum/repos.d")

if __name__ == "__main__":

    #setup()
    #url = "http://ftp.uni-bayreuth.de/linux/fedora/linux/development/rawhide/source/SRPMS/p/"
    #results = get_fedora_list(url)

    #for i in results:
    #    print(i)

    tar2rpm(filename="jason-1.5.tar.gz", source=None)

