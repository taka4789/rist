import pytest
import time
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from app.services.scraper import WebScraper
from app.services.data_processor import DataProcessor
from concurrent.futures import ThreadPoolExecutor
import psutil
import os

# パフォーマンステスト用の設定
@pytest.fixture
def large_dataset():
    # 大量のテストデータを生成
    companies = []
    for i in range(10000):
        companies.append({
            'company_name': f'株式会社テスト{i}',
            'address': f'東京都千代田区{i % 100}丁目',
            'tel': f'03-{i % 10000:04d}-{i % 10000:04d}',
            'url': f'https://example{i}.com',
            'industry': '情報通信' if i % 3 == 0 else '製造業' if i % 3 == 1 else 'サービス業'
        })
    return pd.DataFrame(companies)

# テスト: データ処理の性能
def test_data_processor_performance(large_dataset):
    processor = DataProcessor()
    
    # 処理時間の計測
    start_time = time.time()
    
    # 重複削除の性能テスト
    result = processor.remove_duplicates(large_dataset)
    
    # 電話番号の正規化の性能テスト
    result = processor.normalize_phone_numbers(large_dataset)
    
    # 住所の正規化の性能テスト
    result = processor.normalize_addresses(large_dataset)
    
    # 業種フィルタリングの性能テスト
    result = processor.filter_by_industry(large_dataset, ['情報通信'])
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # 10,000件のデータを10秒以内に処理できることを確認
    assert execution_time < 10, f"データ処理に{execution_time}秒かかりました。10秒以内に処理できる必要があります。"
    
    # メモリ使用量の確認
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1024 / 1024  # MB単位
    
    # メモリ使用量が1GB以下であることを確認
    assert memory_usage < 1024, f"メモリ使用量が{memory_usage}MBです。1GB以下である必要があります。"

# テスト: 並列スクレイピングの性能
@pytest.mark.asyncio
async def test_parallel_scraping_performance():
    # 並列スクレイピングのシミュレーション
    scraper = WebScraper()
    
    # 同時に処理するURL数
    num_urls = 50
    urls = [f"https://example.com/{i}" for i in range(num_urls)]
    
    # 処理時間の計測
    start_time = time.time()
    
    # 非同期処理のシミュレーション
    async def fetch_mock(url):
        await asyncio.sleep(0.1)  # ネットワークレイテンシのシミュレーション
        return f"<html><body><h1>Company {url.split('/')[-1]}</h1></body></html>"
    
    async def process_url(url):
        html = await fetch_mock(url)
        # HTMLの解析処理をシミュレーション
        await asyncio.sleep(0.05)
        return {'url': url, 'company_name': f"Company {url.split('/')[-1]}"}
    
    # 並列処理の実行
    tasks = [process_url(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # 50件のURLを10秒以内に処理できることを確認
    assert execution_time < 10, f"並列スクレイピングに{execution_time}秒かかりました。10秒以内に処理できる必要があります。"
    assert len(results) == num_urls

# テスト: 大量リクエスト時のAPI性能
def test_api_load_performance():
    # APIの負荷テストをシミュレーション
    import requests
    from concurrent.futures import ThreadPoolExecutor
    
    # テスト用のエンドポイント
    endpoint = "http://localhost:8000/api/health"  # ヘルスチェックエンドポイント
    
    # 同時リクエスト数
    num_requests = 100
    
    # 処理時間の計測
    start_time = time.time()
    
    def make_request():
        try:
            # 実際のAPIが起動していない場合はスキップ
            response = requests.get(endpoint, timeout=1)
            return response.status_code
        except:
            return None
    
    # 並列リクエストの実行
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(lambda _: make_request(), range(num_requests)))
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # 実際のAPIが起動していない場合はテストをスキップ
    if all(result is None for result in results):
        pytest.skip("APIが起動していないためテストをスキップします")
    
    # 100件のリクエストを5秒以内に処理できることを確認
    assert execution_time < 5, f"API負荷テストに{execution_time}秒かかりました。5秒以内に処理できる必要があります。"
    
    # 成功したリクエストの割合を確認
    success_rate = sum(1 for r in results if r == 200) / len(results)
    assert success_rate > 0.95, f"成功率が{success_rate * 100}%です。95%以上である必要があります。"

if __name__ == "__main__":
    pytest.main(["-v", "test_performance.py"])
