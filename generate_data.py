#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大家庭成员记录 - 数据生成脚本

功能：
    扫描 images/ 目录下的所有子文件夹，自动生成 gallery-data.json 数据文件
    每个子文件夹代表一个家庭成员
    自动读取照片EXIF拍摄日期，支持视频文件

文件名规则：
    - avatar.jpg (或 .jpeg/.png/.webp) = 成员头像（必须）
    - YYYY-MM-DD_描述文字.jpg = 照片文件，会自动解析日期和描述
    - .mp4/.mov/.avi 等 = 视频文件

使用方法：
    python generate_data.py

输出：
    data/gallery-data.json

作者：AI Assistant
日期：2024
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

# 尝试导入 PIL 用于读取 EXIF
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL 库未安装，将使用文件修改时间作为日期")
    print("📦 建议安装: pip install Pillow")
    print("")


# ============================================
# 配置
# ============================================

# 支持的图片格式
SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}

# 支持的视频格式
SUPPORTED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.m4v', '.3gp'}

# 所有支持的格式
SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_VIDEO_EXTENSIONS

# 头像文件名（不含扩展名）
AVATAR_NAMES = {'avatar', 'head', 'portrait', 'icon', '头像'}

# 数据文件输出路径
OUTPUT_FILE = Path('data/gallery-data.json')

# 图片目录路径
IMAGES_DIR = Path('images')


# ============================================
# 工具函数
# ============================================

def is_image_file(filename: str) -> bool:
    """检查文件是否为支持的图片格式"""
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_IMAGE_EXTENSIONS


def is_video_file(filename: str) -> bool:
    """检查文件是否为支持的视频格式"""
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_VIDEO_EXTENSIONS


def is_media_file(filename: str) -> bool:
    """检查文件是否为支持的媒体格式"""
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS


def is_avatar_file(filename: str) -> bool:
    """检查文件是否为头像文件"""
    name_without_ext = Path(filename).stem.lower()
    return name_without_ext in AVATAR_NAMES


def get_exif_date(image_path: Path) -> tuple:
    """
    从图片EXIF数据中提取拍摄日期
    
    Returns:
        tuple: (date_str: YYYY-MM-DD格式, sortDate: 时间戳) 或 (None, None)
    """
    if not PIL_AVAILABLE:
        return None, None
    
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if not exif_data:
                return None, None
            
            # 查找拍摄日期标签
            date_taken = None
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                # DateTimeOriginal = 拍摄日期
                # DateTimeDigitized = 数字化日期
                # DateTime = 修改日期
                if tag in ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime']:
                    date_taken = value
                    if tag == 'DateTimeOriginal':  # 优先使用原始拍摄日期
                        break
            
            if date_taken:
                # EXIF日期格式: "2024:02:15 14:30:00"
                match = re.match(r'(\d{4}):(\d{2}):(\d{2})', str(date_taken))
                if match:
                    year, month, day = match.groups()
                    date_str = f"{year}-{month}-{day}"
                    sort_date = datetime(int(year), int(month), int(day)).timestamp() * 1000
                    return date_str, int(sort_date)
    
    except Exception as e:
        pass
    
    return None, None


