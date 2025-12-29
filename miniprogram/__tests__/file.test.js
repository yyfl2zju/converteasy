/**
 * file.js 单元测试
 * 测试文件操作相关函数
 */

// Mock wx 对象
global.wx = {
  chooseMessageFile: jest.fn(),
  downloadFile: jest.fn(),
  openDocument: jest.fn(),
  shareFileMessage: jest.fn(),
  setClipboardData: jest.fn(),
  showToast: jest.fn(),
  showLoading: jest.fn(),
  hideLoading: jest.fn(),
  getFileSystemManager: jest.fn(() => ({
    saveFile: jest.fn()
  })),
  canIUse: jest.fn(),
  env: {
    USER_DATA_PATH: '/wxfile/user'
  }
};

// 需要在 mock wx 之后再 require
const {
  chooseMessageFile,
  downloadFile,
  openDocument,
  shareFile,
  isPreviewSupported
} = require('../utils/file');

describe('chooseMessageFile', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('应正确调用 wx.chooseMessageFile', async () => {
    const mockFiles = [
      { path: '/tmp/file1.pdf', name: 'file1.pdf', size: 1024 }
    ];
    global.wx.chooseMessageFile.mockImplementation((options) => {
      options.success({ tempFiles: mockFiles });
    });

    const result = await chooseMessageFile(['pdf', 'doc']);

    expect(result).toEqual(mockFiles);
    expect(global.wx.chooseMessageFile).toHaveBeenCalledWith(
      expect.objectContaining({
        count: 9,
        type: 'file',
        extension: ['pdf', 'doc']
      })
    );
  });

  test('应自动处理带点的扩展名', async () => {
    global.wx.chooseMessageFile.mockImplementation((options) => {
      options.success({ tempFiles: [] });
    });

    await chooseMessageFile(['.pdf', '.doc', '.docx']);

    expect(global.wx.chooseMessageFile).toHaveBeenCalledWith(
      expect.objectContaining({
        extension: ['pdf', 'doc', 'docx']
      })
    );
  });

  test('应支持自定义文件数量', async () => {
    global.wx.chooseMessageFile.mockImplementation((options) => {
      options.success({ tempFiles: [] });
    });

    await chooseMessageFile(['pdf'], 5);

    expect(global.wx.chooseMessageFile).toHaveBeenCalledWith(
      expect.objectContaining({
        count: 5
      })
    );
  });

  test('选择失败应 reject', async () => {
    global.wx.chooseMessageFile.mockImplementation((options) => {
      options.fail({ errMsg: 'user canceled' });
    });

    await expect(chooseMessageFile(['pdf']))
      .rejects.toEqual({ errMsg: 'user canceled' });
  });

  test('空扩展名数组应不限制类型', async () => {
    global.wx.chooseMessageFile.mockImplementation((options) => {
      options.success({ tempFiles: [] });
    });

    await chooseMessageFile([]);

    expect(global.wx.chooseMessageFile).toHaveBeenCalledWith(
      expect.objectContaining({
        extension: undefined
      })
    );
  });
});

describe('downloadFile', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('应正确下载文件', async () => {
    const tempPath = '/tmp/downloaded_file.pdf';
    global.wx.downloadFile.mockImplementation((options) => {
      options.success({ tempFilePath: tempPath });
    });

    const result = await downloadFile('https://example.com/file.pdf');

    expect(result).toBe(tempPath);
    expect(global.wx.downloadFile).toHaveBeenCalledWith(
      expect.objectContaining({
        url: 'https://example.com/file.pdf'
      })
    );
  });

  test('下载失败应 reject', async () => {
    global.wx.downloadFile.mockImplementation((options) => {
      options.fail({ errMsg: 'network error' });
    });

    await expect(downloadFile('https://example.com/file.pdf'))
      .rejects.toThrow('下载失败');
  });

  test('无临时文件路径应 reject', async () => {
    global.wx.downloadFile.mockImplementation((options) => {
      options.success({ tempFilePath: null });
    });

    await expect(downloadFile('https://example.com/file.pdf'))
      .rejects.toThrow('下载失败');
  });
});

