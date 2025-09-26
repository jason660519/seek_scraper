import asyncio
import json
import logging
from pathlib import Path
from src.scrapers.playwright_scraper import PlaywrightScraper

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_improved_scraper():
    """測試改進後的爬蟲"""
    
    async with PlaywrightScraper() as scraper:
        # 測試搜索URL
        search_url = "https://www.seek.com.au/ai-machine-learning-data-scientist-jobs/in-Sydney-NSW"
        
        print(f"開始測試改進後的爬蟲...")
        print(f"搜索URL: {search_url}")
        
        # 導航到搜索頁面
        success = await scraper.navigate_to_url(search_url)
        if not success:
            print("導航失敗")
            return
        
        # 提取工作連結
        job_links = await scraper.extract_job_links()
        print(f"找到 {len(job_links)} 個工作連結")
        
        if job_links:
            # 保存連結
            links_data = {
                "total_links": len(job_links),
                "links": job_links[:10],  # 只保存前10個
                "timestamp": time.time()
            }
            
            with open("debug_output/improved_links.json", "w", encoding="utf-8") as f:
                json.dump(links_data, f, indent=2, ensure_ascii=False)
            
            print(f"前5個連結:")
            for i, link in enumerate(job_links[:5]):
                print(f"  {i+1}. {link}")
            
            # 測試提取詳細信息（第一個工作）
            if job_links:
                print(f"\n測試提取第一個工作的詳細信息...")
                first_job_url = job_links[0]
                
                # 創建輸出目錄
                output_dir = Path("debug_output/improved_job_details")
                output_dir.mkdir(exist_ok=True)
                
                # 提取詳細信息
                job_details = await scraper.scrape_job_details(first_job_url, str(output_dir))
                
                if job_details:
                    print(f"成功提取工作詳細信息: {job_details.get('title', '未知標題')}")
                    print(f"公司: {job_details.get('company', '未知公司')}")
                    print(f"地點: {job_details.get('location', '未知地點')}")
                else:
                    print("提取工作詳細信息失敗")
        
        # 提取總頁數
        total_pages = await scraper.extract_total_pages()
        print(f"\n總頁數: {total_pages}")
        
        print("\n測試完成！")

if __name__ == "__main__":
    import time
    asyncio.run(test_improved_scraper())