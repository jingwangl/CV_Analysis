# -*- coding: utf-8 -*-
"""
阿里云函数计算入口文件
简历分析 RESTful API 服务
"""
import json
import base64
import logging
import traceback

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 延迟加载组件，避免模块加载时失败影响 OPTIONS 请求
resume_parser = None
info_extractor = None
resume_matcher = None

# 简单的内存缓存
cache = {}

def init_components():
    """延迟初始化组件"""
    global resume_parser, info_extractor, resume_matcher
    if resume_parser is None:
        from resume_parser import ResumeParser
        from info_extractor import InfoExtractor
        from matcher import ResumeMatcher
        resume_parser = ResumeParser()
        info_extractor = InfoExtractor()
        resume_matcher = ResumeMatcher()


def create_response(status_code, body, origin=None):
    """创建 HTTP 响应"""
    # CORS 完全交给阿里云 HTTP 触发器配置，代码中不设置任何 CORS 头
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(body, ensure_ascii=False)
    }


def handle_upload(event, origin=None):
    """处理简历上传和解析"""
    try:
        # 获取请求体
        body = event.get("body", "")
        is_base64 = event.get("isBase64Encoded", False)
        
        if is_base64:
            body = base64.b64decode(body)
        
        # 解析 multipart/form-data 或 JSON
        headers = event.get("headers", {})
        content_type = headers.get("content-type") or headers.get("Content-Type", "")
        
        if "multipart/form-data" in content_type:
            # 解析 multipart 数据
            pdf_data = parse_multipart(body, content_type)
        elif "application/json" in content_type:
            # JSON 格式，期望 base64 编码的 PDF
            if isinstance(body, bytes):
                body = body.decode("utf-8")
            json_body = json.loads(body)
            pdf_data = base64.b64decode(json_body.get("file", ""))
        else:
            return create_response(400, {"error": "不支持的内容类型"}, origin)
        
        if not pdf_data:
            return create_response(400, {"error": "未找到 PDF 文件"}, origin)
        
        # 解析 PDF
        logger.info("开始解析 PDF...")
        parsed_result = resume_parser.parse(pdf_data)
        
        if not parsed_result["success"]:
            return create_response(400, {"error": parsed_result["error"]}, origin)
        
        # 提取关键信息
        logger.info("开始提取关键信息...")
        extracted_info = info_extractor.extract(parsed_result["text"])
        
        # 生成缓存 key
        import hashlib
        cache_key = hashlib.md5(pdf_data).hexdigest()
        
        # 缓存结果
        result = {
            "cache_key": cache_key,
            "raw_text": parsed_result["text"],
            "pages": parsed_result["pages"],
            "extracted_info": extracted_info,
            "structured_text": parsed_result["structured_text"]
        }
        cache[cache_key] = result
        
        return create_response(200, {
            "success": True,
            "message": "简历解析成功",
            "data": result
        }, origin)
        
    except Exception as e:
        logger.error(f"处理上传失败: {str(e)}")
        return create_response(500, {"error": f"处理失败: {str(e)}"}, origin)


def handle_match(event, origin=None):
    """处理简历与岗位匹配"""
    try:
        body = event.get("body", "")
        is_base64 = event.get("isBase64Encoded", False)
        
        if is_base64:
            body = base64.b64decode(body).decode("utf-8")
        elif isinstance(body, bytes):
            body = body.decode("utf-8")
            
        json_body = json.loads(body)
        
        # 获取参数
        cache_key = json_body.get("cache_key", "")
        job_description = json_body.get("job_description", "")
        resume_text = json_body.get("resume_text", "")
        extracted_info = json_body.get("extracted_info", {})
        
        if not job_description:
            return create_response(400, {"error": "缺少岗位描述"}, origin)
        
        # 优先使用缓存的简历数据
        if cache_key and cache_key in cache:
            cached_data = cache[cache_key]
            resume_text = cached_data["raw_text"]
            extracted_info = cached_data["extracted_info"]
        elif not resume_text:
            return create_response(400, {"error": "缺少简历数据，请先上传简历或提供 cache_key"}, origin)
        
        # 计算匹配度
        logger.info("开始计算匹配度...")
        match_result = resume_matcher.match(resume_text, job_description, extracted_info)
        
        return create_response(200, {
            "success": True,
            "message": "匹配分析完成",
            "data": match_result
        }, origin)
        
    except Exception as e:
        logger.error(f"匹配分析失败: {str(e)}")
        return create_response(500, {"error": f"匹配分析失败: {str(e)}"}, origin)


