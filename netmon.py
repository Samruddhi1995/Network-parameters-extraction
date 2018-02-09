import MySQLdb as mdb
import paramiko
import threading
import os.path
import subprocess
import datetime
import time
import sys
import re

if len(sys.argv) == 4:
    ip_file = sys.argv[1]
    ssh_auth_file = sys.argv[2]
    sql_auth_file = sys.argv[3]
    print "\nThe script will be executed using above files\n"
    
else:
    print "\nInvalid number of files are entered. Please try again.\n"
    sys.exit()
    
#checking the validity of the ip addresses in ip_file and cheaking their rechability
def is_ip_valid():
    #gobal list of ip addresses
    global iplist
    iplist = []

    while True:
            flag1 = []
            try:
                f = open (ip_file,'r')
                f.seek(0)
                iplist = f.readlines()
                f.close()
                
                #print iplist
                
            except IOError:
                
                print "\nFile %s does not exists, please try again :) \n" %ip_file
                continue
            
    #checking validity of the IP addresses
            
            for ip in iplist:
                a = ip.split('.')
                if (len(a)==4) and (1 <= int(a[0]) <= 223) and (int(a[0]) != 127) and (int(a[0]) != 169 or int(a[1]) != 254) and (0 <= int(a[0]) <= 255 and 0 <= int(a[1]) <= 255 and 0 <= int(a[2]) <= 255 and 0 <= int(a[3]) <= 255):
                    flag1.append(True)
                    continue
                else:
                    flag1.append(False)
                    break
                
            #print flag1
        
            if False in flag1:
                print "\nFile contains atleat one invalid IP address. Please the file again.\n"
                sys.exit()
            else:
                print "\nAll IP addresss are valid\n"
                break
        
#checking the conectivity to all addresss by ping 
        

    print "\nChecking IP reachability. Please wait...\n"
    
    check2 = False
    
    while True:
        #print iplist
        for ip in iplist:
            exit_code = subprocess.call(['ping', '-c', '2', '-w', '2', '-q', '-n', ip], stdout = subprocess.PIPE)
            #print exit_code
            if exit_code  == 0:
                check2 = True
                continue
            
            elif exit_code == 2:
                print "\n* No response from device %s." % ip
                check2 = False
                break
            
            else:
                print "\n Ping to the following %s device has FAILED" % ip
                check2 = False
                break
            
        if check2 == False:
            print "\nPing to atleast one device failed. Please check the connectivity. \n"
            sys.exit()
            
        elif check2 == True:
            print "\nAll devices are rechable. Checking the SSH connection.\n"
            break
        break


def validate_ssh_auth_file():
    while True:
        if os.path.isfile(ssh_auth_file) == True:
            print "\nSSH Username/password file has been validated.\n"
            break
        
        else:
            print "\n* File %s does not exist! Please check and try again!\n" % ssh_auth_file
            sys.exit()
            
def validate_sql_auth_file():
    while True:
        if os.path.isfile(sql_auth_file) == True:
            print "\nSQL Username/password file has been validated.\n"
            break
        
        else:
            print "\n* File %s does not exist! Please check and try again!\n" % sql_auth_file
            sys.exit()
#setting up sql connection using authentication info from sql_auth_file and errors in connection are written in SQL_errors        

def sql_connection(command, values):
    global check 
    f1 = open(sql_auth_file,"r")
    f1.seek(0)
    host = ((f1.readlines()[0]).split(","))[0]
    f1.seek(0)
    user = ((f1.readlines()[0]).split(","))[1]
    f1.seek(0)
    password = ((f1.readlines()[0]).split(","))[2]
    f1.seek(0)
    database = ((((f1.readlines()[0]).split(","))[3])).rstrip("\n")
    try:
        #print "\nErrors in connection are written in file SQL_errors\n"
        connection = mdb.connect(host,user,password,database )
        cursor = connection.cursor()
        cursor.execute("USE netmon")
        cursor.execute(command, values)
        connection.commit()
    except mdb.Error as err:
        check = False
        f2 = open("SQL_errors","a")
        print >>f2, (str(datetime.datetime.now())+" "+str(err[0])+" "+err[1])
        f2.close()
        print "flag is"+str(check)
    f1.close()
    
