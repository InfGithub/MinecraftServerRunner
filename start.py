
import os
import json
import time
import subprocess

def run_cmd( cmd_str='', echo_print=1):
    from subprocess import run 
    if echo_print == 1:
        print('\nCommand="{}"'.format(cmd_str))
    run(cmd_str, shell=True)

java_home=os.environ.get('JAVA_HOME')
java_path=java_home+"bin\javaw.exe"
java_exists=os.path.exists(java_path)
java_get=subprocess.Popen(args=['java','--version'],shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out,err=java_get.communicate()
java_version=out.decode("ascii")[0:-1].split('\r')[0].split(' ')[1]
def main():
    global Xms,Xmx,jarcore_name,jarcore_loader,data,Version,Forcedrun

    with open("options.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
    Xms=data['Xms']
    Xmx=data['Xmx']
    Version=data['Version']
    jarcore_name=data['jarcore_name']
    jarcore_loader=data['jarcore_loader']
    Forcedrun=data['Forcedrun']

    def flp():
        global run
        Version2=int(Version.split('.')[1])
        java_version1=int(java_version.split('.')[0])
        if (Version2<=17 and java_version1==8) or (Version2>16 and Version2<21 and java_version1==17) or (Version2>20 and java_version1==21) or Forcedrun=='True':
            if jarcore_loader=='Vanilla' or jarcore_loader=='Fabric' or jarcore_loader=='Quilt' or (Version2<17 and (jarcore_loader=='Forge' or jarcore_loader=='Neoforge')):
                run="java -server -Xms{}G -Xmx{}G -jar {} nogui".format(Xms,Xmx,jarcore_name)
            else :
                if (jarcore_loader=='Forge' or jarcore_loader=='Neoforge') and Version2>=17 :
                    run="java @user_jvm_args.txt @libraries/net/minecraftforge/forge/--------/win_args.txt %*-nogui"
                else :
                    run="pause"
        else :
            run="Error"
            
    def m1():
        
        def s1():
            flp()
            os.system('cls')
            
            if run!="Error":
                run_cmd(run)
            else :
                os.system('color 0C')
                print("Java 版本不对！请更换正确的 Java 版本。")
                print("Azul 下载地址：")
                print("https://www.azul.com/downloads/")
            os.system('pause')
            main()

        def s2():
            main()

        os.system('color 0B')
        os.system('cls')

        print('-'*64)
        print(data)
        print('直接关闭程序后服务器有可能不会关闭，请手动在任务管理器关闭或提前输入stop命令。')
        print("(Neo)Forge加载器需要自己手动设置启动脚本，且其不会被程序配置影响，需要手动调整。")
        print('-'*64)
        print('[1] 启动服务器')
        print('[2] 返回任务执行界面。')
        print('-'*64)

        choice=input('输入：')
        locals()['s'+choice]()

    def m2():

        def r1():

            flp()
            os.system('cls')

            if run!="Error":
                print('-'*64)
                print('请输入将要重启的次数，0为退出，-1为永远自动重启。')
                print('-'*64)

                tick=int(input("次数："))

                if tick==0:
                    main()
                else :
                    if tick==-1:
                        fortick=65536
                    else:
                        fortick=tick

                    for t in range(fortick):
                        os.system('cls')
                        os.system('title Times {}'.format(t+1))

                        run_cmd(run)
                        print("服务器已关闭。")
                        if t!=(fortick-1):
                            print("时间：{}".format(time.asctime()))
                            print("15秒后重启......")
                            for i in range(16):
                                time.sleep(1)
                                print(str(15-i)+'...')
                            print('服务器已启动。')
            else :
                os.system('color 0C')
                print("Java 版本不对！请更换正确的 Java 版本。")
                print("Azul 下载地址：")
                print("https://www.azul.com/downloads/")
                os.system('pause')
            main()
        def r2():
            main()

        os.system('color 0B')
        os.system('cls')

        home_dir = os.environ.get('JAVA_HOME')

        print('-'*64)
        print(data)
        print('直接关闭程序后服务器有可能不会关闭，请手动在任务管理器关闭或提前输入stop命令。')
        print("(Neo)Forge加载器需要自己手动设置启动脚本，且其不会被程序配置影响，需要手动调整。")
        print('-'*64)
        print('[1] 启动服务器（自动重启）')
        print('[2] 返回任务执行界面。')
        print('-'*64)

        choice=input('输入：')
        locals()['r'+choice]()

    def m3():

        os.system('color 0B')
        os.system('cls')

        with open('eula.txt','w') as file:
            file.write('eula=true\n')
        print('eula.txt 已修改。')
        os.system('pause')
        main()

    def m4():

        def o1():
            global Xms
            os.system('cls')
            print('-'*64)
            print('最小内存（Gib）')
            print('原数值：'+str(Xms))
            print('-'*64)
            print('请输入将修改的数值。')
            print('-'*64)
            Xms=int(input('输入：'))
            os.system('cls')
            print('最小内存（Gib）已修改。')
            os.system('pause')
            m4()
        
        def o2():
            global Xmx
            os.system('cls')
            print('-'*64)
            print('最大内存（Gib）')
            print('原数值：'+str(Xmx))
            print('-'*64)
            print('请输入将修改的数值。')
            print('-'*64)
            Xmx=int(input('输入：'))
            os.system('cls')
            print('最大内存（Gib）已修改。')
            os.system('pause')
            m4()

        def o3():
            global jarcore_name
            os.system('cls')
            print('-'*64)
            print('服务器核心名称（jar）')
            print('原名称：'+jarcore_name)
            print('-'*64)
            print('请输入将修改的名称。')
            print('-'*64)
            jarcore_name=input('输入：')
            os.system('cls')
            print('服务器核心名称（jar）已修改。')
            os.system('pause')
            m4()

        def o4():
            global jarcore_loader
            os.system('cls')
            print('-'*64)
            print('服务器加载器')
            print('原服务器加载器：'+jarcore_loader)
            print('-'*64)
            print('Vanilla')
            print('Fabric')
            print('Quilt')
            print('-'*64)
            print('Forge')
            print('Neoforge')
            jarcore_loader=input('输入：')
            os.system('cls')
            print('服务器加载器已修改。')
            os.system('pause')
            m4()

        def o5():
            global Version
            os.system('cls')
            print('-'*64)
            print('服务器游戏版本')
            print('原版本：'+Version)
            print('-'*64)
            print('请输入将修改的版本。')
            print('-'*64)
            Version=input('输入：')
            os.system('cls')
            print('服务器游戏版本已修改。')
            os.system('pause')
            m4()

        def o6():
            global Xms,Xmx,jarcore_name,jarcore_loader,data
            data['Xms']=Xms
            data['Xmx']=Xmx
            data['jarcore_name']=jarcore_name
            data['jarcore_loader']=jarcore_loader
            with open('options.json','w',encoding='utf-8') as file:
                file.write(json.dumps(data, indent=4))
            main()

        def o0():
            global Forcedrun
            os.system('cls')
            print('-'*64)
            print('强制启动服务器（绕过版本检测）')
            print('原状态：'+Forcedrun)
            print('-'*64)
            print('请输入将修改的状态。')
            print('-'*64)
            jarcore_name=input('输入：')
            os.system('cls')
            print('强制启动服务器（绕过版本检测）已修改。')
            os.system('pause')
            m4()

        os.system('color 0F')
        os.system('cls')
        print('-'*64)
        print('请选择将修改的配置。')
        print('-'*64)
        print('[1] 设置最小内存（Gib）')
        print('[2] 设置最大内存（Gib）')
        print('[3] 设置服务器核心名称（jar）')
        print('[4] 设置服务器加载器')
        print('[5] 设置服务器游戏版本')
        print('[6] 返回执行任务界面。')
        choice=input('输入：')

        locals()['o'+choice]()

    def m5():

        os.system('color 0A')
        os.system('cls')

        print('-'*64)
        print("JAVA_HOME ："+java_home)
        print("JAVA_path ："+java_path)
        print("java_version ："+java_version)
        print('-'*64)
        print(out.decode("ascii")[0:-1])
        print('-'*64)
        flp()
        if run=="Error":
            os.system('color 0C')
            print("Java 版本不对！请更换正确的 Java 版本。")
            print("Azul 下载地址：")
            print("https://www.azul.com/downloads/")
            print('-'*64)

        os.system('pause')

        main()

    def m6():

        os.system('color 0D')
        os.system('cls')
        print('Minecraft Server Runner 已关闭。')

    flp()

    os.system('title Minecraft Server Runner')
    os.system('color 0A')
    os.system('cls')

    print('-'*64)
    print("INFINITIVE")
    print('-'*64)
    print('请选择将执行的任务。')
    print('-'*64)
    print('[1] 启动服务器')
    print('[2] 启动服务器（自动重启）')
    print('[3] 创建/修改 eula.txt')
    print('[4] 修改启动配置')
    print('[5] 检测服务器运行环境')
    
    print('[6] 关闭 Minecraft Server Runner')
    print('-'*64)
    choice=input('输入：')

    locals()['m'+choice]()

if __name__=='__main__':
    main()
