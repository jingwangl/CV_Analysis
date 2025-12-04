/**
 * CV Analysis - 智能简历分析系统
 * 前端交互脚本
 */

// API 配置 - 从 config.js 读取，如未定义则使用默认值
const API_BASE_URL = (typeof CONFIG !== 'undefined' && CONFIG.API_BASE_URL) 
    ? CONFIG.API_BASE_URL 
    : 'https://your-fc-endpoint.cn-hangzhou.fcapp.run';

// DOM 元素
const elements = {
    fileInput: document.getElementById('file-input'),
    uploadArea: document.getElementById('upload-area'),
    fileInfo: document.getElementById('file-info'),
    fileName: document.getElementById('file-name'),
    fileSize: document.getElementById('file-size'),
    removeFile: document.getElementById('remove-file'),
    analyzeBtn: document.getElementById('analyze-btn'),
    parsedSection: document.getElementById('parsed-section'),
    matchSection: document.getElementById('match-section'),
    scoreSection: document.getElementById('score-section'),
    jobDescription: document.getElementById('job-description'),
    matchBtn: document.getElementById('match-btn'),
    toastContainer: document.getElementById('toast-container'),
    steps: document.querySelectorAll('.step')
};

// 状态
let state = {
    selectedFile: null,
    parsedData: null,
    cacheKey: null
};

// 初始化
document.addEventListener('DOMContentLoaded', init);

function init() {
    setupUploadArea();
    setupButtons();
}

// 设置上传区域
function setupUploadArea() {
    const { uploadArea, fileInput } = elements;

    // 点击上传
    uploadArea.addEventListener('click', () => fileInput.click());

    // 文件选择
    fileInput.addEventListener('change', handleFileSelect);

    // 拖拽上传
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // 移除文件
    elements.removeFile.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFile();
    });
}

// 设置按钮
function setupButtons() {
    elements.analyzeBtn.addEventListener('click', handleAnalyze);
    elements.matchBtn.addEventListener('click', handleMatch);
}

// 处理文件选择
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

// 处理文件
function handleFile(file) {
    // 验证文件类型
    if (file.type !== 'application/pdf') {
        showToast('请上传 PDF 格式的文件', 'error');
        return;
    }

    // 验证文件大小 (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showToast('文件大小不能超过 10MB', 'error');
        return;
    }

    state.selectedFile = file;
    
    // 显示文件信息
    elements.fileName.textContent = file.name;
    elements.fileSize.textContent = formatFileSize(file.size);
    elements.fileInfo.style.display = 'flex';
    elements.uploadArea.style.display = 'none';
    elements.analyzeBtn.disabled = false;

    showToast('文件已选择，点击开始解析', 'info');
}

// 清除文件
function clearFile() {
    state.selectedFile = null;
    state.parsedData = null;
    state.cacheKey = null;
    
    elements.fileInput.value = '';
    elements.fileInfo.style.display = 'none';
    elements.uploadArea.style.display = 'block';
    elements.analyzeBtn.disabled = true;
    elements.parsedSection.style.display = 'none';
    elements.matchSection.style.display = 'none';
    elements.scoreSection.style.display = 'none';
    
    updateStep(1);
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// 处理解析
async function handleAnalyze() {
    if (!state.selectedFile) {
        showToast('请先选择文件', 'error');
        return;
    }

    const btn = elements.analyzeBtn;
    setButtonLoading(btn, true);

    try {
        // 读取文件为 Base64
        const base64Data = await readFileAsBase64(state.selectedFile);
        
        // 调用 API
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file: base64Data
            })
        });

        const result = await response.json();
        console.log('API 返回结果:', result);

        if (!response.ok) {
            throw new Error(result.error || `请求失败: ${response.status}`);
        }
        
        if (!result.success) {
            throw new Error(result.error || '解析失败');
        }
        
        if (!result.data) {
            throw new Error('返回数据为空');
        }

        // 保存结果
        state.parsedData = result.data;
        state.cacheKey = result.data.cache_key || '';

        // 显示结果
        displayParsedResult(result.data);
        
        showToast('简历解析成功！', 'success');
        updateStep(2);

    } catch (error) {
        console.error('解析错误:', error);
        showToast(error.message || '解析失败，请重试', 'error');
    } finally {
        setButtonLoading(btn, false);
    }
}

