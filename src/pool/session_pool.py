import os
import json
import random
from pydantic import BaseModel
from loguru import logger
from .fetcher import DoubaoAutomator

class DoubaoSession(BaseModel):
    """豆包API会话配置"""
    cookie: str
    device_id: str
    tea_uuid: str
    web_id: str
    room_id: str
    x_flow_trace: str
    phone: str = ""
    
    def to_dict(self) -> dict[str, str]:
        """转换为字典"""
        return {
            "cookie": self.cookie,
            "device_id": self.device_id,
            "tea_uuid": self.tea_uuid,
            "web_id": self.web_id,
            "room_id": self.room_id,
            "x_flow_trace": self.x_flow_trace,
            "phone": self.phone,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, str]) -> 'DoubaoSession':
        return cls(**data)


class SessionPool:
    """豆包API会话池，管理多个账号配置"""
    def __init__(self, config_file: str = "session.json"):
        # conversation_id -> DoubaoSession
        self.session_map: dict[str, DoubaoSession] = {}
        self.auth_sessions: list[DoubaoSession] = []
        self.guest_sessions: list[DoubaoSession] = [] 
        
        # 确保配置文件路径是相对于项目根目录的绝对路径
        if not os.path.isabs(config_file):
            # 方法1: 优先使用当前工作目录（支持从任何位置运行）
            if os.path.exists(os.path.join(os.getcwd(), config_file)):
                config_file = os.path.join(os.getcwd(), config_file)
            else:
                # 方法2: 从当前文件位置向上查找项目根目录
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = current_dir
                
                # 向上查找包含app.py的目录作为项目根目录
                while project_root != os.path.dirname(project_root):
                    if os.path.exists(os.path.join(project_root, 'app.py')):
                        config_file = os.path.join(project_root, config_file)
                        break
                    project_root = os.path.dirname(project_root)
                else:
                    # 如果都没找到，使用当前工作目录
                    config_file = os.path.join(os.getcwd(), config_file)
        
        self.config_file = config_file
        self.load_from_file()
    
    def create_session(
        self,
        guest: bool,
        cookie: str,
        device_id: str,
        tea_uuid: str,
        web_id: str,
        room_id: str,
        x_flow_trace: str,
        phone: str = ""
    ) -> DoubaoSession:
        """创建新会话配置"""
        session = DoubaoSession(
            cookie=cookie,
            device_id=device_id,
            tea_uuid=tea_uuid,
            web_id=web_id,
            room_id=room_id,
            x_flow_trace=x_flow_trace,
            phone=phone
        )
        if guest:
            self.guest_sessions.append(session)
        else:
            self.auth_sessions.append(session)
        return session
    
    def get_session(self, conversation_id: str | None = None, guest: bool = False, phone: str | None = None) -> DoubaoSession | None:
        """获取会话配置，支持多种筛选方式
        
        Args:
            conversation_id: 会话ID筛选
            guest: 是否获取游客会话
            phone: 手机号筛选
            
        筛选优先级：
        1. conversation_id + phone: 从session_map中获取指定conversation_id的会话，并验证phone匹配
        2. conversation_id only: 从session_map中获取指定conversation_id的会话
        3. phone only: 从对应会话池中随机获取匹配phone的会话（新会话池，不复用conversation_id映射）
        4. 无筛选条件: 从对应会话池中随机获取会话
        """
        # 情况1: 有conversation_id，从session_map中查找
        if conversation_id is not None:
            session = self.session_map.get(conversation_id)
            if session:
                # 如果指定了phone，需要验证匹配
                if phone is not None and session.phone != phone:
                    return None
                return session
            return None
        
        # 情况2: 仅有phone筛选，从会话池中筛选（新会话，不使用session_map）
        sessions = self.guest_sessions if guest else self.auth_sessions
        if phone is not None:
            matching_sessions = [s for s in sessions if s.phone == phone]
            return random.choice(matching_sessions) if matching_sessions else None
        
        # 情况3: 无筛选条件，随机返回
        return random.choice(sessions) if sessions else None
    
    def set_session(self, conversation_id: str, session: DoubaoSession):
        """将会话与conversation_id关联"""
        self.session_map[conversation_id] = session
    
    def del_session(self, session: DoubaoSession):
        """删除会话"""
        if session in self.auth_sessions:
            self.auth_sessions.remove(session)
        elif session in self.guest_sessions:
            self.guest_sessions.remove(session)
        self.save_to_file()
    
    def save_to_file(self):
        """保存会话配置到文件"""
        try:
            data = [session.to_dict() for session in (self.auth_sessions + self.guest_sessions)]
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.debug(f"会话配置已保存到文件: {self.config_file}")
        except Exception as e:
            logger.error(f"保存会话配置到文件失败: {str(e)}")
    
    def load_from_file(self):
        """从文件加载会话配置"""
        if not os.path.exists(self.config_file):
            return logger.warning(f"会话配置文件不存在: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for session_data in data:
                # 只提取create_session需要的参数
                session_params = {
                    'cookie': session_data.get('cookie', ''),
                    'device_id': session_data.get('device_id', ''),
                    'tea_uuid': session_data.get('tea_uuid', ''),
                    'web_id': session_data.get('web_id', ''),
                    'room_id': session_data.get('room_id', ''),
                    'x_flow_trace': session_data.get('x_flow_trace', ''),
                    'phone': session_data.get('phone', ''),
                }
                
                # 检查是否为有效会话（必要字段不为空）
                if session_params['cookie'] and session_params['device_id']:
                    self.create_session(guest=False, **session_params)
                else:
                    logger.warning(f"跳过无效会话配置: 缺少cookie或device_id")
            
            logger.info(f"已从文件加载 {len(self.auth_sessions)} 个认证会话配置")
        except Exception as e:
            logger.error(f"从文件加载会话配置失败: {str(e)}")
    
    async def fetch_guest_session(self, num: int):
        for _ in range(num):
            automator = DoubaoAutomator()
            self.create_session(
                guest=True,
                **(await automator.run_automation())
            )


session_pool = SessionPool()

__all__ = [
    "DoubaoSession",
    "SessionPool",
    "session_pool"
] 