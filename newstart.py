import os
import json
import time
import subprocess as sp

class MCServerRunner:
    def __init__(self):
        java_home=os.environ.get('JAVA_HOME')
        java_path=java_home+"bin\javaw.exe"
        java_exists=os.path.exists(java_path)
        java_get=sp.Popen(args=['java','--version'],shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
        out,err=java_get.communicate()
        java_version=out.decode("ascii")[0:-1].split('\r')[0].split(' ')[1]
        print(type(err),err)
    def run_cmd(self, cmd_str='', echo_print=1):
        if echo_print == 1:
            print('\nCommand="{}"'.format(cmd_str))
        sp.run(cmd_str, shell=True)

if __name__=='__main__':
    MCServerRunner()