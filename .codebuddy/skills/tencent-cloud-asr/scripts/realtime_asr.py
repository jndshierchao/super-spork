#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tencent Cloud Realtime ASR
实时语音识别示例
"""

import base64
import hashlib
import hmac
import json
import threading
import time
import wave
from datetime import datetime
from urllib.parse import urlencode

try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


class RealtimeASRClient:
    """腾讯云实时语音识别客户端"""
    
    def __init__(self, secret_id: str, secret_key: str, app_id: str):
        """
        初始化实时ASR客户端
        
        Args:
            secret_id: 腾讯云SecretId
            secret_key: 腾讯云SecretKey
            app_id: 应用ID
        """
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.app_id = app_id
        self.ws = None
        self.is_recording = False
        self.audio_thread = None
        self.result_callback = None
    
    def set_result_callback(self, callback):
        """设置结果回调函数"""
        self.result_callback = callback
    
    def _generate_auth(self, url: str) -> tuple:
        """生成鉴权信息"""
        timestamp = int(time.time())
        
        # 生成authstring
        authstring = f"tc3_date={timestamp}"
        
        # 签名
        signature = self._sign(url, timestamp)
        
        return timestamp, signature, authstring
    
    def _sign(self, url: str, timestamp: int) -> str:
        """生成签名"""
        # 简化的签名计算
        sign_str = f"GET{url.split('//')[1]}?auth={timestamp}"
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def connect(self, engine_type: str = "16k") -> bool:
        """
        连接到实时ASR服务
        
        Args:
            engine_type: 引擎类型
            
        Returns:
            是否连接成功
        """
        if not WEBSOCKET_AVAILABLE:
            print("Warning: websocket-client not installed")
            print("Install with: pip install websocket-client")
            return False
        
        # 腾讯云实时ASR WebSocket URL
        url = f"wss://asr.cloud.tencent.com/ws/api/v1/?appid={self.app_id}&engine_type={engine_type}&timestamp={int(time.time())}"
        
        try:
            self.ws = websocket.WebSocketApp(
                url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            
            # 启动WebSocket客户端
            self.ws.run_forever()
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def _on_message(self, ws, message):
        """收到消息"""
        try:
            data = json.loads(message)
            
            if data.get("code") == 0:
                result = data.get("result", {})
                text = result.get("text", "")
                if text and self.result_callback:
                    self.result_callback(text)
            else:
                error_msg = data.get("message", "Unknown error")
                print(f"ASR Error: {error_msg}")
                
        except json.JSONDecodeError:
            print(f"Invalid message: {message}")
    
    def _on_error(self, ws, error):
        """错误处理"""
        print(f"Error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """连接关闭"""
        print("Connection closed")
    
    def _on_open(self, ws):
        """连接打开"""
        print("Connected to Tencent Cloud Realtime ASR")
        
        # 发送初始化消息
        init_msg = {
            "action": "init",
            "appid": self.app_id,
            "token": "",  # 需要token
            "cluster": "volcengine_streaming_common"
        }
        ws.send(json.dumps(init_msg))
    
    def send_audio(self, audio_data: bytes):
        """
        发送音频数据
        
        Args:
            audio_data: 音频数据（PCM格式）
        """
        if self.ws and self.ws.sock and self.ws.sock.connected:
            # 发送音频数据
            self.ws.send(audio_data, opcode=websocket.ABNF.OPCODE_BINARY)
    
    def start_recording(self, audio_device: int = None):
        """
        开始录音并识别
        
        Args:
            audio_device: 音频设备ID
        """
        self.is_recording = True
        
        def record_and_send():
            try:
                import pyaudio
                
                p = pyaudio.PyAudio()
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    input_device_index=audio_device,
                    frames_per_buffer=1024
                )
                
                print("Recording... Press Ctrl+C to stop")
                
                while self.is_recording:
                    audio_data = stream.read(1024)
                    self.send_audio(audio_data)
                    
                stream.stop_stream()
                stream.close()
                p.terminate()
                
            except ImportError:
                print("PyAudio not installed")
                print("Install with: pip install pyaudio")
            except Exception as e:
                print(f"Recording error: {e}")
        
        self.audio_thread = threading.Thread(target=record_and_send)
        self.audio_thread.start()
    
    def stop_recording(self):
        """停止录音"""
        self.is_recording = False
        
        if self.audio_thread:
            self.audio_thread.join()
        
        if self.ws:
            self.ws.close()


class VoiceDialogue:
    """语音对话系统"""
    
    def __init__(self, secret_id: str, secret_key: str, app_id: str):
        """
        初始化语音对话系统
        
        Args:
            secret_id: 腾讯云SecretId
            secret_key: 腾讯云SecretKey
            app_id: 应用ID
        """
        self.asr = RealtimeASRClient(secret_id, secret_key, app_id)
        self.tts = None  # TTS客户端
        self.nlp = None  # NLP处理器
        self.is_active = False
    
    def set_nlp_handler(self, handler):
        """设置NLP处理器"""
        self.nlp = handler
    
    def set_tts(self, tts_client):
        """设置TTS客户端"""
        self.tts = tts_client
    
    def start(self):
        """启动语音对话"""
        self.is_active = True
        
        # 设置ASR结果回调
        self.asr.set_result_callback(self._process_speech)
        
        # 启动ASR
        self.asr.connect()
        self.asr.start_recording()
    
    def stop(self):
        """停止语音对话"""
        self.is_active = False
        self.asr.stop_recording()
    
    def _process_speech(self, text: str):
        """
        处理识别到的文本
        
        Args:
            text: 识别的文本
        """
        print(f"Recognized: {text}")
        
        if not self.nlp:
            # 如果没有NLP处理器，回显
            response = f"你说的是: {text}"
        else:
            # 调用NLP处理
            response = self.nlp.process(text)
        
        print(f"Response: {response}")
        
        # 合成语音
        if self.tts:
            audio = self.tts.synthesize(response)
            # 播放音频
            self._play_audio(audio)
    
    def _play_audio(self, audio_data: bytes):
        """播放音频"""
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                output=True
            )
            
            stream.write(audio_data)
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except ImportError:
            print("PyAudio not installed for audio playback")


# 示例用法
if __name__ == "__main__":
    # 配置凭证
    SECRET_ID = "your_secret_id"
    SECRET_KEY = "your_secret_key"
    APP_ID = "your_app_id"
    
    # 创建实时ASR客户端
    realtime_asr = RealtimeASRClient(SECRET_ID, SECRET_KEY, APP_ID)
    
    # 或者创建语音对话系统
    # dialogue = VoiceDialogue(SECRET_ID, SECRET_KEY, APP_ID)
    # dialogue.start()
    
    print("Realtime ASR client initialized")
    print("Please set your credentials to use")
