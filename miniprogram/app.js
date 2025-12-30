// app.js
App({
  onLaunch() {
    console.log('ConvertEasy 小程序启动');

    // 从本地存储加载夜间模式设置
    const darkMode = wx.getStorageSync('darkMode') || false;
    this.globalData.darkMode = darkMode;

    // 应用夜间模式
    if (darkMode) {
      wx.setBackgroundTextStyle({ textStyle: 'light' });
    }
  },

  globalData: {
    // API 基础地址（可选覆盖）
    // apiBaseUrl: 'http://localhost:8080/'
    darkMode: false
  },

  // 切换夜间模式
  toggleDarkMode() {
    const newMode = !this.globalData.darkMode;
    this.globalData.darkMode = newMode;

    // 保存到本地存储
    wx.setStorageSync('darkMode', newMode);

    // 提示用户
    wx.showToast({
      title: newMode ? '已切换到夜间模式' : '已切换到日间模式',
      icon: 'success',
      duration: 1500
    });

    return newMode;
  }
});
