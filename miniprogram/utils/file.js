/**
 * 文件操作工具模块
 * 包含文件选择、下载、预览、分享等功能
 */

const { getExt, copyToClipboard, showLoading, hideLoading, showToast } = require('./common');

/**
 * 从微信聊天选择文件
 * @param {string[]} allowedExt - 允许的扩展名列表（可带点或不带点）
 * @param {number} count - 最多选择数量
 * @returns {Promise<Array>} 选择的文件列表
 */
function chooseMessageFile(allowedExt, count = 9) {
  return new Promise((resolve, reject) => {
    // 微信 API 要求扩展名不带点，如 ['mp3', 'wav']
    // 自动处理传入的带点格式，如 ['.mp3', '.wav'] -> ['mp3', 'wav']
    const normalizedExt = Array.isArray(allowedExt)
      ? allowedExt.map(ext => ext.replace(/^\./, ''))
      : [];

    console.log('chooseMessageFile - 原始扩展名:', allowedExt);
    console.log('chooseMessageFile - 处理后扩展名:', normalizedExt);

    wx.chooseMessageFile({
      count,
      type: 'file',
      extension: normalizedExt.length > 0 ? normalizedExt : undefined,
      success: (res) => {
        console.log('chooseMessageFile - 选择成功:', res.tempFiles);
        resolve(res.tempFiles);
      },
      fail: (err) => {
        console.error('文件选择失败:', err);
        reject(err);
      }
    });
  });
}

/**
 * 下载文件到临时路径
 * @param {string} url - 文件 URL
 * @returns {Promise<string>} 临时文件路径
 */
function downloadFile(url) {
  return new Promise((resolve, reject) => {
    wx.downloadFile({
      url,
      success: (res) => {
        if (res.tempFilePath) {
          resolve(res.tempFilePath);
        } else {
          reject(new Error('下载失败，未获取到临时文件路径'));
        }
      },
      fail: (err) => {
        console.error('下载文件失败:', err);
        reject(new Error('下载失败: ' + (err.errMsg || '网络错误')));
      }
    });
  });
}

/**
 * 保存文件到本地
 * @param {string} tempFilePath - 临时文件路径
 * @param {string} fileName - 文件名
 * @returns {Promise<string>} 保存后的文件路径
 */
function saveFile(tempFilePath, fileName) {
  return new Promise((resolve, reject) => {
    const fileManager = wx.getFileSystemManager();
    const savePath = `${wx.env.USER_DATA_PATH}/${fileName || 'converted_file'}`;

    fileManager.saveFile({
      tempFilePath,
      filePath: savePath,
      success: (saveRes) => {
        resolve(saveRes.savedFilePath);
      },
      fail: (saveErr) => {
        console.error('保存文件失败:', saveErr);
        reject(saveErr);
      }
    });
  });
}

/**
 * 打开文档预览
 * @param {string} filePath - 文件路径
 * @param {boolean} showMenu - 是否显示菜单
 * @returns {Promise<void>}
 */
function openDocument(filePath, showMenu = true) {
  return new Promise((resolve, reject) => {
    wx.openDocument({
      filePath,
      showMenu,
      success: () => {
        console.log('文档打开成功');
        resolve();
      },
      fail: (err) => {
        console.error('文档打开失败:', err);
        reject(err);
      }
    });
  });
}

/**
 * 分享文件
 * @param {string} filePath - 本地文件路径
 * @param {string} fallbackUrl - 降级时复制的链接
 * @returns {Promise<void>}
 */
function shareFile(filePath, fallbackUrl) {
  return new Promise((resolve, reject) => {
    if (wx.canIUse('shareFileMessage')) {
      wx.shareFileMessage({
        filePath,
        success: () => {
          console.log('文件分享成功');
          resolve();
        },
        fail: (shareErr) => {
          console.error('文件分享失败:', shareErr);
          // 降级方案：复制链接
          if (fallbackUrl) {
            copyToClipboard(fallbackUrl).then(resolve).catch(reject);
          } else {
            reject(new Error('分享失败'));
          }
        }
      });
    } else if (fallbackUrl) {
      // 不支持 shareFileMessage，直接复制链接
      copyToClipboard(fallbackUrl).then(resolve).catch(reject);
    } else {
      reject(new Error('不支持文件分享'));
    }
  });
}

/**
 * 检查文件扩展名是否可预览（微信支持）
 * @param {string} filename - 文件名
 * @returns {boolean}
 */
function isPreviewSupported(filename) {
  const ext = getExt(filename).toLowerCase();
  const previewableExts = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'];
  return previewableExts.includes(ext);
}

/**
 * 尝试打开文档（支持降级处理）
 * @param {string} tempPath - 临时文件路径
 * @param {string} fileName - 文件名
 * @returns {Promise<void>}
 */
async function tryOpenDocument(tempPath, fileName) {
  const ext = getExt(fileName).toLowerCase();
  const openableExts = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'];

  if (openableExts.includes(ext)) {
    try {
      await openDocument(tempPath, true);
    } catch (err) {
      showToast('文件已下载但无法打开', 'none');
    }
  } else {
    showToast(`文件已下载，请在文件管理中查看`, 'none', 3000);
  }
}

/**
 * 处理文件下载并保存
 * @param {string} fileUrl - 文件 URL
 * @param {string} fileName - 文件名
 * @returns {Promise<void>}
 */
async function downloadAndSaveFile(fileUrl, fileName) {
  showLoading('下载中...');

  try {
    const tempPath = await downloadFile(fileUrl);
    hideLoading();

    try {
      await saveFile(tempPath, fileName);
      showToast('下载成功', 'success');
    } catch (saveErr) {
      // 保存失败时尝试直接打开
      await tryOpenDocument(tempPath, fileName);
    }
  } catch (err) {
    hideLoading();
    showToast('下载失败', 'none');
    throw err;
  }
}

/**
 * 处理文件预览
 * @param {string} fileUrl - 文件 URL
 * @param {string} fileName - 文件名（用于错误提示）
 * @returns {Promise<void>}
 */
async function previewDocument(fileUrl, fileName) {
  showLoading('加载中...');

  try {
    const tempPath = await downloadFile(fileUrl);
    hideLoading();

    try {
      await openDocument(tempPath, true);
    } catch (err) {
      const fileExt = getExt(fileName).toLowerCase();
      let errorMsg = '预览失败';
      if (err && err.errMsg && err.errMsg.includes('filetype not supported')) {
        errorMsg = `微信不支持预览 ${fileExt} 格式文件`;
      }
      showToast(errorMsg, 'none', 3000);
    }
  } catch (err) {
    hideLoading();
    showToast('预览失败，请重试', 'none');
    throw err;
  }
}

/**
 * 处理文件分享
 * @param {string} fileUrl - 文件 URL
 * @returns {Promise<void>}
 */
async function shareRemoteFile(fileUrl) {
  showLoading('准备分享...');

  try {
    const tempPath = await downloadFile(fileUrl);
    hideLoading();
    await shareFile(tempPath, fileUrl);
  } catch (err) {
    hideLoading();
    // 下载失败时直接复制链接
    await copyToClipboard(fileUrl);
  }
}

module.exports = {
  chooseMessageFile,
  downloadFile,
  saveFile,
  openDocument,
  shareFile,
  isPreviewSupported,
  tryOpenDocument,
  downloadAndSaveFile,
  previewDocument,
  shareRemoteFile
};
