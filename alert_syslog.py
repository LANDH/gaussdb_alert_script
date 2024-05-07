import socket
import requests
import hmac
import hashlib
import time
import json
import urllib.parse
import base64
import re

# 配置信息
SYSLOG_SERVER_IP = 'xx.xx.xx.xx'  # Syslog服务器IP地址
SYSLOG_SERVER_PORT = 514  # Syslog服务器端口号,TCP协议端口
# 钉钉、飞书、企微机器人
WEBHOOK_URL = '<钉钉、飞书、企微机器人地址>'  # Webhook URL地址
WEBHOOK_SECRET = '<钉钉、飞书、企微机器人token>'  # Webhook Secret令牌

def send_to_dingtalk(message):
    """
    向钉钉发送消息

    Args:
        message (str): 消息内容
    """
    timestamp = str(round(time.time() * 1000))
    secret_enc = WEBHOOK_SECRET.encode('utf-8')
    string_to_sign = f'{timestamp}\n{WEBHOOK_SECRET}'
    hmac_code = hmac.new(secret_enc, string_to_sign.encode('utf-8'), hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    headers = {'Content-Type': 'application/json'}
    data = {
        'msgtype': 'markdown',
        'markdown': {
            'title': 'Alarm Notification',
            'text': message
        },
        'sign': sign,
        'timestamp': timestamp
    }

    response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(data))
    print("钉钉Webhook平台响应:", response.text)

def fix_nested_json(raw_message):
    """
    修复嵌套的JSON消息格式

    Args:
        raw_message (str): 原始消息

    Returns:
        dict: 修复后的JSON数据
    """
    try:
        corrected = re.sub(r'"\{', '{', raw_message)
        corrected = re.sub(r'\}"', '}', corrected)
        corrected = corrected.replace('"{', '{')
        corrected = corrected.replace('}"', '}')
        corrected = corrected.replace('\\"', '"')
        return json.loads(corrected)
    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        return None

def format_status(status):
    """
    格式化告警状态

    Args:
        status (str): 告警状态

    Returns:
        str: 格式化后的状态
    """
    if status == "RAISED":
        return f"<font color=\"#FF0000\">正在发生⚠️</font>"
    elif status in ["Recovered", "Cleared"]:
        return f"<font color=\"#00FF00\">告警恢复😀</font>"
    else:
        return status

def format_level(level):
    """
    格式化告警等级

    Args:
        level (str): 告警等级

    Returns:
        str: 格式化后的等级
    """
    if level == "WARNING":
        return f"<font color=\"#0000FF\">低危(🔥)</font>"
    elif level == "CRITICAL":
        return f"<font color=\"#FFA500\">中危(🔥🔥)</font>"
    elif level == "FAULT":
        return f"<font color=\"#FF0000\">高危(🔥🔥🔥)</font>"
    else:
        return level

def convert_to_markdown(data):
    """
    将数据转换为Markdown格式

    Args:
        data (dict): 原始数据

    Returns:
        str: Markdown格式的消息
    """
    if data is None or 'EventDesc' not in data:
        return "Error in data format or missing 'EventDesc' key."
    event_desc = data.get('EventDesc')
    if not event_desc or 'records' not in event_desc:
        return "Error: 'EventDesc' is missing or 'records' not found."
    
    markdown_message = ""
    for record in event_desc['records']:
        alarm_info = record.get('value')
        if not alarm_info:
            continue

        status = alarm_info.get('Status', 'N/A')
        formatted_status = format_status(status)

        level = alarm_info.get('Level', 'N/A')
        formatted_level = format_level(level)

        markdown_message += f"**告警名称:** {alarm_info.get('alarmName', 'N/A')}  \n"
        markdown_message += f"**告警状态:** {formatted_status}  \n"
        markdown_message += f"**告警等级:** {formatted_level}  \n"
        markdown_message += f"**触发时间:** {alarm_info.get('alarmRaisedTime', 'N/A')}  \n"
        markdown_message += f"**首次触发时间:** {alarm_info.get('alarmFirstRaisedTime', 'N/A')}  \n"
        markdown_message += f"**告警集群名称:** {alarm_info.get('ClusterName', 'N/A')}  \n"
        markdown_message += f"**告警主机名称:** {alarm_info.get('HostName', 'N/A')}  \n"
        markdown_message += f"**告警主机 IP:** {alarm_info.get('HostIP', 'N/A')}  \n"
        markdown_message += f"**Source Type:** {alarm_info.get('SourceType', 'N/A')}  \n"
        markdown_message += f"**告警详情:** {alarm_info.get('Details', 'N/A')}  \n"
        markdown_message += f"**Current Observed Value:** {alarm_info.get('CurrentObservedValue', 'N/A')}  \n"
        markdown_message += f"**故障处理建议:** {alarm_info.get('Suggestions', 'N/A')}  \n"

    return markdown_message

def syslog_server():
    """
    Syslog服务器
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SYSLOG_SERVER_IP, SYSLOG_SERVER_PORT))
    server_socket.listen(5)
    print(f"Syslog server is listening on {SYSLOG_SERVER_IP}:{SYSLOG_SERVER_PORT}")

    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection from {address} has been established.")
        message = client_socket.recv(4096).decode('utf-8')
        print(f"Received raw syslog message from {address}: {message}")

        json_start = message.find('{')
        json_data = fix_nested_json(message[json_start:])

        markdown_message = convert_to_markdown(json_data)
        send_to_dingtalk(markdown_message)

        client_socket.close()

if __name__ == "__main__":
    syslog_server()
