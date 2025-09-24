#!/usr/bin/env python3
"""
并发安全测试脚本
测试多线程同时更新session.json的安全性
"""

import threading
import time
import random
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_concurrent_update(thread_id: int, phone_suffix: int):
    """
    模拟并发更新session.json
    """
    url = "http://localhost:8001/api/monitor/report"
    
    # 模拟不同用户的数据
    test_data = {
        "user": {
            "phone": f"1877991428{phone_suffix}",
            "name": f"测试用户{thread_id}"
        },
        "request": {
            "url": "https://www.doubao.com/samantha/chat/completion?aid=497858&device_id=123",
            "method": "POST",
            "timestamp": "2025-09-24T17:30:00.000Z",
            "cookies": f"test_cookie_{thread_id}=value_{thread_id}; session_id=session_{thread_id}",
            "searchParams": {
                "aid": "497858",
                "device_id": f"device_{thread_id}",
                "tea_uuid": f"uuid_{thread_id}",
                "web_id": f"web_{thread_id}"
            }
        }
    }
    
    try:
        # 随机延迟，增加并发冲突概率
        time.sleep(random.uniform(0, 0.1))
        
        response = requests.post(url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 线程{thread_id} (手机号{phone_suffix}): 更新成功")
            return True
        else:
            print(f"❌ 线程{thread_id}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 线程{thread_id}: {str(e)}")
        return False

def run_concurrent_test():
    """
    运行并发测试
    """
    print("🧪 开始并发安全测试...")
    print("=" * 50)
    
    # 测试参数
    num_threads = 10  # 并发线程数
    num_phones = 3    # 不同手机号数量（会产生更新冲突）
    
    # 创建线程池
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # 提交任务
        futures = []
        for i in range(num_threads):
            # 让多个线程使用相同的手机号，测试并发更新同一记录
            phone_suffix = i % num_phones
            future = executor.submit(test_concurrent_update, i, phone_suffix)
            futures.append(future)
        
        # 收集结果
        success_count = 0
        for future in as_completed(futures):
            if future.result():
                success_count += 1
    
    print("=" * 50)
    print(f"📊 测试结果: {success_count}/{num_threads} 成功")
    
    # 检查session.json的完整性
    try:
        with open("session.json", 'r', encoding='utf-8') as f:
            sessions = json.load(f)
            print(f"📄 session.json状态: {len(sessions)}个会话记录")
            
            # 打印所有记录
            for i, session in enumerate(sessions, 1):
                phone = session.get('phone', 'N/A')
                status = session.get('status', 'N/A')
                updated = session.get('updated_at', 'N/A')
                print(f"  {i}. 手机号: {phone}, 状态: {status}, 更新时间: {updated}")
                
    except Exception as e:
        print(f"❌ 读取session.json失败: {str(e)}")

if __name__ == "__main__":
    # 检查服务是否运行
    try:
        response = requests.get("http://localhost:8001/api/monitor/status", timeout=5)
        if response.status_code == 200:
            print("✅ 服务运行正常，开始测试")
            run_concurrent_test()
        else:
            print("❌ 服务未正常运行")
    except Exception as e:
        print(f"❌ 无法连接到服务: {str(e)}")
        print("请确保DoubaoFreeApi服务正在运行在 http://localhost:8001")