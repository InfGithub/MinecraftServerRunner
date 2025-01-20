import os
import json
import time
import subprocess as sp
import argparse as ap

class MCServerRunner:
    def __init__(self):
        java_home=os.environ.get('JAVA_HOME')
        java_path=java_home+"bin\javaw.exe"
        java_exists=os.path.exists(java_path)
        java_get=sp.Popen(args=['java','--version'],shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
        out,err=java_get.communicate()
        self.java_ver=out.decode("ascii")[0:-1].split('\r')[0].split(' ')[1]
        with open("options.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.Xms=data['Xms']
        self.Xmx=data['Xmx']
        self.ver=data['Version']
        self.jarcore_name=data['jarcore_name']
        self.jarcore_loader=data['jarcore_loader']
        self.Forcedrun=data['Forcedrun']
    def flp(self):
        ver2=int(self.ver.split('.')[1])
        java_ver1=int(self.java_ver.split('.')[0])
        if (ver2<=17 and java_ver1==8) or (16 <ver2 <21 and java_ver1==17) or (ver2>20 and java_ver1==21) or self.Forcedrun:
            if self.jarcore_loader in ('Vanilla','Fabric','Quilt') or (ver2<17 and (self.jarcore_loader in ('Forge','Neoforge'))):
                run="java -server -Xms{}G -Xmx{}G -jar {} nogui".format(self.Xms,self.Xmx,self.jarcore_name)
            else :
                if (self.jarcore_loader in ('Forge','Neoforge')) and ver2>=17 :
                    run="java @user_jvm_args.txt @libraries/net/minecraftforge/forge/--------/win_args.txt %*-nogui"
                else :
                    run="pause"
        else :
            run="Error"
    def run_cmd(self, cmd_str='', echo_print=1):
        if echo_print == 1:
            print('\nCommand="{}"'.format(cmd_str))
        sp.run(cmd_str, shell=True)

if __name__=='__main__':
    MCServerRunner()