def parse_photo_filename(filename: str) -> dict:
    """
    解析照片文件名，提取日期和描述
    
    支持的格式：
        - YYYY-MM-DD_描述文字.jpg
        - YYYY_MM_DD_描述文字.jpg
        - YYYY年MM月DD日_描述文字.jpg
        - 描述文字.jpg
    
    Returns:
        dict: 包含 date, desc, sortDate 的字典
    """
    stem = Path(filename).stem
    
    # 尝试匹配 YYYY-MM-DD_描述 格式
    pattern1 = r'^(\d{4})[-_](\d{1,2})[-_](\d{1,2})[_-](.+)$'
    match = re.match(pattern1, stem)
    
    if match:
        year, month, day, desc = match.groups()
        date_str = f"{year}-{int(month):02d}-{int(day):02d}"
        sort_date = datetime(int(year), int(month), int(day)).timestamp() * 1000
        return {
            'date': date_str,
            'desc': desc.strip(),
            'sortDate': int(sort_date)
        }
    
    # 尝试匹配 YYYY年MM月DD日_描述 格式
    pattern2 = r'^(\d{4})年(\d{1,2})月(\d{1,2})日[_-]?(.+)?$'
    match = re.match(pattern2, stem)
    
    if match:
        year, month, day, desc = match.groups()
        date_str = f"{year}-{int(month):02d}-{int(day):02d}"
        sort_date = datetime(int(year), int(month), int(day)).timestamp() * 1000
        return {
            'date': date_str,
            'desc': (desc or '美好瞬间').strip(),
            'sortDate': int(sort_date)
        }
    
    # 尝试匹配纯日期格式 YYYY-MM-DD 或 YYYY_MM_DD
    pattern3 = r'^(\d{4})[-_](\d{1,2})[-_](\d{1,2})$'
    match = re.match(pattern3, stem)
    
    if match:
        year, month, day = match.groups()
        date_str = f"{year}-{int(month):02d}-{int(day):02d}"
        sort_date = datetime(int(year), int(month), int(day)).timestamp() * 1000
        return {
            'date': date_str,
            'desc': '美好瞬间',
            'sortDate': int(sort_date)
        }
    
    # 无法解析，使用文件名作为描述
    return {
        'date': None,
        'desc': stem,
        'sortDate': None
    }


def get_file_modification_time(filepath: Path) -> tuple:
    """获取文件修改时间"""
    try:
        mtime = filepath.stat().st_mtime
        dt = datetime.fromtimestamp(mtime)
        date_str = dt.strftime('%Y-%m-%d')
        sort_date = int(mtime * 1000)
        return date_str, sort_date
    except Exception:
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        sort_date = int(now.timestamp() * 1000)
        return date_str, sort_date


def process_media_file(file_path: Path) -> dict:
    """
    处理媒体文件（图片或视频）

    Returns:
        dict: 包含媒体信息的字典
    """
    filename = file_path.name
    is_video = is_video_file(filename)

    # 解析文件名（已禁用文件名日期解析，只用EXIF拍摄日期）
    file_info = {
        'date': None,
        'desc': Path(filename).stem,
        'sortDate': None
    }

    # 获取日期优先级：
    # 1. 图片EXIF拍摄日期
    # 2. 文件修改时间
    if is_image_file(filename):
        # 尝试读取EXIF（仅图片）
        exif_date, exif_sort = get_exif_date(file_path)
        if exif_date:
            file_info['date'] = exif_date
            file_info['sortDate'] = exif_sort
            file_info['dateSource'] = 'exif'
        else:
            # 使用文件修改时间
            date_str, sort_date = get_file_modification_time(file_path)
            file_info['date'] = date_str
            file_info['sortDate'] = sort_date
            file_info['dateSource'] = 'file'
    else:
        # 视频使用文件修改时间
        date_str, sort_date = get_file_modification_time(file_path)
        file_info['date'] = date_str
        file_info['sortDate'] = sort_date
        file_info['dateSource'] = 'file'

    # 添加文件路径和类型
    file_info['src'] = str(file_path).replace('\\', '/')
    file_info['type'] = 'video' if is_video else 'image'

    return file_info


def scan_member_folder(folder_path: Path) -> dict:
    """扫描单个成员文件夹"""
    member_id = folder_path.name
    avatar_path = None
    media_files = []
    
    # 遍历文件夹中的所有文件
    for file_path in folder_path.iterdir():
        if not file_path.is_file():
            continue
        
        # 检查是否为媒体文件
        if not is_media_file(file_path.name):
            continue
        
        # 检查是否为头像
        if is_avatar_file(file_path.name) and is_image_file(file_path.name):
            avatar_path = str(file_path).replace('\\', '/')
            continue
        
        # 处理媒体文件
        media_info = process_media_file(file_path)
        media_files.append(media_info)
    
    # 按日期排序（倒序，最新的在前）
    media_files.sort(key=lambda x: x.get('sortDate', 0), reverse=True)
    
    return {
        'id': member_id,
        'name': member_id,
        'avatar': avatar_path,
        'photos': media_files
    }


