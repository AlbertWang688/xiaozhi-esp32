#!/usr/bin/env python3
"""
简单的ESP32 NVS内容查看工具
使用ESP-IDF工具直接读取NVS分区内容
"""

import subprocess
import sys
import os
import json
import tempfile
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, 
                              text=True, cwd=cwd)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"错误: {result.stderr.strip()}"
    except Exception as e:
        return f"执行命令失败: {e}"

def get_nvs_partition_info():
    """获取NVS分区信息"""
    print("=== NVS分区信息 ===")
    cmd = "idf.py partition-table"
    output = run_command(cmd)
    print(output)
    return output

def extract_nvs_partition():
    """从分区表中提取NVS分区信息"""
    cmd = "idf.py partition-table"
    output = run_command(cmd)
    
    nvs_info = {}
    for line in output.split('\n'):
        if 'nvs' in line.lower() and 'data' in line.lower():
            parts = line.split()
            if len(parts) >= 4:
                nvs_info = {
                    'name': parts[0],
                    'type': parts[1],
                    'subtype': parts[2],
                    'offset': parts[3],
                    'size': parts[4] if len(parts) > 4 else '未知'
                }
                break
    return nvs_info

def read_nvs_partition(port):
    """读取NVS分区内容"""
    print(f"\n=== 从设备 {port} 读取NVS分区 ===")
    
    # 获取NVS分区信息
    nvs_info = extract_nvs_partition()
    if not nvs_info:
        print("未找到NVS分区信息")
        return None
        
    print(f"NVS分区: {nvs_info}")
    
    # 读取NVS分区数据
    offset = nvs_info['offset']
    size = nvs_info['size']
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # 使用esptool读取NVS分区
        cmd = f"python -m esptool --chip esp32s3 -p {port} read_flash {offset} {size} {temp_filename}"
        print(f"执行命令: {cmd}")
        result = run_command(cmd)
        
        if "错误" in result:
            print(f"读取NVS分区失败: {result}")
            return None
            
        print("NVS分区读取成功")
        
        # 使用nvs_partition_gen工具解析NVS数据
        cmd = f"python -m nvs_partition_gen nvs_dump {temp_filename}"
        nvs_content = run_command(cmd)
        
        if "错误" in nvs_content:
            print(f"解析NVS数据失败: {nvs_content}")
            return None
            
        return nvs_content
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

def parse_nvs_dump(nvs_dump):
    """解析nvs_dump工具的输出"""
    nvs_data = {}
    current_namespace = None
    
    for line in nvs_dump.split('\n'):
        line = line.strip()
        
        # 解析命名空间
        if line.startswith('Namespace:'):
            current_namespace = line.split(':', 1)[1].strip()
            nvs_data[current_namespace] = {}
            
        # 解析键值对
        elif current_namespace and ':' in line and not line.startswith('==='):
            try:
                key_part, value_part = line.split(':', 1)
                key = key_part.strip()
                value_info = value_part.strip()
                
                # 解析值和类型
                if '[' in value_info and ']' in value_info:
                    # 格式: value [type]
                    value_str, type_str = value_info.split('[', 1)
                    value = value_str.strip()
                    data_type = type_str.replace(']', '').strip()
                    
                    # 转换值类型
                    if data_type == 'str':
                        pass  # 保持字符串
                    elif data_type in ['i32', 'u32']:
                        try:
                            value = int(value)
                        except ValueError:
                            pass
                    elif data_type == 'u8':
                        try:
                            value = int(value)
                        except ValueError:
                            pass
                    
                    nvs_data[current_namespace][key] = {
                        'value': value,
                        'type': data_type
                    }
                    
            except Exception as e:
                print(f"解析行失败: {line}, 错误: {e}")
    
    return nvs_data

def display_nvs_data(nvs_data):
    """显示NVS数据"""
    if not nvs_data:
        print("未找到NVS数据")
        return
        
    print("\n" + "="*50)
    print("NVS内容汇总")
    print("="*50)
    
    for namespace, items in nvs_data.items():
        print(f"\n命名空间: {namespace}")
        print("-" * 30)
        
        if not items:
            print("  (空)")
            continue
            
        for key, info in items.items():
            value = info['value']
            data_type = info['type']
            print(f"  {key}: {value} ({data_type})")

def save_to_json(nvs_data, filename="nvs_backup.json"):
    """保存NVS数据到JSON文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(nvs_data, f, indent=2, ensure_ascii=False)
        print(f"\nNVS数据已保存到: {filename}")
    except Exception as e:
        print(f"保存文件失败: {e}")

def get_serial_ports():
    """获取可用的串口列表"""
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        return [port.device for port in ports]
    except ImportError:
        print("请安装pyserial: pip install pyserial")
        return []

def main():
    print("ESP32 NVS内容查看工具")
    print("=" * 40)
    
    # 检查ESP-IDF环境
    if "IDF_PATH" not in os.environ:
        print("警告: 未检测到ESP-IDF环境")
        print("请确保在ESP-IDF环境中运行此脚本")
        return
    
    # 获取串口列表
    ports = get_serial_ports()
    if not ports:
        print("未找到可用的串口设备")
        return
        
    print("可用的串口:")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port}")
    
    # 选择串口
    try:
        choice = input(f"\n选择串口 (1-{len(ports)}): ").strip()
        port_index = int(choice) - 1
        if 0 <= port_index < len(ports):
            selected_port = ports[port_index]
        else:
            print("无效选择")
            return
    except ValueError:
        print("请输入数字")
        return
    
    # 显示分区信息
    get_nvs_partition_info()
    
    # 读取NVS数据
    nvs_dump = read_nvs_partition(selected_port)
    if nvs_dump:
        print("\n原始NVS数据:")
        print(nvs_dump)
        
        # 解析并显示NVS数据
        nvs_data = parse_nvs_dump(nvs_dump)
        display_nvs_data(nvs_data)
        
        # 询问是否保存
        save = input("\n是否保存到JSON文件? (y/n): ").lower().strip()
        if save == 'y':
            filename = input("输入文件名 (默认: nvs_backup.json): ").strip()
            if not filename:
                filename = "nvs_backup.json"
            save_to_json(nvs_data, filename)
    else:
        print("无法读取NVS数据")

if __name__ == "__main__":
    # 检查必要的Python包
    try:
        import serial.tools.list_ports
    except ImportError:
        print("缺少必要的Python包，请安装:")
        print("pip install pyserial")
        sys.exit(1)
        
    main()
