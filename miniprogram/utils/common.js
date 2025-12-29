/**
 * 通用工具函数模块
 * 包含文件大小格式化、扩展名提取等通用功能
 */

/**
 * 格式化文件大小
 * @param {number} bytes - 文件字节数
 * @returns {string} 格式化后的文件大小字符串
 */
function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * 提取文件扩展名（带点、小写）
 * @param {string} name - 文件名
 * @returns {string} 扩展名，如 ".docx"
 */
function getExt(name) {
  if (!name) return '';
  const i = name.lastIndexOf('.');
  return i >= 0 ? name.slice(i).toLowerCase() : '';
}

/**
 * 延时等待
 * @param {number} ms - 等待毫秒数
 * @returns {Promise<void>}
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @returns {Promise<void>}
 */
function copyToClipboard(text) {
  return new Promise((resolve, reject) => {
    wx.setClipboardData({
      data: text,
      success: () => {
        wx.showToast({
          title: '链接已复制，可分享给好友',
          icon: 'none'
        });
        resolve();
      },
      fail: () => {
        wx.showToast({
          title: '复制失败',
          icon: 'none'
        });
        reject(new Error('复制失败'));
      }
    });
  });
}

/**
 * 显示加载提示
 * @param {string} title - 提示文字
 */
function showLoading(title = '加载中...') {
  wx.showLoading({ title, mask: true });
}

/**
 * 隐藏加载提示
 */
function hideLoading() {
  wx.hideLoading();
}

/**
 * 显示 Toast 提示
 * @param {string} title - 提示文字
 * @param {string} icon - 图标类型 'success' | 'loading' | 'none'
 * @param {number} duration - 显示时长
 */
function showToast(title, icon = 'none', duration = 2000) {
  wx.showToast({ title, icon, duration });
}

module.exports = {
  formatSize,
  getExt,
  sleep,
  copyToClipboard,
  showLoading,
  hideLoading,
  showToast
};
