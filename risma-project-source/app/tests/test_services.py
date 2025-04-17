import pytest
from app.services.scraper import WebScraper
from app.services.data_processor import DataProcessor
import pandas as pd
import numpy as np

# WebScraperのテスト
class TestWebScraper:
    def setup_method(self):
        self.scraper = WebScraper()
    
    def test_parse_company_info(self):
        # テスト用のHTMLコンテンツ
        html_content = """
        <div class="company-card">
            <h2 class="company-name">株式会社テスト</h2>
            <p class="company-address">東京都千代田区1-1-1</p>
            <p class="company-tel">03-1234-5678</p>
            <a href="https://example.com" class="company-url">Webサイト</a>
        </div>
        """
        
        # 企業情報の抽出テスト
        company_info = self.scraper.parse_company_info(html_content)
        
        assert company_info is not None
        assert company_info.get('company_name') == '株式会社テスト'
        assert company_info.get('address') == '東京都千代田区1-1-1'
        assert company_info.get('tel') == '03-1234-5678'
        assert company_info.get('url') == 'https://example.com'
    
    def test_extract_industry_from_text(self):
        # 業種抽出のテスト
        text = "当社はIT・情報通信業界でシステム開発を行っています。"
        industry = self.scraper.extract_industry_from_text(text)
        
        assert industry is not None
        assert "IT" in industry or "情報通信" in industry
    
    def test_normalize_company_name(self):
        # 会社名の正規化テスト
        test_cases = [
            ("株式会社テスト", "株式会社テスト"),
            ("テスト（株）", "株式会社テスト"),
            ("テスト株式会社", "株式会社テスト"),
            ("㈱テスト", "株式会社テスト"),
            ("テスト(株)", "株式会社テスト")
        ]
        
        for input_name, expected_output in test_cases:
            assert self.scraper.normalize_company_name(input_name) == expected_output

# DataProcessorのテスト
class TestDataProcessor:
    def setup_method(self):
        self.processor = DataProcessor()
    
    def test_remove_duplicates(self):
        # 重複削除のテスト
        data = pd.DataFrame({
            'company_name': ['株式会社テスト', '株式会社サンプル', '株式会社テスト'],
            'tel': ['03-1234-5678', '03-8765-4321', '03-1234-5678'],
            'address': ['東京都千代田区', '東京都新宿区', '東京都千代田区']
        })
        
        result = self.processor.remove_duplicates(data)
        
        assert len(result) == 2
        assert 'company_name' in result.columns
        assert 'tel' in result.columns
        assert 'address' in result.columns
    
    def test_normalize_phone_numbers(self):
        # 電話番号の正規化テスト
        data = pd.DataFrame({
            'tel': ['03-1234-5678', '03(1234)5678', '０３１２３４５６７８', '03.1234.5678']
        })
        
        result = self.processor.normalize_phone_numbers(data)
        
        for phone in result['tel']:
            assert phone == '03-1234-5678'
    
    def test_normalize_addresses(self):
        # 住所の正規化テスト
        data = pd.DataFrame({
            'address': ['東京都千代田区丸の内１－１', '東京都千代田区丸の内1-1', 'Tokyo, Chiyoda-ku']
        })
        
        result = self.processor.normalize_addresses(data)
        
        for address in result['address']:
            assert '東京都千代田区丸の内' in address
    
    def test_filter_by_industry(self):
        # 業種フィルタリングのテスト
        data = pd.DataFrame({
            'company_name': ['株式会社テスト', '株式会社サンプル', '株式会社デモ'],
            'industry': ['IT・情報通信', '製造業', 'IT・情報通信']
        })
        
        result = self.processor.filter_by_industry(data, ['IT・情報通信'])
        
        assert len(result) == 2
        assert all(industry == 'IT・情報通信' for industry in result['industry'])
    
    def test_filter_by_location(self):
        # 地域フィルタリングのテスト
        data = pd.DataFrame({
            'company_name': ['株式会社テスト', '株式会社サンプル', '株式会社デモ'],
            'address': ['東京都千代田区', '大阪府大阪市', '東京都新宿区']
        })
        
        result = self.processor.filter_by_location(data, prefecture='東京都')
        
        assert len(result) == 2
        assert all('東京都' in address for address in result['address'])

if __name__ == "__main__":
    pytest.main(["-v", "test_services.py"])
