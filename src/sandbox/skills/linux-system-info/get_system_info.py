#!/usr/bin/env python3
"""
系统信息收集脚本
"""
import platform
import sys
import subprocess
import json
import os
import socket
from datetime import datetime

def get_network_info():
    """获取网络信息，包括IP地址"""
    network_info = {}
    
    try:
        # 获取主机名
        hostname = socket.gethostname()
        network_info['主机名'] = hostname
        
        # 获取所有网络接口的IP地址
        interfaces = {}
        
        # 获取IPv4地址
        try:
            # 获取本机所有IP地址
            all_ips = socket.getaddrinfo(hostname, None)
            ipv4_addresses = []
            ipv6_addresses = []
            
            for ip_info in all_ips:
                ip_addr = ip_info[4][0]
                if ':' in ip_addr:  # IPv6
                    if ip_addr not in ipv6_addresses and not ip_addr.startswith('fe80'):
                        ipv6_addresses.append(ip_addr)
                else:  # IPv4
                    if ip_addr not in ipv4_addresses and not ip_addr.startswith('127.'):
                        ipv4_addresses.append(ip_addr)
            
            interfaces['IPv4地址'] = ipv4_addresses if ipv4_addresses else ['未找到']
            interfaces['IPv6地址'] = ipv6_addresses if ipv6_addresses else ['未找到']
        except Exception as e:
            interfaces['错误'] = f'获取IP地址失败: {str(e)}'
        
        # 获取主要IP地址（用于连接外网的IP）
        try:
            # 创建一个UDP socket连接到公共DNS服务器
            # 这不会实际发送数据，只是为了确定本机的出口IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            primary_ip = s.getsockname()[0]
            s.close()
            interfaces['主要IP地址'] = primary_ip
        except Exception as e:
            interfaces['主要IP地址'] = f'获取失败: {str(e)}'
        
        network_info['网络接口'] = interfaces
        
        # 使用系统命令获取更详细的网络信息
        try:
            if platform.system() == 'Windows':
                # Windows系统使用ipconfig
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
                network_info['详细配置'] = result.stdout
            else:
                # Linux/Mac系统使用ifconfig或ip命令
                try:
                    result = subprocess.run(['ip', 'addr'], capture_output=True, text=True, timeout=10)
                    network_info['详细配置'] = result.stdout
                except:
                    result = subprocess.run(['ifconfig'], capture_output=True, text=True, timeout=10)
                    network_info['详细配置'] = result.stdout
        except Exception as e:
            network_info['详细配置'] = f'获取详细配置失败: {str(e)}'
            
    except Exception as e:
        network_info['错误'] = f'获取网络信息失败: {str(e)}'
    
    return network_info

def get_system_info():
    """收集并返回系统信息字典"""
    print("hello---------正在收集系统信息...")
    info = {}

    # 1. 操作系统信息
    info['操作系统'] = {
        '系统': platform.system(),
        '版本': platform.version(),
        '发行版': platform.release(),
        '架构': platform.architecture()[0],
        '机器': platform.machine(),
        '处理器': platform.processor(),
    }

    # 2. Python环境信息
    info['Python环境'] = {
        '版本': sys.version,
        '可执行文件': sys.executable,
        '路径': sys.path
    }

    # 3. 网络信息
    info['网络信息'] = get_network_info()

    # 4. 当前工作目录和用户
    info['当前状态'] = {
        '工作目录': os.getcwd(),
        '用户名': os.getenv('USERNAME') or os.getenv('USER'),
        '时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return info

if __name__ == '__main__':
    print("=" * 50)
    print("            系统信息报告")
    print("=" * 50)
    sys_info = get_system_info()

    for category, data in sys_info.items():
        print(f"\n【{category}】")
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"  {key}: {value}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for k, v in item.items():
                        print(f"    {k}: {v}")
                    print()  # 每个磁盘信息后空一行
                else:
                    print(f"  - {item}")
        else:
            print(f"  {data}")
    print("\n" + "=" * 50)