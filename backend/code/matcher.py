# -*- coding: utf-8 -*-
"""
简历与岗位匹配评分模块 - 优化版（支持 AI 分析）
"""
import re
import math
import os
import json
import logging
import http.client
from collections import Counter

logger = logging.getLogger(__name__)


class ResumeMatcher:
    """简历匹配器"""
    
    def __init__(self):
        # 检查是否配置了 AI API
        self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        self.use_ai = bool(self.api_key)
        if self.use_ai:
            logger.info("AI 分析功能已启用（DashScope）")
        else:
            logger.info("AI 分析功能未启用，使用传统匹配算法")
        
        # 扩展技能关键词库
        self.skill_keywords = [
            # 编程语言
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "php", "ruby",
            "swift", "kotlin", "scala", "r语言", "perl", "lua",
            # 前端框架
            "react", "vue", "angular", "node.js", "node", "jquery", "bootstrap",
            # 后端框架
            "spring", "springboot", "django", "flask", "fastapi", "express", "laravel", "rails",
            "mybatis", "hibernate", "struts",
            # 数据库
            "mysql", "postgresql", "mongodb", "redis", "oracle", "sql server", "sqlite",
            "elasticsearch", "hbase", "cassandra", "neo4j",
            # 工具和平台
            "docker", "kubernetes", "k8s", "aws", "azure", "gcp", "阿里云", "腾讯云",
            "linux", "git", "jenkins", "ci/cd", "nginx", "apache",
            # AI/ML
            "机器学习", "深度学习", "tensorflow", "pytorch", "keras", "scikit-learn",
            "nlp", "自然语言处理", "计算机视觉", "cnn", "rnn", "lstm", "transformer",
            # 其他
            "restful", "graphql", "microservices", "微服务", "分布式", "高并发"
        ]
        
        # 岗位描述关键词（用于判断描述是否有效）
        self.job_keywords = [
            "岗位", "职位", "招聘", "要求", "职责", "工作", "经验", "学历", "技能",
            "开发", "工程师", "经理", "主管", "专员", "助理", "负责", "参与",
            "熟悉", "掌握", "了解", "精通", "具备", "拥有"
        ]
    
    def match(self, resume_text, job_description, extracted_info=None):
        """计算简历与岗位的匹配度"""
        
        # 验证岗位描述有效性
        job_validity = self._validate_job_description(job_description)
        if not job_validity["valid"]:
            return {
                "overall_score": 0,
                "skill_match": {
                    "score": 0,
                    "matched_skills": [],
                    "missing_skills": [],
                    "extra_skills": []
                },
                "experience_match": {
                    "score": 0,
                    "analysis": job_validity["reason"]
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
                "text_similarity_score": 0,
                "recommendations": [job_validity["reason"]],
                "ai_analysis": None
            }
        
        # 提取技能
        resume_skills = self._extract_skills(resume_text)
        job_skills = self._extract_skills(job_description)
        
        # 计算技能匹配
        skill_result = self._calc_skill_match(resume_skills, job_skills)
        
        # 计算文本相似度（改进版）
        similarity = self._calc_similarity_improved(resume_text, job_description)
        
        # 计算经验匹配
        exp_result = {"score": 70, "analysis": "未检测到明确经验要求"}
        if extracted_info:
            exp_result = self._calc_experience_match(
                extracted_info.get("optional_info", {}),
                job_description
            )
        
        # 计算学历匹配
        edu_result = self._calc_education_match(
            extracted_info.get("optional_info", {}) if extracted_info else {},
            job_description
        )
        
        # 计算关键词匹配
        keyword_result = self._calc_keyword_match(resume_text, job_description)
        
        # AI 分析（如果可用）
        ai_result = None
        ai_score = None
        if self.use_ai:
            try:
                ai_result = self._ai_analyze_match(
                    resume_text, 
                    job_description, 
                    extracted_info,
                    skill_result,
                    exp_result,
                    edu_result
                )
                if ai_result and "score" in ai_result:
                    ai_score = ai_result["score"]
                    logger.info(f"AI 分析完成，评分: {ai_score}")
            except Exception as e:
                logger.error(f"AI 分析失败: {str(e)}", exc_info=True)
                ai_result = {"error": str(e)}
        
        # 综合评分（调整权重）
        if ai_score is not None:
            # 如果 AI 分析可用，使用 AI 评分作为主要参考，传统算法作为辅助
            overall = (
                ai_score * 0.50 +  # AI 评分权重 50%
                skill_result["score"] * 0.20 +
                similarity * 0.15 +
                exp_result["score"] * 0.08 +
                edu_result["score"] * 0.05 +
                keyword_result["score"] * 0.02
            )
        else:
            # 传统算法评分
            overall = (
                skill_result["score"] * 0.35 +
                similarity * 0.25 +
                exp_result["score"] * 0.15 +
                edu_result["score"] * 0.10 +
                keyword_result["score"] * 0.15
            )
        
        # 如果岗位描述中没有提取到任何技能，降低评分
        if not job_skills and len(job_description.strip()) < 50:
            overall = overall * 0.5
        
        return {
            "overall_score": round(overall, 1),
            "skill_match": skill_result,
            "experience_match": exp_result,
            "education_match": edu_result,
            "keyword_match": keyword_result,
            "text_similarity_score": round(similarity, 1),
            "recommendations": self._generate_recommendations(skill_result, exp_result, overall, job_skills, ai_result),
            "ai_analysis": ai_result
        }
    
    def _validate_job_description(self, job_desc):
        """验证岗位描述是否有效"""
        if not job_desc or not job_desc.strip():
            return {"valid": False, "reason": "岗位描述为空"}
        
        job_desc = job_desc.strip()
        
        # 检查长度
        if len(job_desc) < 10:
            return {"valid": False, "reason": "岗位描述过短，请提供更详细的岗位要求"}
        
        # 检查是否全是数字或特殊字符
        if re.match(r'^[\d\s\W]+$', job_desc):
            return {"valid": False, "reason": "岗位描述无效，请提供有意义的文字描述"}
        
        # 检查是否包含有效关键词
        has_keywords = any(kw in job_desc for kw in self.job_keywords)
        has_skills = any(skill in job_desc.lower() for skill in self.skill_keywords[:20])  # 检查前20个常见技能
        
        # 如果既没有关键词也没有技能，但长度足够，可能是有效描述
        if len(job_desc) > 30 and (has_keywords or has_skills):
            return {"valid": True, "reason": ""}
        elif len(job_desc) > 50:
            # 长度足够，即使没有关键词也认为可能有效
            return {"valid": True, "reason": ""}
        else:
            return {"valid": False, "reason": "岗位描述内容不足，请提供更详细的岗位要求、技能要求等信息"}
    
    def _extract_skills(self, text):
        """提取技能"""
        text_lower = text.lower()
        found = []
        for skill in self.skill_keywords:
            # 使用单词边界匹配，避免误匹配
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.append(skill)
        return found
    
    def _calc_skill_match(self, resume_skills, job_skills):
        """计算技能匹配度"""
        if not job_skills:
            return {
                "score": 50,  # 没有技能要求时给中等分
                "matched_skills": resume_skills,
                "missing_skills": [],
                "extra_skills": []
            }
        
        resume_set = set(resume_skills)
        job_set = set(job_skills)
        
        matched = resume_set & job_set
        missing = job_set - resume_set
        extra = resume_set - job_set
        
        # 计算匹配度：匹配的技能数 / 要求的技能数
        score = len(matched) / len(job_set) * 100 if job_set else 50
        
        return {
            "score": round(score, 1),
            "matched_skills": list(matched),
            "missing_skills": list(missing),
            "extra_skills": list(extra)
        }
    
    def _calc_similarity_improved(self, text1, text2):
        """改进的文本相似度计算"""
        def tokenize(text):
            # 提取中文词和英文词
            words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]{2,}', text.lower())
            # 过滤掉纯数字和单个字符
            words = [w for w in words if not w.isdigit() and len(w) > 1]
            return words
        
        words1 = tokenize(text1)
        words2 = tokenize(text2)
        
        if not words1 or not words2:
            return 0  # 如果一方没有有效词汇，相似度为0
        
        # 如果一方词汇太少，可能是无效输入
        if len(words2) < 3:
            return 0
        
        c1 = Counter(words1)
        c2 = Counter(words2)
        
        all_words = set(c1.keys()) | set(c2.keys())
        
        v1 = [c1.get(w, 0) for w in all_words]
        v2 = [c2.get(w, 0) for w in all_words]
        
        dot = sum(a * b for a, b in zip(v1, v2))
        n1 = math.sqrt(sum(a * a for a in v1))
        n2 = math.sqrt(sum(b * b for b in v2))
        
        if n1 == 0 or n2 == 0:
            return 0
        
        similarity = dot / (n1 * n2) * 100
        
        # 如果相似度异常高但词汇差异很大，可能是巧合，降低分数
        if similarity > 80 and len(set(words1) & set(words2)) < len(words2) * 0.3:
            similarity = similarity * 0.7
        
        return round(similarity, 1)
    
    def _calc_keyword_match(self, resume_text, job_desc):
        """计算关键词匹配"""
        # 提取岗位描述中的关键词
        job_keywords = self._extract_keywords(job_desc)
        resume_keywords = self._extract_keywords(resume_text)
        
        if not job_keywords:
            return {
                "score": 50,
                "matched_keywords": [],
                "total_keywords": 0
            }
        
        matched = set(job_keywords) & set(resume_keywords)
        score = len(matched) / len(job_keywords) * 100 if job_keywords else 50
        
        return {
            "score": round(score, 1),
            "matched_keywords": list(matched),
            "total_keywords": len(job_keywords)
        }
    
    def _extract_keywords(self, text):
        """提取关键词（技能、技术栈、工具等）"""
        keywords = []
        text_lower = text.lower()
        
        # 提取技能关键词
        for skill in self.skill_keywords:
            if skill in text_lower:
                keywords.append(skill)
        
        # 提取其他常见关键词
        common_keywords = [
            "开发", "设计", "测试", "运维", "管理", "分析", "优化",
            "项目", "团队", "沟通", "协作", "学习", "创新"
        ]
        for kw in common_keywords:
            if kw in text:
                keywords.append(kw)
        
        return list(set(keywords))
    
    def _calc_experience_match(self, optional_info, job_desc):
        """计算经验匹配"""
        resume_exp = optional_info.get("experience_years", "")
        
        resume_years = 0
        if resume_exp:
            m = re.search(r"(\d+)", str(resume_exp))
            if m:
                resume_years = int(m.group(1))
        
        # 从岗位描述提取要求
        required = 0
        patterns = [
            r"(\d+)\s*年[以上]*[工作]*经[验历]",
            r"(\d+)\+?\s*年",
            r"经[验历][：:\s]*(\d+)\s*年"
        ]
        for pattern in patterns:
            m = re.search(pattern, job_desc)
            if m:
                required = int(m.group(1))
                break
        
        if required == 0:
            return {"score": 70, "analysis": "岗位未明确经验要求"}
        
        if resume_years >= required:
            return {"score": 100, "analysis": f"满足经验要求（{resume_years}年 >= {required}年）"}
        elif resume_years >= required * 0.7:
            return {"score": 70, "analysis": f"基本满足（{resume_years}年 / {required}年）"}
        else:
            score = max(30, resume_years / required * 100)
            return {"score": round(score, 1), "analysis": f"经验不足（{resume_years}年 < {required}年）"}
    
    def _calc_education_match(self, optional_info, job_desc):
        """计算学历匹配"""
        resume_edu = optional_info.get("education", "")
        
        edu_levels = {
            "博士": 5, "硕士": 4, "研究生": 4, "本科": 3, "学士": 3,
            "大专": 2, "专科": 2, "高中": 1
        }
        
        resume_level = 0
        for edu, level in edu_levels.items():
            if edu in str(resume_edu):
                resume_level = level
                break
        
        # 从岗位描述提取要求
        required_level = 0
        required_edu = ""
        for edu, level in edu_levels.items():
            if edu in job_desc:
                required_level = level
                required_edu = edu
                break
        
        if required_level == 0:
            return {"score": 70, "analysis": "岗位未明确学历要求"}
        
        if resume_level >= required_level:
            return {"score": 100, "analysis": f"满足学历要求（要求{required_edu}，实际{resume_edu or '未识别'}）"}
        elif resume_level == required_level - 1:
            return {"score": 60, "analysis": f"学历略低于要求（要求{required_edu}，实际{resume_edu or '未识别'}）"}
        else:
            return {"score": 30, "analysis": f"学历不满足要求（要求{required_edu}，实际{resume_edu or '未识别'}）"}
    
    def _generate_recommendations(self, skill_result, exp_result, overall, job_skills, ai_result=None):
        """生成改进建议"""
        recs = []
        
        # 优先使用 AI 建议
        if ai_result and "recommendations" in ai_result:
            ai_recs = ai_result["recommendations"]
            if isinstance(ai_recs, list):
                recs.extend(ai_recs[:3])  # 使用 AI 的前3条建议
            elif isinstance(ai_recs, str):
                recs.append(ai_recs)
        
        # 技能相关建议
        missing = skill_result.get("missing_skills", [])
        if missing:
            recs.append(f"建议补充以下技能：{', '.join(missing[:5])}")
        
        matched = skill_result.get("matched_skills", [])
        if matched:
            recs.append(f"已匹配的技能：{', '.join(matched[:5])}")
        
        # 经验相关建议
        if exp_result.get("score", 100) < 70:
            recs.append("建议在简历中更详细地描述相关工作经验")
        
        # 综合评分建议
        if overall < 40:
            recs.append("整体匹配度较低，建议根据岗位要求调整简历内容，突出相关技能和经验")
        elif overall < 60:
            recs.append("匹配度中等，建议针对岗位要求优化简历，突出匹配的技能和项目经验")
        elif overall < 80:
            recs.append("匹配度良好，建议进一步突出核心技能和项目亮点")
        else:
            recs.append("简历与岗位匹配度较高，继续保持")
        
        # 如果岗位没有明确技能要求
        if not job_skills:
            recs.append("提示：岗位描述中未检测到明确的技能要求，建议提供更详细的岗位描述以获得更精准的匹配分析")
        
        return recs[:5]  # 最多返回5条建议
    
    def _ai_analyze_match(self, resume_text, job_description, extracted_info, skill_result, exp_result, edu_result):
        """使用 AI 模型分析简历与岗位的匹配度"""
        if not self.api_key:
            return None
        
        try:
            # 构建提示词
            prompt = self._build_ai_prompt(resume_text, job_description, extracted_info, skill_result, exp_result, edu_result)
            
            # 调用 DashScope API
            response = self._call_dashscope_api(prompt)
            
            if response:
                # 解析 AI 返回结果
                return self._parse_ai_response(response)
            else:
                return None
                
        except Exception as e:
            logger.error(f"AI 分析异常: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    def _build_ai_prompt(self, resume_text, job_description, extracted_info, skill_result, exp_result, edu_result):
        """构建 AI 分析提示词"""
        # 提取关键信息摘要
        basic_info = extracted_info.get("basic_info", {}) if extracted_info else {}
        optional_info = extracted_info.get("optional_info", {}) if extracted_info else {}
        
        prompt = f"""你是一位专业的 HR 招聘专家，请对以下简历与岗位的匹配度进行深度分析。

## 岗位要求：
{job_description}

## 简历信息：

### 基本信息：
- 姓名：{basic_info.get('name', '未识别')}
- 电话：{basic_info.get('phone', '未识别')}
- 邮箱：{basic_info.get('email', '未识别')}
- 地址：{basic_info.get('address', '未识别')}

### 其他信息：
- 求职意向：{optional_info.get('job_intention', '未识别')}
- 工作年限：{optional_info.get('experience_years', '未识别')}
- 学历：{optional_info.get('education', '未识别')}

### 技能匹配情况：
- 已匹配技能：{', '.join(skill_result.get('matched_skills', [])[:10])}
- 缺失技能：{', '.join(skill_result.get('missing_skills', [])[:10])}

### 经验匹配：{exp_result.get('analysis', '未分析')}
### 学历匹配：{edu_result.get('analysis', '未分析')}

### 完整简历文本（前2000字）：
{resume_text[:2000]}

## 分析任务：

请从以下维度进行专业分析，并给出 0-100 的匹配度评分：

1. **技能匹配度**：简历中的技能是否满足岗位要求
2. **经验匹配度**：工作经验和项目经历是否与岗位需求相关
3. **学历匹配度**：学历背景是否符合岗位要求
4. **综合匹配度**：整体评估简历与岗位的匹配程度

请以 JSON 格式返回分析结果，格式如下：
{{
    "score": 85,
    "skill_analysis": "技能匹配度分析...",
    "experience_analysis": "经验匹配度分析...",
    "education_analysis": "学历匹配度分析...",
    "overall_analysis": "综合匹配度分析...",
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["不足1", "不足2"],
    "recommendations": ["建议1", "建议2", "建议3"]
}}

请确保返回的是有效的 JSON 格式，不要包含任何其他文字说明。"""
        
        return prompt
    
    def _call_dashscope_api(self, prompt):
        """调用 DashScope API"""
        try:
            conn = http.client.HTTPSConnection("dashscope.aliyuncs.com")
            
            payload = json.dumps({
                "model": "qwen-turbo",
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                "parameters": {
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            })
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            conn.request("POST", "/api/v1/services/aigc/text-generation/generation", payload, headers)
            res = conn.getresponse()
            data = res.read()
            
            if res.status == 200:
                result = json.loads(data.decode("utf-8"))
                if "output" in result and "choices" in result["output"]:
                    content = result["output"]["choices"][0]["message"]["content"]
                    return content
                else:
                    logger.error(f"DashScope API 返回格式异常: {result}")
                    return None
            else:
                logger.error(f"DashScope API 调用失败: {res.status} - {data.decode('utf-8')}")
                return None
                
        except Exception as e:
            logger.error(f"调用 DashScope API 异常: {str(e)}", exc_info=True)
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _parse_ai_response(self, response_text):
        """解析 AI 返回的 JSON 结果"""
        try:
            # 尝试提取 JSON 部分（可能包含 markdown 代码块）
            text = response_text.strip()
            
            # 移除可能的 markdown 代码块标记
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            # 解析 JSON
            result = json.loads(text)
            
            # 验证必要字段
            if "score" not in result:
                logger.warning("AI 返回结果缺少 score 字段")
                return None
            
            # 确保 score 在 0-100 范围内
            score = float(result.get("score", 0))
            score = max(0, min(100, score))
            result["score"] = round(score, 1)
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"解析 AI 返回 JSON 失败: {str(e)}, 原始内容: {response_text[:200]}")
            # 尝试从文本中提取数字作为评分
            score_match = re.search(r'"score"\s*:\s*(\d+(?:\.\d+)?)', response_text)
            if score_match:
                score = float(score_match.group(1))
                score = max(0, min(100, score))
                return {
                    "score": round(score, 1),
                    "error": "JSON 解析失败，仅提取了评分",
                    "raw_response": response_text[:500]
                }
            return None
        except Exception as e:
            logger.error(f"解析 AI 响应异常: {str(e)}")
            return None
