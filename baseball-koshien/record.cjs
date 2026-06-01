const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function main() {
  console.log("Starting Playwright recording for Baseball Koshien...");
  const browser = await chromium.launch({
    headless: true
  });
  
  const renderDir = path.join(__dirname, 'renders');
  if (!fs.existsSync(renderDir)){
    fs.mkdirSync(renderDir, { recursive: true });
  }

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: {
      dir: renderDir,
      size: { width: 1920, height: 1080 }
    }
  });

  const page = await context.newPage();
  
  // 載入本地 index.html
  const filePath = path.resolve(__dirname, 'index.html');
  console.log(`Navigating to: file://${filePath}`);
  await page.goto('file://' + filePath);
  
  // 等待頁面與字體載入完成
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => document.fonts.ready);
  
  // 啟動簡報
  console.log("Triggering startPresentation() in the browser...");
  await page.evaluate(() => {
    window.startPresentation();
  });
  
  // 9 個場景 * 5 秒 = 45 秒 (45000 ms) + 2000 ms 緩衝
  const totalDurationMs = 45000 + 2000;
  console.log(`Recording video for ${totalDurationMs / 1000} seconds...`);
  
  await page.waitForTimeout(totalDurationMs);
  
  // 獲取錄影檔案路徑
  const video = page.video();
  let videoPath = null;
  if (video) {
    videoPath = await video.path();
    console.log(`Raw video recorded to: ${videoPath}`);
  }
  
  await context.close();
  await browser.close();

  if (videoPath && fs.existsSync(videoPath)) {
    const destPath = path.join(renderDir, 'raw_recording.webm');
    fs.copyFileSync(videoPath, destPath);
    fs.unlinkSync(videoPath); // 刪除亂數名稱的原始檔
    console.log(`Successfully moved raw video to: ${destPath}`);
  } else {
    console.error("Error: Video file was not generated.");
  }
}

main().catch(err => {
  console.error("Recording script crashed:", err);
  process.exit(1);
});
