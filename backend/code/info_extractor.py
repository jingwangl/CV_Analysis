# -*- coding: utf-8 -*-
"""
关键信息提取模块
使用正则表达式和 AI 模型提取简历中的关键信息
"""
import re
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class InfoExtractor:
    """信息提取器"""
    
    def __init__(self):
        # 阿里云 DashScope API 配置
        self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        self.use_ai = bool(self.api_key)
        
        # 正则表达式模式
        self.patterns = {
            "phone": [
                r"(?:手机|电话|联系电话|Tel|Phone|Mobile)[：:\s]*([1][3-9]\d{9})",
                r"([1][3-9]\d{9})",
                r"(\d{3,4}[-\s]?\d{7,8})"
            ],
            "email": [
                r"(?:邮箱|Email|E-mail|电子邮件)[：:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
                r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
            ],
            "name": [
                r"(?:姓名|Name)[：:\s]*([^\n\r\t,，。、；;]+)",
                r"^([^\n\r\t,，。、；;\d]{2,4})(?=\s|$)"
            ],
            "address": [
                r"(?:地址|住址|Address|现居|居住地)[：:\s]*([^\n\r]+)",
                r"((?:北京|上海|广州|深圳|杭州|成都|武汉|南京|西安|重庆|天津|苏州|郑州|长沙|东莞|青岛|沈阳|宁波|昆明)[市]?[^\n\r,，。]{0,30})"
            ],
            "education": [
                r"((?:博士|硕士|本科|大专|高中|学士|MBA|EMBA)[研究生]?)",
                r"((?:清华|北大|复旦|交大|浙大|中科大|南大|武大|华科|中大|哈工大|西交|同济|北航|北理|天大|南开|川大|山大|吉大|厦大|东南|中南|湖南|重大)[大学]?)"
            ],
            "experience_years": [
                r"(\d+)[年\s]*(?:以上)?(?:工作)?经[验历]",
                r"(?:工作)?经[验历][：:\s]*(\d+)[年]",
                r"(\d+)\+?[年\s]*(?:开发|工作|从业)"
            ],
            "job_intention": [
                r"(?:求职意向|期望职位|应聘岗位|目标岗位)[：:\s]*([^\n\r]+)",
                r"(?:期望|意向)[：:\s]*([^\n\r]+)"
            ]
        }
    
    def extract(self, text: str) -> Dict[str, Any]:
        """
        从简历文本中提取关键信息
        
        Args:
            text: 简历文本
            
        Returns:
            dict: 提取的关键信息
        """
        result = {
            "basic_info": {
                "name": None,
                "phone": None,
                "email": None,
                "address": None
            },
            "optional_info": {
                "job_intention": None,
                "experience_years": None,
                "education": None
            },
            "skills": [],
            "extraction_method": "regex"
        }
        
        # 使用正则表达式提取基本信息
        result["basic_info"]["phone"] = self._extract_pattern(text, "phone")
        result["basic_info"]["email"] = self._extract_pattern(text, "email")
        result["basic_info"]["name"] = self._extract_name(text)
        result["basic_info"]["address"] = self._extract_pattern(text, "address")
        
        # 提取可选信息
        result["optional_info"]["job_intention"] = self._extract_pattern(text, "job_intention")
        result["optional_info"]["experience_years"] = self._extract_experience_years(text)
        result["optional_info"]["education"] = self._extract_education(text)
        
        # 提取技能
        result["skills"] = self._extract_skills(text)
        
        # 如果配置了 AI API，使用 AI 增强提取
        if self.use_ai:
            try:
                ai_result = self._extract_with_ai(text)
                if ai_result:
                    result = self._merge_results(result, ai_result)
                    result["extraction_method"] = "ai_enhanced"
            except Exception as e:
                logger.warning(f"AI 提取失败，使用正则结果: {str(e)}")
        
        return result
    
    def _extract_pattern(self, text: str, pattern_name: str) -> Optional[str]:
        """使用正则表达式提取信息"""
        patterns = self.patterns.get(pattern_name, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_name(self, text: str) -> Optional[str]:
        """提取姓名"""
        # 首先尝试从明确标记中提取
        name_patterns = [
            r"(?:姓\s*名|Name)[：:\s]*([^\n\r\t,，。、；;\d]{2,4})",
            r"(?:简\s*历|个人简历|Resume)[：:\s]*([^\n\r\t,，。、；;\d]{2,4})"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if 2 <= len(name) <= 4 and self._is_valid_chinese_name(name):
                    return name
        
        # 尝试从文本开头提取
        lines = text.strip().split("\n")[:5]
        for line in lines:
            line = line.strip()
            if 2 <= len(line) <= 4 and self._is_valid_chinese_name(line):
                return line
        
        return None
    
    def _is_valid_chinese_name(self, name: str) -> bool:
        """检查是否是有效的中文姓名"""
        # 常见中文姓氏
        common_surnames = [
            "王", "李", "张", "刘", "陈", "杨", "黄", "赵", "周", "吴",
            "徐", "孙", "马", "胡", "朱", "郭", "何", "高", "林", "罗",
            "郑", "梁", "谢", "宋", "唐", "许", "韩", "冯", "邓", "曹",
            "彭", "曾", "萧", "田", "董", "袁", "潘", "于", "蒋", "蔡",
            "余", "杜", "叶", "程", "苏", "魏", "吕", "丁", "任", "沈",
            "姚", "卢", "姜", "崔", "钟", "谭", "陆", "汪", "范", "金"
        ]
        
        if not name:
            return False
        
        # 检查第一个字是否是常见姓氏
        if name[0] in common_surnames:
            return True
        
        # 检查是否全是中文字符
        return all("\u4e00" <= char <= "\u9fff" for char in name)
    
    def _extract_experience_years(self, text: str) -> Optional[str]:
        """提取工作年限"""
        patterns = self.patterns.get("experience_years", [])
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                years = match.group(1)
                return f"{years}年"
        
        return None
    
    def _extract_education(self, text: str) -> Optional[str]:
        """提取学历信息"""
        education_levels = ["博士", "硕士研究生", "硕士", "本科", "学士", "大专", "专科", "高中", "MBA", "EMBA"]
        
        for level in education_levels:
            if level in text:
                return level
        
        return None
    
    def _extract_skills(self, text: str) -> list:
        """提取技能列表"""
        # 常见技术技能关键词
        skill_keywords = [
            # 编程语言
            "Python", "Java", "JavaScript", "TypeScript", "C\\+\\+", "C#", "Go", "Rust",
            "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R语言",
            # 前端
            "React", "Vue", "Angular", "HTML", "CSS", "Node.js", "Webpack", "jQuery",
            # 后端
            "Spring", "Django", "Flask", "FastAPI", "Express", "Laravel", "Rails",
            # 数据库
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQL Server", "Elasticsearch",
            # 云服务和DevOps
            "AWS", "Azure", "阿里云", "腾讯云", "Docker", "Kubernetes", "K8s", "Jenkins", "Git",
            # AI/ML
            "机器学习", "深度学习", "TensorFlow", "PyTorch", "NLP", "计算机视觉", "大模型",
            # 其他
            "Linux", "Nginx", "Apache", "RabbitMQ", "Kafka", "微服务", "RESTful", "GraphQL"
        ]
        
        skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            pattern = r"\b" + skill.lower() + r"\b"
            if re.search(pattern, text_lower, re.IGNORECASE):
                # 保持原始大小写
                skills.append(skill.replace("\\+\\+", "++"))
        
        return list(set(skills))
    
    def _extract_with_ai(self, text: str) -> Optional[Dict[str, Any]]:
        """使用阿里云 DashScope API 提取信息"""
        try:
            import http.client
            
            # 构建提示词
            prompt = f"""请从以下简历文本中提取关键信息，以 JSON 格式返回：

简历文本：
{text[:3000]}

请提取以下信息并以 JSON 格式返回：
{{
    "basic_info": {{
        "name": "姓名",
        "phone": "手机号",
        "email": "邮箱",
        "address": "地址"
    }},
    "optional_info": {{
        "job_intention": "求职意向",
        "experience_years": "工作年限",
        "education": "最高学历"
    }},
    "skills": ["技能1", "技能2", ...]
}}

只返回 JSON，不要其他内容。如果某个字段无法提取，设为 null。"""

            # 调用 DashScope API
            conn = http.client.HTTPSConnection("dashscope.aliyuncs.com")
            
            payload = json.dumps({
                "model": "qwen-turbo",
                "input": {
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                "parameters": {
                    "result_format": "message"
                }
            })
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            conn.request("POST", "/api/v1/services/aigc/text-generation/generation", payload, headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode("utf-8"))
            
            if "output" in data and "choices" in data["output"]:
                content = data["output"]["choices"][0]["message"]["content"]
                # 提取 JSON 部分
                json_match = re.search(r"\{[\s\S]*\}", content)
                if json_match:
                    return json.loads(json_match.group())
            
            return None
            
        except Exception as e:
            logger.error(f"AI 提取失败: {str(e)}")
            return None
    
    def _merge_results(self, regex_result: Dict, ai_result: Dict) -> Dict:
        """合并正则和 AI 提取结果，优先使用 AI 结果"""
        merged = regex_result.copy()
        
        # 合并 basic_info
        if "basic_info" in ai_result:
            for key, value in ai_result["basic_info"].items():
                if value and not merged["basic_info"].get(key):
                    merged["basic_info"][key] = value
        
        # 合并 optional_info
        if "optional_info" in ai_result:
            for key, value in ai_result["optional_info"].items():
                if value and not merged["optional_info"].get(key):
                    merged["optional_info"][key] = value
        
        # 合并 skills
        if "skills" in ai_result and ai_result["skills"]:
            existing_skills = set(s.lower() for s in merged["skills"])
            for skill in ai_result["skills"]:
                if skill and skill.lower() not in existing_skills:
                    merged["skills"].append(skill)
        
        return merged

