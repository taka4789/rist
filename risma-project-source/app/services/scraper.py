import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
from urllib.parse import urlparse, urljoin, quote_plus
import re
import time
import random

logger = logging.getLogger(__name__)

class WebScraper:
    """
    Webスクレイピングを行うクラス
    """
    def __init__(self, max_concurrent_requests: int = 5, timeout: int = 30, delay_between_requests: float = 1.0):
        self.max_concurrent_requests = max_concurrent_requests
        self.timeout = timeout
        self.delay_between_requests = delay_between_requests
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
        # 検索エンジンのURLテンプレート
        self.search_engines = {
            "google": "https://www.google.com/search?q={query}&num=100",
            "bing": "https://www.bing.com/search?q={query}&count=50",
            "yahoo_japan": "https://search.yahoo.co.jp/search?p={query}&n=50",
        }
        # 電話帳サイトのURLテンプレート
        self.directory_sites = {
            "townpage": "https://itp.ne.jp/result/?keyword={query}",
            "navitime": "https://www.navitime.co.jp/category/search?keyword={query}",
        }
    
    async def search_by_keyword(self, keywords: List[str], max_results: int = 100, exclude_keywords: List[str] = None) -> List[Dict[str, Any]]:
        """
        キーワード検索を行い、企業情報を取得する
        """
        results = []
        search_urls = []
        
        # 検索クエリを生成
        for keyword in keywords:
            # 検索エンジン用のクエリ
            query = f"{keyword} 会社 企業 電話番号"
            for engine, url_template in self.search_engines.items():
                search_urls.append(url_template.format(query=quote_plus(query)))
            
            # 電話帳サイト用のクエリ
            for site, url_template in self.directory_sites.items():
                search_urls.append(url_template.format(query=quote_plus(keyword)))
        
        # 非同期でリクエストを実行
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # セマフォを使用して同時リクエスト数を制限
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            
            async def fetch_with_semaphore(url):
                async with semaphore:
                    # リクエスト間の遅延
                    await asyncio.sleep(self.delay_between_requests * (0.5 + random.random()))
                    return await self.fetch_search_results(session, url)
            
            tasks = [fetch_with_semaphore(url) for url in search_urls]
            search_results = await asyncio.gather(*tasks)
            
            # 検索結果から企業URLを抽出
            company_urls = []
            for result in search_results:
                extracted_urls = self.extract_company_urls(result)
                logger.info(f"Extracted {len(extracted_urls)} URLs from search result")
                company_urls.extend(extracted_urls)
            
            # 重複を削除
            company_urls = list(set(company_urls))
            logger.info(f"Total unique company URLs: {len(company_urls)}")
            
            # 最大結果数を制限
            company_urls = company_urls[:max_results * 2]  # 余裕を持って取得
            
            # 企業ページから情報を抽出
            company_tasks = []
            for url in company_urls:
                # リクエスト間の遅延
                await asyncio.sleep(self.delay_between_requests * random.random())
                company_tasks.append(self.fetch_company_info(session, url))
            
            company_results = await asyncio.gather(*company_tasks)
            
            # 有効な結果のみを追加
            for result in company_results:
                if result and "name" in result and result["name"]:
                    # 除外キーワードでフィルタリング
                    if exclude_keywords:
                        exclude = False
                        for keyword in exclude_keywords:
                            if keyword.lower() in result.get("name", "").lower():
                                exclude = True
                                break
                        if exclude:
                            continue
                    
                    results.append(result)
                    
                    # 最大結果数に達したら終了
                    if len(results) >= max_results:
                        break
        
        logger.info(f"Final company results: {len(results)}")
        return results
    
    async def search_by_industry_location(self, industry_codes: List[str], prefectures: Optional[List[str]] = None, 
                                         cities: Optional[List[str]] = None, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        業種と住所で検索を行い、企業情報を取得する
        """
        results = []
        search_urls = []
        
        # 検索クエリを生成
        for industry in industry_codes:
            location_terms = []
            if prefectures:
                location_terms.extend(prefectures)
            if cities:
                location_terms.extend(cities)
            
            location_str = " ".join(location_terms) if location_terms else "日本"
            
            # 検索エンジン用のクエリ
            query = f"{industry} {location_str} 会社 企業 電話番号"
            for engine, url_template in self.search_engines.items():
                search_urls.append(url_template.format(query=quote_plus(query)))
            
            # 電話帳サイト用のクエリ
            for site, url_template in self.directory_sites.items():
                if location_terms:
                    for location in location_terms:
                        combined_query = f"{industry} {location}"
                        search_urls.append(url_template.format(query=quote_plus(combined_query)))
                else:
                    search_urls.append(url_template.format(query=quote_plus(industry)))
        
        # 非同期でリクエストを実行
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # セマフォを使用して同時リクエスト数を制限
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            
            async def fetch_with_semaphore(url):
                async with semaphore:
                    # リクエスト間の遅延
                    await asyncio.sleep(self.delay_between_requests * (0.5 + random.random()))
                    return await self.fetch_search_results(session, url)
            
            tasks = [fetch_with_semaphore(url) for url in search_urls]
            search_results = await asyncio.gather(*tasks)
            
            # 検索結果から企業URLを抽出
            company_urls = []
            for result in search_results:
                extracted_urls = self.extract_company_urls(result)
                logger.info(f"Extracted {len(extracted_urls)} URLs from search result")
                company_urls.extend(extracted_urls)
            
            # 重複を削除
            company_urls = list(set(company_urls))
            logger.info(f"Total unique company URLs: {len(company_urls)}")
            
            # 最大結果数を制限
            company_urls = company_urls[:max_results * 2]  # 余裕を持って取得
            
            # 企業ページから情報を抽出
            company_tasks = []
            for url in company_urls:
                # リクエスト間の遅延
                await asyncio.sleep(self.delay_between_requests * random.random())
                company_tasks.append(self.fetch_company_info(session, url))
            
            company_results = await asyncio.gather(*company_tasks)
            
            # 有効な結果のみを追加
            for result in company_results:
                if result and "name" in result and result["name"]:
                    # 業種と住所でフィルタリング
                    if self.match_industry_location(result, industry_codes, prefectures, cities):
                        results.append(result)
                        
                        # 最大結果数に達したら終了
                        if len(results) >= max_results:
                            break
        
        logger.info(f"Final company results: {len(results)}")
        return results
    
    def match_industry_location(self, company: Dict[str, Any], industry_codes: List[str], 
                               prefectures: Optional[List[str]] = None, 
                               cities: Optional[List[str]] = None) -> bool:
        """
        企業情報が業種と住所の条件に一致するかチェックする
        """
        # 業種のマッチング
        industry_match = False
        if "industry" in company and company["industry"]:
            for code in industry_codes:
                if code.lower() in company["industry"].lower():
                    industry_match = True
                    break
        elif "industry_code" in company and company["industry_code"]:
            if company["industry_code"] in industry_codes:
                industry_match = True
        else:
            # 業種情報がない場合は、会社名や説明文から推測
            for code in industry_codes:
                if ("name" in company and code.lower() in company["name"].lower()) or \
                   ("description" in company and company["description"] and code.lower() in company["description"].lower()):
                    industry_match = True
                    break
        
        # 業種が一致しない場合は早期リターン
        if not industry_match:
            return False
        
        # 住所のマッチング（都道府県と市区町村）
        if not prefectures and not cities:
            # 住所条件がない場合は業種のみでマッチ
            return True
        
        location_match = False
        address = company.get("address", "")
        prefecture = company.get("prefecture", "")
        city = company.get("city", "")
        
        # 都道府県のマッチング
        if prefectures:
            if prefecture and prefecture in prefectures:
                # 都道府県が一致
                if not cities:
                    # 市区町村の指定がない場合は都道府県のみでマッチ
                    location_match = True
                elif city and city in cities:
                    # 市区町村も一致
                    location_match = True
            elif not prefecture and address:
                # 都道府県が取得できていない場合は住所全体で検索
                for pref in prefectures:
                    if pref in address:
                        if not cities:
                            # 市区町村の指定がない場合は都道府県のみでマッチ
                            location_match = True
                            break
                        else:
                            # 市区町村も検索
                            for c in cities:
                                if c in address:
                                    location_match = True
                                    break
                            if location_match:
                                break
        elif cities:
            # 都道府県の指定がなく、市区町村のみ指定
            if city and city in cities:
                location_match = True
            elif not city and address:
                # 市区町村が取得できていない場合は住所全体で検索
                for c in cities:
                    if c in address:
                        location_match = True
                        break
        
        return location_match
    
    async def fetch_search_results(self, session: aiohttp.ClientSession, url: str) -> str:
        """
        検索結果ページを取得する
        """
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.error(f"Error fetching search results: {response.status} - {url}")
                    return ""
        except Exception as e:
            logger.error(f"Exception during search request: {str(e)} - {url}")
            return ""
    
    def extract_company_urls(self, html_content: str) -> List[str]:
        """
        検索結果から企業URLを抽出する
        """
        if not html_content:
            return []
        
        urls = []
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Google検索結果からリンクを抽出
            for link in soup.select("a[href]"):
                href = link.get("href", "")
                
                # Google検索結果の形式
                if href.startswith("/url?q="):
                    href = href.split("/url?q=")[1].split("&")[0]
                
                # 相対URLを絶対URLに変換
                if href.startswith("/"):
                    base_url = self.extract_base_url(html_content)
                    if base_url:
                        href = urljoin(base_url, href)
                
                # 不要なURLを除外
                if self.is_valid_company_url(href):
                    urls.append(href)
        except Exception as e:
            logger.error(f"Error extracting company URLs: {str(e)}")
        
        return urls
    
    def extract_base_url(self, html_content: str) -> Optional[str]:
        """
        HTMLからベースURLを抽出する
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # <base> タグからURLを取得
            base_tag = soup.find("base", href=True)
            if base_tag:
                return base_tag["href"]
            
            # <meta property="og:url"> からURLを取得
            og_url = soup.find("meta", property="og:url")
            if og_url and og_url.get("content"):
                return og_url["content"]
            
            # URLを含む可能性のあるタグから検索
            canonical = soup.find("link", rel="canonical")
            if canonical and canonical.get("href"):
                return canonical["href"]
            
            # ページ内の最初のリンクからドメインを推測
            first_link = soup.find("a", href=True)
            if first_link:
                href = first_link["href"]
                if href.startswith("http"):
                    parsed = urlparse(href)
                    return f"{parsed.scheme}://{parsed.netloc}"
        except Exception as e:
            logger.error(f"Error extracting base URL: {str(e)}")
        
        return None
    
    def is_valid_company_url(self, url: str) -> bool:
        """
        有効な企業URLかどうかを判定する
        """
        # 無効なURLを除外
        invalid_domains = [
            "google.com", "youtube.com", "facebook.com", "twitter.com", 
            "instagram.com", "linkedin.com", "wikipedia.org", "amazon.co.jp",
            "amazon.com", "rakuten.co.jp", "yahoo.co.jp", "bing.com",
            "microsoft.com", "apple.com", "github.com", "gitlab.com",
            "bitbucket.org", "stackoverflow.com", "qiita.com", "note.com"
        ]
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # 無効なドメインを除外
            for invalid in invalid_domains:
                if invalid in domain:
                    return False
            
            # 有効なスキームとドメインを持つURLのみ
            return parsed.scheme in ["http", "https"] and domain and "." in domain
        except:
            return False
    
    async def fetch_company_info(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """
        企業ページから情報を抽出する
        """
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    return self.extract_company_data(html, url)
                else:
                    logger.error(f"Error fetching company page: {response.status} - {url}")
                    return {}
        except Exception as e:
            logger.error(f"Exception during company page request: {str(e)} - {url}")
            return {}
    
    def extract_company_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        HTMLから企業情報を抽出する
        """
        if not html_content:
            return {}
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # 基本情報を初期化
            company_data = {
                "name": "",
                "address": "",
                "phone": "",
                "email": "",
                "website": url,
                "industry": "",
                "prefecture": "",
                "city": "",
                "representative": "",
                "established_year": None,
                "capital": None,
                "employees": None,
                "annual_revenue": None,
                "has_fax": False,
                "has_contact_form": False,
                "source_url": url,
                "description": ""
            }
            
            # タイトルから会社名を推測
            title = soup.title.text if soup.title else ""
            if title:
                company_data["name"] = self.clean_company_name(title)
            
            # メタデータから情報を抽出
            meta_description = soup.find("meta", {"name": "description"})
            if meta_description and meta_description.get("content"):
                description = meta_description["content"]
                company_data["description"] = description
                
                # 説明文から電話番号を抽出
                phone = self.extract_phone_number(description)
                if phone:
                    company_data["phone"] = phone
            
            # OGPから情報を抽出
            og_title = soup.find("meta", {"property": "og:title"})
            if og_title and og_title.get("content") and not company_data["name"]:
                company_data["name"] = self.clean_company_name(og_title["content"])
            
            og_description = soup.find("meta", {"property": "og:description"})
            if og_description and og_description.get("content") and not company_data["description"]:
                company_data["description"] = og_description["content"]
            
            # 会社名を探す（h1, h2タグなど）
            if not company_data["name"]:
                for tag in ["h1", "h2", "h3"]:
                    elements = soup.find_all(tag)
                    for element in elements:
                        text = element.get_text().strip()
                        if text and len(text) < 50:  # 短いテキストのみ
                            company_data["name"] = self.clean_company_name(text)
                            break
                    if company_data["name"]:
                        break
            
            # 電話番号を探す
            phone_patterns = [
                r"電話番号", r"TEL", r"Tel", r"tel", r"電話", r"お問い合わせ", r"連絡先"
            ]
            for pattern in phone_patterns:
                elements = soup.find_all(text=lambda text: text and pattern in text)
                for element in elements:
                    parent = element.parent
                    # 親要素とその周辺のテキストを確認
                    surrounding_text = parent.get_text() if parent else ""
                    phone = self.extract_phone_number(surrounding_text)
                    if phone:
                        company_data["phone"] = phone
                        break
                if company_data["phone"]:
                    break
            
            # 住所を探す
            address_patterns = [
                r"住所", r"所在地", r"本社", r"支社", r"オフィス", r"事務所"
            ]
            for pattern in address_patterns:
                elements = soup.find_all(text=lambda text: text and pattern in text)
                for element in elements:
                    parent = element.parent
                    # 親要素とその周辺のテキストを確認
                    surrounding_text = parent.get_text() if parent else ""
                    address = self.extract_address(surrounding_text)
                    if address:
                        company_data["address"] = address
                        # 住所から都道府県と市区町村を抽出
                        prefecture, city = self.extract_prefecture_city(address)
                        if prefecture:
                            company_data["prefecture"] = prefecture
                        if city:
                            company_data["city"] = city
                        break
                if company_data["address"]:
                    break
            
            # メールアドレスを探す
            email_elements = soup.select("a[href^='mailto:']")
            if email_elements:
                email = email_elements[0]["href"].replace("mailto:", "")
                company_data["email"] = email
            
            # 代表者名を探す
            representative_patterns = [
                r"代表", r"社長", r"CEO", r"代表取締役"
            ]
            for pattern in representative_patterns:
                elements = soup.find_all(text=lambda text: text and pattern in text)
                for element in elements:
                    parent = element.parent
                    # 親要素とその周辺のテキストを確認
                    surrounding_text = parent.get_text() if parent else ""
                    representative = self.extract_representative(surrounding_text)
                    if representative:
                        company_data["representative"] = representative
                        break
                if company_data["representative"]:
                    break
            
            # 設立年を探す
            established_patterns = [
                r"設立", r"創業", r"創立"
            ]
            for pattern in established_patterns:
                elements = soup.find_all(text=lambda text: text and pattern in text)
                for element in elements:
                    parent = element.parent
                    # 親要素とその周辺のテキストを確認
                    surrounding_text = parent.get_text() if parent else ""
                    year = self.extract_year(surrounding_text)
                    if year:
                        company_data["established_year"] = year
                        break
                if company_data["established_year"]:
                    break
            
            # 資本金を探す
            capital_patterns = [
                r"資本金"
            ]
            for pattern in capital_patterns:
                elements = soup.find_all(text=lambda text: text and pattern in text)
                for element in elements:
                    parent = element.parent
                    # 親要素とその周辺のテキストを確認
                    surrounding_text = parent.get_text() if parent else ""
                    capital = self.extract_capital(surrounding_text)
                    if capital:
                        company_data["capital"] = capital
                        break
                if company_data["capital"]:
                    break
            
            # 従業員数を探す
            employees_patterns = [
                r"従業員", r"社員", r"人数", r"スタッフ"
            ]
            for pattern in employees_patterns:
                elements = soup.find_all(text=lambda text: text and pattern in text)
                for element in elements:
                    parent = element.parent
                    # 親要素とその周辺のテキストを確認
                    surrounding_text = parent.get_text() if parent else ""
                    employees = self.extract_employees(surrounding_text)
                    if employees:
                        company_data["employees"] = employees
                        break
                if company_data["employees"]:
                    break
            
            # 業種を探す
            industry_patterns = [
                r"業種", r"事業内容", r"業界"
            ]
            for pattern in industry_patterns:
                elements = soup.find_all(text=lambda text: text and pattern in text)
                for element in elements:
                    parent = element.parent
                    # 親要素とその周辺のテキストを確認
                    surrounding_text = parent.get_text() if parent else ""
                    industry = self.extract_industry(surrounding_text)
                    if industry:
                        company_data["industry"] = industry
                        break
                if company_data["industry"]:
                    break
            
            # FAXの有無を確認
            fax_patterns = [r"FAX", r"Fax", r"fax", r"ファックス"]
            company_data["has_fax"] = any(pattern in html_content for pattern in fax_patterns)
            
            # 問い合わせフォームの有無を確認
            contact_patterns = [r"お問い合わせ", r"Contact", r"contact", r"問い合わせ", r"フォーム"]
            form_tags = soup.find_all("form")
            company_data["has_contact_form"] = len(form_tags) > 0 or any(pattern in html_content for pattern in contact_patterns)
            
            return company_data
        
        except Exception as e:
            logger.error(f"Error extracting company data: {str(e)} - {url}")
            return {}
    
    def clean_company_name(self, text: str) -> str:
        """
        テキストから会社名を抽出・クリーニングする
        """
        # 会社名の後ろについている可能性のある不要な文字列
        suffixes = [
            "株式会社", "有限会社", "合同会社", "公式サイト", "公式ホームページ", 
            "オフィシャルサイト", "ホーム", "トップ", "- ", " | ", "｜"
        ]
        
        # 不要な文字列を削除
        name = text
        for suffix in suffixes:
            name = name.replace(suffix, "")
        
        # 前後の空白を削除
        name = name.strip()
        
        # 会社名が短すぎる場合は元のテキストを使用
        if len(name) < 2:
            # 株式会社などの文字列を前に移動
            for company_type in ["株式会社", "有限会社", "合同会社"]:
                if company_type in text:
                    return company_type + text.replace(company_type, "").strip()
            return text.strip()
        
        return name
    
    def extract_phone_number(self, text: str) -> str:
        """
        テキストから電話番号を抽出する
        """
        # 電話番号のパターン
        patterns = [
            r"0\d{1,4}[-(]?\d{1,4}[-)]*\d{4}",  # 一般的な電話番号
            r"0120[-(]?\d{3}[-)]*\d{3}",        # フリーダイヤル
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # 最初にマッチした電話番号を返す
                phone = matches[0]
                # 区切り文字を統一
                phone = re.sub(r"[^\d]", "-", phone)
                return phone
        
        return ""
    
    def extract_address(self, text: str) -> str:
        """
        テキストから住所を抽出する
        """
        # 都道府県のリスト
        prefectures = [
            "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
            "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
            "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
            "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
            "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
            "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
            "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
        ]
        
        # 都道府県から始まる住所を探す
        for prefecture in prefectures:
            pattern = f"{prefecture}[^\n。、]{5,50}"
            matches = re.findall(pattern, text)
            if matches:
                # 最初にマッチした住所を返す
                address = matches[0]
                # 不要な文字を削除
                address = re.sub(r"[「」『』【】\(\)]", "", address)
                return address
        
        # 郵便番号から始まる住所を探す
        zip_pattern = r"〒?\d{3}[-－]?\d{4}[^\n。、]{5,50}"
        matches = re.findall(zip_pattern, text)
        if matches:
            address = matches[0]
            address = re.sub(r"[「」『』【】\(\)]", "", address)
            return address
        
        return ""
    
    def extract_prefecture_city(self, address: str) -> tuple:
        """
        住所から都道府県と市区町村を抽出する
        """
        # 都道府県のリスト
        prefectures = [
            "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
            "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
            "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
            "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
            "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
            "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
            "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
        ]
        
        prefecture = ""
        city = ""
        
        # 都道府県を抽出
        for pref in prefectures:
            if pref in address:
                prefecture = pref
                # 都道府県の後の文字列を取得
                after_pref = address[address.index(pref) + len(pref):]
                
                # 市区町村を抽出
                city_match = re.search(r"([^\s]{2,6}[市区町村])", after_pref)
                if city_match:
                    city = city_match.group(1)
                
                break
        
        return prefecture, city
    
    def extract_representative(self, text: str) -> str:
        """
        テキストから代表者名を抽出する
        """
        # 代表者名のパターン
        patterns = [
            r"代表[者取締役社員].*?[:：]?\s*([^\s\d]{2,10})",
            r"社長.*?[:：]?\s*([^\s\d]{2,10})",
            r"CEO.*?[:：]?\s*([^\s\d]{2,10})"
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text)
            if matches:
                return matches.group(1).strip()
        
        return ""
    
    def extract_year(self, text: str) -> Optional[int]:
        """
        テキストから設立年を抽出する
        """
        # 設立年のパターン
        patterns = [
            r"設立.*?(\d{4})年",
            r"創業.*?(\d{4})年",
            r"創立.*?(\d{4})年",
            r"(\d{4})年.*?設立",
            r"(\d{4})年.*?創業",
            r"(\d{4})年.*?創立"
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text)
            if matches:
                try:
                    year = int(matches.group(1))
                    # 妥当な年かチェック
                    if 1800 <= year <= 2025:
                        return year
                except:
                    pass
        
        # 和暦の場合
        era_patterns = [
            r"昭和(\d{1,2})年",  # 昭和
            r"平成(\d{1,2})年",  # 平成
            r"令和(\d{1,2})年"   # 令和
        ]
        
        for i, pattern in enumerate(era_patterns):
            matches = re.search(pattern, text)
            if matches:
                try:
                    era_year = int(matches.group(1))
                    # 和暦を西暦に変換
                    if i == 0:  # 昭和
                        year = 1925 + era_year
                    elif i == 1:  # 平成
                        year = 1988 + era_year
                    else:  # 令和
                        year = 2018 + era_year
                    
                    # 妥当な年かチェック
                    if 1800 <= year <= 2025:
                        return year
                except:
                    pass
        
        return None
    
    def extract_capital(self, text: str) -> Optional[int]:
        """
        テキストから資本金を抽出する（単位：万円）
        """
        # 資本金のパターン
        patterns = [
            r"資本金.*?(\d[\d,，\.．]*)億?千?万?円",
            r"資本金.*?(\d[\d,，\.．]*)億?千?万?円"
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text)
            if matches:
                try:
                    # カンマや句読点を削除
                    amount_str = re.sub(r"[,，\.．]", "", matches.group(1))
                    amount = int(amount_str)
                    
                    # 単位を考慮
                    if "億" in text:
                        amount *= 10000  # 億円 → 万円
                    elif "千万" in text:
                        amount *= 1000  # 千万円 → 万円
                    elif "万" not in text:
                        amount //= 10000  # 円 → 万円
                    
                    return amount
                except:
                    pass
        
        return None
    
    def extract_employees(self, text: str) -> Optional[int]:
        """
        テキストから従業員数を抽出する
        """
        # 従業員数のパターン
        patterns = [
            r"従業員.*?(\d[\d,，]*)名?人?",
            r"社員.*?(\d[\d,，]*)名?人?",
            r"スタッフ.*?(\d[\d,，]*)名?人?",
            r"(\d[\d,，]*)名?人?.*?従業員",
            r"(\d[\d,，]*)名?人?.*?社員",
            r"(\d[\d,，]*)名?人?.*?スタッフ"
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text)
            if matches:
                try:
                    # カンマを削除
                    employees_str = re.sub(r"[,，]", "", matches.group(1))
                    employees = int(employees_str)
                    
                    # 妥当な数かチェック
                    if 1 <= employees <= 1000000:
                        return employees
                except:
                    pass
        
        return None
    
    def extract_industry(self, text: str) -> str:
        """
        テキストから業種を抽出する
        """
        # 業種のパターン
        patterns = [
            r"業種.*?[:：]?\s*([^\n。、]{2,30})",
            r"事業内容.*?[:：]?\s*([^\n。、]{2,30})",
            r"業界.*?[:：]?\s*([^\n。、]{2,30})"
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text)
            if matches:
                return matches.group(1).strip()
        
        return ""