def scan_images_directory() -> dict:
    """扫描整个 images 目录"""
    members = []
    galleries = {}
    
    # 确保图片目录存在
    if not IMAGES_DIR.exists():
        print(f"⚠️  图片目录不存在: {IMAGES_DIR}")
        print("📝 创建空目录...")
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        return {'members': [], 'galleries': {}}
    
    # 遍历所有子文件夹
    for item in sorted(IMAGES_DIR.iterdir()):
        if not item.is_dir():
            continue
        
        member_data = scan_member_folder(item)
        
        # 统计图片和视频数量
        photo_count = sum(1 for p in member_data['photos'] if p['type'] == 'image')
        video_count = sum(1 for p in member_data['photos'] if p['type'] == 'video')
        
        # 添加到成员列表
        members.append({
            'id': member_data['id'],
            'name': member_data['name'],
            'avatar': member_data['avatar'],
            'photoCount': photo_count,
            'videoCount': video_count,
            'totalCount': len(member_data['photos'])
        })
        
        # 添加到相册字典
        galleries[member_data['id']] = member_data['photos']
        
        # 输出统计
        count_info = f"{photo_count} 张照片"
        if video_count > 0:
            count_info += f", {video_count} 个视频"
        print(f"  ✅ {member_data['name']}: {count_info}")
    
    return {
        'members': members,
        'galleries': galleries
    }


def save_data(data: dict) -> bool:
    """保存数据到 JSON 文件"""
    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存数据文件失败: {e}")
        return False


def print_statistics(data: dict):
    """打印统计信息"""
    members = data.get('members', [])
    galleries = data.get('galleries', {})
    
    total_photos = sum(m.get('photoCount', 0) for m in members)
    total_videos = sum(m.get('videoCount', 0) for m in members)
    
    print("\n" + "=" * 50)
    print("📊 统计信息")
    print("=" * 50)
    print(f"👨‍👩‍👧‍👦 家庭成员: {len(members)} 人")
    print(f"📷 照片总数: {total_photos} 张")
    if total_videos > 0:
        print(f"🎬 视频总数: {total_videos} 个")
    
    if members:
        print("\n📁 成员详情:")
        for member in members:
            avatar_status = "✅" if member.get('avatar') else "⚠️ 无头像"
            count_info = f"{member['photoCount']} 张照片"
            if member.get('videoCount', 0) > 0:
                count_info += f", {member['videoCount']} 个视频"
            print(f"   • {member['name']}: {count_info} [{avatar_status}]")
    
    print("=" * 50)


def main():
    """主函数"""
    print("👨‍👩‍👧‍👦 大家庭成员记录 - 数据生成脚本")
    print("=" * 50)
    
    if not PIL_AVAILABLE:
        print("\n⚠️  提示: 安装 Pillow 后可读取照片拍摄日期")
        print("   pip install Pillow\n")
    
    # 扫描图片目录
    print(f"🔍 正在扫描目录: {IMAGES_DIR}/")
    data = scan_images_directory()
    
    # 保存数据
    print(f"\n💾 正在保存数据: {OUTPUT_FILE}")
    if save_data(data):
        print("✅ 数据保存成功!")
    else:
        print("❌ 数据保存失败!")
        return 1
    
    # 打印统计
    print_statistics(data)
    
    print("\n🎉 完成! 现在可以打开网页查看相册了。")
    print("-" * 50)
    
    return 0


if __name__ == '__main__':
    exit(main())