describe('openDocument', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('应正确打开文档', async () => {
    global.wx.openDocument.mockImplementation((options) => {
      options.success();
    });

    await openDocument('/tmp/file.pdf');

    expect(global.wx.openDocument).toHaveBeenCalledWith(
      expect.objectContaining({
        filePath: '/tmp/file.pdf',
        showMenu: true
      })
    );
  });

  test('应支持隐藏菜单', async () => {
    global.wx.openDocument.mockImplementation((options) => {
      options.success();
    });

    await openDocument('/tmp/file.pdf', false);

    expect(global.wx.openDocument).toHaveBeenCalledWith(
      expect.objectContaining({
        filePath: '/tmp/file.pdf',
        showMenu: false
      })
    );
  });

  test('打开失败应 reject', async () => {
    global.wx.openDocument.mockImplementation((options) => {
      options.fail({ errMsg: 'filetype not supported' });
    });

    await expect(openDocument('/tmp/file.xyz'))
      .rejects.toEqual({ errMsg: 'filetype not supported' });
  });
});

describe('shareFile', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.wx.canIUse.mockReturnValue(true);
  });

  test('支持 shareFileMessage 时应直接分享', async () => {
    global.wx.shareFileMessage.mockImplementation((options) => {
      options.success();
    });

    await shareFile('/tmp/file.pdf', 'https://fallback.url');

    expect(global.wx.shareFileMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        filePath: '/tmp/file.pdf'
      })
    );
  });

  test('分享失败时应降级复制链接', async () => {
    global.wx.shareFileMessage.mockImplementation((options) => {
      options.fail({ errMsg: 'share failed' });
    });
    global.wx.setClipboardData.mockImplementation((options) => {
      options.success();
    });

    await shareFile('/tmp/file.pdf', 'https://fallback.url');

    expect(global.wx.setClipboardData).toHaveBeenCalledWith(
      expect.objectContaining({
        data: 'https://fallback.url'
      })
    );
  });

  test('不支持 shareFileMessage 时应复制链接', async () => {
    global.wx.canIUse.mockReturnValue(false);
    global.wx.setClipboardData.mockImplementation((options) => {
      options.success();
    });

    await shareFile('/tmp/file.pdf', 'https://fallback.url');

    expect(global.wx.shareFileMessage).not.toHaveBeenCalled();
    expect(global.wx.setClipboardData).toHaveBeenCalledWith(
      expect.objectContaining({
        data: 'https://fallback.url'
      })
    );
  });

  test('无降级链接且不支持分享应 reject', async () => {
    global.wx.canIUse.mockReturnValue(false);

    await expect(shareFile('/tmp/file.pdf', null))
      .rejects.toThrow('不支持文件分享');
  });
});

describe('isPreviewSupported', () => {
  test('应支持常见文档格式预览', () => {
    expect(isPreviewSupported('document.pdf')).toBe(true);
    expect(isPreviewSupported('document.doc')).toBe(true);
    expect(isPreviewSupported('document.docx')).toBe(true);
    expect(isPreviewSupported('document.xls')).toBe(true);
    expect(isPreviewSupported('document.xlsx')).toBe(true);
    expect(isPreviewSupported('document.ppt')).toBe(true);
    expect(isPreviewSupported('document.pptx')).toBe(true);
  });

  test('不支持的格式应返回 false', () => {
    expect(isPreviewSupported('document.txt')).toBe(false);
    expect(isPreviewSupported('document.html')).toBe(false);
    expect(isPreviewSupported('document.csv')).toBe(false);
    expect(isPreviewSupported('audio.mp3')).toBe(false);
  });

  test('应处理大写扩展名', () => {
    expect(isPreviewSupported('DOCUMENT.PDF')).toBe(true);
    expect(isPreviewSupported('FILE.DOCX')).toBe(true);
  });
});
