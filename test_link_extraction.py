import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

async def simple_link_test():
    """簡單的連結提取測試"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://www.seek.com.au/ai-machine-learning-data-scientist-jobs/in-Sydney-NSW"
        print(f"導航到: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)  # 增加等待時間
        
        # 保存截圖和HTML
        await page.screenshot(path="debug_output/page_screenshot.png", full_page=True)
        html_content = await page.content()
        Path("debug_output/page_content.html").write_text(html_content, encoding='utf-8')
        print("已保存截圖和HTML內容")
        
        # 測試不同的提取方法
        methods = [
            {
                "name": "原始方法",
                "script": """
                    () => {
                        const links = [];
                        const jobElements = document.querySelectorAll('a[href*="/job/"]');
                        jobElements.forEach(element => {
                            if (element.href && !element.href.includes('type=promoted')) {
                                links.push(element.href);
                            }
                        });
                        return [...new Set(links)];
                    }
                """
            },
            {
                "name": "改進方法1 - 有文本內容",
                "script": """
                    () => {
                        const links = [];
                        const jobElements = document.querySelectorAll('a[href*="/job/"]');
                        jobElements.forEach(element => {
                            if (element.href && 
                                !element.href.includes('type=promoted') && 
                                element.textContent && 
                                element.textContent.trim()) {
                                links.push(element.href);
                            }
                        });
                        return [...new Set(links)];
                    }
                """
            },
            {
                "name": "改進方法2 - cardTitle",
                "script": """
                    () => {
                        const links = [];
                        const jobElements = document.querySelectorAll('a[href*="/job/"]');
                        jobElements.forEach(element => {
                            if (element.href && 
                                !element.href.includes('type=promoted') && 
                                element.href.includes('origin=cardTitle')) {
                                links.push(element.href);
                            }
                        });
                        return [...new Set(links)];
                    }
                """
            },
            {
                "name": "改進方法3 - 兩者結合",
                "script": """
                    () => {
                        const links = [];
                        const jobElements = document.querySelectorAll('a[href*="/job/"]');
                        jobElements.forEach(element => {
                            if (element.href && 
                                !element.href.includes('type=promoted') && 
                                element.textContent && 
                                element.textContent.trim() &&
                                element.href.includes('origin=cardTitle')) {
                                links.push(element.href);
                            }
                        });
                        return [...new Set(links)];
                    }
                """
            }
        ]
        
        for method in methods:
            try:
                result = await page.evaluate(method["script"])
                print(f"{method['name']}: 找到 {len(result)} 個連結")
                if result:
                    print(f"  前3個: {result[:3]}")
            except Exception as e:
                print(f"{method['name']}: 錯誤 - {e}")
        
        # 測試選擇器是否存在
        print("\n測試選擇器:")
        selectors = [
            'a[href*="/job/"]',
            'a[data-automation="jobTitle"]',
            'a[href*="/job/"][href*="origin=cardTitle"]'
        ]
        
        for selector in selectors:
            count = await page.locator(selector).count()
            print(f"{selector}: {count} 個元素")
            
            if count > 0:
                # 獲取第一個元素的屬性
                element = page.locator(selector).first
                href = await element.get_attribute('href')
                text = await element.text_content()
                print(f"  示例: href='{href[:80]}...', text='{text[:50]}...'")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_link_test())