def open_ssh_conn(ip):
    try:
        f3 = open(ssh_auth_file, 'r')
        f3.seek(0)
        username = f3.readlines()[0].split(',')[0]
        f3.seek(0)
        password = f3.readlines()[0].split(',')[1].rstrip("\n")
        f3.close()
        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        session.connect(ip, username = username, password = password)
        connection = session.invoke_shell()	
        connection.send("enable\n")
        time.sleep(3)
        connection.send("cisco\n")
        time.sleep(3)
        connection.send("terminal length 0\n")
        time.sleep(3)
        connection.send("config t\n")
        time.sleep(3)
        selected_cisco_commands = '''do show version | include IOS&\
                                  do show version | include uptime&\
                                  do show ip protocols | include Routing Protocol&\
                                  do show interfaces | include bia&\
                                  do show ip int br | include (Ethernet|Serial)&\
                                  do show processes cpu | include CPU utilization&'''
                                 
        
        #Splitting commands by the "&" character
        command_list = selected_cisco_commands.split("&")
        
        #Writing each line in the command string to the device
        for each_line in command_list:
            connection.send(each_line + '\n')
            time.sleep(4)
        
        #Checking command output for IOS syntax errors
        global output
        output = connection.recv(65535)
        #print output
        if re.search(r"% Invalid input detected at", output):
            print "* There was at least one IOS syntax error on device %s \n" % ip
            
        else:
            print "* SSH Successful for device %s \n" % ip
            
    except paramiko.AuthenticationException:
        print "Invalid SSH username or password. \nPlease check the username/password file or the device configuration!\n"
        
def extract_parameters(output):
    global dict_cpu_util
    dict_cpu_util = {}
    dev_hostname = re.search(r"(.+) uptime is", output)
    hostname = dev_hostname.group(1)
    #print hostname
    
    vendor = re.search(r"(.+) Software,(.+)", output)
    vendor_name = vendor.group(1)
    #print vendor_name

    
    dev_os = re.search(r"Version (.+),", output)
    IOSVersion = dev_os.group(1)
    #print IOSVersion
    
    mac = re.findall(r"\(bia (.+)\)",output)
    mac = mac[0]
    #print mac[0]
    
    uptime = re.search(r"uptime is(.+)",output)
    uptime_list = uptime.group(1).split(",")
    #print uptime_list
    time_min = 0
    time_hours = 0
    time_week = 0
    time_day = 0
    time_year = 0
    for i in uptime_list:
        if "minute" in i:
            time_min =  int((i.split(" "))[1]) * 60
        elif "hour" in i:
            time_hours =  int((i.split(" "))[1]) * 3600
        elif "day" in i:
            time_day =  int((i.split(" "))[1]) * 86400 
        elif "week" in i:
            time_week =  int((i.split(" "))[1]) * 604800
        elif "year" in i:
            time_year =  int((i.split(" "))[1]) * 31449600       
    uptime_final =  time_min + time_hours + time_day + time_week + time_year
    #print "uptime is " + str(uptime_final)
    
    
    
    routing = re.findall(r'Routing Protocol is "(.+)"',output)
    #print routing
    external_protocols = []
    internal_protocols = []
    for i in range(1,len(routing)):
        if "bgp" in routing[i]:
            external_protocols.append(routing[i])
        else:
            internal_protocols.append(routing[i])
            
    int_pro = ",".join(internal_protocols)
    ext_pro = ",".join(external_protocols)
    #print "routing pro" + int_pro + ext_pro
    command = (
        "REPLACE INTO NetworkDevices (hostname,macaddr,IOSversion,uptime,introutingpro,extroutingpro)"
        "VALUES(%s, %s, %s, %s, %s, %s)"
    )
    data = (hostname,mac,IOSVersion,uptime_final,int_pro,ext_pro)
    
    sql_connection(command,data)
    #"REPLACE INTO NetworkDevices (hostname,macaddr,IOSversion,uptime,introutingpro,extroutingpro) VALUES(%s %s %s %d %s %s)",(hostname,mac,IOSVersion,uptime_final,int_pro,ext_pro)
    cpu_util = re.search(r"five minutes: (.+)%", output)
    cpu_util_last_5min = cpu_util.group(1)
    #print cpu_util_last_5min
    dict_cpu_util[hostname] = cpu_util_last_5min 
    #collect all cpu utilization values then calculate average and top 3
    
       
def top_1(each_dict):
    top1 = []
    for host, usage in sorted(each_dict.items(), key = lambda x: x[1], reverse = True)[-1:]:
        top1.append(host)
        top1_list = ",".join(top1)
    return top1_list
    #print top
def avg_cpu_utilization(cpu_dict):
    list = []
    for i in cpu_dict.values():
        list.append(float(i))
    cpu_avg =  sum(list) / float (len(cpu_dict.values()))
    top = top_1(dict_cpu_util)
    top_str = "".join(top)
    command = (
        "INSERT INTO CPUutilization(cpuutilization,Top3devices,Polltimestamp)"
        "VALUES(%s, %s, %s)"
    )
    data = (cpu_avg, top_str, datetime.datetime.now())
    
    sql_connection(command,data)
    #print cpu_avg





try:
    check = True

    print "\nErrors in connection are written in file SQL_errors\n"
    is_ip_valid()
    validate_ssh_auth_file()
    validate_sql_auth_file()
    print "\nChecking SSH connection and extracting parameters. Will take some time.\n"
    for ip in iplist:
        open_ssh_conn(ip)
        extract_parameters(output)
    #print dict_cpu_util
    avg_cpu_utilization(dict_cpu_util)
    if (check == False):
        print "There was error in exporting the data to MYSQL"
        
except KeyboardInterrupt:
    print "\n program aborted by user. Exiting.....\n"
    sys.exit()
        
