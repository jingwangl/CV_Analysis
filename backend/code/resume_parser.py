# -*- coding: utf-8 -*-
"""
简历 PDF 解析模块
支持多页 PDF 解析，文本提取和结构化处理
"""
import re
import io
import logging

logger = logging.getLogger(__name__)


class ResumeParser:
    """简历解析器"""
    
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
            "语言能力", "外语水平"
        ]
    
    def parse(self, pdf_data):
        """
        解析 PDF 文件
        
        Args:
            pdf_data: PDF 文件的二进制数据
            
        Returns:
            dict: 包含解析结果的字典
        """
        try:
            import pdfplumber
            
            # 从二进制数据创建 PDF 对象
            pdf_file = io.BytesIO(pdf_data)
            
            with pdfplumber.open(pdf_file) as pdf:
                pages_text = []
                full_text = ""
                
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    pages_text.append({
                        "page_number": i + 1,
                        "text": page_text
                    })
                    full_text += page_text + "\n"
                
                # 清洗和结构化文本
                cleaned_text = self._clean_text(full_text)
                structured_text = self._structure_text(cleaned_text)
                
                return {
                    "success": True,
                    "text": cleaned_text,
                    "pages": pages_text,
                    "page_count": len(pdf.pages),
                    "structured_text": structured_text
                }
                
        except ImportError:
            logger.error("pdfplumber 未安装")
            return {
                "success": False,
                "error": "PDF 解析库未安装"
            }
        except Exception as e:
            logger.error(f"PDF 解析失败: {str(e)}")
            return {
                "success": False,
                "error": f"PDF 解析失败: {str(e)}"
            }
    
    def _clean_text(self, text):
        """
        清洗文本
        - 去除多余空白字符
        - 统一换行符
        - 去除特殊字符
        """
        if not text:
            return ""
        
        # 统一换行符
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # 去除多余空行（保留最多两个连续换行）
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        # 去除行首行尾空白
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)
        
        # 去除多余空格
        text = re.sub(r" {2,}", " ", text)
        
        # 去除特殊不可见字符
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        
        return text.strip()
    
    def _structure_text(self, text):
        """
        对文本进行结构化处理
        识别并分割各个部分
        """
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
            
            # 检查是否是新的部分标题
            is_section_header = False
            for keyword in self.section_keywords:
                if keyword in line and len(line) < 30:
                    # 保存当前部分
                    if current_content:
                        if current_section not in sections:
                            sections[current_section] = []
                        sections[current_section].extend(current_content)
                    
                    # 开始新部分
                    current_section = self._normalize_section_name(keyword)
                    current_content = []
                    is_section_header = True
                    break
            
            if not is_section_header:
                current_content.append(line)
        
        # 保存最后一个部分
        if current_content:
            if current_section not in sections:
                sections[current_section] = []
            sections[current_section].extend(current_content)
        
        # 将列表转换为字符串
        for key in sections:
            sections[key] = "\n".join(sections[key])
        
        return sections
    
    def _normalize_section_name(self, keyword):
        """标准化部分名称"""
        mapping = {
            "个人信息": "个人信息",
            "基本信息": "个人信息",
            "联系方式": "个人信息",
            "教育背景": "教育经历",
            "教育经历": "教育经历",
            "学历": "教育经历",
            "工作经历": "工作经历",
            "工作经验": "工作经历",
            "职业经历": "工作经历",
            "项目经历": "项目经历",
            "项目经验": "项目经历",
            "专业技能": "技能",
            "技能特长": "技能",
            "技术技能": "技能",
            "自我评价": "自我评价",
            "个人简介": "自我评价",
            "个人总结": "自我评价",
            "求职意向": "求职意向",
            "期望职位": "求职意向",
            "获奖情况": "获奖情况",
            "荣誉奖项": "获奖情况",
            "证书": "证书",
            "资格证书": "证书",
            "语言能力": "语言能力",
            "外语水平": "语言能力"
        }
        return mapping.get(keyword, keyword)

