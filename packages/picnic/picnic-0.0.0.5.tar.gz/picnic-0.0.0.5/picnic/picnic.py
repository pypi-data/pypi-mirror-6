import os
import shutil
import subprocess as sp

files_path = os.path.dirname(os.path.realpath(__file__))
files_path = os.path.join(files_path, 'picnic_files')

def execute(*commands):
    for comm in commands:
        print ("picnic - Running : %s"%comm)
        p = sp.Popen(comm, shell=True, stderr = sp.PIPE)
        p.wait()
        print (p.stderr.read())
        

def copy_file(name,dst = None, replace=None):
    """
    Copy a file in the files/ subfolder at the given destination
    (see usage below) and change some stuff in the file
    
    name: file or path to file. The file copied will be files/name
    dst: name of the destination file (relative to working dir)
    changes: a dict of what to replace in the file, e.g.
        { '$PACKAGE_NAME':'MyCoolPackage', '$AUTHOR':'John Wayne'} 
    """
    if isinstance(name,list):
        name = os.path.join(*name)
    if isinstance(dst,list):
        dst = os.path.join(*dst)
    if dst is None:
        dst = name
    shutil.copyfile(os.path.join(files_path,name),dst)
    if replace:
        # replace what has to be replaced in the file template
        with open(dst, 'r') as f:
            s = f.read()
        for k,v in replace.items():
            s = s.replace(k,v)
        with open(dst, 'w') as f:
            s = f.write(s)
