#!/usr/bin/env python3
"""
ESP32 NVS内容查看工具
用于查看设备中NVS存储的所有内容，包括所有命名空间和键值对
"""

import subprocess
import sys
import os
import json
import argparse
from pathlib import Path

class NVSViewer:
    def __init__(self, port=None, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.project_dir = Path(__file__).parent.parent
        
    def run_command(self, cmd, capture_output=True):
        """运行命令并返回结果"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=capture_output, 
                                  text=True, cwd=self.project_dir)
            if result.returncode == 0:
                return result.stdout.strip() if capture_output else True
            else:
                return f"错误: {result.stderr.strip()}" if capture_output else False
        except Exception as e:
            return f"执行命令失败: {e}" if capture_output else False

    def get_serial_ports(self):
        """获取可用的串口列表"""
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        return [port.device for port in ports]

    def build_nvs_reader(self):
        """构建NVS读取工具"""
        print("构建项目...")
        
        # 构建整个项目
        cmd = "idf.py build"
        result = self.run_command(cmd, capture_output=False)
        if not result:
            print("构建失败")
            return None
            
        # 检查主程序是否构建成功
        build_dir = self.project_dir / "build"
        main_binary = build_dir / "xiaozhi.bin"
        
        if main_binary.exists():
            print("项目构建成功")
            return str(main_binary)
        else:
            print("主程序构建失败")
            return None

    def flash_nvs_reader(self, port):
        """烧录NVS读取工具到设备"""
        print(f"烧录到设备 {port}...")
        cmd = f"idf.py -p {port} flash"
        return self.run_command(cmd, capture_output=False)

    def read_nvs_via_monitor(self, port, timeout=15):
        """通过串口监视器读取NVS内容"""
        import threading
        import time
        import serial
        
        nvs_data = {}
        current_namespace = None
        
        def read_serial():
            nonlocal nvs_data, current_namespace
            try:
                ser = serial.Serial(port, self.baudrate, timeout=1)
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"设备输出: {line}")
                        
                        # 解析命名空间开始
                        if "=== 命名空间:" in line:
                            ns_name = line.split(":")[1].strip()
                            current_namespace = ns_name
                            nvs_data[current_namespace] = {}
                            print(f"发现命名空间: {ns_name}")
                            
                        # 解析键值对
                        elif current_namespace and ":" in line and "(" in line and ")" in line:
                            try:
                                # 解析格式: "key (类型): value"
                                parts = line.split(":", 1)
                                if len(parts) == 2:
                                    key_part = parts[0].strip()
                                    value = parts[1].strip()
                                    
                                    # 提取键名和类型
                                    key_parts = key_part.split("(")
                                    if len(key_parts) == 2:
                                        key = key_parts[0].strip()
                                        type_info = key_parts[1].replace(")", "").strip()
                                        
                                        # 转换值类型
                                        if type_info == "字符串":
                                            pass  # 保持字符串
                                        elif type_info == "整数":
                                            value = int(value)
                                        elif type_info == "布尔":
                                            value = value.lower() == "true"
                                        elif type_info == "U8":
                                            value = int(value)
                                        
                                        nvs_data[current_namespace][key] = {
                                            "value": value,
                                            "type": type_info
                                        }
                                        print(f"  读取: {key} = {value} ({type_info})")
                            except Exception as e:
                                print(f"解析行失败: {line}, 错误: {e}")
                                
            except Exception as e:
                print(f"串口读取失败: {e}")
        
        # 启动串口读取线程
        thread = threading.Thread(target=read_serial)
        thread.daemon = True
        thread.start()
        
        # 检查是否需要构建和烧录
        build_dir = self.project_dir / "build"
        main_binary = build_dir / "xiaozhi.bin"
        
        if not main_binary.exists():
            print("项目未构建，开始构建...")
            if not self.build_nvs_reader():
                print("构建失败，无法继续")
                return nvs_data
        
        # 烧录固件
        print(f"烧录固件到设备 {port}...")
        if self.flash_nvs_reader(port):
            print("等待设备重启并读取NVS内容...")
            thread.join(timeout + 5)  # 增加等待时间
        else:
            print("烧录失败")
            
        return nvs_data

    def get_nvs_partition_info(self):
        """获取NVS分区信息"""
        print("\n=== NVS分区信息 ===")
        cmd = "idf.py partition-table"
        output = self.run_command(cmd)
        print(output)

    def list_all_namespaces(self):
        """列出所有可能的命名空间"""
        common_namespaces = [
            "websocket", "mcp", "assets", "settings", "system", "wifi",
            "mqtt", "ota", "audio", "display", "network", "blob"
        ]
        return common_namespaces

    def display_nvs_data(self, nvs_data):
        """以友好的格式显示NVS数据"""
        if not nvs_data:
            print("未读取到NVS数据")
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
                value = info["value"]
                data_type = info["type"]
                print(f"  {key}: {value} ({data_type})")

    def save_to_json(self, nvs_data, filename="nvs_backup.json"):
        """将NVS数据保存为JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(nvs_data, f, indent=2, ensure_ascii=False)
            print(f"\nNVS数据已保存到: {filename}")
        except Exception as e:
            print(f"保存文件失败: {e}")

    def interactive_mode(self):
        """交互式模式"""
        print("ESP32 NVS内容查看工具")
        print("=" * 40)
        
        # 获取串口列表
        ports = self.get_serial_ports()
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
            
        # 读取NVS数据
        print(f"\n连接到设备: {selected_port}")
        nvs_data = self.read_nvs_via_monitor(selected_port)
        
        # 显示结果
        self.display_nvs_data(nvs_data)
        
        # 询问是否保存
        save = input("\n是否保存到JSON文件? (y/n): ").lower().strip()
        if save == 'y':
            filename = input("输入文件名 (默认: nvs_backup.json): ").strip()
            if not filename:
                filename = "nvs_backup.json"
            self.save_to_json(nvs_data, filename)

def main():
    parser = argparse.ArgumentParser(description='ESP32 NVS内容查看工具')
    parser.add_argument('-p', '--port', help='串口设备路径')
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help='波特率')
    parser.add_argument('-o', '--output', help='输出JSON文件名')
    parser.add_argument('--list-ports', action='store_true', help='列出可用串口')
    parser.add_argument('--partition-info', action='store_true', help='显示分区信息')
    
    args = parser.parse_args()
    
    viewer = NVSViewer(args.port, args.baudrate)
    
    if args.list_ports:
        ports = viewer.get_serial_ports()
        print("可用串口:")
        for port in ports:
            print(f"  {port}")
        return
            
    if args.partition_info:
        viewer.get_nvs_partition_info()
        return
        
    if args.port:
        # 命令行模式
        nvs_data = viewer.read_nvs_via_monitor(args.port)
        viewer.display_nvs_data(nvs_data)
        if args.output:
            viewer.save_to_json(nvs_data, args.output)
    else:
        # 交互式模式
        viewer.interactive_mode()

if __name__ == "__main__":
    # 检查是否在ESP-IDF环境中
    if "IDF_PATH" not in os.environ:
        print("警告: 未检测到ESP-IDF环境")
        print("请确保在ESP-IDF环境中运行此脚本")
        print("或者使用: source export.sh (在ESP-IDF目录中)")
        
    # 检查必要的Python包
    try:
        import serial
        import serial.tools.list_ports
    except ImportError:
        print("缺少必要的Python包，请安装:")
        print("pip install pyserial")
        sys.exit(1)
        
    main()
