/**
 * formats.js 单元测试
 * 测试格式配置和工具函数
 */

const {
  DOCUMENT_SOURCE_FORMATS,
  DOCUMENT_TARGET_FORMATS,
  DOCUMENT_FORMAT_DISPLAY_NAMES,
  DOCUMENT_CONVERSION_MAP,
  DOCUMENT_ALLOWED_EXTENSIONS,
  DOCUMENT_ICONS,
  AUDIO_SOURCE_FORMATS,
  AUDIO_FORMAT_DISPLAY_NAMES,
  AUDIO_CONVERSION_MAP,
  AUDIO_ALLOWED_EXTENSIONS,
  getAllowedExtensions,
  getFileIcon,
  getFormatDisplayName,
  getTargetDisplayNames
} = require('../utils/formats');

describe('文档格式配置', () => {
  test('DOCUMENT_SOURCE_FORMATS 应包含常用文档格式', () => {
    expect(DOCUMENT_SOURCE_FORMATS).toContain('pdf');
    expect(DOCUMENT_SOURCE_FORMATS).toContain('doc');
    expect(DOCUMENT_SOURCE_FORMATS).toContain('docx');
    expect(DOCUMENT_SOURCE_FORMATS).toContain('xls');
    expect(DOCUMENT_SOURCE_FORMATS).toContain('xlsx');
    expect(DOCUMENT_SOURCE_FORMATS).toContain('ppt');
    expect(DOCUMENT_SOURCE_FORMATS).toContain('pptx');
    expect(DOCUMENT_SOURCE_FORMATS).toContain('txt');
  });

  test('DOCUMENT_TARGET_FORMATS 应包含所有目标格式', () => {
    expect(DOCUMENT_TARGET_FORMATS).toContain('pdf');
    expect(DOCUMENT_TARGET_FORMATS).toContain('csv');
    expect(DOCUMENT_TARGET_FORMATS).toContain('odt');
    expect(DOCUMENT_TARGET_FORMATS).toContain('ods');
    expect(DOCUMENT_TARGET_FORMATS).toContain('odp');
  });

  test('DOCUMENT_FORMAT_DISPLAY_NAMES 应有正确的显示名称', () => {
    expect(DOCUMENT_FORMAT_DISPLAY_NAMES.pdf).toBe('PDF');
    expect(DOCUMENT_FORMAT_DISPLAY_NAMES.doc).toBe('Word(.doc)');
    expect(DOCUMENT_FORMAT_DISPLAY_NAMES.docx).toBe('Word(.docx)');
    expect(DOCUMENT_FORMAT_DISPLAY_NAMES.xls).toBe('Excel(.xls)');
    expect(DOCUMENT_FORMAT_DISPLAY_NAMES.xlsx).toBe('Excel(.xlsx)');
  });

  test('DOCUMENT_CONVERSION_MAP 应定义有效的转换路径', () => {
    expect(DOCUMENT_CONVERSION_MAP.pdf).toContain('doc');
    expect(DOCUMENT_CONVERSION_MAP.pdf).toContain('docx');
    expect(DOCUMENT_CONVERSION_MAP.doc).toContain('pdf');
    expect(DOCUMENT_CONVERSION_MAP.docx).toContain('pdf');
    expect(DOCUMENT_CONVERSION_MAP.txt).toContain('doc');
  });

  test('DOCUMENT_ALLOWED_EXTENSIONS 应包含带点的扩展名', () => {
    expect(DOCUMENT_ALLOWED_EXTENSIONS.pdf).toContain('.pdf');
    expect(DOCUMENT_ALLOWED_EXTENSIONS.doc).toContain('.doc');
    expect(DOCUMENT_ALLOWED_EXTENSIONS.html).toContain('.html');
    expect(DOCUMENT_ALLOWED_EXTENSIONS.html).toContain('.htm');
  });

  test('DOCUMENT_ICONS 应为每个格式提供图标', () => {
    expect(DOCUMENT_ICONS['.pdf']).toBeDefined();
    expect(DOCUMENT_ICONS['.doc']).toBeDefined();
    expect(DOCUMENT_ICONS['.xls']).toBeDefined();
    expect(DOCUMENT_ICONS['.ppt']).toBeDefined();
  });
});

