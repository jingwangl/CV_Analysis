# -*- coding: utf-8 -*-
"""
简历与岗位匹配评分模块
使用关键词匹配和 AI 模型计算匹配度
"""
import re
import os
import json
import math
import logging
from typing import Dict, Any, List
from collections import Counter

logger = logging.getLogger(__name__)


class ResumeMatcher:
    """简历匹配器"""
    
    def __init__(self):
        # 阿里云 DashScope API 配置
        self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        self.use_ai = bool(self.api_key)
        
        # 技能权重配置
        self.skill_weights = {
            "programming_language": 1.0,
            "framework": 0.9,
            "database": 0.8,
            "tool": 0.7,
            "soft_skill": 0.5
        }
        
        # 技能分类
        self.skill_categories = {
            "programming_language": [
                "python", "java", "javascript", "typescript", "c++", "c#", "go", 
                "rust", "php", "ruby", "swift", "kotlin", "scala", "r"
            ],
            "framework": [
                "react", "vue", "angular", "spring", "django", "flask", "fastapi",
                "express", "node.js", "laravel", "rails", "springboot", "mybatis"
            ],
            "database": [
                "mysql", "postgresql", "mongodb", "redis", "oracle", "sql server",
                "elasticsearch", "hbase", "cassandra", "sqlite"
            ],
            "tool": [
                "docker", "kubernetes", "k8s", "jenkins", "git", "linux", "nginx",
                "aws", "azure", "阿里云", "腾讯云", "kafka", "rabbitmq"
            ],
            "soft_skill": [
                "沟通", "团队", "协作", "领导", "管理", "学习", "创新", "责任"
            ]
        }
    
    def match(self, resume_text: str, job_description: str, extracted_info: Dict = None) -> Dict[str, Any]:
        """
        计算简历与岗位的匹配度
        
        Args:
            resume_text: 简历文本
            job_description: 岗位描述
            extracted_info: 已提取的简历信息
            
        Returns:
            dict: 匹配结果
        """
        result = {
            "overall_score": 0,
            "skill_match": {
                "score": 0,
                "matched_skills": [],
                "missing_skills": [],
                "extra_skills": []
            },
            "experience_match": {
                "score": 0,
                "analysis": ""
            },
            "education_match": {
                "score": 0,
                "analysis": ""
            },
            "keyword_match": {
                "score": 0,
                "matched_keywords": [],
                "total_keywords": 0
            },
            "ai_analysis": None,
            "recommendations": []
        }
        
        # 提取岗位需求关键词
        job_keywords = self._extract_job_keywords(job_description)
        resume_keywords = self._extract_resume_keywords(resume_text)
        
        # 计算技能匹配
        skill_result = self._calculate_skill_match(resume_keywords, job_keywords)
        result["skill_match"] = skill_result
        
        # 计算关键词匹配
        keyword_result = self._calculate_keyword_match(resume_text, job_keywords)
        result["keyword_match"] = keyword_result
        
        # 计算经验匹配
        if extracted_info:
            experience_result = self._calculate_experience_match(
                extracted_info.get("optional_info", {}),
                job_description
            )
            result["experience_match"] = experience_result
            
            education_result = self._calculate_education_match(
                extracted_info.get("optional_info", {}),
                job_description
            )
            result["education_match"] = education_result
        
        # 计算文本相似度
        similarity_score = self._calculate_text_similarity(resume_text, job_description)
        
        # 如果配置了 AI，使用 AI 进行深度分析
        if self.use_ai:
            try:
                ai_analysis = self._analyze_with_ai(resume_text, job_description)
                if ai_analysis:
                    result["ai_analysis"] = ai_analysis
            except Exception as e:
                logger.warning(f"AI 分析失败: {str(e)}")
        
        # 计算综合得分
        weights = {
            "skill": 0.35,
            "keyword": 0.20,
            "experience": 0.20,
            "education": 0.10,
            "similarity": 0.15
        }
        
        overall_score = (
            result["skill_match"]["score"] * weights["skill"] +
            result["keyword_match"]["score"] * weights["keyword"] +
            result["experience_match"]["score"] * weights["experience"] +
            result["education_match"]["score"] * weights["education"] +
            similarity_score * weights["similarity"]
        )
        
        result["overall_score"] = round(overall_score, 1)
        result["text_similarity_score"] = round(similarity_score, 1)
        
        # 生成建议
        result["recommendations"] = self._generate_recommendations(result)
        
        return result
    
    def _extract_job_keywords(self, job_description: str) -> Dict[str, List[str]]:
        """提取岗位需求关键词"""
        keywords = {
            "required_skills": [],
            "preferred_skills": [],
            "experience_requirement": None,
            "education_requirement": None,
            "other_keywords": []
        }
        
        text_lower = job_description.lower()
        
        # 提取技能要求
        for category, skills in self.skill_categories.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    keywords["required_skills"].append(skill)
        
        # 提取经验要求
        exp_patterns = [
            r"(\d+)[年\s]*(?:以上)?(?:工作)?经[验历]",
            r"(?:要求|需要)(\d+)[年]"
        ]
        for pattern in exp_patterns:
            match = re.search(pattern, job_description)
            if match:
                keywords["experience_requirement"] = int(match.group(1))
                break
        
        # 提取学历要求
        edu_levels = {
            "博士": 5,
            "硕士": 4,
            "本科": 3,
            "大专": 2,
            "专科": 2
        }
        for edu, level in edu_levels.items():
            if edu in job_description:
                keywords["education_requirement"] = edu
                break
        
        return keywords
    
    def _extract_resume_keywords(self, resume_text: str) -> List[str]:
        """提取简历关键词"""
        keywords = []
        text_lower = resume_text.lower()
        
        for category, skills in self.skill_categories.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    keywords.append(skill)
        
        return list(set(keywords))
    
    def _calculate_skill_match(self, resume_skills: List[str], job_keywords: Dict) -> Dict:
        """计算技能匹配度"""
        required_skills = set(s.lower() for s in job_keywords.get("required_skills", []))
        resume_skills_lower = set(s.lower() for s in resume_skills)
        
        if not required_skills:
            return {
                "score": 70,  # 如果没有明确要求，给个基础分
                "matched_skills": list(resume_skills_lower),
                "missing_skills": [],
                "extra_skills": []
            }
        
        matched = required_skills.intersection(resume_skills_lower)
        missing = required_skills - resume_skills_lower
        extra = resume_skills_lower - required_skills
        
        # 计算加权得分
        total_weight = 0
        matched_weight = 0
        
        for skill in required_skills:
            weight = self._get_skill_weight(skill)
            total_weight += weight
            if skill in matched:
                matched_weight += weight
        
        score = (matched_weight / total_weight * 100) if total_weight > 0 else 0
        
        return {
            "score": round(score, 1),
            "matched_skills": list(matched),
            "missing_skills": list(missing),
            "extra_skills": list(extra)
        }
    
    def _get_skill_weight(self, skill: str) -> float:
        """获取技能权重"""
        skill_lower = skill.lower()
        for category, skills in self.skill_categories.items():
            if skill_lower in [s.lower() for s in skills]:
                return self.skill_weights.get(category, 0.5)
        return 0.5
    
    def _calculate_keyword_match(self, resume_text: str, job_keywords: Dict) -> Dict:
        """计算关键词匹配度"""
        all_keywords = (
            job_keywords.get("required_skills", []) +
            job_keywords.get("preferred_skills", []) +
            job_keywords.get("other_keywords", [])
        )
        
        if not all_keywords:
            return {
                "score": 70,
                "matched_keywords": [],
                "total_keywords": 0
            }
        
        resume_lower = resume_text.lower()
        matched = [kw for kw in all_keywords if kw.lower() in resume_lower]
        
        score = (len(matched) / len(all_keywords) * 100) if all_keywords else 0
        
        return {
            "score": round(score, 1),
            "matched_keywords": matched,
            "total_keywords": len(all_keywords)
        }
    
    def _calculate_experience_match(self, optional_info: Dict, job_description: str) -> Dict:
        """计算经验匹配度"""
        resume_exp = optional_info.get("experience_years", "")
        
        # 提取数字
        resume_years = 0
        if resume_exp:
            match = re.search(r"(\d+)", str(resume_exp))
            if match:
                resume_years = int(match.group(1))
        
        # 从岗位描述提取要求
        required_years = 0
        exp_patterns = [
            r"(\d+)[年\s]*(?:以上)?(?:工作)?经[验历]",
            r"(?:要求|需要)(\d+)[年]"
        ]
        for pattern in exp_patterns:
            match = re.search(pattern, job_description)
            if match:
                required_years = int(match.group(1))
                break
        
        if required_years == 0:
            return {"score": 80, "analysis": "岗位未明确经验要求"}
        
        if resume_years >= required_years:
            score = 100
            analysis = f"满足经验要求（要求{required_years}年，实际{resume_years}年）"
        elif resume_years >= required_years * 0.7:
            score = 70
            analysis = f"基本满足经验要求（要求{required_years}年，实际{resume_years}年）"
        else:
            score = max(30, resume_years / required_years * 100)
            analysis = f"经验略有不足（要求{required_years}年，实际{resume_years}年）"
        
        return {"score": round(score, 1), "analysis": analysis}
    
    def _calculate_education_match(self, optional_info: Dict, job_description: str) -> Dict:
        """计算学历匹配度"""
        edu_levels = {
            "博士": 5,
            "硕士研究生": 4,
            "硕士": 4,
            "本科": 3,
            "学士": 3,
            "大专": 2,
            "专科": 2,
            "高中": 1
        }
        
        resume_edu = optional_info.get("education", "")
        resume_level = 0
        for edu, level in edu_levels.items():
            if edu in str(resume_edu):
                resume_level = level
                break
        
        # 从岗位描述提取要求
        required_level = 0
        required_edu = ""
        for edu, level in edu_levels.items():
            if edu in job_description:
                required_level = level
                required_edu = edu
                break
        
        if required_level == 0:
            return {"score": 80, "analysis": "岗位未明确学历要求"}
        
        if resume_level >= required_level:
            score = 100
            analysis = f"满足学历要求（要求{required_edu}，实际{resume_edu}）"
        elif resume_level == required_level - 1:
            score = 70
            analysis = f"学历略低于要求（要求{required_edu}，实际{resume_edu}）"
        else:
            score = 40
            analysis = f"学历不满足要求（要求{required_edu}，实际{resume_edu}）"
        
        return {"score": round(score, 1), "analysis": analysis}
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（使用 TF-IDF + 余弦相似度）"""
        # 简单的词频统计
        def tokenize(text):
            # 中文分词（简单版本）
            words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text.lower())
            return words
        
        words1 = tokenize(text1)
        words2 = tokenize(text2)
        
        if not words1 or not words2:
            return 0
        
        # 计算词频
        counter1 = Counter(words1)
        counter2 = Counter(words2)
        
        # 获取所有词汇
        all_words = set(counter1.keys()) | set(counter2.keys())
        
        # 计算向量
        vec1 = [counter1.get(word, 0) for word in all_words]
        vec2 = [counter2.get(word, 0) for word in all_words]
        
        # 计算余弦相似度
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        similarity = dot_product / (norm1 * norm2)
        return similarity * 100
    
    def _analyze_with_ai(self, resume_text: str, job_description: str) -> Dict:
        """使用 AI 进行深度匹配分析"""
        try:
            import http.client
            
            prompt = f"""请分析以下简历与岗位的匹配度：

