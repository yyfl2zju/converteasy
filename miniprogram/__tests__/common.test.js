/**
 * common.js 单元测试
 * 测试通用工具函数
 */

const { formatSize, getExt, sleep } = require('../utils/common');

describe('formatSize', () => {
  test('应该正确格式化字节', () => {
    expect(formatSize(0)).toBe('0 B');
    expect(formatSize(512)).toBe('512 B');
    expect(formatSize(1023)).toBe('1023 B');
  });

  test('应该正确格式化 KB', () => {
    expect(formatSize(1024)).toBe('1.0 KB');
    expect(formatSize(1536)).toBe('1.5 KB');
    expect(formatSize(1024 * 100)).toBe('100.0 KB');
    expect(formatSize(1024 * 1024 - 1)).toBe('1024.0 KB');
  });

  test('应该正确格式化 MB', () => {
    expect(formatSize(1024 * 1024)).toBe('1.0 MB');
    expect(formatSize(1024 * 1024 * 1.5)).toBe('1.5 MB');
    expect(formatSize(1024 * 1024 * 100)).toBe('100.0 MB');
  });
});

describe('getExt', () => {
  test('应该正确提取文件扩展名', () => {
    expect(getExt('document.pdf')).toBe('.pdf');
    expect(getExt('file.docx')).toBe('.docx');
    expect(getExt('audio.mp3')).toBe('.mp3');
  });

  test('应该将扩展名转为小写', () => {
    expect(getExt('DOCUMENT.PDF')).toBe('.pdf');
    expect(getExt('File.DOCX')).toBe('.docx');
    expect(getExt('AUDIO.MP3')).toBe('.mp3');
  });

  test('应该处理多个点的文件名', () => {
    expect(getExt('file.backup.pdf')).toBe('.pdf');
    expect(getExt('my.document.v2.docx')).toBe('.docx');
  });

  test('应该处理没有扩展名的文件', () => {
    expect(getExt('README')).toBe('');
    expect(getExt('Makefile')).toBe('');
  });

  test('应该处理空值或无效输入', () => {
    expect(getExt('')).toBe('');
    expect(getExt(null)).toBe('');
    expect(getExt(undefined)).toBe('');
  });

  test('应该处理隐藏文件', () => {
    expect(getExt('.gitignore')).toBe('.gitignore');
    expect(getExt('.env')).toBe('.env');
  });
});

describe('sleep', () => {
  test('应该返回一个 Promise', () => {
    const result = sleep(0);
    expect(result).toBeInstanceOf(Promise);
  });

  test('应该在指定时间后 resolve', async () => {
    const start = Date.now();
    await sleep(50);
    const elapsed = Date.now() - start;
    expect(elapsed).toBeGreaterThanOrEqual(45); // 允许小误差
    expect(elapsed).toBeLessThan(100);
  });

  test('sleep(0) 应该几乎立即 resolve', async () => {
    const start = Date.now();
    await sleep(0);
    const elapsed = Date.now() - start;
    expect(elapsed).toBeLessThan(50);
  });
});
