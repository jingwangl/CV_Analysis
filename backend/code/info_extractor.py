# -*- coding: utf-8 -*-
"""
关键信息提取模块 - 处理分散文本格式
"""
import re
import logging

logger = logging.getLogger(__name__)


class InfoExtractor:
    """信息提取器"""
    
    def __init__(self):
        pass
    
    def extract(self, text):
        """从简历文本中提取关键信息"""
        # 先清理文本，合并分散的字符
        cleaned_text = self._clean_scattered_text(text)
        
        result = {
            "basic_info": {
                "name": self._extract_name(cleaned_text),
                "phone": self._extract_phone(cleaned_text, text),
                "email": self._extract_email(cleaned_text, text),
                "address": self._extract_address(cleaned_text)
            },
            "optional_info": {
                "job_intention": self._extract_job_intention(cleaned_text),
                "experience_years": self._extract_experience(cleaned_text),
                "education": self._extract_education(cleaned_text)
            },
            "skills": self._extract_skills(cleaned_text),
            "extraction_method": "regex"
        }
        return result
    
    def _clean_scattered_text(self, text):
        """清理分散的文本，合并字符"""
        if not text:
            return ""
        
        # 移除单个字母/数字之间的空格
        # 例如 "P y t h o n" -> "Python"
        result = []
        chars = list(text)
        i = 0
        
        while i < len(chars):
            c = chars[i]
            result.append(c)
            
            # 如果当前是字母/数字，下一个是空格，再下一个也是字母/数字
            if i + 2 < len(chars):
                if (c.isalnum() and chars[i+1] == ' ' and 
                    len(chars[i+2:]) > 0 and chars[i+2].isalnum()):
                    # 检查是否是单字符模式
                    if i == 0 or not chars[i-1].isalnum():
                        # 可能是分散文本，跳过空格
                        i += 1  # 跳过空格
            i += 1
        
        text = ''.join(result)
        
        # 更激进的清理：移除所有单字符之间的空格
        # 处理类似 "77 3 62 80 72 @ qq .co m" 的情况
        text = re.sub(r'(\d) (\d)', r'\1\2', text)  # 数字之间
        text = re.sub(r'(\d) (\d)', r'\1\2', text)  # 再次执行
        text = re.sub(r'(\w) @ (\w)', r'\1@\2', text)  # @符号
        text = re.sub(r'@ (\w+) \.', r'@\1.', text)  # 邮箱域名
        text = re.sub(r'\. co m', '.com', text)
        text = re.sub(r'\. cn', '.cn', text)
        text = re.sub(r'qq \.', 'qq.', text)
        text = re.sub(r'163 \.', '163.', text)
        text = re.sub(r'gmail \.', 'gmail.', text)
        
        return text
    
    def _extract_phone(self, cleaned_text, original_text):
        """提取手机号"""
        # 先尝试从清理后的文本提取
        patterns = [
            r"1[3-9]\d{9}",
            r"1[3-9]\d[- ]?\d{4}[- ]?\d{4}"
        ]
        for p in patterns:
            match = re.search(p, cleaned_text)
            if match:
                return re.sub(r'[- ]', '', match.group())
        
        # 尝试从原始文本提取分散的手机号
        # 匹配类似 "1 8 8 0 0 1 2 8 1 0 6" 或 "18 80 01 28 10 6"
        scattered = re.search(r'1[3-9][\d\s]{10,20}', original_text)
        if scattered:
            digits = re.sub(r'\s', '', scattered.group())
            if len(digits) == 11 and digits[0] == '1' and digits[1] in '3456789':
                return digits
        
        return None
    
    def _extract_email(self, cleaned_text, original_text):
        """提取邮箱"""
        # 标准格式
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        match = re.search(pattern, cleaned_text)
        if match:
            return match.group()
        
        # 尝试从原始文本重建邮箱
        # 匹配类似 "77 3 62 80 72 @ qq .co m"
        email_pattern = r'([\d\w][\d\w\s]{2,20})\s*@\s*([\w\s]+)\s*\.\s*(com|cn|net|org)'
        match = re.search(email_pattern, original_text, re.IGNORECASE)
        if match:
            local = re.sub(r'\s', '', match.group(1))
            domain = re.sub(r'\s', '', match.group(2))
            suffix = match.group(3)
            return f"{local}@{domain}.{suffix}"
        
        return None
    
    def _extract_name(self, text):
        """提取姓名"""
        # 常见中文姓氏
        surnames = "王李张刘陈杨黄赵周吴徐孙马胡朱郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾萧田董袁潘于蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石戴贾韦夏邱方侯邹熊孟秦白毛江"
        
        # 从标记中提取
        patterns = [
            r"(?:姓\s*名|Name)[：:\s]*([^\n\r\t,，。、]{2,4})",
        ]
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if 2 <= len(name) <= 4:
                    return name
        
        # 在文本开头查找中文名字
        for line in text.split('\n')[:10]:
            line = line.strip()
            # 检查是否是 2-4 个中文字符，且第一个是姓氏
            if 2 <= len(line) <= 4:
                if line[0] in surnames and all('\u4e00' <= c <= '\u9fff' for c in line):
                    return line
        
        return None
    
    def _extract_address(self, text):
        """提取地址"""
        cities = "北京|上海|广州|深圳|杭州|成都|武汉|南京|西安|重庆|天津|苏州|郑州|长沙|东莞|青岛|沈阳|宁波|昆明|合肥|厦门|无锡|大连|福州|济南|哈尔滨|长春|太原|南昌|南宁|贵阳|海口"
        pattern = rf"({cities})[市]?[^\n,，。]{{0,30}}"
        match = re.search(pattern, text)
        return match.group() if match else None
    
    def _extract_job_intention(self, text):
        """提取求职意向"""
        patterns = [
            r"(?:求职意向|期望职位|应聘岗位|目标职位)[：:\s]*([^\n\r]{2,30})",
        ]
        for p in patterns:
            match = re.search(p, text)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_experience(self, text):
        """提取工作年限"""
        patterns = [
            r"(\d+)\s*年[以上]*[工作]*经[验历]",
            r"经[验历][：:\s]*(\d+)\s*年",
            r"(\d+)\s*[+]*\s*years?",
        ]
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                return f"{match.group(1)}年"
        return None
    
    def _extract_education(self, text):
        """提取学历"""
        levels = ["博士", "硕士", "研究生", "本科", "学士", "大专", "专科", "Master", "Bachelor", "PhD"]
        text_lower = text.lower()
        for level in levels:
            if level.lower() in text_lower:
                return level
        return None
    
    def _extract_skills(self, text):
        """提取技能"""
        skill_keywords = [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin",
            "React", "Vue", "Angular", "Node.js", "Node", "Spring", "Django", "Flask", "FastAPI", "Express",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQL Server", "SQLite",
            "Docker", "Kubernetes", "K8s", "AWS", "Azure", "GCP", "Linux", "Git", "GitHub",
            "机器学习", "深度学习", "TensorFlow", "PyTorch", "NLP", "CNN", "RNN", "LSTM",
            "HTML", "CSS", "REST", "API", "TCP", "UDP", "HTTP", "HTTPS",
            "Figma", "Photoshop", "AI", "ML", "DL"
        ]
        
        # 清理文本中的空格以便匹配
        text_cleaned = re.sub(r'(\w) (\w)', r'\1\2', text)
        text_cleaned = re.sub(r'(\w) (\w)', r'\1\2', text_cleaned)
        text_lower = text_cleaned.lower()
        
        found = []
        for skill in skill_keywords:
            # 使用单词边界或直接匹配
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                found.append(skill)
            elif skill.lower() in text_lower:
                found.append(skill)
        
        return list(set(found))
