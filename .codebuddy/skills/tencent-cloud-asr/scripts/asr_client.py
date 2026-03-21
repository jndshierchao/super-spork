#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tencent Cloud ASR Client
语音转文字客户端
"""

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime
from urllib.parse import urlencode

try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.asr.v20190614 import asr_client, models
    TENCENT_SDK_AVAILABLE = True
except ImportError:
    TENCENT_SDK_AVAILABLE = False


class TencentASR:
    """腾讯云ASR客户端"""
    
    def __init__(self, secret_id: str, secret_key: str, region: str = "ap-guangzhou"):
        """
        初始化ASR客户端
        
        Args:
            secret_id: 腾讯云SecretId
            secret_key: 腾讯云SecretKey
            region: 地域，默认广州
        """
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        
        if TENCENT_SDK_AVAILABLE:
            self.cred = credential.Credential(secret_id, secret_key)
            self.client = self._create_client()
        else:
            self.client = None
    
    def _create_client(self):
        """创建ASR客户端"""
        httpProfile = HttpProfile()
        httpProfile.endpoint = "asr.tencentcloudapi.com"
        httpProfile.reqMethod = "POST"
        httpProfile.reqTimeout = 60
        
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        
        return asr_client.AsrClient(self.cred, self.region, clientProfile)
    
    def recognize(self, audio_path: str, engine_type: str = "16k", 
                  speaker_diarization: int = 0, word_info: int = 0) -> dict:
        """
        识别音频文件
        
        Args:
            audio_path: 音频文件路径
            engine_type: 引擎类型，"16k"或"8k"
            speaker_diarization: 是否开启说话人分离，0不开启，1开启
            word_info: 是否返回词级别时间戳，0不开启，1开启
            
        Returns:
            识别结果字典
        """
        # 读取音频文件
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        # Base64编码
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # 使用SDK
        if TENCENT_SDK_AVAILABLE and self.client:
            return self._recognize_sdk(audio_base64, engine_type, speaker_diarization, word_info)
        else:
            # 使用API直连方式
            return self._recognize_api(audio_base64, engine_type, speaker_diarization, word_info)
    
    def _recognize_sdk(self, audio_base64: str, engine_type: str, 
                       speaker_diarization: int, word_info: int) -> dict:
        """使用SDK识别"""
        req = models.DescribeRecordingStatusRequest()
        req.EngineModelType = engine_type
        req.ChannelNum = 1
        req.SpeakerDiarization = speaker_diarization
        req.WordInfo = word_info
        
        # 对于文件识别，使用同步识别API
        # 这里使用录音识别请求
        req = models.CreateRecTaskRequest()
        req.EngineModelType = engine_type
        req.ChannelNum = 1
        req.SpeakerDiarization = speaker_diarization
        req.WordInfo = word_info
        req.AudioData = audio_base64
        
        resp = self.client.CreateRecTask(req)
        return json.loads(resp.to_json_string())
    
    def _recognize_api(self, audio_base64: str, engine_type: str,
                       speaker_diarization: int, word_info: int) -> dict:
        """使用API直连方式识别"""
        # 生成签名
        timestamp = int(time.time())
        
        # 构建请求参数
        params = {
            "Action": "CreateRecTask",
            "Version": "2019-06-14",
            "Region": self.region,
            "EngineModelType": engine_type,
            "ChannelNum": 1,
            "SpeakerDiarization": speaker_diarization,
            "WordInfo": word_info,
            "AudioData": audio_base64,
            "Timestamp": timestamp,
            "Nonce": timestamp,
            "SecretId": self.secret_id,
        }
        
        # 生成签名
        sign_str = self._generate_sign(params)
        params["Signature"] = sign_str
        
        return {
            "status": "pending",
            "message": "Please install tencentcloud-sdk-python-core to use full functionality",
            "params": params
        }
    
    def _generate_sign(self, params: dict) -> str:
        """生成腾讯云API签名"""
        # 排序并编码参数
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_str = "POSTasr.tencentcloudapi.com/?" + urlencode(sorted_params)
        
        # HMAC-SHA1签名
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def recognize_url(self, url: str, engine_type: str = "16k",
                      speaker_diarization: int = 0) -> dict:
        """
        通过URL识别音频
        
        Args:
            url: 音频文件URL
            engine_type: 引擎类型
            speaker_diarization: 是否开启说话人分离
            
        Returns:
            任务信息
        """
        if not TENCENT_SDK_AVAILABLE or not self.client:
            return {"error": "SDK not available"}
        
        req = models.CreateRecTaskRequest()
        req.EngineModelType = engine_type
        req.ChannelNum = 1
        req.SpeakerDiarization = speaker_diarization
        req.Url = url
        
        resp = self.client.CreateRecTask(req)
        return json.loads(resp.to_json_string())
    
    def get_result(self, task_id: int) -> dict:
        """
        获取识别结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            识别结果
        """
        if not TENCENT_SDK_AVAILABLE or not self.client:
            return {"error": "SDK not available"}
        
        req = models.DescribeTaskStatusRequest()
        req.TaskId = task_id
        
        resp = self.client.DescribeTaskStatus(req)
        return json.loads(resp.to_json_string())


class RealtimeASR:
    """实时语音识别客户端"""
    
    def __init__(self, secret_id: str, secret_key: str, app_id: str):
        """
        初始化实时ASR
        
        Args:
            secret_id: 腾讯云SecretId
            secret_key: 腾讯云SecretKey
            app_id: 应用ID
        """
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.app_id = app_id
        self.ws = None
    
    def start(self, engine_type: str = "16k"):
        """
        开始实时识别
        
        Args:
            engine_type: 引擎类型
        """
        # 实时ASR需要使用WebSocket连接
        # 这里提供接口，实际实现需要根据腾讯云实时ASR文档
        print(f"Starting realtime ASR with engine: {engine_type}")
        print("Note: Realtime ASR requires WebSocket implementation")
    
    def stop(self):
        """停止实时识别"""
        if self.ws:
            self.ws.close()
        print("Realtime ASR stopped")


# 示例用法
if __name__ == "__main__":
    # 配置你的腾讯云凭证
    SECRET_ID = "your_secret_id"
    SECRET_KEY = "your_secret_key"
    
    # 创建客户端
    asr = TencentASR(SECRET_ID, SECRET_KEY)
    
    # 识别音频文件
    # result = asr.recognize("test.wav")
    # print(result)
    
    print("Tencent Cloud ASR Client initialized")
    print("Please set your credentials and audio file path to use")
