import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

async def cloudflare_bypass_test():
    """測試繞過 Cloudflare 保護"""
    
    async with async_playwright() as p:
        # 使用更真實的瀏覽器配置
        browser = await p.chromium.launch(
            headless=False,  # 無頭模式可能更容易被檢測
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-web-security',
                '--disable-features=BlockInsecurePrivateNetworkRequests',
                '--disable-features=OutOfBlinkCors',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        )
        
        # 設置更真實的用戶代理和視口
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='Australia/Sydney'
        )
        
        # 添加腳本來繞過檢測
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            window.chrome = {
                runtime: {},
                loadTimes: function() { return {}; }
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        page = await context.new_page()
        
        # 添加額外的等待和重試邏輯
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"嘗試 {attempt + 1}: 導航到 SEEK...")
                
                # 先訪問主頁
                await page.goto("https://www.seek.com.au", wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                
                # 檢查是否被重定向到驗證頁面
                if 'moment' in page.url or 'challenge' in page.url:
                    print("檢測到 Cloudflare 驗證頁面，等待...")
                    await page.wait_for_timeout(10000)  # 等待更長時間
                
                # 現在訪問搜索頁面
                search_url = "https://www.seek.com.au/ai-machine-learning-data-scientist-jobs/in-Sydney-NSW"
                await page.goto(search_url, wait_until="domcontentloaded")
                await page.wait_for_timeout(5000)
                
                # 保存頁面狀態
                await page.screenshot(path=f"debug_output/bypass_attempt_{attempt + 1}.png", full_page=True)
                html_content = await page.content()
                Path(f"debug_output/bypass_content_{attempt + 1}.html").write_text(html_content, encoding='utf-8')
                
                # 檢查頁面標題
                title = await page.title()
                print(f"頁面標題: {title}")
                
                if 'moment' not in title.lower() and 'just a moment' not in html_content.lower():
                    print("成功繞過驗證！")
                    break
                else:
                    print("仍在驗證頁面，重試...")
                    
            except Exception as e:
                print(f"嘗試 {attempt + 1} 失敗: {e}")
                if attempt == max_retries - 1:
                    raise
        
        # 測試連結提取
        print("\n測試連結提取:")
        
        # 方法1: 等待工作列表加載
        try:
            await page.wait_for_selector('article', timeout=10000)
            print("找到 article 元素")
        except:
            print("未找到 article 元素")
        
        # 方法2: 直接提取所有連結
        all_links = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                return links.map(link => ({
                    href: link.href,
                    text: link.textContent?.trim() || '',
                    className: link.className
                })).filter(link => link.href.includes('/job/'));
            }
        """)
        
        print(f"找到 {len(all_links)} 個工作連結")
        if all_links:
            # 保存所有連結
            Path("debug_output/all_job_links.json").write_text(
                json.dumps(all_links, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            print("前5個連結:")
            for link in all_links[:5]:
                print(f"  {link['href'][:80]}... - {link['text'][:50]}...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(cloudflare_bypass_test())