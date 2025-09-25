#!/usr/bin/env python3
"""
豆包图片去水印脚本
利用image_thumb(左上角水印)和image_ori(右下角水印)进行智能合成
"""

import requests
from PIL import Image
from io import BytesIO
import os
from datetime import datetime

def download_image(url):
    """下载图片并返回PIL Image对象"""
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

def merge_images(thumb_img, ori_img):
    """
    合并两张图片去除水印
    thumb_img: 左上角有水印的图片 (用右下角部分)
    ori_img: 右下角有水印的图片 (用左上角部分)
    """
    # 确保两张图片尺寸相同
    if thumb_img.size != ori_img.size:
        # 如果尺寸不同，将ori_img缩放到和thumb_img相同尺寸
        ori_img = ori_img.resize(thumb_img.size, Image.Resampling.LANCZOS)
        print(f"图片尺寸不同，已将ori图片缩放到 {thumb_img.size}")
    
    width, height = thumb_img.size
    
    # 创建新的图片作为结果
    result_img = Image.new('RGB', (width, height))
    
    # 从thumb_img取右下角3/4区域 (去除左上角水印)
    # 从ori_img取左上角3/4区域 (去除右下角水印)
    
    # 计算分割点
    split_x = width // 2
    split_y = height // 2
    
    # 方案1: 对角线分割
    # 左上角用ori_img，右下角用thumb_img
    
    # 先贴上ori_img作为底图
    result_img.paste(ori_img, (0, 0))
    
    # 然后用thumb_img的右下角覆盖result_img的右下角
    thumb_right_bottom = thumb_img.crop((split_x, split_y, width, height))
    result_img.paste(thumb_right_bottom, (split_x, split_y))
    
    print(f"图片合成完成: 使用ori图片的左上角 + thumb图片的右下角")
    return result_img

def remove_watermark_from_urls(thumb_url, ori_url, output_filename=None):
    """
    从两个URL下载图片并进行去水印处理
    """
    print(f"下载thumb图片: {thumb_url}")
    thumb_img = download_image(thumb_url)
    print(f"thumb图片尺寸: {thumb_img.size}")
    
    print(f"下载ori图片: {ori_url}")
    ori_img = download_image(ori_url)
    print(f"ori图片尺寸: {ori_img.size}")
    
    # 合并图片
    result_img = merge_images(thumb_img, ori_img)
    
    # 生成输出文件名
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"doubao_no_watermark_{timestamp}.png"
    
    # 保存结果
    result_img.save(output_filename, "PNG")
    print(f"无水印图片已保存: {output_filename}")
    
    return output_filename

def test_with_sample_urls():
    """
    测试函数 - 使用示例URL
    请替换为实际的豆包图片URL
    """
    # 这里需要替换为实际的豆包图片URL
    thumb_url = "https://example.com/thumb.png"  # 左上角水印
    ori_url = "https://example.com/ori.png"      # 右下角水印
    
    try:
        result_file = remove_watermark_from_urls(thumb_url, ori_url)
        print(f"处理成功！文件保存为: {result_file}")
    except Exception as e:
        print(f"处理失败: {e}")

if __name__ == "__main__":
    print("豆包图片去水印工具")
    print("=" * 50)
    
    # 交互式输入URL
    print("请输入两个图片URL:")
    thumb_url = input("thumb图片URL (左上角水印): ").strip()
    ori_url = input("ori图片URL (右下角水印): ").strip()
    
    if thumb_url and ori_url:
        try:
            result_file = remove_watermark_from_urls(thumb_url, ori_url)
            print(f"\n✅ 处理完成！无水印图片已保存为: {result_file}")
        except Exception as e:
            print(f"\n❌ 处理失败: {e}")
    else:
        print("URL不能为空，退出程序")