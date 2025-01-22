# Author: EricDing618
# 导入模块
import os,shutil
import json
import time
import subprocess as sp
import argparse as ap

class MCServerRunner:
    def __init__(self):
        # 获取Java参数
        self.java_home=os.environ.get('JAVA_HOME')
        self.java_path=self.java_home+"bin\javaw.exe"
        java_exists=os.path.exists(self.java_path)
        java_get=sp.Popen(args=['java','--version'],shell=True,stdout=sp.PIPE, stderr=sp.PIPE)
        out,err=java_get.communicate()
        self.java_ver=out.decode("ascii")[0:-1].split('\r')[0].split(' ')[1]

        #获取程序配置
        with open("options.json", 'r', encoding='utf-8') as file:
            self.data = json.load(file)
        self.Xms=self.data['Xms']
        self.Xmx=self.data['Xmx']
        self.ver=self.data['Version']
        self.jarcore_name=self.data['jarcore_name']
        self.jarcore_loader=self.data['jarcore_loader']
        self.Forcedrun=self.data['Forcedrun']

        self.flp()
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
        else: # 如果Java版本有误设为False
            self.cmd=False

    def cmd_parse(self):
        parser=ap.ArgumentParser(description='MinecraftServerRunner帮助列表')
        parser.add_argument('--env',dest='env',action='store_true',default=False,help='检测服务器运行环境。')
        parser.add_argument('-rm','--remove',dest='rm',action='store_true',default=False,help='运行结束后删除生成的文件。')
        rungroup=parser.add_argument_group('启动服务器命令组')
        rungroup.add_argument('-s','--start',dest='start',action='store_true',default=False,help='启动服务器。')
        rungroup.add_argument('-re','--restart',dest='rstimes',default=0,type=int,help='将要重启的次数，-1为永远自动重启（默认为0，可选）。')
        changegroup=parser.add_argument_group('修改配置命令组')
        changegroup.add_argument('-e','--eula',dest='eula',action='store_true',default=False,help='创建/修改eula.txt。')
        changegroup.add_argument('-c','--config',dest='cfg',default=None,choices=['Xms','Xmx','jarcore_name','jarcore_loader','Version','Forcedrun'],help='修改启动配置')
        changegroup.add_argument('-v','--value',dest='val',default=None,type=str,help='options.json配置对应的值。')
        args=parser.parse_args()
        if self.Forcedrun or self.cmd:
            if args.env:
                print("JAVA_HOME ："+self.java_home)
                print("JAVA_path ："+self.java_path)
                print("java_version ："+self.java_ver)
            elif args.rm:
                self.rm_svfiles()
            elif args.start:
                print('直接关闭程序后服务器有可能不会关闭，请手动在任务管理器关闭或提前输入stop命令。\n(Neo)Forge加载器需要自己手动设置启动脚本，且其不会被程序配置影响，需要手动调整。')
                if args.rstimes:
                    fortick=65536 if args.rstimes==-1 else args.rstimes
                    for t in range(fortick):
                        os.system('cls')
                        os.system('title Times {}'.format(t+1))
                        self.run_cmd(self.cmd)
                        print("服务器已关闭。")
                        if t!=(fortick-1):
                            print("时间：{}".format(time.asctime()))
                            print("15秒后重启......")
                            for i in range(16):
                                time.sleep(1)
                                print(str(15-i)+'...')
                            print('服务器已启动。')
                else:
                    self.run_cmd(self.cmd)
            elif args.eula:
                with open('eula.txt','w') as file:
                    file.write('eula=true\n')
                print('eula.txt 已修改。')
            elif args.cfg:
                self.data[args.cfg]=args.val if args.cfg in ('jarcore_name','jarcore_loader','Version') else int(args.val) if args.cfg in ('Xms','Xmx') else True if 'true' in args.val.lower() else False
                with open('options.json','w',encoding='utf-8') as file:
                    file.write(json.dumps(self.data, indent=4))
        else:
            print("Java 版本有误！请更换正确的 Java 版本。\nAzul 下载地址：\nhttps://www.azul.com/downloads/")

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