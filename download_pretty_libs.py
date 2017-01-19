#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import sys
import re
import sys
import os
import subprocess
import platform
import zipfile

# Github address information
GITHUB_URL = "https://www.github.com/KiCad"
GITHUB_FP_LIB_TABLE = "https://raw.githubusercontent.com/KiCad/kicad-library/master/template/fp-lib-table.for-github"
FP_LIB_TABLE_FILE = "fp-lib-table.txt"
STATIC_ZIP = "archive/master.zip"

if sys.version_info[0] == 2:
    import urllib2 as urllib
else:
    import urllib.request as urlrequest

parser = argparse.ArgumentParser(description="Download KiCad footprint libraries, and keep them up to date")
parser.add_argument("-l", "--lib", help="Select which libraries to download (regex filter)", action="store")
parser.add_argument("-i", "--ignore", help="Select which libraries to ignore (regex filter)", action="store")
parser.add_argument("-s", "--static", help="Download static copies of each library (no git integration)", action="store_true")

args = parser.parse_args()
    
def Fail(msg, result=-1):
    print(msg)
    sys.exit(result)
    
# Download a file, with a simple progress bar
def DownloadFile(url, save_file):

    def reporthook(bnum, bsize, tsize):
        progress = bnum * bsize
        s = "Downloaded: n bytes" #% (progress,)
        sys.stdout.write("\rDownloaded: {n} bytes{blank}".format(n=progress,blank=" "*(15-len(str(progress)))),)
        #sys.stderr.write("\n")
        sys.stdout.flush()
    
    try:
        result = urlrequest.urlretrieve(url, save_file, reporthook)
        print("")
        return True
    except:
        return False
        
def RepoUrl(repo):
    return "{base}/{repo}".format(base=GITHUB_URL, repo=repo)
        
# Git Clone a repository
def CloneRepository(repo):
        
    # Clone
    Call('git clone {url}'.format(url=RepoUrl(repo)))
    
    return True

# Make a static copy of a repository
def StaticCopyRepository(repo):
    
    url = "{repo}/{zip}".format(repo=RepoUrl(repo), zip=STATIC_ZIP)
    zip_file = repo + ".zip"
    
    print("Downloading",repo)
    
    if DownloadFile(url, zip_file):
    
        tmp_dir = repo + ".tmp"
        # Extract top-level zip into a temporary folder
        with zipfile.ZipFile(zip_file) as archive:
            archive.extractall(tmp_dir)
    
        # Zip folder now has folder named with the '-master' suffix
        master = os.path.sep.join([tmp_dir, repo + "-master"]) 
        os.rename(master,repo)
    
        # Cleanup - delete tmp and zip files
        os.rmdir(tmp_dir)
        os.remove(zip_file)
    
        return True
    else:
        print("Error downloading",repo)
        return False

def Call(cmd):

    cmd = [cmd]

    # Windows requires that commands are piped through cmd.exe
    if platform.platform().lower().count('windows') > 0:
        cmd = ["cmd", "/c"] + cmd
    
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    for line in iter(pipe.stdout.readline, b''):
        line = line.decode('utf-8')
        print(line.rstrip())

try:
    # Download the footprint-library-table
    print("Downloading .pretty library table from Github")
    result = urlrequest.urlopen(GITHUB_FP_LIB_TABLE)
    lib_table_data = result.read().decode("utf-8")
except:
    Fail("Error loading fp-lib-table from github.")

# Extract .pretty library information
PRETTY_REGEX = 'lib \(name ([^\)]*)\)\(type Github\)\(uri \${KIGITHUB}\/([^\)]*)\)\(options "[^"]*"\)\(descr ([^\)]*)'

base_dir = os.getcwd()
    
libs = lib_table_data.split("\n")

dl_count = 0

# Parse each line of the fp-lib-table file, and extract .pretty library information
for lib in libs:
    result = re.search(PRETTY_REGEX, lib)

    if not result or len(result.groups()) is not 3:
        continue
        
    name, url, description = result.groups()
    
    # Check that this matches the provided regex
    if args.lib:
        if not re.search(args.lib, name, flags=re.IGNORECASE):
            continue
            
    # Check that this does NOT match the ignore filter
    if args.ignore:
        if re.search(args.ignore, name, flags=re.IGNORECASE):
            continue
    
    # Check if the repository exists
    if os.path.exists(url):
        print(url, "exists, skipping...")
        continue

    # Ignore libraries marked as 'deprecated'
    if description.lower().count("deprecated") > 0:
        print(name, "is deprecated - skipping")
        continue

    if not args.static:
        CloneRepository(url)
    else:
        StaticCopyRepository(url)
        
print("Done")
sys.exit(0)
