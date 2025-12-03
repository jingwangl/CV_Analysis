/**
 * 配置文件
 * 部署后请修改 API_BASE_URL 为你的阿里云函数计算 HTTP 触发器地址
 */

const CONFIG = {
    // 阿里云函数计算 API 地址
    // 部署后请替换为实际地址，格式: https://xxx.cn-hangzhou.fcapp.run
    API_BASE_URL: https://cv-analysis-api-swgpsxkdgl.cn-hangzhou.fcapp.run',
    
    // 最大文件大小 (10MB)
    MAX_FILE_SIZE: 10 * 1024 * 1024,
    
    // 支持的文件类型
    SUPPORTED_TYPES: ['application/pdf'],
    
    // Toast 显示时间 (ms)
    TOAST_DURATION: 3000
};

// 导出配置
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}

