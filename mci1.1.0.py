#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft 图片提取工具（自配置版本）
配置直接保存在脚本自身末尾的注释块中。
"""

import os
import sys
import json
import shutil
from pathlib import Path

# ---------- 配置模板 ----------
# 以下两个标记用于定位配置区域，请不要删除或修改格式
# === CONFIG START ===
# {"source_root": null}
# === CONFIG END ===

# 其他默认配置（不变部分）
TARGET_DIR_NAME = "输出文件夹"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif", ".webp"}
SCREENSHOT_KEYWORD = "\\screenshots\\"

# ---------- 自配置读写函数 ----------
def load_config_from_self():
    """从脚本自身末尾的配置块中读取 JSON 配置，返回字典"""
    script_path = Path(__file__).resolve()
    with open(script_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_marker = "# === CONFIG START ===\n"
    end_marker = "# === CONFIG END ===\n"
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if line == start_marker:
            start_idx = i
        elif line == end_marker and start_idx != -1:
            end_idx = i
            break

    if start_idx == -1 or end_idx == -1:
        # 没有找到配置块，返回默认空配置
        return {}

    # 提取配置内容（从 start_idx+1 到 end_idx-1）
    config_lines = lines[start_idx+1:end_idx]
    config_str = ''.join(config_lines).strip()
    if not config_str:
        return {}
    try:
        return json.loads(config_str)
    except json.JSONDecodeError:
        return {}

def save_config_to_self(config_dict):
    """将配置字典写入脚本自身的配置块中"""
    script_path = Path(__file__).resolve()
    with open(script_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_marker = "# === CONFIG START ===\n"
    end_marker = "# === CONFIG END ===\n"
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if line == start_marker:
            start_idx = i
        elif line == end_marker and start_idx != -1:
            end_idx = i
            break

    if start_idx == -1 or end_idx == -1:
        print("错误：找不到配置块，无法保存配置。")
        return False

    # 生成新的配置内容（JSON 格式化）
    new_config_str = json.dumps(config_dict, indent=2, ensure_ascii=False)

    # 替换配置块内容（保留开始和结束标记）
    new_lines = lines[:start_idx+1] + [new_config_str + "\n"] + lines[end_idx:]

    # 写回文件（使用临时文件保证原子性）
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    except IOError:
        print("错误：无法写入脚本自身，请检查文件权限。")
        return False

# ---------- 其他函数 ----------
def get_desktop():
    return Path(os.environ.get("USERPROFILE", os.path.expanduser("~"))) / "Desktop"

def get_target_dir():
    target = get_desktop() / TARGET_DIR_NAME
    target.mkdir(exist_ok=True)
    return target

def is_image(file_path):
    return file_path.suffix.lower() in IMAGE_EXTENSIONS

def is_screenshot(file_path):
    return SCREENSHOT_KEYWORD in str(file_path) or f"{os.sep}screenshots{os.sep}" in str(file_path)

def get_version_name(file_path, source_root):
    rel = file_path.relative_to(source_root)
    parts = rel.parts
    return parts[0] if parts else "unknown"

def copy_file(src, dst):
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"复制失败: {src.name} - {e}")
        return False

def collect_images(source_root, only_screenshots):
    all_images = []
    for file in source_root.rglob("*"):
        if file.is_file() and is_image(file):
            if only_screenshots and not is_screenshot(file):
                continue
            all_images.append(file)
    return all_images

def show_menu():
    print("\n" + "=" * 40)
    print("    Minecraft 图片提取工具".center(40))
    print("=" * 40)
    print("请选择操作模式：")
    print("  1 - 仅截图 + 平铺输出（文件名加版本前缀）")
    print("  2 - 仅截图 + 按版本文件夹输出（原文件名）")
    print("  3 - 全量   + 平铺输出（文件名加版本前缀）")
    print("  4 - 全量   + 按版本文件夹输出（原文件名）")
    print("  Q - 退出")
    choice = input("\n请输入数字 (1-4) 或 Q: ").strip().upper()
    return choice

def get_source_root_interactively(last_root=None):
    if last_root:
        print(f"\n上次使用的源目录: {last_root}")
        choice = input("是否使用该目录？(Y/n): ").strip().lower()
        if choice in ('', 'y', 'yes'):
            p = Path(last_root)
            if p.exists() and p.is_dir():
                return p
            else:
                print("警告：上次目录不存在，请重新输入。")
    while True:
        print("\n请输入 Minecraft 版本目录的完整路径")
        print("（例如 D:\\MC  PCL2\\.minecraft\\versions，输入 Q 退出）")
        path_input = input("路径: ").strip()
        if path_input.upper() == 'Q':
            sys.exit(0)
        path_input = path_input.strip('"').strip("'")
        p = Path(path_input)
        if p.exists() and p.is_dir():
            return p
        else:
            print(f"目录不存在或不是一个文件夹: {path_input}，请重新输入。")

def main():
    # 1. 加载配置（从自身）
    config = load_config_from_self()
    last_root = config.get("source_root")

    # 2. 获取源目录（交互式）
    source_root = get_source_root_interactively(last_root)

    # 3. 如果目录有变化，保存新配置
    if not last_root or str(source_root) != last_root:
        if save_config_to_self({"source_root": str(source_root)}):
            print("已保存新目录配置。")
        else:
            print("警告：配置保存失败，但将继续使用新目录。")

    # 4. 主循环
    while True:
        choice = show_menu()
        if choice == 'Q':
            print("退出程序。")
            break
        if choice not in ('1', '2', '3', '4'):
            print("输入无效，请重新选择。")
            continue

        only_screenshots = choice in ('1', '2')
        use_flat = choice in ('1', '3')
        mode_desc = {
            '1': "仅截图，平铺输出",
            '2': "仅截图，按版本文件夹输出",
            '3': "全量扫描，平铺输出",
            '4': "全量扫描，按版本文件夹输出",
        }[choice]

        print(f"\n您选择了: {mode_desc}")
        print("正在扫描文件，请稍候...")

        images = collect_images(source_root, only_screenshots)
        total = len(images)
        if total == 0:
            print("未找到符合条件的图片文件，请检查目录和筛选条件。")
            input("按回车键返回菜单...")
            continue

        print(f"找到 {total} 张图片，开始复制...")
        target_root = get_target_dir()
        success = 0
        error = 0

        try:
            from tqdm import tqdm
            iterator = tqdm(images, desc="复制进度", unit="张")
        except ImportError:
            iterator = images

        for i, img in enumerate(iterator, 1):
            if 'tqdm' not in sys.modules:
                print(f"\r进度: {i}/{total} ({i*100//total}%)", end="")

            version = get_version_name(img, source_root)
            if use_flat:
                dest = target_root / f"{version}_{img.name}"
            else:
                dest = target_root / version / img.name

            if copy_file(img, dest):
                success += 1
            else:
                error += 1

        if 'tqdm' not in sys.modules:
            print()
        print(f"\n复制完成！成功: {success} 张，失败: {error} 张。")
        print(f"文件已保存至: {target_root}")
        input("按回车键返回菜单...")

if __name__ == "__main__":
    main()