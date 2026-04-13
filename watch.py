#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
家庭照片画廊 - 文件夹监控脚本

功能：
    使用 watchdog 库监控 images/ 文件夹的变动
    当有任何文件被添加、删除或修改时，自动重新生成 gallery-data.json

使用方法：
    1. 首次运行前安装依赖:
       pip install watchdog
    
    2. 启动监控:
       python watch.py
    
    3. 保持脚本运行，开始往 images/ 文件夹添加照片
    
    4. 按 Ctrl+C 停止监控

特点：
    - 实时响应文件变动
    - 自动去重（短时间内多次变动只执行一次）
    - 支持所有图片格式 (.jpg .jpeg .png .webp)
    - 控制台彩色输出

作者：AI Assistant
日期：2024
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

# 尝试导入 watchdog
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️  watchdog 库未安装")
    print("📦 请运行: pip install watchdog")
    print("")


# ============================================
# 配置
# ============================================

# 要监控的目录
WATCH_DIRECTORY = Path('images')

# 数据生成脚本路径
GENERATE_SCRIPT = Path('generate_data.py')

# 去重时间间隔（秒）
# 在此时间间隔内的多次变动只会触发一次重新生成
DEBOUNCE_INTERVAL = 2.0

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


# ============================================
# 彩色输出工具
# ============================================

class Colors:
    """ANSI 颜色代码"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # 前景色
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # 背景色
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'


def print_header():
    """打印程序标题"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 60)
    print("🏠 家庭照片画廊 - 实时监控")
    print("=" * 60)
    print(f"{Colors.RESET}")
    print(f"📁 监控目录: {Colors.YELLOW}{WATCH_DIRECTORY}/{Colors.RESET}")
    print(f"📝 生成脚本: {Colors.YELLOW}{GENERATE_SCRIPT}{Colors.RESET}")
    print(f"⏱️  去重间隔: {Colors.YELLOW}{DEBOUNCE_INTERVAL}秒{Colors.RESET}")
    print(f"{Colors.DIM}")
    print("-" * 60)
    print(f"{Colors.RESET}")


def print_event(event_type: str, path: str, is_directory: bool = False):
    """打印文件变动事件"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    # 根据事件类型选择颜色
    color = Colors.WHITE
    icon = "📝"
    if event_type == 'created':
        color = Colors.GREEN
        icon = "✨"
    elif event_type == 'deleted':
        color = Colors.RED
        icon = "🗑️"
    elif event_type == 'modified':
        color = Colors.YELLOW
        icon = "📝"
    elif event_type == 'moved':
        color = Colors.BLUE
        icon = "📦"
    
    item_type = "📁" if is_directory else "📄"
    
    print(f"{Colors.DIM}[{timestamp}]{Colors.RESET} {icon} {color}{event_type.upper()}{Colors.RESET} {item_type} {path}")


def print_info(message: str):
    """打印信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{Colors.DIM}[{timestamp}]{Colors.RESET} {Colors.BLUE}ℹ️  {message}{Colors.RESET}")