// 读取文件为 Base64
function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// 显示解析结果
function displayParsedResult(data) {
    const { extracted_info, raw_text, skills } = data;
    
    // 基本信息
    const basicInfo = extracted_info.basic_info || {};
    const basicInfoGrid = document.getElementById('basic-info-grid');
    basicInfoGrid.innerHTML = `
        ${createInfoItem('姓名', basicInfo.name)}
        ${createInfoItem('电话', basicInfo.phone)}
        ${createInfoItem('邮箱', basicInfo.email)}
        ${createInfoItem('地址', basicInfo.address)}
    `;

    // 可选信息
    const optionalInfo = extracted_info.optional_info || {};
    const optionalInfoGrid = document.getElementById('optional-info-grid');
    optionalInfoGrid.innerHTML = `
        ${createInfoItem('求职意向', optionalInfo.job_intention)}
        ${createInfoItem('工作年限', optionalInfo.experience_years)}
        ${createInfoItem('学历背景', optionalInfo.education)}
    `;

    // 技能
    const skillsContainer = document.getElementById('skills-container');
    const extractedSkills = extracted_info.skills || [];
    if (extractedSkills.length > 0) {
        skillsContainer.innerHTML = extractedSkills
            .map(skill => `<span class="skill-tag">${escapeHtml(skill)}</span>`)
            .join('');
    } else {
        skillsContainer.innerHTML = '<span class="info-item-value empty">未识别到技能标签</span>';
    }

    // 原始文本
    document.getElementById('raw-text').textContent = raw_text || '无内容';

    // 显示区域
    elements.parsedSection.style.display = 'block';
    elements.matchSection.style.display = 'block';
    
    // 滚动到结果区域
    elements.parsedSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 创建信息项
function createInfoItem(label, value) {
    const displayValue = value || '未识别';
    const emptyClass = value ? '' : 'empty';
    return `
        <div class="info-item">
            <div class="info-item-label">${label}</div>
            <div class="info-item-value ${emptyClass}">${escapeHtml(displayValue)}</div>
        </div>
    `;
}

// 处理匹配
async function handleMatch() {
    const jobDesc = elements.jobDescription.value.trim();
    
    if (!jobDesc) {
        showToast('请输入岗位描述', 'error');
        return;
    }

    if (!state.parsedData) {
        showToast('请先解析简历', 'error');
        return;
    }

    const btn = elements.matchBtn;
    setButtonLoading(btn, true);

    try {
        const response = await fetch(`${API_BASE_URL}/match`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cache_key: state.cacheKey,
                job_description: jobDesc,
                resume_text: state.parsedData.raw_text,
                extracted_info: state.parsedData.extracted_info
            })
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.error || '匹配分析失败');
        }

        // 显示匹配结果
        displayMatchResult(result.data);
        
        showToast('匹配分析完成！', 'success');
        updateStep(3);

    } catch (error) {
        console.error('匹配错误:', error);
        showToast(error.message || '匹配分析失败，请重试', 'error');
    } finally {
        setButtonLoading(btn, false);
    }
}

