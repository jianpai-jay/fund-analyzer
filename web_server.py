# -*- coding: utf-8 -*-
"""
基金研究助手 - Web控制面板启动脚本
支持手机访问的一键推送功能
"""
import sys
import os
import socket

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web_app import run_web_app

def get_local_ip():
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == '__main__':
    local_ip = get_local_ip()

    print("=" * 60)
    print("基金研究助手 - Web控制面板")
    print("=" * 60)
    print()
    print("手机访问地址:")
    print(f"   http://{local_ip}:5000")
    print()
    print("电脑访问地址:")
    print("   http://localhost:5000")
    print()
    print("功能说明:")
    print("  - 一键分析并推送: 分析所有基金并推送到微信")
    print("  - 刷新状态: 手动刷新运行状态")
    print()
    print("使用提示:")
    print("  1. 确保手机和电脑在同一WiFi网络")
    print("  2. 在手机浏览器中输入上面的地址")
    print("  3. 点击大按钮即可一键分析并推送")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    print()

    run_web_app(host='0.0.0.0', port=5000, debug=False)
