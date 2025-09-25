"""
集成到DoubaoFreeApi的图片去水印功能
在doubao_service.py中处理图片时自动去水印
"""

import requests
from PIL import Image
from io import BytesIO
import asyncio
import aiohttp
from typing import Optional, Tuple

async def download_image_async(session: aiohttp.ClientSession, url: str) -> Image.Image:
    """异步下载图片"""
    async with session.get(url) as response:
        if response.status == 200:
            content = await response.read()
            return Image.open(BytesIO(content))
        else:
            raise Exception(f"下载图片失败: {response.status}")

def merge_images_remove_watermark(thumb_img: Image.Image, ori_img: Image.Image) -> Image.Image:
    """
    智能合并去水印
    thumb_img: 左上角有水印 (使用右下角)
    ori_img: 右下角有水印 (使用左上角)
    """
    # 确保尺寸一致
    if thumb_img.size != ori_img.size:
        ori_img = ori_img.resize(thumb_img.size, Image.Resampling.LANCZOS)
    
    width, height = thumb_img.size
    
    # 创建结果图片
    result_img = Image.new('RGB', (width, height))
    
    # 计算分割线 - 使用对角线分割获得最佳效果
    split_x = width // 2
    split_y = height // 2
    
    # 使用ori图片作为底图(去右下角水印)
    result_img.paste(ori_img, (0, 0))
    
    # 用thumb图片的右下角覆盖(去左上角水印的部分)
    thumb_right_bottom = thumb_img.crop((split_x, split_y, width, height))
    result_img.paste(thumb_right_bottom, (split_x, split_y))
    
    return result_img

async def process_watermark_removal(thumb_url: str, ori_url: str) -> Optional[str]:
    """
    处理去水印并返回无水印图片URL或本地路径
    """
    try:
        async with aiohttp.ClientSession() as session:
            # 并行下载两张图片
            thumb_task = download_image_async(session, thumb_url)
            ori_task = download_image_async(session, ori_url)
            
            thumb_img, ori_img = await asyncio.gather(thumb_task, ori_task)
            
            # 合并去水印
            result_img = merge_images_remove_watermark(thumb_img, ori_img)
            
            # 保存到临时文件或上传到云存储
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                result_img.save(tmp_file.name, 'PNG')
                return tmp_file.name
                
    except Exception as e:
        print(f"去水印处理失败: {e}")
        return None

# 同步版本用于测试
def process_watermark_removal_sync(thumb_url: str, ori_url: str, output_path: str = None) -> str:
    """
    同步版本的去水印处理，用于快速测试
    """
    # 下载图片
    thumb_response = requests.get(thumb_url)
    ori_response = requests.get(ori_url)
    
    thumb_img = Image.open(BytesIO(thumb_response.content))
    ori_img = Image.open(BytesIO(ori_response.content))
    
    print(f"Thumb图片尺寸: {thumb_img.size}")
    print(f"Ori图片尺寸: {ori_img.size}")
    
    # 去水印处理
    result_img = merge_images_remove_watermark(thumb_img, ori_img)
    
    # 保存
    if not output_path:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"no_watermark_{timestamp}.png"
    
    result_img.save(output_path, 'PNG')
    print(f"无水印图片已保存: {output_path}")
    
    return output_path