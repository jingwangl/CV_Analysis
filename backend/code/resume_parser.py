# -*- coding: utf-8 -*-
"""
简历 PDF 解析模块 - 使用 PyMuPDF (fitz)
"""
import re
import logging
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class ResumeParser:
    """简历解析器 - 使用 PyMuPDF"""
    
    def __init__(self):
        self.section_keywords = [
            "个人信息", "基本信息", "联系方式",
            "教育背景", "教育经历", "学历",
            "工作经历", "工作经验", "职业经历",
            "项目经历", "项目经验",
            "专业技能", "技能特长", "技术技能",
            "自我评价", "个人简介", "个人总结",
            "求职意向", "期望职位",
            "获奖情况", "荣誉奖项",
            "证书", "资格证书",
        ]
    
    def parse(self, pdf_data):
        """解析 PDF 文件"""
        try:
            # 使用 PyMuPDF 解析
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            
            pages_text = []
            full_text = ""
            
            for page_num, page in enumerate(doc):
                # 提取文本，保持布局
                text = page.get_text("text")
                pages_text.append({
                    "page_number": page_num + 1,
                    "text": text
                })
                full_text += text + "\n"
            
            doc.close()
            
            # 清洗文本
            cleaned = self._clean_text(full_text)
            
            if len(cleaned) < 20:
                return {
                    "success": False,
                    "error": "PDF 文本内容太少，可能是扫描版或图片版简历"
                }
            
            # 结构化处理
            structured = self._structure_text(cleaned)
            
            return {
                "success": True,
                "text": cleaned,
                "pages": pages_text,
                "page_count": len(pages_text),
                "structured_text": structured
            }
            
        except Exception as e:
            logger.error(f"PDF 解析错误: {e}")
            return {
                "success": False,
                "error": f"PDF 解析失败: {str(e)}"
            }
    
    def _clean_text(self, text):
        """清洗文本"""
        if not text:
            return ""
        
        # 统一换行符
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # 去除多余空行
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        # 去除多余空格
        text = re.sub(r"[ \t]{2,}", " ", text)
        
        # 去除特殊字符
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        
        # 去除首尾空白
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join([l for l in lines if l])
        
        return text.strip()
    
    def _structure_text(self, text):
        """结构化文本 - 识别各个部分"""
        if not text:
            return {}
        
        sections = {}
        current_section = "其他"
        current_content = []
        
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是段落标题
            is_header = False
            for keyword in self.section_keywords:
                if keyword in line and len(line) < 30:
                    # 保存当前段落
                    if current_content:
                        if current_section not in sections:
                            sections[current_section] = []
                        sections[current_section].extend(current_content)
                    
                    # 开始新段落
                    current_section = self._normalize_section(keyword)
                    current_content = []
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # 保存最后一个段落
        if current_content:
            if current_section not in sections:
                sections[current_section] = []
            sections[current_section].extend(current_content)
        
        # 转换为字符串
        for key in sections:
            if isinstance(sections[key], list):
                sections[key] = "\n".join(sections[key])
        
        return sections
    
    def _normalize_section(self, keyword):
        """标准化段落名称"""
        mapping = {
            "个人信息": "个人信息", "基本信息": "个人信息", "联系方式": "个人信息",
            "教育背景": "教育经历", "教育经历": "教育经历", "学历": "教育经历",
            "工作经历": "工作经历", "工作经验": "工作经历", "职业经历": "工作经历",
            "项目经历": "项目经历", "项目经验": "项目经历",
            "专业技能": "技能", "技能特长": "技能", "技术技能": "技能",
            "自我评价": "自我评价", "个人简介": "自我评价", "个人总结": "自我评价",
            "求职意向": "求职意向", "期望职位": "求职意向",
            "获奖情况": "获奖情况", "荣誉奖项": "获奖情况",
            "证书": "证书", "资格证书": "证书",
        }
        return mapping.get(keyword, keyword)
