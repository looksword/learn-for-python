# -*- coding:utf-8 -*-
import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
import paramiko
import os
import csv

_XFER_FILE = 'FILE'
_XFER_DIR  = 'DIR'

_TXTDIR = os.path.join(os.getcwd(),'log')
if not os.path.exists(_TXTDIR):
    os.mkdir(_TXTDIR)

def Write2Txt(txtdir,txtname,appendtext):
    txtpath = os.path.join(txtdir,txtname)
    with open(txtpath,"a+") as f:
        f.write(appendtext + '\n')

class MainWindow(object):
    # 构造方法
    def __init__(self, arg):
        # 超类调用
        super(MainWindow, self).__init__()

        # 赋值参数[字典]
        # 参数格式 arg = {'ip':'填ip','user':'用户名','password':'密码','port':22}
        self.arg = arg
        # 赋值参数[FTP]
        self.sftp = None

        # 调试日志
        print(self.arg)


    # 启动程序
    def startup(self):
        # 连接FTP
        if self.sftp != None:
            print(u'您已经成功连接了')
        tmpstr = u'开始连接...用户名:'+self.arg['user']+u'  密码:'+self.arg['password']+' IP:'+self.arg['ip']+u' 端口:'+str(self.arg['port'])
        print(tmpstr)
        Write2Txt(_TXTDIR,self.arg['sn'] + r'.txt',tmpstr)
        try:
            transport = paramiko.Transport((self.arg['ip'], self.arg['port']))
            transport.connect(username=self.arg['user'], password=self.arg['password'])
            self.sftp = paramiko.SFTPClient.from_transport(transport)
            print(u'连接成功 '+self.arg['ip'])
        except Exception as e:
            print(u'连接失败：'+str(e))

    # 关闭程序
    def shutdown(self):
        # 关闭FTP
        if self.sftp:
            self.sftp.close() 
            print('### disconnect sftp server: %s!'%self.arg['ip'])
            Write2Txt(_TXTDIR,self.arg['sn'] + r'.txt','### disconnect sftp server: %s!'%self.arg['ip'])
            self.sftp = None 

    # 处理上传
    def upload(self, source, target, replace):
        ### 操作数据
        # 来源路径
        source = source.replace('\\', '/')
        # 目标路径
        target = target.replace('\\', '/')


        ### 验证数据
        if not os.path.exists(source):
            print(u'来源资源不存在，请检查：' + source)
            Write2Txt(_TXTDIR,self.arg['sn'] + r'.txt',u'来源资源不存在，请检查：' + source)
            return


        ### 格式数据
        # 格式化目标路径
        self.__makePath(target)


        ### 处理数据
        # 文件媒体数据(文件类型, 文件名称)
        filetype, filename = self.__filetype(source)
        # 判断文件类型
        if filetype == _XFER_DIR:
            # 1.目录 
            self.uploadDir(source, target, replace)
        elif filetype == _XFER_FILE:
            # 2.文件 
            self.uploadFile(source, filename, replace)
        
        return


    # 传送目录
    def uploadDir(self, source, target, replace):
        ### 验证数据
        # 判断目录存在
        if not os.path.isdir(source):   
            print(u'这个函数是用来传送本地目录的')
            Write2Txt(_TXTDIR,self.arg['sn'] + r'.txt',u'这个函数是用来传送本地目录的')
            return

        ### 处理数据
        # 遍历目录内容，上传资源
        for file in os.listdir(source):
            # 资源路径
            filepath = os.path.join(source, file) 

            # 判断资源文件类型
            if os.path.isfile(filepath): 
                # 1.文件
                self.uploadFile(filepath, file, replace) 
            elif os.path.isdir(filepath):
                # 2.目录
                try:
                    self.sftp.chdir(file) 
                except:
                    self.sftp.mkdir(file)
                    self.sftp.chdir(file) 
                self.uploadDir(filepath, file, replace)

        ### 重置数据
        # 返回上一层目录
        self.sftp.chdir('..') 

    # 传送文件
    def uploadFile(self, filepath, filename, replace):
        ### 验证数据
        # 验证文件类型
        if not os.path.isfile(filepath):
            print(u'这个函数是用来传送单个文件的')
            Write2Txt(_TXTDIR,self.arg['sn'] + r'.txt',u'这个函数是用来传送单个文件的')
            return
        # 验证文件存在
        if not os.path.exists(filepath):
            print(u'err:本地文件不存在，检查一下'+filepath)
            Write2Txt(_TXTDIR,self.arg['sn'] + r'.txt',u'err:本地文件不存在，检查一下'+filepath)
            return
        # 验证FTP已连接
        if self.sftp == None:
            print(u'sftp 还未链接')
            Write2Txt(_TXTDIR,self.arg['sn'] + r'.txt',u'sftp 还未链接')
            return


        ### 处理数据
