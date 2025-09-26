import asyncio
import json
import time
from pathlib import Path
from playwright.async_api import async_playwright

async def debug_page_content():
    """調試頁面內容提取"""
    
    # 創建輸出目錄
    output_dir = Path("debug_output")
    output_dir.mkdir(exist_ok=True)
    
    async with async_playwright() as p:
        # 啟動瀏覽器
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 導航到 SEEK 搜索頁面
        url = "https://www.seek.com.au/ai-machine-learning-data-scientist-jobs/in-Sydney-NSW"
        print(f"導航到: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        
        # 等待一點時間讓頁面加載
        await page.wait_for_timeout(3000)
        
        # 保存頁面內容
        html_content = await page.content()
        html_path = output_dir / "debug_page.html"
        html_path.write_text(html_content, encoding='utf-8')
        print(f"頁面 HTML 已保存到: {html_path}")
        
        # 保存截圖
        screenshot_path = output_dir / "debug_screenshot.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"頁面截圖已保存到: {screenshot_path}")
        
        # 測試不同的選擇器
        print("\n測試不同的選擇器:")
        
        # 測試工作連結選擇器
        job_links = await page.evaluate("""
            () => {
                const links = [];
                const jobElements = document.querySelectorAll('a[href*="/job/"]');
                jobElements.forEach(element => {
                    if (element.href && !element.href.includes('type=promoted')) {
                        links.push({
                            href: element.href,
                            text: element.textContent?.trim() || '',
                            className: element.className
                        });
                    }
                });
                return links;
            }
        """)
        
        print(f"找到 {len(job_links)} 個工作連結:")
        for i, link in enumerate(job_links[:5]):  # 只顯示前5個
            print(f"  {i+1}. {link['text'][:50]}... -> {link['href'][:80]}...")
        
        # 測試其他可能的選擇器
        other_selectors = [
            'a[data-automation="jobTitle"]',
            'a[data-automation="jobLink"]',
            'h3 a[href*="/job/"]',
            'article a[href*="/job/"]',
            '[data-automation="jobListing"] a[href*="/job/"]'
        ]
        
        for selector in other_selectors:
            elements = await page.query_selector_all(selector)
            print(f"\n選擇器 '{selector}' 找到 {len(elements)} 個元素")
            
            if elements:
                # 獲取前3個元素的信息
                for i, element in enumerate(elements[:3]):
                    href = await element.get_attribute('href')
                    text = await element.text_content()
                    print(f"  {i+1}. {text[:50]}... -> {href[:80] if href else '無 href'}")
        
        # 保存所有連結到 JSON
        all_links_path = output_dir / "debug_all_links.json"
        all_links_path.write_text(json.dumps(job_links, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"\n所有連結已保存到: {all_links_path}")
        
        await browser.close()
        print("\n瀏覽器已關閉")

if __name__ == "__main__":
    asyncio.run(debug_page_content())