import requests
import time
import os
import json
import random
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd

# 爬取網站內容
def scrape_article(url, retries=3):
    """爬取單篇文章內容"""
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "zh-TW,zh;q=0.9"}
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            if response.status_code == 404:
                return None, "404 - 頁面不存在"
            if response.status_code != 200:
                return None, f"狀態碼: {response.status_code}"

            soup = BeautifulSoup(response.text, 'html.parser')

            # 抓取標題
            title_tag = soup.find('h1', class_='page-title')
            title = title_tag.get_text(strip=True) if title_tag else "標題缺失"

            # 抓取日期
            date_tag = soup.find('time') or soup.find('span', class_='date') or soup.find('div', class_='entity-list-date')
            date = date_tag.get_text(strip=True).replace("發布日期/", "").strip() if date_tag else "日期缺失"

            # 改善抓取內容
            possible_divs = ['node__content', 'article-content', 'content']
            content = None
            for div_class in possible_divs:
                content_div = soup.find('div', class_=div_class)
                if content_div:
                    content = '\n'.join(list(content_div.stripped_strings))
                    break

            if not content:
                content = '\n'.join([p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)])

            if not content:
                content = "內容缺失"

            return {"url": url, "title": title, "date": date, "content": content}, None
        except Exception as e:
            print(f"錯誤: {e}")
            time.sleep(3)
    return None, "連續失敗 3 次"

# 紀錄失敗頁面
def save_failed_log(fail_log_path, failed_ids):
    with open(fail_log_path, "a", encoding="utf-8") as f:
        for page_id in failed_ids:
            f.write(f"{page_id}\n")
    print(f"失敗記錄已紀錄於 {fail_log_path}")

# 主程式
def main():
    total_start = 5200 # 開始 ID
    total_end = 5201   # 結束 ID

    save_dir = r"C:\\Users\\Leon\\Desktop\\事實查核中心資料\\爬蟲資料"
    os.makedirs(save_dir, exist_ok=True)

    # 動態命名檔案，避免覆蓋
    json_file_name = f"tfc_articles_{total_start}_to_{total_end}.json"
    fail_log_name = f"failed_articles_{total_start}_to_{total_end}.txt"
    json_file_path = os.path.join(save_dir, json_file_name)
    fail_log_path = os.path.join(save_dir, fail_log_name)

    failed_ids = deque()
    articles = []

    print(f"輸出檔案名稱: {json_file_name}")
    
    # 清空已有檔案
    if os.path.exists(json_file_path):
        os.remove(json_file_path)

    for page_id in range(total_start, total_end + 1):
        url = f"https://tfc-taiwan.org.tw/articles/{page_id}"
        print(f"正在爬取 ID: {page_id}")
        data, error = scrape_article(url)

        if data:
            print(f"成功爬取: {data['title']} - {url}")
            articles.append(data)
            with open(json_file_path, 'a', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                f.write('\n')
        else:
            print(f"爬取失敗: {url} 原因: {error}")
            failed_ids.append(page_id)

        # 隨機休息
        wait_time = random.randint(5, 10)  # 減少等待時間範圍
        print(f"休息 {wait_time} 秒後繼續...")
        time.sleep(wait_time)

    save_failed_log(fail_log_path, failed_ids)

    # 使用 pandas 讀取 JSON 並顯示內容
    print("\n爬取完成，顯示所有結果:")
    df = pd.read_json(json_file_path, lines=True, encoding='utf-8')
    print(df)

if __name__ == "__main__":
    main()
