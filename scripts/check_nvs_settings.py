#!/usr/bin/env python3
"""
NVS设置检查工具
用于查看ESP32设备中NVS存储的配置值
"""

import subprocess
import sys
import os

def run_esp_idf_command(cmd):
    """运行ESP-IDF命令并返回输出"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"错误: {result.stderr.strip()}"
    except Exception as e:
        return f"执行命令失败: {e}"

def check_nvs_partition_info():
    """检查NVS分区信息"""
    print("=== NVS分区信息 ===")
    # 使用idf.py partition_table 命令查看分区信息
    cmd = "idf.py partition-table"
    output = run_esp_idf_command(cmd)
    print(output)

def check_nvs_dump():
    """使用nvs_dump工具查看NVS内容"""
    print("\n=== NVS内容转储 ===")
    # 使用nvs_dump工具（需要先构建项目）
    cmd = "idf.py build"
    print("构建项目...")
    build_output = run_esp_idf_command(cmd)
    if "错误" in build_output:
        print(f"构建失败: {build_output}")
        return
    
    # 尝试使用nvs_dump
    cmd = "python -m esptool --chip esp32s3 read_flash 0x9000 0x6000 nvs.bin && python -m nvs_partition_gen nvs_dump nvs.bin"
    dump_output = run_esp_idf_command(cmd)
    print(dump_output)

def check_common_namespaces():
    """检查常见的命名空间"""
    print("\n=== 常见命名空间检查 ===")
    namespaces = ["websocket", "mcp", "assets", "settings", "system", "wifi"]
    
    for ns in namespaces:
        print(f"\n命名空间: {ns}")
        # 使用idf.py monitor来查看日志输出
        # 这里我们只能提供指导，因为实际读取需要设备运行
        print(f"  在设备运行时，检查日志中关于 {ns} 的配置信息")

def main():
    print("ESP32 NVS设置检查工具")
    print("=====================")
    
    # 检查是否在ESP-IDF环境中
    if "IDF_PATH" not in os.environ:
        print("警告: 未检测到ESP-IDF环境")
        print("请确保在ESP-IDF环境中运行此脚本")
    
    # 检查NVS分区信息
    check_nvs_partition_info()
    
    # 检查NVS内容
    check_nvs_dump()
    
    # 检查常见命名空间
    check_common_namespaces()
    
    print("\n=== 手动检查方法 ===")
    print("1. 使用idf.py monitor查看设备启动日志")
    print("2. 在设备运行时，通过串口发送命令查看配置")
    print("3. 使用nvs_dump工具分析NVS分区")
    print("4. 在应用程序中添加调试代码来打印配置值")

if __name__ == "__main__":
    main()
