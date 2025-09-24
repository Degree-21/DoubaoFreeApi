from fastapi import APIRouter, HTTPException, Query
from src.model.request import SessionConfigRequest, SessionConfigUpdateRequest
import json
import os

router = APIRouter()


@router.post("/config")
async def set_session_config(config: SessionConfigRequest):
    """设置session.json配置"""
    try:
        # 读取现有的session.json文件
        session_file_path = "session.json"
        
        # 如果文件存在，读取现有数据
        if os.path.exists(session_file_path):
            with open(session_file_path, 'r', encoding='utf-8') as f:
                sessions = json.load(f)
        else:
            sessions = []
        
        # 创建新的session配置
        new_session = {
            "cookie": config.cookie,
            "device_id": config.device_id,
            "tea_uuid": config.tea_uuid,
            "web_id": config.web_id,
            "room_id": config.room_id,
            "x_flow_trace": config.x_flow_trace
        }
        
        # 如果列表为空或只有一个元素，替换或添加
        if len(sessions) == 0:
            sessions.append(new_session)
        else:
            sessions[0] = new_session  # 替换第一个session
        
        # 写回文件
        with open(session_file_path, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=4, ensure_ascii=False)
        
        return {"message": "Session配置已更新", "config": new_session}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新session配置失败: {str(e)}")


@router.get("/status")
async def get_session_status(phone: str = Query(..., description="手机号")):
    """检查指定手机号的session.json状态"""
    try:
        session_file_path = "session.json"
        
        if not os.path.exists(session_file_path):
            return {"status": "not_found", "message": "session.json文件不存在", "phone": phone}
        
        with open(session_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        # 如果文件只包含 "active" 字符串，返回active状态
        if content == "active":
            return {"status": "active", "message": f"手机号 {phone} 的会话状态为active", "phone": phone}
        
        # 尝试解析为JSON
        try:
            sessions = json.loads(content)
            if len(sessions) == 0:
                return {"status": "empty", "message": f"手机号 {phone} 没有session配置", "phone": phone}
            
            # 查找匹配的phone
            matching_session = None
            for session in sessions:
                if session.get("phone") == phone:
                    matching_session = session
                    break
            
            if matching_session:
                # 检查session是否有效
                required_fields = ["cookie", "device_id", "tea_uuid", "web_id", "x_flow_trace"]
                missing_fields = [field for field in required_fields if not matching_session.get(field)]
                
                if missing_fields:
                    return {
                        "status": "incomplete", 
                        "message": f"手机号 {phone} 的session配置不完整，缺少: {', '.join(missing_fields)}", 
                        "phone": phone,
                        "missing_fields": missing_fields
                    }
                else:
                    return {
                        "status": "configured", 
                        "message": f"手机号 {phone} 的session配置完整", 
                        "phone": phone,
                        "session": matching_session
                    }
            else:
                return {
                    "status": "not_found_phone", 
                    "message": f"未找到手机号 {phone} 的session配置", 
                    "phone": phone,
                    "available_phones": [s.get("phone", "未知") for s in sessions if isinstance(s, dict)]
                }
                
        except json.JSONDecodeError:
            return {"status": "invalid", "message": f"手机号 {phone} - session.json格式错误", "phone": phone}
    
    except Exception as e:
        return {"status": "error", "message": f"读取手机号 {phone} 的session文件失败: {str(e)}", "phone": phone}


@router.get("/config")
async def get_session_config():
    """获取当前session.json配置"""
    try:
        session_file_path = "session.json"
        
        if not os.path.exists(session_file_path):
            raise HTTPException(status_code=404, detail="session.json文件不存在")
        
        with open(session_file_path, 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        
        if len(sessions) == 0:
            raise HTTPException(status_code=404, detail="没有找到session配置")
        
        return {"config": sessions[0]}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="session.json文件格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取session配置失败: {str(e)}")


@router.put("/config")
async def update_session_config(config: SessionConfigRequest):
    """完全更新session.json配置"""
    try:
        session_file_path = "session.json"
        
        if not os.path.exists(session_file_path):
            raise HTTPException(status_code=404, detail="session.json文件不存在")
        
        with open(session_file_path, 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        
        if len(sessions) == 0:
            raise HTTPException(status_code=404, detail="没有找到session配置")
        
        # 完全替换第一个session配置
        updated_session = {
            "cookie": config.cookie,
            "device_id": config.device_id,
            "tea_uuid": config.tea_uuid,
            "web_id": config.web_id,
            "room_id": config.room_id,
            "x_flow_trace": config.x_flow_trace
        }
        
        sessions[0] = updated_session
        
        # 写回文件
        with open(session_file_path, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=4, ensure_ascii=False)
        
        return {"message": "Session配置已完全更新", "config": updated_session}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="session.json文件格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新session配置失败: {str(e)}")


@router.patch("/config")
async def partial_update_session_config(config: SessionConfigUpdateRequest):
    """部分更新session.json配置"""
    try:
        session_file_path = "session.json"
        
        if not os.path.exists(session_file_path):
            raise HTTPException(status_code=404, detail="session.json文件不存在")
        
        with open(session_file_path, 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        
        if len(sessions) == 0:
            raise HTTPException(status_code=404, detail="没有找到session配置")
        
        # 获取当前配置
        current_session = sessions[0]
        
        # 只更新提供的字段
        update_fields = {}
        if config.cookie is not None:
            current_session["cookie"] = config.cookie
            update_fields["cookie"] = config.cookie
        if config.device_id is not None:
            current_session["device_id"] = config.device_id
            update_fields["device_id"] = config.device_id
        if config.tea_uuid is not None:
            current_session["tea_uuid"] = config.tea_uuid
            update_fields["tea_uuid"] = config.tea_uuid
        if config.web_id is not None:
            current_session["web_id"] = config.web_id
            update_fields["web_id"] = config.web_id
        if config.room_id is not None:
            current_session["room_id"] = config.room_id
            update_fields["room_id"] = config.room_id
        if config.x_flow_trace is not None:
            current_session["x_flow_trace"] = config.x_flow_trace
            update_fields["x_flow_trace"] = config.x_flow_trace
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="没有提供要更新的字段")
        
        # 写回文件
        with open(session_file_path, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=4, ensure_ascii=False)
        
        return {
            "message": "Session配置已部分更新", 
            "updated_fields": update_fields,
            "config": current_session
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="session.json文件格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"部分更新session配置失败: {str(e)}")


@router.delete("/config")
async def delete_session_config():
    """删除session.json配置"""
    try:
        session_file_path = "session.json"
        
        if not os.path.exists(session_file_path):
            raise HTTPException(status_code=404, detail="session.json文件不存在")
        
        with open(session_file_path, 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        
        if len(sessions) == 0:
            raise HTTPException(status_code=404, detail="没有找到session配置")
        
        # 移除第一个session配置
        removed_session = sessions.pop(0)
        
        # 写回文件
        with open(session_file_path, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=4, ensure_ascii=False)
        
        return {
            "message": "Session配置已删除", 
            "deleted_config": removed_session,
            "remaining_sessions": len(sessions)
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="session.json文件格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除session配置失败: {str(e)}")