岗位描述：
{job_description[:1500]}

简历内容：
{resume_text[:2000]}

请以 JSON 格式返回分析结果：
{{
    "match_score": 0-100的匹配分数,
    "strengths": ["优势1", "优势2", ...],
    "weaknesses": ["不足1", "不足2", ...],
    "suggestions": ["建议1", "建议2", ...],
    "summary": "简要总结"
}}

只返回 JSON，不要其他内容。"""

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
                json_match = re.search(r"\{[\s\S]*\}", content)
                if json_match:
                    return json.loads(json_match.group())
            
            return None
            
        except Exception as e:
            logger.error(f"AI 分析失败: {str(e)}")
            return None
    
    def _generate_recommendations(self, result: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于技能匹配生成建议
        skill_match = result.get("skill_match", {})
        missing_skills = skill_match.get("missing_skills", [])
        if missing_skills:
            recommendations.append(f"建议补充以下技能：{', '.join(missing_skills[:5])}")
        
        # 基于经验匹配生成建议
        exp_match = result.get("experience_match", {})
        if exp_match.get("score", 100) < 70:
            recommendations.append("建议在简历中更详细地描述相关工作经验")
        
        # 基于学历匹配生成建议
        edu_match = result.get("education_match", {})
        if edu_match.get("score", 100) < 70:
            recommendations.append("建议突出相关培训或认证经历")
        
        # 基于综合得分生成建议
        overall_score = result.get("overall_score", 0)
        if overall_score < 60:
            recommendations.append("整体匹配度较低，建议根据岗位要求调整简历内容")
        elif overall_score < 80:
            recommendations.append("匹配度中等，建议针对岗位要求优化简历亮点")
        
        # 从 AI 分析中提取建议
        ai_analysis = result.get("ai_analysis")
        if ai_analysis and "suggestions" in ai_analysis:
            for suggestion in ai_analysis["suggestions"][:3]:
                if suggestion not in recommendations:
                    recommendations.append(suggestion)
        
        return recommendations[:5]  # 最多返回5条建议

