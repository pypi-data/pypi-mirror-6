# -*- coding: utf-8 -*-


from __future__ import print_function
from .version import VERSION, RELEASE_DATE, WEBPAGE, LICENSE
import sys

def print_help():
    import sys
    
    print('''SImpleSTAtGENerator (%(version)s)

Usage:
    %(executable)s %(script)s [options] [files..] 
    
Available options:
    -h, --help              This help screen
    -v, --verbose           Print informational messages
    -d, --debug             Print debug messages
    -q, --quiet             Don't even print anything
    -p, --preserve          Don't write any output files
    -g, --graph=NAME        Generate only graph named NAME
                            (may be passed several times)
    -C, --conf-dir=PATH     Add PATH as base dir for all relative pathes
                            This may be passed several times to mark 
                            multiple lookup paths
    -O, --out-dir=PATH      Place output files under PATH (overrides pathes
                            given in config files)
        --cmd-line          Print rrdtool commands that may be used to generate
                            graphs (do _not_ implies --preserve)
        --print-templates   Print available templates (implies --preserve)


Any other arguments passed would be treated as configuration files.
You may want to pass as many config files as you need. All of them would 
be parsed and all graph would be generated.
When no files given, then configuration would be read from STDIN.


Released at: %(release_date)s
Licensed under: %(license)s
Author: Slawek Lis <lis.slawek@gmail.com> 

Please let me know your opinion about this app. It would be nice to know 
if I should develop it more or not.

Source and bug reporting at: %(webpage)s
''' % {
            'version': VERSION,
            'release_date': RELEASE_DATE,
            'executable': sys.executable,
            'script': sys.argv[0],
            'webpage': WEBPAGE,
            'license': LICENSE,
        })