describe('音频格式配置', () => {
  test('AUDIO_SOURCE_FORMATS 应包含常用音频格式', () => {
    expect(AUDIO_SOURCE_FORMATS).toContain('mp3');
    expect(AUDIO_SOURCE_FORMATS).toContain('wav');
    expect(AUDIO_SOURCE_FORMATS).toContain('aac');
    expect(AUDIO_SOURCE_FORMATS).toContain('flac');
    expect(AUDIO_SOURCE_FORMATS).toContain('m4a');
    expect(AUDIO_SOURCE_FORMATS).toContain('ogg');
  });

  test('AUDIO_FORMAT_DISPLAY_NAMES 应有正确的显示名称', () => {
    expect(AUDIO_FORMAT_DISPLAY_NAMES.mp3).toBe('MP3');
    expect(AUDIO_FORMAT_DISPLAY_NAMES.wav).toBe('WAV');
    expect(AUDIO_FORMAT_DISPLAY_NAMES.flac).toBe('FLAC');
  });

  test('AUDIO_CONVERSION_MAP 应定义有效的转换路径', () => {
    expect(AUDIO_CONVERSION_MAP.mp3).toContain('wav');
    expect(AUDIO_CONVERSION_MAP.wav).toContain('mp3');
    expect(AUDIO_CONVERSION_MAP.flac).toContain('mp3');
  });

  test('AUDIO_ALLOWED_EXTENSIONS 应包含带点的扩展名', () => {
    expect(AUDIO_ALLOWED_EXTENSIONS.mp3).toContain('.mp3');
    expect(AUDIO_ALLOWED_EXTENSIONS.wav).toContain('.wav');
    expect(AUDIO_ALLOWED_EXTENSIONS.flac).toContain('.flac');
  });
});

describe('getAllowedExtensions', () => {
  test('应返回文档格式的扩展名列表', () => {
    expect(getAllowedExtensions('document', 'pdf')).toEqual(['.pdf']);
    expect(getAllowedExtensions('document', 'html')).toEqual(['.html', '.htm']);
    expect(getAllowedExtensions('document', 'doc')).toEqual(['.doc']);
  });

  test('应返回音频格式的扩展名列表', () => {
    expect(getAllowedExtensions('audio', 'mp3')).toEqual(['.mp3']);
    expect(getAllowedExtensions('audio', 'wav')).toEqual(['.wav']);
    expect(getAllowedExtensions('audio', 'flac')).toEqual(['.flac']);
  });

  test('对于未知格式应返回空数组', () => {
    expect(getAllowedExtensions('document', 'unknown')).toEqual([]);
    expect(getAllowedExtensions('audio', 'unknown')).toEqual([]);
    expect(getAllowedExtensions('video', 'mp4')).toEqual([]);
  });
});

describe('getFileIcon', () => {
  test('应返回文档格式的图标', () => {
    expect(getFileIcon('.pdf')).toBe('📄');
    expect(getFileIcon('.doc')).toBe('📝');
    expect(getFileIcon('.docx')).toBe('📝');
    expect(getFileIcon('.xls')).toBe('📊');
    expect(getFileIcon('.xlsx')).toBe('📊');
    expect(getFileIcon('.ppt')).toBe('📋');
    expect(getFileIcon('.pptx')).toBe('📋');
  });

  test('应处理大写扩展名', () => {
    expect(getFileIcon('.PDF')).toBe('📄');
    expect(getFileIcon('.DOC')).toBe('📝');
    expect(getFileIcon('.XLS')).toBe('📊');
  });

  test('对于未知扩展名应返回默认图标', () => {
    expect(getFileIcon('.unknown')).toBe('📁');
    expect(getFileIcon('.xyz')).toBe('📁');
  });
});

describe('getFormatDisplayName', () => {
  test('应返回文档格式的显示名称', () => {
    expect(getFormatDisplayName('document', 'pdf')).toBe('PDF');
    expect(getFormatDisplayName('document', 'doc')).toBe('Word(.doc)');
    expect(getFormatDisplayName('document', 'docx')).toBe('Word(.docx)');
    expect(getFormatDisplayName('document', 'xls')).toBe('Excel(.xls)');
  });

  test('应返回音频格式的显示名称', () => {
    expect(getFormatDisplayName('audio', 'mp3')).toBe('MP3');
    expect(getFormatDisplayName('audio', 'wav')).toBe('WAV');
    expect(getFormatDisplayName('audio', 'flac')).toBe('FLAC');
  });

  test('对于未知格式应返回大写的格式名', () => {
    expect(getFormatDisplayName('document', 'unknown')).toBe('UNKNOWN');
    expect(getFormatDisplayName('audio', 'xyz')).toBe('XYZ');
    expect(getFormatDisplayName('video', 'mp4')).toBe('MP4');
  });
});

describe('getTargetDisplayNames', () => {
  test('应返回文档目标格式的显示名称列表', () => {
    const targets = ['pdf', 'doc', 'txt'];
    const names = getTargetDisplayNames('document', targets);
    expect(names).toEqual(['PDF', 'Word(.doc)', 'TXT']);
  });

  test('应返回音频目标格式的显示名称列表', () => {
    const targets = ['mp3', 'wav', 'flac'];
    const names = getTargetDisplayNames('audio', targets);
    expect(names).toEqual(['MP3', 'WAV', 'FLAC']);
  });

  test('空数组应返回空数组', () => {
    expect(getTargetDisplayNames('document', [])).toEqual([]);
    expect(getTargetDisplayNames('audio', [])).toEqual([]);
  });
});