#         # 判断文件存在是否覆盖
#         if not replace:
#             if filename in self.sftp.listdir():
#                 print(u'[*] 这个文件已经存在了，选择跳过:' + filepath + ' -> ' + self.sftp.getcwd() + '/' + filename
#                 return
        # 上传文件
        try:
            self.sftp.put(filepath, filename)
            print(u'[+] 上传成功:' + filepath + ' -> ' + self.sftp.getcwd() + '/' + filename)
            Write2Txt(_TXTDIR,self.arg['sn'] + r'.txt',u'[+] 上传成功:' + filepath + ' -> ' + self.sftp.getcwd() + '/' + filename)
        except Exception as e:
            print(u'[+] 上传失败:' + filepath + ' because ' + str(e))
            Write2Txt(_TXTDIR,self.arg['sn'] + r'.txt',u'[+] 上传失败:' + filepath + ' because ' + str(e))


    # 获得文件媒体数据({文件/目录, 文件名称})
    def __filetype(self, source):
        # 判断文件类型
        if os.path.isfile(source):
            # 1.文件
            index = source.rfind('/')
            return _XFER_FILE, source[index+1:]
        elif os.path.isdir(source):  
            # 2.目录
            return _XFER_DIR, ''


    # 创建目标路径
    # 说明: 目标路径不存在则依次创建路径目录
    def __makePath(self, target):
        # 切换根目录
        self.sftp.chdir('/')

        # 分割目标目录为目录单元集合
        data = target.split('/')
        # 进入目标目录, 目录不存在则创建
        for item in data:
            try:
                self.sftp.chdir(item) 
                print(u'要上传的目录已经存在，选择性进入合并：' + item)
                Write2Txt(_TXTDIR,self.arg['sn'] + r'.txt',u'要上传的目录已经存在，选择性进入合并：' + item)
            except:
                self.sftp.mkdir(item)
                self.sftp.chdir(item) 
                print(u'要上传的目录不存在，创建目录：' + item)
                Write2Txt(_TXTDIR,self.arg['sn'] + r'.txt',u'要上传的目录已经存在，选择性进入合并：' + item)

    def main(source, target, replace=False):
        arg = {'ip':填ip,'user':填用户名,'password':填密码,'port':22}

        me  = MainWindow(arg)
        me.startup()

        me.upload(source, target, replace)
        me.shutdown()

def ssh_exec_command(host,user,password, cmd,sn,timeout=10):
    """
    使用ssh连接远程服务器执行命令
    :param host: 主机名
    :param user: 用户名
    :param password: 密码
    :param cmd: 执行的命令
    :param seconds: 超时时间(默认)，必须是int类型
    :return: dict
    """
    result = {'status': 1, 'data': None}  # 返回结果
    try:
        ssh = paramiko.SSHClient()  # 创建一个新的SSHClient实例
        ssh.banner_timeout = timeout
        # 设置host key,如果在"known_hosts"中没有保存相关的信息, SSHClient 默认行为是拒绝连接, 会提示yes/no
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, 22, user, password, timeout=timeout)  # 连接远程服务器,超时时间1秒
        stdin, stdout, stderr = ssh.exec_command(cmd,get_pty=True,timeout=timeout)  # 执行命令
        out = stdout.readlines()    # 执行结果,readlines会返回列表
        # 执行状态,0表示成功，1表示失败
        channel = stdout.channel
        status = channel.recv_exit_status()
        ssh.close()  # 关闭ssh连接

        # 修改返回结果
        result['status'] = status
        result['data'] = out
        return result
    except Exception as e:
        print(e)
        print("错误, 登录服务器或者执行命令超时!!! ip: {} 命令: {}".format(ip,cmd))
        Write2Txt(_TXTDIR,self.arg['sn'] + r'.txt',"错误, 登录服务器或者执行命令超时!!! ip: {} 命令: {}".format(ip,cmd))

if __name__ == '__main__':
    ip_sn = []
    with open('ip_sn.csv', 'r', newline='') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            ip_sn.append(row)
    print(ip_sn)
    
    for row in ip_sn:
        # """
        # 先熟悉一下sftp有哪些用法  sftp.listdir(可以传参可以为空) 返回当前目录下清单列表
        # mkdir 创建目录对应rmdir   sftp.put(本地路径,远程要存的文件名) chdir进入子目录
        # """
        host = row[0]#'10.1.45.37'
        sn = row[1]
        user = 'root'
        password = '123456'
        cmd = 'chmod -R 777 /custom'
        arg = {'ip':'填ip','user':'填用户名','password':'填密码','port':22,'sn':'logname'}
        arg['ip'] = host
        arg['user'] = user
        arg['password'] = password
        arg['sn'] = sn
        
        me  = MainWindow(arg)
        me.startup()
        # 要上传的本地文件夹路径
        source = os.getcwd()+r'/custom'#r'E:\looksword\jupyter\custom'
        # 上传到哪里 [远程目录]
        target = r'/custom'
        replace = True
        me.upload(source, target, replace)
        me.shutdown()

        ssh_exec_command(host,user,password,cmd,sn)
        
        print(sn)
        Write2Txt(_TXTDIR,sn + r'.txt',sn+' finish upload.\n')
