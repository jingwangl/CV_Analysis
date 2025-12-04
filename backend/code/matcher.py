# -*- coding: utf-8 -*-
"""
简历与岗位匹配评分模块
"""
import re
import math
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class ResumeMatcher:
    """简历匹配器"""
    
    def __init__(self):
        # 扩展技能关键词库
        self.skill_keywords = [
            # 编程语言（按常见度排序，优先匹配）
            "java", "python", "go", "c++", "javascript", "typescript", "c#", "rust", "php", "ruby",
            "swift", "kotlin", "scala", "r语言", "perl", "lua",
            # 前端框架
            "react", "vue", "angular", "node.js", "node", "jquery", "bootstrap",
            # 后端框架
            "spring", "springboot", "django", "flask", "fastapi", "express", "laravel", "rails",
            "mybatis", "hibernate", "struts",
            # 数据库
            "mysql", "oracle", "postgresql", "mongodb", "redis", "sql server", "sqlite",
            "elasticsearch", "hbase", "cassandra", "neo4j"
            # 工具和平台
            "docker", "kubernetes", "k8s", "aws", "azure", "gcp", "阿里云", "腾讯云",
            "linux", "git", "jenkins", "ci/cd", "nginx", "apache",
            # 网络协议和技术
            "tcp/ip", "tcp", "http", "https", "websocket", "grpc",
            # 系统和技术概念
            "多线程", "网络编程", "jvm", "sql优化", "性能优化",
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
                "text_similarity_score": 0,
                "recommendations": [job_validity["reason"]]
            }
        
        # 提取技能
        resume_skills_from_text = self._extract_skills(resume_text)
        job_skills = self._extract_skills(job_description)
        
        # 如果 extracted_info 中有技能信息，优先使用（格式可能不同）
        resume_skills_from_info = []
        if extracted_info and "skills" in extracted_info:
            resume_skills_from_info = extracted_info["skills"]
            if isinstance(resume_skills_from_info, list):
                # 标准化技能名称（转为小写）
                resume_skills_from_info = [s.lower() if isinstance(s, str) else str(s).lower() for s in resume_skills_from_info]
        
        # 合并两个来源的技能，去重
        all_resume_skills = list(set(resume_skills_from_text + resume_skills_from_info))
        
        # 记录提取的技能（用于调试）
        logger.info(f"从岗位描述中提取到技能: {job_skills} (共{len(job_skills)}个)")
        logger.info(f"从简历文本中提取到技能: {resume_skills_from_text} (共{len(resume_skills_from_text)}个)")
        logger.info(f"从简历信息中提取到技能: {resume_skills_from_info} (共{len(resume_skills_from_info)}个)")
        logger.info(f"合并后的简历技能: {all_resume_skills} (共{len(all_resume_skills)}个)")
        
        # 计算技能匹配
        skill_result = self._calc_skill_match(all_resume_skills, job_skills)
        
        # 详细记录匹配过程
        logger.info(f"技能匹配结果: 匹配={skill_result.get('matched_skills', [])}, 缺失={skill_result.get('missing_skills', [])}, 额外={skill_result.get('extra_skills', [])}")
        
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
        
        # 综合评分（移除关键词匹配，权重重新分配）
        overall = (
            skill_result["score"] * 0.45 +      # 技能匹配权重提升：35% → 45%
            similarity * 0.30 +                  # 文本相似度权重提升：25% → 30%
            exp_result["score"] * 0.15 +        # 经验匹配：15%（不变）
            edu_result["score"] * 0.10           # 学历匹配：10%（不变）
        )
        
        # 如果岗位描述中没有提取到任何技能，降低评分
        if not job_skills and len(job_description.strip()) < 50:
            overall = overall * 0.5
        
        return {
            "overall_score": round(overall, 1),
            "skill_match": skill_result,
            "experience_match": exp_result,
            "education_match": edu_result,
            "text_similarity_score": round(similarity, 1),
            "recommendations": self._generate_recommendations(skill_result, exp_result, overall, job_skills)
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
        """提取技能（改进版，支持中文标点和特殊格式）"""
        if not text:
            return []
        
        # 预处理文本：将中文标点和连接词替换为空格，便于匹配
        text_lower = text.lower()
        # 替换常见的中文标点和连接词为空格（包括中文顿号、逗号等）
        text_normalized = re.sub(r'[、，,；;或|等]', ' ', text_lower)
        # 移除多余空格，但保留单个空格
        text_normalized = re.sub(r'\s+', ' ', text_normalized)
        
        # 调试：记录处理后的文本片段
        if len(text_normalized) > 0:
            logger.debug(f"技能提取 - 原始文本片段: {text[:200]}")
            logger.debug(f"技能提取 - 标准化后文本片段: {text_normalized[:200]}")
        
        found = []
        found_positions = {}  # 记录已找到的技能位置，避免重复
        
        # 按长度从长到短排序，优先匹配长技能（如 "tcp/ip" 应该在 "tcp" 之前）
        sorted_skills = sorted(self.skill_keywords, key=lambda x: len(x), reverse=True)
        
        for skill in sorted_skills:
            # 跳过已找到的技能（避免重复）
            if skill in found:
                continue
            
            skill_lower = skill.lower()
            skill_escaped = re.escape(skill_lower)
            
            # 构建匹配模式
            # 对于包含特殊字符的技能（如 c++, c#, tcp/ip），使用精确匹配
            if '+' in skill or '#' in skill or '/' in skill:
                # 特殊字符技能：在标点符号或空格前后都可以匹配
                # 例如：匹配 "c++"、"C++"、"c++，"、" c++ " 等
                # 注意：对于 "tcp/ip"，需要匹配 "tcp/ip" 或 "tcp ip" 或 "tcpip"
                if '/' in skill:
                    # 对于 tcp/ip，也匹配 tcp ip 或 tcpip
                    parts = skill.split('/')
                    pattern = r'(?:^|[\s、，,；;或|])' + re.escape(parts[0].lower()) + r'[\s/]*' + re.escape(parts[1].lower()) + r'(?:[\s、，,；;或|]|$)'
                else:
                    pattern = r'(?:^|[\s、，,；;或|])' + skill_escaped + r'(?:[\s、，,；;或|]|$)'
            elif re.match(r'^[a-zA-Z0-9]+$', skill):
                # 纯字母数字技能：使用单词边界
                # 在标准化文本中，单词边界应该能正确匹配
                # 但为了更可靠，也在标点符号前后匹配
                pattern = r'(?:^|\b|[\s、，,；;或|])' + skill_escaped + r'(?:\b|[\s、，,；;或|]|$)'
            else:
                # 中文技能或其他：直接匹配
                pattern = skill_escaped
            
            # 在标准化文本中搜索（已处理标点符号）
            matches = list(re.finditer(pattern, text_normalized, re.IGNORECASE))
            
            # 如果没找到，也在原始小写文本中搜索（处理一些边界情况）
            if not matches:
                matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
            
            # 处理匹配结果
            for match in matches:
                start, end = match.span()
                # 检查是否与已找到的技能重叠（如果新技能更长，替换旧的）
                overlap = False  # 初始化 overlap 变量
                overlap_skills = []
                for existing_skill, (existing_start, existing_end) in found_positions.items():
                    if not (end <= existing_start or start >= existing_end):
                        # 如果新技能更长，替换旧技能
                        if len(skill) > len(existing_skill):
                            overlap_skills.append(existing_skill)
                        else:
                            overlap = True
                            break
                
                if not overlap:
                    # 移除被替换的技能
                    for old_skill in overlap_skills:
                        if old_skill in found:
                            found.remove(old_skill)
                        if old_skill in found_positions:
                            del found_positions[old_skill]
                    
                    found.append(skill)
                    found_positions[skill] = (start, end)
                    break  # 每个技能只记录一次
        
        # 去重并保持顺序
        seen = set()
        result = []
        for skill in found:
            if skill not in seen:
                seen.add(skill)
                result.append(skill)
        
        return result
    
    def _calc_skill_match(self, resume_skills, job_skills):
        """计算技能匹配度（标准化技能名称后匹配）"""
        if not job_skills:
            return {
                "score": 50,  # 没有技能要求时给中等分
                "matched_skills": resume_skills,
                "missing_skills": [],
                "extra_skills": []
            }
        
        # 标准化技能名称：全部转为小写，去除空格，处理等价技能
        def normalize_skill(skill):
            if not isinstance(skill, str):
                skill = str(skill)
            skill = skill.lower().strip()
            # 处理等价技能：tcp/ip 和 tcp 等价，http 和 https 不等价但可以关联
            # 将 tcp/ip 标准化为 tcp（因为如果会 tcp/ip，肯定也会 tcp）
            if skill == "tcp/ip":
                return "tcp"
            return skill
        
        # 创建标准化映射，同时保留原始技能
        resume_normalized = [normalize_skill(s) for s in resume_skills]
        job_normalized = [normalize_skill(s) for s in job_skills]
        
        # 创建反向映射：标准化技能 -> 原始技能列表
        resume_normalized_to_original = {}
        for orig, norm in zip(resume_skills, resume_normalized):
            if norm not in resume_normalized_to_original:
                resume_normalized_to_original[norm] = []
            resume_normalized_to_original[norm].append(orig)
        
        job_normalized_to_original = {}
        for orig, norm in zip(job_skills, job_normalized):
            if norm not in job_normalized_to_original:
                job_normalized_to_original[norm] = []
            job_normalized_to_original[norm].append(orig)
        
        # 使用标准化后的技能进行匹配
        resume_set = set(resume_normalized)
        job_set = set(job_normalized)
        
        # 详细日志：显示标准化后的技能
        logger.info(f"标准化后的简历技能: {resume_set}")
        logger.info(f"标准化后的岗位技能: {job_set}")
        
        matched_normalized = resume_set & job_set
        missing_normalized = job_set - resume_set
        extra_normalized = resume_set - job_set
        
        logger.info(f"标准化后的匹配结果: 匹配={matched_normalized}, 缺失={missing_normalized}, 额外={extra_normalized}")
        
        # 将匹配结果映射回原始技能名称（保留原始格式）
        # 优先使用岗位描述中的原始格式，如果岗位中没有则使用简历中的
        matched_original = []
        for norm_skill in matched_normalized:
            # 优先使用岗位描述中的原始格式
            if norm_skill in job_normalized_to_original:
                matched_original.append(job_normalized_to_original[norm_skill][0])
            elif norm_skill in resume_normalized_to_original:
                matched_original.append(resume_normalized_to_original[norm_skill][0])
        
        missing_original = []
        for norm_skill in missing_normalized:
            if norm_skill in job_normalized_to_original:
                missing_original.append(job_normalized_to_original[norm_skill][0])
        
        extra_original = []
        for norm_skill in extra_normalized:
            if norm_skill in resume_normalized_to_original:
                extra_original.append(resume_normalized_to_original[norm_skill][0])
        
        # 计算匹配度：匹配的技能数 / 要求的技能数
        score = len(matched_normalized) / len(job_set) * 100 if job_set else 50
        
        logger.info(f"技能匹配详情: 匹配={matched_original}, 缺失={missing_original}, 额外={extra_original}")
        
        return {
            "score": round(score, 1),
            "matched_skills": matched_original,
            "missing_skills": missing_original,
            "extra_skills": extra_original
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
    
    def _generate_recommendations(self, skill_result, exp_result, overall, job_skills):
        """生成改进建议"""
        recs = []
        
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
