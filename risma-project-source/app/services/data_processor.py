import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any, Optional, Set
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    企業データの処理・クレンジングを行うクラス
    """
    def __init__(self):
        # 法人格の正規化パターン
        self.company_suffixes = {
            r'株式会社': '(株)',
            r'有限会社': '(有)',
            r'合同会社': '(同)',
            r'一般社団法人': '(一社)',
            r'公益社団法人': '(公社)',
            r'一般財団法人': '(一財)',
            r'公益財団法人': '(公財)',
            r'社会福祉法人': '(福)',
            r'医療法人': '(医)',
            r'学校法人': '(学)',
            r'宗教法人': '(宗)',
            r'特定非営利活動法人': 'NPO法人',
        }
        
        # 都道府県の正規化
        self.prefecture_mapping = {
            '北海道': '北海道', '青森': '青森県', '岩手': '岩手県', '宮城': '宮城県',
            '秋田': '秋田県', '山形': '山形県', '福島': '福島県', '茨城': '茨城県',
            '栃木': '栃木県', '群馬': '群馬県', '埼玉': '埼玉県', '千葉': '千葉県',
            '東京': '東京都', '神奈川': '神奈川県', '新潟': '新潟県', '富山': '富山県',
            '石川': '石川県', '福井': '福井県', '山梨': '山梨県', '長野': '長野県',
            '岐阜': '岐阜県', '静岡': '静岡県', '愛知': '愛知県', '三重': '三重県',
            '滋賀': '滋賀県', '京都': '京都府', '大阪': '大阪府', '兵庫': '兵庫県',
            '奈良': '奈良県', '和歌山': '和歌山県', '鳥取': '鳥取県', '島根': '島根県',
            '岡山': '岡山県', '広島': '広島県', '山口': '山口県', '徳島': '徳島県',
            '香川': '香川県', '愛媛': '愛媛県', '高知': '高知県', '福岡': '福岡県',
            '佐賀': '佐賀県', '長崎': '長崎県', '熊本': '熊本県', '大分': '大分県',
            '宮崎': '宮崎県', '鹿児島': '鹿児島県', '沖縄': '沖縄県'
        }
        
        # 業種コードマッピング
        self.industry_code_mapping = {
            'IT・情報通信': '233',
            'メーカー': '210',
            '商社': '220',
            '小売': '221',
            '金融': '240',
            '保険': '241',
            '不動産': '250',
            '建設': '251',
            '運輸・物流': '260',
            'マスコミ': '270',
            '広告・マーケティング': '271',
            'コンサルティング': '280',
            '人材・教育': '290',
            '医療・福祉': '300',
            '飲食・宿泊': '310',
            'サービス': '320',
            '公的機関': '330',
            'その他': '999'
        }
    
    def normalize_company_data(self, company_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        企業データを正規化する
        """
        normalized_data = []
        
        for company_data in company_data_list:
            if not company_data or not company_data.get("name"):
                continue
            
            normalized = company_data.copy()
            
            # 会社名の正規化
            if "name" in normalized:
                normalized["name"] = self.normalize_company_name(normalized["name"])
            
            # 電話番号の正規化
            if "phone" in normalized:
                normalized["phone"] = self.normalize_phone_number(normalized["phone"])
            
            # 住所の正規化
            if "address" in normalized:
                normalized["address"] = self.normalize_address(normalized["address"])
                
                # 都道府県と市区町村の抽出
                if not normalized.get("prefecture") or not normalized.get("city"):
                    prefecture, city = self.extract_prefecture_city(normalized["address"])
                    if prefecture and not normalized.get("prefecture"):
                        normalized["prefecture"] = prefecture
                    if city and not normalized.get("city"):
                        normalized["city"] = city
            
            # 業種の正規化と業種コードの設定
            if "industry" in normalized and normalized["industry"]:
                normalized["industry"] = self.normalize_industry(normalized["industry"])
                if not normalized.get("industry_code"):
                    normalized["industry_code"] = self.get_industry_code(normalized["industry"])
            
            # 空白・タブ・改行の削除
            for key, value in normalized.items():
                if isinstance(value, str):
                    normalized[key] = self.clean_whitespace(value)
            
            normalized_data.append(normalized)
        
        return normalized_data
    
    def normalize_company_name(self, name: str) -> str:
        """
        会社名を正規化する
        """
        if not name:
            return ""
        
        # 前後の空白を削除
        name = name.strip()
        
        # 法人格の正規化
        for pattern, replacement in self.company_suffixes.items():
            name = re.sub(f'{pattern}', replacement, name)
        
        # カッコの正規化
        name = re.sub(r'（', '(', name)
        name = re.sub(r'）', ')', name)
        
        # 全角英数字を半角に変換
        name = self.convert_fullwidth_to_halfwidth(name)
        
        return name
    
    def normalize_phone_number(self, phone: str) -> str:
        """
        電話番号を正規化する
        """
        if not phone:
            return ""
        
        # 空白、ハイフン、カッコを削除
        phone = re.sub(r'[\s\-（）\(\)]', '', phone)
        
        # 全角数字を半角に変換
        phone = self.convert_fullwidth_to_halfwidth(phone)
        
        # 市外局番、市内局番、番号の区切りを追加
        if len(phone) == 10:  # 固定電話（市外局番2桁）
            phone = f"{phone[:2]}-{phone[2:6]}-{phone[6:]}"
        elif len(phone) == 11:  # 携帯電話または固定電話（市外局番3桁）
            if phone.startswith("0"):
                if phone.startswith("090") or phone.startswith("080") or phone.startswith("070"):  # 携帯電話
                    phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
                else:  # 固定電話
                    phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
        elif len(phone) == 9:  # 固定電話（市外局番なし）
            phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
        
        return phone
    
    def normalize_address(self, address: str) -> str:
        """
        住所を正規化する
        """
        if not address:
            return ""
        
        # 前後の空白を削除
        address = address.strip()
        
        # 全角英数字を半角に変換
        address = self.convert_fullwidth_to_halfwidth(address)
        
        # 都道府県の正規化
        for short_name, full_name in self.prefecture_mapping.items():
            if address.startswith(short_name) and not address.startswith(full_name):
                address = address.replace(short_name, full_name, 1)
                break
        
        # 番地表記の正規化
        address = re.sub(r'([0-9]+)－([0-9]+)', r'\1-\2', address)  # 全角ハイフンを半角に
        address = re.sub(r'([0-9]+)番地?([0-9]+)', r'\1-\2', address)  # 「番地」を「-」に
        
        # 建物名の前にスペースを追加
        address = re.sub(r'([0-9]+階)([^\s])', r'\1 \2', address)
        address = re.sub(r'([0-9]+F)([^\s])', r'\1 \2', address)
        
        return address
    
    def extract_prefecture_city(self, address: str) -> tuple:
        """
        住所から都道府県と市区町村を抽出する
        """
        if not address:
            return "", ""
        
        prefecture = ""
        city = ""
        
        # 都道府県を抽出
        for full_name in self.prefecture_mapping.values():
            if full_name in address:
                prefecture = full_name
                # 都道府県の後の文字列を取得
                after_pref = address[address.index(full_name) + len(full_name):]
                
                # 市区町村を抽出
                city_match = re.search(r'([^\s]{2,6}[市区町村])', after_pref)
                if city_match:
                    city = city_match.group(1)
                
                break
        
        return prefecture, city
    
    def normalize_industry(self, industry: str) -> str:
        """
        業種を正規化する
        """
        if not industry:
            return ""
        
        # 前後の空白を削除
        industry = industry.strip()
        
        # 全角英数字を半角に変換
        industry = self.convert_fullwidth_to_halfwidth(industry)
        
        return industry
    
    def get_industry_code(self, industry: str) -> str:
        """
        業種からコードを取得する
        """
        if not industry:
            return ""
        
        # 業種名から最も近いコードを探す
        for name, code in self.industry_code_mapping.items():
            if name in industry or industry in name:
                return code
        
        # 部分一致で探す
        for name, code in self.industry_code_mapping.items():
            for word in name.split('・'):
                if word in industry:
                    return code
        
        return "999"  # その他
    
    def clean_whitespace(self, text: str) -> str:
        """
        空白、タブ、改行を整理する
        """
        if not text:
            return ""
        
        # 連続する空白、タブ、改行を1つの空白に置換
        text = re.sub(r'\s+', ' ', text)
        # 前後の空白を削除
        text = text.strip()
        
        return text
    
    def convert_fullwidth_to_halfwidth(self, text: str) -> str:
        """
        全角英数字を半角に変換する
        """
        if not text:
            return ""
        
        # 全角英数字の変換テーブル
        fullwidth_chars = "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"
        halfwidth_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        
        # 変換テーブルを作成
        table = str.maketrans(fullwidth_chars, halfwidth_chars)
        
        # 変換を適用
        return text.translate(table)
    
    def remove_duplicates(self, company_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        重複する企業データを削除する
        """
        if not company_data_list:
            return []
        
        # 重複チェック用のキー
        unique_companies = {}
        
        for company in company_data_list:
            # 会社名と電話番号をキーとして使用
            name = company.get("name", "")
            phone = company.get("phone", "")
            
            # 会社名のみ、または電話番号のみでも重複チェック
            name_key = name.lower() if name else ""
            phone_key = re.sub(r'[^\d]', '', phone) if phone else ""
            
            # 両方空の場合はスキップ
            if not name_key and not phone_key:
                continue
            
            # キーの生成
            if name_key and phone_key:
                key = f"{name_key}_{phone_key}"
            elif name_key:
                key = f"name_{name_key}"
            else:
                key = f"phone_{phone_key}"
            
            # 重複チェック
            if key not in unique_companies:
                unique_companies[key] = company
            else:
                # 既存のデータとマージ（より多くの情報を持つ方を優先）
                existing = unique_companies[key]
                merged = self.merge_company_data(existing, company)
                unique_companies[key] = merged
        
        return list(unique_companies.values())
    
    def merge_company_data(self, company1: Dict[str, Any], company2: Dict[str, Any]) -> Dict[str, Any]:
        """
        2つの企業データをマージする（より多くの情報を持つ方を優先）
        """
        merged = {}
        
        # すべてのキーを取得
        all_keys = set(company1.keys()) | set(company2.keys())
        
        for key in all_keys:
            value1 = company1.get(key, "")
            value2 = company2.get(key, "")
            
            # 数値型の場合
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                # 0以外の値を優先
                if value1 != 0 and value2 != 0:
                    merged[key] = max(value1, value2)
                elif value1 != 0:
                    merged[key] = value1
                else:
                    merged[key] = value2
            # 文字列型の場合
            elif isinstance(value1, str) and isinstance(value2, str):
                # 空でない長い方を優先
                if value1 and value2:
                    merged[key] = value1 if len(value1) >= len(value2) else value2
                elif value1:
                    merged[key] = value1
                else:
                    merged[key] = value2
            # ブール型の場合
            elif isinstance(value1, bool) and isinstance(value2, bool):
                # Trueを優先
                merged[key] = value1 or value2
            # その他の型の場合
            else:
                # 空でない方を優先
                if value1 and value2:
                    merged[key] = value1
                elif value1:
                    merged[key] = value1
                else:
                    merged[key] = value2
        
        return merged
    
    def filter_by_industry(self, company_data_list: List[Dict[str, Any]], industry_codes: List[str]) -> List[Dict[str, Any]]:
        """
        業種コードでフィルタリングする
        """
        if not industry_codes:
            return company_data_list
        
        filtered_data = []
        
        for company in company_data_list:
            industry_code = company.get("industry_code", "")
            industry = company.get("industry", "")
            
            # 業種コードが一致
            if industry_code and industry_code in industry_codes:
                filtered_data.append(company)
                continue
            
            # 業種名から判断
            if industry:
                for code in industry_codes:
                    for name, mapping_code in self.industry_code_mapping.items():
                        if mapping_code == code and (name in industry or industry in name):
                            filtered_data.append(company)
                            break
                    else:
                        continue
                    break
        
        return filtered_data
    
    def filter_by_location(self, company_data_list: List[Dict[str, Any]], prefectures: Optional[List[str]] = None, cities: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        都道府県と市区町村でフィルタリングする
        """
        if not prefectures and not cities:
            return company_data_list
        
        filtered_data = []
        
        for company in company_data_list:
            prefecture = company.get("prefecture", "")
            city = company.get("city", "")
            address = company.get("address", "")
            
            # 都道府県のフィルタリング
            prefecture_match = False
            if prefectures:
                if prefecture and prefecture in prefectures:
                    prefecture_match = True
                elif not prefecture and address:
                    for pref in prefectures:
                        if pref in address:
                            prefecture_match = True
                            break
            else:
                prefecture_match = True
            
            # 都道府県が一致しない場合はスキップ
            if not prefecture_match:
                continue
            
            # 市区町村のフィルタリング
            city_match = False
            if cities:
                if city and city in cities:
                    city_match = True
                elif not city and address:
                    for c in cities:
                        if c in address:
                            city_match = True
                            break
            else:
                city_match = True
            
            # 市区町村も一致する場合のみ追加
            if city_match:
                filtered_data.append(company)
        
        return filtered_data
    
    def preprocess_csv_data(self, csv_content: str) -> str:
        """
        CSVデータの前処理を行う
        """
        if not csv_content:
            return ""
        
        # 空白行の削除
        lines = csv_content.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        
        # 空白、タブの正規化
        normalized_lines = []
        for line in non_empty_lines:
            # 連続する空白、タブを1つのカンマに置換
            normalized = re.sub(r'\s+', ',', line)
            normalized_lines.append(normalized)
        
        return "\n".join(normalized_lines)
    
    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        データフレームの列名を標準化する
        """
        if df.empty:
            return df
        
        # 列名のマッピング
        column_mapping = {
            '会社名': 'name',
            '企業名': 'name',
            '法人名': 'name',
            '名称': 'name',
            '住所': 'address',
            '所在地': 'address',
            '電話': 'phone',
            '電話番号': 'phone',
            'TEL': 'phone',
            'Tel': 'phone',
            'メール': 'email',
            'メールアドレス': 'email',
            'E-mail': 'email',
            'Email': 'email',
            'URL': 'website',
            'ホームページ': 'website',
            'HP': 'website',
            'WEB': 'website',
            '業種': 'industry',
            '業界': 'industry',
            '代表': 'representative',
            '代表者': 'representative',
            '代表取締役': 'representative',
            '設立': 'established_year',
            '設立年': 'established_year',
            '創業': 'established_year',
            '資本金': 'capital',
            '従業員': 'employees',
            '従業員数': 'employees',
            '社員数': 'employees',
            '都道府県': 'prefecture',
            '市区町村': 'city',
            'FAX': 'fax',
            'Fax': 'fax',
        }
        
        # 列名を標準化
        renamed_columns = {}
        for col in df.columns:
            col_lower = col.lower()
            for jp_name, en_name in column_mapping.items():
                if jp_name.lower() in col_lower or col_lower in jp_name.lower():
                    renamed_columns[col] = en_name
                    break
        
        # 列名を変更
        if renamed_columns:
            df = df.rename(columns=renamed_columns)
        
        return df
    
    def process_csv_file(self, file_path: str) -> pd.DataFrame:
        """
        CSVファイルを処理する
        """
        try:
            # CSVファイルを読み込む
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # Shift-JISで試す
                df = pd.read_csv(file_path, encoding='shift_jis')
            except:
                try:
                    # CP932で試す
                    df = pd.read_csv(file_path, encoding='cp932')
                except:
                    # その他のエンコーディングで試す
                    df = pd.read_csv(file_path, encoding='latin1')
        
        # 列名を標準化
        df = self.standardize_columns(df)
        
        # 欠損値を空文字列に置換
        df = df.fillna("")
        
        # 文字列型の列のみ処理
        for col in df.select_dtypes(include=['object']).columns:
            # 空白、タブ、改行を整理
            df[col] = df[col].apply(lambda x: self.clean_whitespace(str(x)) if pd.notna(x) else "")
            
            # 列に応じた正規化
            if col == 'name':
                df[col] = df[col].apply(self.normalize_company_name)
            elif col == 'phone':
                df[col] = df[col].apply(self.normalize_phone_number)
            elif col == 'address':
                df[col] = df[col].apply(self.normalize_address)
            elif col == 'industry':
                df[col] = df[col].apply(self.normalize_industry)
        
        # 都道府県と市区町村を抽出
        if 'address' in df.columns and ('prefecture' not in df.columns or 'city' not in df.columns):
            prefecture_city = df['address'].apply(self.extract_prefecture_city)
            if 'prefecture' not in df.columns:
                df['prefecture'] = prefecture_city.apply(lambda x: x[0])
            if 'city' not in df.columns:
                df['city'] = prefecture_city.apply(lambda x: x[1])
        
        # 業種コードを設定
        if 'industry' in df.columns and 'industry_code' not in df.columns:
            df['industry_code'] = df['industry'].apply(self.get_industry_code)
        
        return df
    
    def export_to_csv(self, company_data_list: List[Dict[str, Any]], file_path: str, encoding: str = 'utf-8') -> bool:
        """
        企業データをCSVファイルにエクスポートする
        """
        if not company_data_list:
            return False
        
        try:
            # DataFrameに変換
            df = pd.DataFrame(company_data_list)
            
            # 列の順序を指定
            columns_order = [
                'name', 'address', 'phone', 'email', 'website', 
                'industry', 'industry_code', 'prefecture', 'city',
                'representative', 'established_year', 'capital', 'employees',
                'has_fax', 'has_contact_form', 'source_url'
            ]
            
            # 存在する列のみを使用
            available_columns = [col for col in columns_order if col in df.columns]
            
            # 列を並べ替え
            df = df[available_columns]
            
            # CSVに保存
            df.to_csv(file_path, index=False, encoding=encoding)
            
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return False
