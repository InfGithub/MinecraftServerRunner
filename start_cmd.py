# 导入模块
import os,shutil
import json
import time
import subprocess as sp
import argparse as ap

class MCServerRunner:
    def __init__(self):
        # 获取Java参数
        java_home=os.environ.get('JAVA_HOME')
        java_path=java_home+"bin\javaw.exe"
        java_exists=os.path.exists(java_path)
        java_get=sp.Popen(args=['java','--version'],shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
        out,err=java_get.communicate()
        self.java_ver=out.decode("ascii")[0:-1].split('\r')[0].split(' ')[1]

        #获取程序配置
        with open("options.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.Xms=data['Xms']
        self.Xmx=data['Xmx']
        self.ver=data['Version']
        self.jarcore_name=data['jarcore_name']
        self.jarcore_loader=data['jarcore_loader']
        self.Forcedrun=data['Forcedrun']

        #命令行参数传入
        self.cmd_parse()

    def flp(self):
        '''获取服务器启动脚本参数'''
        ver2=int(self.ver.split('.')[1])
        java_ver1=int(self.java_ver.split('.')[0])
        if (ver2<=17 and java_ver1==8) or (16 <ver2 <21 and java_ver1==17) or (ver2>20 and java_ver1==21) or self.Forcedrun:
            if self.jarcore_loader in ('Vanilla','Fabric','Quilt') or (ver2<17 and (self.jarcore_loader in ('Forge','Neoforge'))):
                self.cmd = f"java -server -Xms{self.Xms}G -Xmx{self.Xmx}G -jar {self.jarcore_name} nogui"
            else:
                if (self.jarcore_loader in ('Forge','Neoforge')) and ver2>=17 :
                    self.cmd="java @user_jvm_args.txt @libraries/net/minecraftforge/forge/--------/win_args.txt %*-nogui"
                else:
                    self.cmd="pause"
        else: # 如果Java版本不对设为Error
            run="Error"

    def cmd_parse(self):
        parser=ap.ArgumentParser(description='MinecraftServerRunner帮助列表')
        parser.add_argument('-s','--start',dest='start',action='store_true',default=False,help='启动服务器。')
        parser.add_argument('-re','--restart',dest='rstimes',default=0,type=int,help='将要重启的次数，-1为永远自动重启（默认为0，可选）。')
        parser.add_argument('-rm','--remove',dest='rm',action='store_true',default=False,help='运行结束后删除生成的文件。')
        parser.add_argument('-e','--eula',dest='eula',action='store_true',default=False,help='创建/修改eula.txt。')
        parser.add_argument('-c','--config',dest='cfg',default=None,choices=['Xms','Xmx','jarcore_name','jarcore_loader','Version','Forcedrun'],help='修改启动配置')
    def rm_svfiles(self):
        for p in ('.fabric','libraries','logs','mods','versions','world','banned-ips.json','banned-players.json','eula.txt','ops.json','server.properties','usercache.json','whitelist.json'): #已知的生成文件
            if os.path.exists(p):
                if os.path.isfile(p):
                    os.remove(p)
                elif os.path.isdir(p):
                    shutil.rmtree(p)
    def run_cmd(self, cmd_str='', echo_print=1):
        '''定义cmd指令函数'''
        if echo_print == 1:
            print('\nCommand="{}"'.format(cmd_str))
        sp.run(cmd_str, shell=True)

if __name__=='__main__':
    MCServerRunner()