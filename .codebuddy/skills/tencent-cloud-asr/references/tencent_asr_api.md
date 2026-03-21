# Tencent Cloud ASR API Reference

## 产品介绍

腾讯云语音识别（ASR）提供业界领先水平的语音转文字服务，支持中文、英文、粤语等多种语言的语音识别。

## 支持的功能

1. **同步识别** - 短语音（≤60秒）实时返回结果
2. **录音文件识别** - 长音频（≤60分钟）异步识别
3. **实时语音识别** - 流式识别，支持实时语音输入
4. **说话人分离** - 识别不同说话人
5. **词级别时间戳** - 返回每个词的时间位置

## API 接口

### 1. 录音文件识别 (CreateRecTask)

**请求地址**: `asr.tencentcloudapi.com`

**请求方法**: POST

**主要参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| Action | String | 是 | CreateRecTask |
| Version | String | 是 | 2019-06-14 |
| EngineModelType | String | 是 | 引擎类型: 16k_zh(中文), 8k_zh(中文8k), 16k_en(英文) |
| ChannelNum | Integer | 是 | 声道数: 1 或 2 |
| SpeakerDiarization | Integer | 否 | 说话人分离: 0(否), 1(是) |
| AudioData | String | 是 | Base64编码的音频数据 |
| Url | String | 否 | 音频URL |

**响应参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| TaskId | Integer | 任务ID |
| RequestId | String | 请求ID |

### 2. 获取识别结果 (DescribeTaskStatus)

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| TaskId | Integer | 是 | 任务ID |

**响应参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| TaskStatus | Integer | 任务状态: 0(处理中), 1(成功), 2(失败) |
| Result | String | 识别结果 |
| ErrorMsg | String | 错误信息 |

### 3. 实时语音识别 (WebSocket)

**WebSocket URL**: `wss://asr.cloud.tencent.com/ws/api/v1/`

**Query参数**:
- appid: 应用ID
- engine_type: 引擎类型
- timestamp: 时间戳
- expired: 过期时间
- signature: 签名

**消息格式**:

初始化:
```json
{
  "action": "init",
  "appid": "xxx",
  "token": "xxx",
  "cluster": "volcengine_streaming_common"
}
```

发送音频:
- 二进制音频数据

识别结果:
```json
{
  "code": 0,
  "message": "success",
  "request_id": "xxx",
  "result": {
    "text": "识别文本",
    "final": 1
  }
}
```

## 签名算法

1. 排序所有参数（除Signature外）
2. 拼接成URL编码的字符串
3. 使用HMAC-SHA1签名
4. Base64编码

## 计费说明

- 录音文件识别: 按音频时长计费
- 实时语音识别: 按识别时长计费

## 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1000 | 参数错误 |
| 1001 | 鉴权失败 |
| 1002 | 余额不足 |
| 1003 | 并发超限 |
| 1004 | 文件大小超限 |
| 1005 | 文件格式不支持 |

## 最佳实践

1. 音频格式推荐使用PCM/WAV（16kHz采样率）
2. 对于长音频，使用录音文件识别接口
3. 实时对话场景使用WebSocket接口
4. 启用说话人分离可识别多人对话
