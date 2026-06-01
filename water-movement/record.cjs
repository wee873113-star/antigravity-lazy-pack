// 用 Playwright 錄製 index.html 畫面，輸出 webm 影片檔（無音訊）
// 之後 ffmpeg 再將其與主音軌合併
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  console.log('啟動 Chromium 瀏覽器進行渲染...');
  const browser = await chromium.launch({
    args: ['--autoplay-policy=no-user-gesture-required', '--mute-audio'],
  });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    recordVideo: { 
      dir: path.join(__dirname, 'renders'), 
      size: { width: 1920, height: 1080 } 
    },
  });
  const page = await context.newPage();
  
  // 開啟 render=true 模式 (自動繞過點擊遮罩並自動播放)
  const fileUrl = 'file:///' + path.join(__dirname, 'index.html').replace(/\\/g, '/') + '?render=true';
  console.log('載入頁面中:', fileUrl);
  await page.goto(fileUrl);
  
  // 等待字型完全載入與開始播放
  await page.waitForTimeout(1000);
  
  // 總片長約 108 秒，我們錄製 109 秒以留緩衝
  console.log('開始錄製影片 (長度 109 秒)...');
  await page.waitForTimeout(109000);
  
  await context.close();
  await browser.close();
  console.log('Playwright 錄影完成！');
})();
