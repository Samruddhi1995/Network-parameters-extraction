# Example 
```
root@debian:~# python netmon.py ipaddress authentication sql_auth

The script will be executed using above files


Errors in connection are written in file SQL_errors


All IP addresss are valid


Checking IP reachability. Please wait...


All devices are rechable. Checking the SSH connection.


SSH Username/password file has been validated.


SQL Username/password file has been validated.


Checking SSH connection and extracting parameters. Will take some time.

* SSH Successful for device 10.1.1.1
```

#Sql database
```
mysql> describe CPUutilization
    -> ;
+----------------+-------------+------+-----+---------+-------+
| Field          | Type        | Null | Key | Default | Extra |
+----------------+-------------+------+-----+---------+-------+
| cpuutilization | float       | YES  |     | NULL    |       |
| Top3devices    | varchar(50) | YES  |     | NULL    |       |
| Polltimestamp  | varchar(30) | YES  |     | NULL    |       |
+----------------+-------------+------+-----+---------+-------+
3 rows in set (0.00 sec)

mysql> describe NetworkDevices;
+---------------+-------------+------+-----+---------+-------+
| Field         | Type        | Null | Key | Default | Extra |
+---------------+-------------+------+-----+---------+-------+
| hostname      | varchar(30) | YES  |     | NULL    |       |
| macaddr       | varchar(20) | NO   | PRI | NULL    |       |
| IOSversion    | varchar(20) | YES  |     | NULL    |       |
| uptime        | int(11)     | YES  |     | NULL    |       |
| introutingpro | varchar(30) | YES  |     | NULL    |       |
| extroutingpro | varchar(30) | YES  |     | NULL    |       |



+----------+----------------+------------+--------+---------------+---------------+
| hostname | macaddr        | IOSversion | uptime | introutingpro | extroutingpro |
+----------+----------------+------------+--------+---------------+---------------+
| R2       | c202.1104.0000 | 12.3(11)T3 |   3060 |          rip  |               |
+----------+----------------+------------+--------+---------------+---------------+

+----------------+-------------+----------------------------+
| cpuutilization | Top3devices | Polltimestamp              |
+----------------+-------------+----------------------------+
|              0 | R2          | 2018-02-09 20:27:36.053683 |
|              0 | R2          | 2018-02-09 20:44:57.553129 |
+----------------+-------------+----------------------------+
```
