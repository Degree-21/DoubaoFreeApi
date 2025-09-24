from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from datetime import datetime
import logging
import os
import threading
import tempfile
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()

# 文件锁，确保session.json的并发安全
_session_file_lock = threading.RLock()

class UserInfo(BaseModel):
    phone: str
    name: str

class RequestData(BaseModel):
    url: str
    aid: Optional[str] = None
    cookies: str
    headers: Optional[Dict[str, Any]] = None
    method: Optional[str] = "GET"
    timestamp: str
    userAgent: Optional[str] = None
    searchParams: Optional[Dict[str, str]] = None
    requestBody: Optional[str] = None

class MonitorReport(BaseModel):
    user: UserInfo
    request: RequestData

def update_session_json(phone: str, search_params: dict, cookies: str):
    """
    线程安全地更新session.json文件
    """
    session_file = "session.json"
    
    with _session_file_lock:  # 使用锁确保并发安全
        try:
            # 读取现有的session数据
            sessions = []
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    try:
                        sessions = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning("session.json 格式错误，将重新创建")
                        sessions = []
            
            # 提取关键参数
            device_id = search_params.get('device_id', '')
            tea_uuid = search_params.get('tea_uuid', '')
            web_id = search_params.get('web_id', '')
            
            # 查找是否已存在该手机号的会话
            session_found = False
            for session in sessions:
                if session.get('phone') == phone:
                    # 更新现有会话
                    session['cookie'] = cookies
                    session['device_id'] = device_id
                    session['tea_uuid'] = tea_uuid
                    session['web_id'] = web_id
                    session['phone'] = phone
                    session['status'] = 'active'  # 可用状态
                    session['updated_at'] = datetime.now().isoformat()
                    session_found = True
                    print(f"   ✅ 更新了手机号 {phone} 的会话数据")
                    break
            
            # 如果没找到，创建新会话
            if not session_found:
                new_session = {
                    "phone": phone,
                    "cookie": cookies,
                    "device_id": device_id,
                    "tea_uuid": tea_uuid,
                    "web_id": web_id,
                    "room_id": "",
                    "x_flow_trace": "",
                    "status": "active",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                sessions.append(new_session)
                print(f"   ✅ 添加了手机号 {phone} 的新会话数据")
            
            # 原子写入操作：先写入临时文件，再替换原文件
            session_file_path = Path(session_file)
            temp_file = None
            
            try:
                # 创建临时文件在同一目录下
                with tempfile.NamedTemporaryFile(
                    mode='w', 
                    encoding='utf-8', 
                    dir=session_file_path.parent,
                    prefix=f".{session_file_path.name}.tmp",
                    delete=False
                ) as temp_file:
                    json.dump(sessions, temp_file, indent=4, ensure_ascii=False)
                    temp_file.flush()  # 确保数据写入磁盘
                    os.fsync(temp_file.fileno())  # 强制同步到磁盘
                
                # 原子替换操作
                if temp_file:
                    shutil.move(temp_file.name, session_file)
                    print(f"   💾 session.json 已安全更新")
                
            except Exception as write_error:
                # 清理临时文件
                if temp_file and os.path.exists(temp_file.name):
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                raise write_error
            
            return True
            
        except Exception as e:
            print(f"   ❌ 更新session.json失败: {str(e)}")
            logger.error(f"更新session.json失败: {str(e)}")
            return False

@router.post("/report")
async def receive_monitor_report(request_data: dict):
    """
    接收浏览器插件上报的监听数据
    """
    try:
        print("=" * 80)
        print(f"📊 豆包API监听数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print("🔧 收到的原始数据:")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        print("=" * 50)
        
        # 解析用户信息
        user = request_data.get('user', {})
        request = request_data.get('request', {})
        
        # 用户信息
        print(f"👤 用户信息:")
        print(f"   姓名: {user.get('name', 'N/A')}")
        print(f"   手机: {user.get('phone', 'N/A')}")
        print()
        
        # URL信息
        print(f"🔗 请求信息:")
        print(f"   URL: {request.get('url', 'N/A')}")
        print(f"   方法: {request.get('method', 'N/A')}")
        print(f"   时间: {request.get('timestamp', 'N/A')}")
        print()
        
        # GET参数
        searchParams = request.get('searchParams', {})
        if searchParams:
            print(f"🎯 GET参数 (共{len(searchParams)}个):")
            for key, value in searchParams.items():
                print(f"   {key}: {value}")
        else:
            print(f"🎯 GET参数: 无")
        print()
        
        # Cookie信息
        cookies = request.get('cookies', '')
        print(f"🍪 Cookie信息 (长度: {len(cookies)}):")
        if cookies:
            # 直接打印完整的Cookie字符串，格式化为k=v;的形式
            print("   Cookie字符串:")
            print(f"   {cookies}")
            
            # 同时显示解析后的Cookie数量
            cookie_list = cookies.split('; ')
            print(f"   (共 {len(cookie_list)} 个Cookie)")
        else:
            print("   无Cookie")
        print()
        
        # 请求体
        requestBody = request.get('requestBody')
        if requestBody:
            print(f"📦 请求体 (长度: {len(requestBody)}):")
            try:
                # 尝试解析JSON
                body_json = json.loads(requestBody)
                print(f"   {json.dumps(body_json, indent=2, ensure_ascii=False)}")
            except:
                # 如果不是JSON，直接显示前200字符
                body_preview = requestBody[:200]
                if len(requestBody) > 200:
                    body_preview += "..."
                print(f"   {body_preview}")
        else:
            print(f"📦 请求体: 无")
        print()
        
        # Headers
        headers = request.get('headers', {})
        if headers and isinstance(headers, dict):
            print(f"📋 请求头:")
            for key, value in headers.items():
                # 截断长头部值
                display_value = str(value) if len(str(value)) <= 100 else str(value)[:97] + "..."
                print(f"   {key}: {display_value}")
        elif headers:
            print(f"📋 请求头 (类型: {type(headers).__name__}):")
            print(f"   {str(headers)[:200]}...")
        else:
            print(f"📋 请求头: 无")
        
        print("=" * 80)
        print()
        
        # 更新session.json
        print("📝 更新会话数据:")
        phone = user.get('phone', '')
        if phone and searchParams and cookies:
            update_session_json(phone, searchParams, cookies)
        else:
            print("   ⚠️  缺少必要数据，跳过更新")
        print()
        
        return {
            "status": "success",
            "message": "数据接收成功",
            "timestamp": datetime.now().isoformat(),
            "received_params": len(searchParams) if searchParams else 0,
            "cookies_count": len(cookies.split('; ')) if cookies else 0,
            "session_updated": bool(phone and searchParams and cookies)
        }
        
    except Exception as e:
        logger.error(f"处理监听数据时出错: {str(e)}")
        print(f"❌ 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理数据时出错: {str(e)}")

@router.get("/status")
async def monitor_status():
    """
    获取监控服务状态
    """
    return {
        "status": "running",
        "service": "Doubao API Monitor",
        "timestamp": datetime.now().isoformat()
    }