// 显示匹配结果
function displayMatchResult(data) {
    // 综合评分
    const overallScore = data.overall_score || 0;
    document.getElementById('overall-score').textContent = Math.round(overallScore);
    
    // 评分环形进度
    const circle = document.getElementById('score-circle');
    const circumference = 339.292; // 2 * PI * 54
    const offset = circumference - (overallScore / 100) * circumference;
    circle.style.strokeDashoffset = offset;
    
    // 设置颜色
    if (overallScore >= 80) {
        circle.style.stroke = '#6bcb77';
        document.getElementById('score-level').textContent = '优秀匹配';
    } else if (overallScore >= 60) {
        circle.style.stroke = '#00d9ff';
        document.getElementById('score-level').textContent = '良好匹配';
    } else if (overallScore >= 40) {
        circle.style.stroke = '#ffc75f';
        document.getElementById('score-level').textContent = '一般匹配';
    } else {
        circle.style.stroke = '#ff6b6b';
        document.getElementById('score-level').textContent = '匹配度较低';
    }

    // 详细评分
    const skillScore = data.skill_match?.score || 0;
    const keywordScore = data.keyword_match?.score || 0;
    const expScore = data.experience_match?.score || 0;
    const eduScore = data.education_match?.score || 0;

    updateScoreBar('skill', skillScore);
    updateScoreBar('keyword', keywordScore);
    updateScoreBar('exp', expScore);
    updateScoreBar('edu', eduScore);

    // 技能分析
    const matchedSkills = data.skill_match?.matched_skills || [];
    const missingSkills = data.skill_match?.missing_skills || [];
    const extraSkills = data.skill_match?.extra_skills || [];

    document.getElementById('matched-skills').innerHTML = 
        matchedSkills.length > 0 
            ? matchedSkills.map(s => `<span class="skill-tag">${escapeHtml(s)}</span>`).join('')
            : '<span class="info-item-value empty">无</span>';

    document.getElementById('missing-skills').innerHTML = 
        missingSkills.length > 0 
            ? missingSkills.map(s => `<span class="skill-tag">${escapeHtml(s)}</span>`).join('')
            : '<span class="info-item-value empty">无</span>';

    document.getElementById('extra-skills').innerHTML = 
        extraSkills.length > 0 
            ? extraSkills.map(s => `<span class="skill-tag">${escapeHtml(s)}</span>`).join('')
            : '<span class="info-item-value empty">无</span>';

    // 建议
    const recommendations = data.recommendations || [];
    const recList = document.getElementById('recommendations');
    recList.innerHTML = recommendations.length > 0
        ? recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('')
        : '<li>暂无建议</li>';

    // AI 分析
    const aiSection = document.getElementById('ai-analysis-section');
    const aiContent = document.getElementById('ai-analysis-content');
    
    if (data.ai_analysis && !data.ai_analysis.error) {
        aiSection.style.display = 'block';
        const ai = data.ai_analysis;
        
        let aiHtml = '';
        
        // AI 评分
        if (ai.score !== undefined) {
            aiHtml += `<div class="ai-score">
                <span class="ai-score-label">AI 匹配评分:</span>
                <span class="ai-score-value">${ai.score}</span>
            </div>`;
        }
        
        // 综合分析
        if (ai.overall_analysis) {
            aiHtml += `<div class="ai-analysis-item">
                <p><strong>📊 综合分析:</strong></p>
                <p>${escapeHtml(ai.overall_analysis)}</p>
            </div>`;
        }
        
        // 技能分析
        if (ai.skill_analysis) {
            aiHtml += `<div class="ai-analysis-item">
                <p><strong>💼 技能匹配分析:</strong></p>
                <p>${escapeHtml(ai.skill_analysis)}</p>
            </div>`;
        }
        
        // 经验分析
        if (ai.experience_analysis) {
            aiHtml += `<div class="ai-analysis-item">
                <p><strong>📈 经验匹配分析:</strong></p>
                <p>${escapeHtml(ai.experience_analysis)}</p>
            </div>`;
        }
        
        // 学历分析
        if (ai.education_analysis) {
            aiHtml += `<div class="ai-analysis-item">
                <p><strong>🎓 学历匹配分析:</strong></p>
                <p>${escapeHtml(ai.education_analysis)}</p>
            </div>`;
        }
        
        // 优势
        if (ai.strengths && ai.strengths.length > 0) {
            aiHtml += `<div class="ai-analysis-item">
                <p><strong>✅ 优势:</strong></p>
                <ul>${ai.strengths.map(s => `<li>${escapeHtml(s)}</li>`).join('')}</ul>
            </div>`;
        }
        
        // 不足
        if (ai.weaknesses && ai.weaknesses.length > 0) {
            aiHtml += `<div class="ai-analysis-item">
                <p><strong>⚠️ 不足:</strong></p>
                <ul>${ai.weaknesses.map(w => `<li>${escapeHtml(w)}</li>`).join('')}</ul>
            </div>`;
        }
        
        // AI 建议（如果单独提供）
        if (ai.recommendations && ai.recommendations.length > 0) {
            aiHtml += `<div class="ai-analysis-item">
                <p><strong>💡 AI 建议:</strong></p>
                <ul>${ai.recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('')}</ul>
            </div>`;
        }
        
        aiContent.innerHTML = aiHtml || '<p>AI 分析结果为空</p>';
    } else if (data.ai_analysis && data.ai_analysis.error) {
        // AI 分析失败，显示错误信息（但不显示错误，因为传统算法仍然可用）
        aiSection.style.display = 'none';
    } else {
        aiSection.style.display = 'none';
    }

    // 显示结果区域
    elements.scoreSection.style.display = 'block';
    
    // 滚动到结果
    elements.scoreSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 更新评分条
function updateScoreBar(type, score) {
    document.getElementById(`${type}-score`).textContent = Math.round(score);
    setTimeout(() => {
        document.getElementById(`${type}-bar`).style.width = `${score}%`;
    }, 100);
}

// 更新步骤
function updateStep(activeStep) {
    elements.steps.forEach((step, index) => {
        const stepNum = index + 1;
        step.classList.remove('active', 'completed');
        
        if (stepNum < activeStep) {
            step.classList.add('completed');
        } else if (stepNum === activeStep) {
            step.classList.add('active');
        }
    });
}

// 设置按钮加载状态
function setButtonLoading(btn, isLoading) {
    const textEl = btn.querySelector('.btn-text');
    const loadingEl = btn.querySelector('.btn-loading');
    
    btn.disabled = isLoading;
    textEl.style.display = isLoading ? 'none' : 'inline';
    loadingEl.style.display = isLoading ? 'inline-flex' : 'none';
}

// 显示 Toast 通知
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    // 自动移除
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// HTML 转义
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 演示模式 - 当 API 不可用时使用模拟数据
async function demoMode() {
    console.log('Demo mode activated - using mock data');
    
    // 模拟解析结果
    const mockParsedData = {
        cache_key: 'demo-123',
        raw_text: '张三\n联系电话：13800138000\n邮箱：zhangsan@email.com\n\n教育背景\n2018-2022 某某大学 计算机科学与技术 本科\n\n工作经历\n2022-至今 某科技公司 软件工程师\n- 负责后端API开发\n- 使用Python和Java进行开发\n\n技能\nPython, Java, MySQL, Redis, Docker, Git',
        extracted_info: {
            basic_info: {
                name: '张三',
                phone: '13800138000',
                email: 'zhangsan@email.com',
                address: '北京市海淀区'
            },
            optional_info: {
                job_intention: '后端开发工程师',
                experience_years: '2年',
                education: '本科'
            },
            skills: ['Python', 'Java', 'MySQL', 'Redis', 'Docker', 'Git']
        }
    };
    
    return mockParsedData;
}

// 检查 API 是否可用
async function checkAPI() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            mode: 'cors'
        });
        return response.ok;
    } catch {
        return false;
    }
}

