# gaussdb_alert_script
高斯数据库告警对接，发送到钉钉、企微、飞书等机器人,带Unicode表情包

#由于政企版高斯数据库官方未直接提供webhook告警方式，故使用python写个程序接收告警并格式化发送到钉钉、企微、飞书等机器人。

#在高斯TPOPS平台上使用syslog方式对接告警
![image](https://github.com/LANDH/gaussdb_alert_script/assets/22723905/56b7014f-1c7f-4418-bb0b-a91240c60fae)

#使用python3版本执行

#配额screen后台运行程序
python3.7  alert_syslog.py

![image](https://github.com/LANDH/gaussdb_alert_script/assets/22723905/79687e01-ed2d-4605-ab4b-60fcd518fa57)
![image](https://github.com/LANDH/gaussdb_alert_script/assets/22723905/4198a36b-78df-4c36-81c1-fbabaf6f3055)

#脚本编写调试不易，还请各位看官交个朋友，打个赏~
![7e861dd982008cb63481c875a0cac4b](https://github.com/LANDH/gaussdb_alert_script/assets/22723905/dbc07cf7-7917-4fa9-9b6a-19b1416eb73e)
