import requests  # 引入 requests 模組用於發送 HTTP 請求
from bs4 import BeautifulSoup  # 引入 BeautifulSoup 模組用於解析 HTML
import pandas as pd  # 引入 pandas 模組用於數據處理和保存
import time  # 引入 time 模組用於程式暫停和等待
import os  # 引入 os 模組用於檔案和目錄操作
from google.cloud import storage  # 引入 GCS 客戶端模組用於上傳檔案到 Google Cloud Storage

# GCS (Google Cloud Storage) 上傳函數
def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """
    將本地檔案上傳到 GCS (Google Cloud Storage)。
    :param bucket_name: GCS 儲存桶名稱
    :param source_file_name: 本地檔案路徑
    :param destination_blob_name: 上傳至 GCS 的目標檔案名稱
    """
    if not os.path.exists(source_file_name):  # 檢查本地檔案是否存在
        print(f"檔案不存在: {source_file_name}")
        return

    storage_client = storage.Client()  # 建立 GCS 客戶端
    bucket = storage_client.bucket(bucket_name)  # 取得目標 GCS 儲存桶
    blob = bucket.blob(destination_blob_name)  # 設定要上傳的檔案名稱

    try:
        blob.upload_from_filename(source_file_name)  # 上傳本地檔案至 GCS
        print(f"文件 {source_file_name} 已上傳至 {bucket_name}/{destination_blob_name}")
    except Exception as e:
        print(f"上傳失敗: {e}")  # 上傳失敗時顯示錯誤訊息

# 追加寫入日誌函數
def append_to_log(file_path, record):
    """
    追加單筆記錄至 CSV 檔案中。
    :param file_path: CSV 檔案路徑
    :param record: 要寫入的記錄，字典格式
    """
    df = pd.DataFrame([record])  # 將記錄轉換成 DataFrame
    df.to_csv(file_path, mode="a", header=not os.path.exists(file_path), index=False)  # 追加寫入，不覆蓋原內容

# 爬取單篇文章內容
def scrape_article(url, retries=3):
    """
    嘗試爬取指定 URL 的文章內容，最多重試 3 次。
    :param url: 文章的 URL
    :param retries: 最大重試次數
    :return: 成功爬取返回字典，失敗返回 None 和錯誤信息
    """
    headers = {  # 設定 HTTP 請求頭，模擬正常瀏覽器訪問
        "User-Agent": "Mozilla/5.0",  # 設定用戶代理
        "Accept-Language": "zh-TW,zh;q=0.9"  # 設定語言偏好
    }
    for attempt in range(retries):  # 重試機制，最多重試 retries 次
        try:
            response = requests.get(url, headers=headers, timeout=10)  # 發送 HTTP GET 請求
            response.encoding = 'utf-8'  # 設定響應內容的編碼格式

            if response.status_code == 404:  # 如果頁面不存在 (HTTP 404)
                print(f"頁面不存在 {url}，狀態碼: 404")
                return None, "404 - 頁面不存在"

            if response.status_code != 200:  # 其他 HTTP 錯誤狀態碼
                print(f"無法訪問頁面 {url}，狀態碼: {response.status_code}")
                return None, f"狀態碼: {response.status_code}"

            soup = BeautifulSoup(response.text, 'html.parser')  # 使用 BeautifulSoup 解析 HTML 內容
            title_tag = soup.find('h1', class_='page-title')  # 提取文章標題
            title = title_tag.get_text(strip=True) if title_tag else "標題缺失"  # 處理標題缺失情況

            date_tag = (  # 提取文章日期
                soup.find('time') or  
                soup.find('span', class_='date') or 
                soup.find('div', class_='entity-list-date')
            )
            date = date_tag.get_text(strip=True).replace("發布日期／", "").strip() if date_tag else "日期缺失"

            content_div = soup.find('div', class_='node__content')  # 提取文章內容區塊
            content = '\n'.join([p.get_text(strip=True) for p in content_div.find_all('p')]) if content_div else "內容缺失"

            return {"url": url, "title": title, "date": date, "content": content}, None  # 返回文章內容
        except Exception as e:  # 異常處理
            print(f"嘗試第 {attempt + 1} 次爬取失敗: {e}")
            time.sleep(3)  # 等待 3 秒後重試
    return None, "連續失敗 3 次"  # 如果多次重試失敗，返回錯誤信息

# 主邏輯
def main():
    """
    主程式：依照文章 ID 範圍爬取文章內容，
    每 50 篇保存成 Excel 檔案，並記錄爬取失敗和被跳過的文章。
    """
    start_id = 4889  # 起始文章 ID
    end_id = 4900  # 結束文章 ID
    base_url = "https://tfc-taiwan.org.tw/articles/"  # 文章的基本 URL
    bucket_name = "fakenewsbda"  # GCS 儲存桶名稱
    temp_dir = "/tmp"  # 本地暫存檔案目錄

    all_articles = []  # 保存成功爬取的文章
    failure_count = 0  # 連續失敗計數
    max_failures = 10  # 設定最大連續失敗次數
    wait_time_failures = 3600  # 連續失敗後的等待時間（1 小時）
    wait_time_save = 1800  # 每 50 篇保存後的等待時間（30 分鐘）

    fail_log_path = os.path.join(temp_dir, "failed_articles.csv")  # 失敗日誌檔案路徑
    skipped_log_path = os.path.join(temp_dir, "skipped_articles.csv")  # 跳過日誌檔案路徑

    while start_id <= end_id:
        url = f"{base_url}{start_id}"  # 生成文章 URL
        print(f"正在爬取文章 ID: {start_id}")
        data, error = scrape_article(url)  # 嘗試爬取文章內容

        if data:  # 成功爬取文章
            all_articles.append(data)
            failure_count = 0  # 重置失敗計數
        elif error == "404 - 頁面不存在":  # 處理被跳過的文章
            print(f"文章 ID {start_id} 被跳過 (404)")
            append_to_log(skipped_log_path, {"id": start_id, "url": url, "reason": error})
        else:  # 記錄失敗文章
            print(f"文章 ID {start_id} 爬取失敗，原因: {error}")
            append_to_log(fail_log_path, {"id": start_id, "url": url, "reason": error})
            failure_count += 1

        if failure_count >= max_failures:  # 若連續失敗達到上限，休息 1 小時
            print(f"連續失敗 {max_failures} 次，休息 1 小時後繼續...")
            time.sleep(wait_time_failures)
            failure_count = 0

        if len(all_articles) >= 50:  # 每 50 篇保存成功的文章
            file_name = f"tfc_articles_{start_id-49}_to_{start_id}.xlsx"
            file_path = os.path.join(temp_dir, file_name)
            try:
                df = pd.DataFrame(all_articles)  # 將成功文章轉為 DataFrame
                df.to_excel(file_path, index=False, engine='openpyxl')  # 保存為 Excel
                print(f"成功文章已保存: {file_path}")
                upload_to_gcs(bucket_name, file_path, file_name)  # 上傳至 GCS
            except Exception as e:
                print(f"保存失敗: {e}")
            all_articles = []  # 清空緩存
            print("保存完畢，休息 30 分鐘...")
            time.sleep(wait_time_save)

        time.sleep(12)  # 符合 robots.txt 規定，等待 12 秒
        start_id += 1  # 文章 ID 增加

    print("所有文章爬取完成！")

if __name__ == "__main__":
    main()  # 執行主程式