def print_success(message: str):
    """打印成功信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{Colors.DIM}[{timestamp}]{Colors.RESET} {Colors.GREEN}✅ {message}{Colors.RESET}")


def print_warning(message: str):
    """打印警告信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{Colors.DIM}[{timestamp}]{Colors.RESET} {Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def print_error(message: str):
    """打印错误信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{Colors.DIM}[{timestamp}]{Colors.RESET} {Colors.RED}❌ {message}{Colors.RESET}")


# ============================================
# 文件系统事件处理器
# ============================================

class ImagesFolderHandler(FileSystemEventHandler):
    """
    图片文件夹变动处理器
    
    处理所有文件系统事件，并在适当的时候触发数据重新生成
    """
    
    def __init__(self):
        self.last_run_time = 0
        self.pending_events = []
    
    def should_process_event(self, event: FileSystemEvent) -> bool:
        """
        判断是否应该处理该事件
        
        规则：
            1. 忽略临时文件和隐藏文件
            2. 只处理支持的图片格式
            3. 忽略非文件/目录事件
        """
        # 获取文件名
        path = Path(event.src_path)
        filename = path.name
        
        # 忽略隐藏文件和临时文件
        if filename.startswith('.') or filename.startswith('~'):
            return False
        
        # 忽略临时文件扩展名
        if filename.endswith('.tmp') or filename.endswith('.temp'):
            return False
        
        # 如果是目录变动，总是处理
        if event.is_directory:
            return True
        
        # 只处理支持的图片格式
        ext = path.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return False
        
        return True
    
    def trigger_regenerate(self):
        """
        触发数据重新生成
        
        使用去重机制，避免短时间内多次触发
        """
        current_time = time.time()
        
        # 检查去重间隔
        if current_time - self.last_run_time < DEBOUNCE_INTERVAL:
            return
        
        self.last_run_time = current_time
        
        print("")
        print_info("检测到变动，正在重新生成数据...")
        
        try:
            # 执行生成脚本
            result = subprocess.run(
                [sys.executable, str(GENERATE_SCRIPT)],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                print_success("数据更新成功!")
                # 输出脚本的统计信息
                for line in result.stdout.split('\n'):
                    if line.strip() and ('统计' in line or '成员' in line or '照片' in line):
                        print(f"   {Colors.DIM}{line}{Colors.RESET}")
            else:
                print_error("数据更新失败!")
                if result.stderr:
                    print(f"{Colors.RED}{result.stderr}{Colors.RESET}")
        
        except Exception as e:
            print_error(f"执行生成脚本时出错: {e}")
        
        print("")
    
    def on_created(self, event: FileSystemEvent):
        """文件/目录创建事件"""
        if self.should_process_event(event):
            print_event('created', event.src_path, event.is_directory)
            self.trigger_regenerate()
    
    def on_deleted(self, event: FileSystemEvent):
        """文件/目录删除事件"""
        if self.should_process_event(event):
            print_event('deleted', event.src_path, event.is_directory)
            self.trigger_regenerate()
    
    def on_modified(self, event: FileSystemEvent):
        """文件/目录修改事件"""
        # 修改事件比较频繁，只处理目录修改
        if event.is_directory:
            return
        
        if self.should_process_event(event):
            print_event('modified', event.src_path, event.is_directory)
            self.trigger_regenerate()
    
    def on_moved(self, event: FileSystemEvent):
        """文件/目录移动/重命名事件"""
        if self.should_process_event(event):
            src = event.src_path
            dest = event.dest_path if hasattr(event, 'dest_path') else 'unknown'
            print_event('moved', f"{src} -> {dest}", event.is_directory)
            self.trigger_regenerate()


# ============================================
# 主函数
# ============================================

def check_environment() -> bool:
    """
    检查运行环境
    
    Returns:
        bool: 环境检查是否通过
    """
    # 检查 watchdog
    if not WATCHDOG_AVAILABLE:
        return False
    
    # 检查监控目录
    if not WATCH_DIRECTORY.exists():
        print_warning(f"监控目录不存在，正在创建: {WATCH_DIRECTORY}/")
        try:
            WATCH_DIRECTORY.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print_error(f"创建目录失败: {e}")
            return False
    
    # 检查生成脚本
    if not GENERATE_SCRIPT.exists():
        print_error(f"生成脚本不存在: {GENERATE_SCRIPT}")
        print_info("请确保 generate_data.py 在当前目录下")
        return False
    
    return True


def main():
    """主函数"""
    # 打印标题
    print_header()
    
    # 检查环境
    if not check_environment():
        return 1
    
    # 首次运行生成脚本
    print_info("首次运行，生成初始数据...")
    try:
        subprocess.run([sys.executable, str(GENERATE_SCRIPT)], check=True)
        print_success("初始数据生成完成!")
    except subprocess.CalledProcessError as e:
        print_error(f"初始数据生成失败: {e}")
        return 1
    
    print("")
    print(f"{Colors.CYAN}{Colors.BOLD}👀 开始监控，按 Ctrl+C 停止...{Colors.RESET}")
    print("")
    
    # 创建事件处理器和观察者
    event_handler = ImagesFolderHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_DIRECTORY), recursive=True)
    
    # 启动观察者
    observer.start()
    
    try:
        # 保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("")
        print_info("接收到停止信号，正在关闭...")
        observer.stop()
    
    # 等待观察者线程结束
    observer.join()
    
    print_success("监控已停止")
    
    return 0


if __name__ == '__main__':
    exit(main())