def parse_multipart(body, content_type):
    """解析 multipart/form-data 数据"""
    try:
        # 获取 boundary
        boundary = None
        for part in content_type.split(";"):
            part = part.strip()
            if part.startswith("boundary="):
                boundary = part[9:].strip('"')
                break
        
        if not boundary:
            return None
        
        if isinstance(body, str):
            body = body.encode("utf-8")
        
        boundary_bytes = boundary.encode("utf-8")
        parts = body.split(b"--" + boundary_bytes)
        
        for part in parts:
            if b"Content-Disposition" in part and b"filename" in part:
                # 找到文件部分
                header_end = part.find(b"\r\n\r\n")
                if header_end != -1:
                    file_data = part[header_end + 4:]
                    # 移除尾部的 boundary 标记
                    if file_data.endswith(b"\r\n"):
                        file_data = file_data[:-2]
                    if file_data.endswith(b"--"):
                        file_data = file_data[:-2]
                    if file_data.endswith(b"\r\n"):
                        file_data = file_data[:-2]
                    return file_data
        
        return None
    except Exception as e:
        logger.error(f"解析 multipart 失败: {str(e)}")
        return None


def get_origin(event):
    """获取请求的 Origin"""
    headers = event.get("headers", {})
    # headers 可能是小写的
    origin = headers.get("origin") or headers.get("Origin") or "https://jingwangl.github.io"
    return origin


def handler(event, context):
    """阿里云函数计算入口"""
    try:
        # 解析事件
        if isinstance(event, str):
            event = json.loads(event)
        elif isinstance(event, bytes):
            event = json.loads(event.decode("utf-8"))
    except Exception as e:
        logger.error(f"解析事件失败: {e}")
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps({"error": "Invalid request"})
        }
    
    # 获取 HTTP 方法和路径
    http_method = event.get("httpMethod") or event.get("method") or event.get("requestContext", {}).get("http", {}).get("method", "GET")
    
    # 先处理 OPTIONS，不依赖任何初始化
    # CORS 完全交给阿里云 HTTP 触发器配置
    if http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps({"message": "OK"})
        }
    
    # 其他请求才需要初始化组件
    try:
        # 获取请求来源
        origin = get_origin(event)
        
        path = (
            event.get("rawPath") or 
            event.get("path") or 
            event.get("requestURI") or 
            event.get("requestContext", {}).get("http", {}).get("path") or
            "/"
        )
        if "?" in path:
            path = path.split("?")[0]
        
        logger.info(f"收到请求: {http_method} {path}")
        
        # 健康检查不需要初始化组件
        if path == "/health" or path == "/" or path == "":
            return create_response(200, {
                "success": True,
                "message": "简历分析 API 服务运行正常",
                "version": "1.0.0",
                "endpoints": {
                    "POST /upload": "上传并解析简历",
                    "POST /match": "简历与岗位匹配评分"
                }
            }, origin)
        
        # 其他路由需要初始化组件
        try:
            init_components()
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return create_response(500, {"error": f"服务初始化失败: {str(e)}"}, origin)
        
        # 路由处理
        if path == "/upload" and http_method == "POST":
            return handle_upload(event, origin)
        elif path == "/match" and http_method == "POST":
            return handle_match(event, origin)
        else:
            # 返回调试信息帮助排查路由问题
            return create_response(404, {
                "error": f"接口不存在: {path}",
                "debug": {
                    "received_path": path,
                    "method": http_method,
                    "event_keys": list(event.keys()),
                    "rawPath": event.get("rawPath"),
                    "path_field": event.get("path")
                }
            }, origin)
            
    except Exception as e:
        logger.error(f"处理请求失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps({"error": f"服务器内部错误: {str(e)}"}, ensure_ascii=False)
        }

