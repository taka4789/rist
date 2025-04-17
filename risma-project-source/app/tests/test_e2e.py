import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# E2Eテスト用の設定
@pytest.fixture(scope="module")
def browser():
    # ヘッドレスモードでChromeを起動
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()

# テスト用のベースURL
BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:3000")

# テスト: ログインページの表示
def test_login_page_loads(browser):
    browser.get(f"{BASE_URL}/login")
    
    # ログインページのタイトルを確認
    assert "リスマ（LisMa）" in browser.title
    
    # ログインフォームの要素が存在することを確認
    email_input = browser.find_element(By.ID, "email")
    password_input = browser.find_element(By.ID, "password")
    login_button = browser.find_element(By.XPATH, "//button[contains(text(), 'ログイン')]")
    
    assert email_input.is_displayed()
    assert password_input.is_displayed()
    assert login_button.is_displayed()

# テスト: ログイン機能
def test_login_functionality(browser):
    browser.get(f"{BASE_URL}/login")
    
    # ログインフォームに入力
    email_input = browser.find_element(By.ID, "email")
    password_input = browser.find_element(By.ID, "password")
    login_button = browser.find_element(By.XPATH, "//button[contains(text(), 'ログイン')]")
    
    email_input.send_keys("test@example.com")
    password_input.send_keys("testpassword")
    login_button.click()
    
    # ダッシュボードにリダイレクトされることを確認
    WebDriverWait(browser, 10).until(
        EC.url_contains("/dashboard")
    )
    
    # ダッシュボードの要素が表示されることを確認
    welcome_text = browser.find_element(By.XPATH, "//h4[contains(text(), 'ようこそ')]")
    assert welcome_text.is_displayed()

# テスト: キーワード検索ページの表示と機能
def test_keyword_search_page(browser):
    # まずログイン
    browser.get(f"{BASE_URL}/login")
    email_input = browser.find_element(By.ID, "email")
    password_input = browser.find_element(By.ID, "password")
    login_button = browser.find_element(By.XPATH, "//button[contains(text(), 'ログイン')]")
    
    email_input.send_keys("test@example.com")
    password_input.send_keys("testpassword")
    login_button.click()
    
    # キーワード検索ページに移動
    WebDriverWait(browser, 10).until(
        EC.url_contains("/dashboard")
    )
    browser.get(f"{BASE_URL}/search/keyword")
    
    # キーワード検索ページの要素が表示されることを確認
    page_title = browser.find_element(By.XPATH, "//h4[contains(text(), 'キーワード検索')]")
    assert page_title.is_displayed()
    
    # キーワード入力フィールドに入力
    keyword_input = browser.find_element(By.XPATH, "//input[contains(@placeholder, 'キーワードを入力')]")
    keyword_input.send_keys("テスト企業")
    keyword_input.send_keys("\n")  # Enterキーを押す
    
    # キーワードチップが表示されることを確認
    keyword_chip = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'MuiChip-root')]"))
    )
    assert "テスト企業" in keyword_chip.text
    
    # リスト名を入力
    list_name_input = browser.find_element(By.ID, "list_name")
    list_name_input.send_keys("テスト検索リスト")
    
    # 検索ボタンがクリック可能になることを確認
    search_button = browser.find_element(By.XPATH, "//button[contains(text(), '検索を開始')]")
    assert search_button.is_enabled()

# テスト: リスト管理ページの表示
def test_lists_page(browser):
    # まずログイン
    browser.get(f"{BASE_URL}/login")
    email_input = browser.find_element(By.ID, "email")
    password_input = browser.find_element(By.ID, "password")
    login_button = browser.find_element(By.XPATH, "//button[contains(text(), 'ログイン')]")
    
    email_input.send_keys("test@example.com")
    password_input.send_keys("testpassword")
    login_button.click()
    
    # リスト管理ページに移動
    WebDriverWait(browser, 10).until(
        EC.url_contains("/dashboard")
    )
    browser.get(f"{BASE_URL}/lists")
    
    # リスト管理ページの要素が表示されることを確認
    page_title = browser.find_element(By.XPATH, "//h4[contains(text(), 'リスト管理')]")
    assert page_title.is_displayed()
    
    # 新規リスト作成ボタンが表示されることを確認
    create_button = browser.find_element(By.XPATH, "//button[contains(text(), '新規リスト作成')]")
    assert create_button.is_displayed()

# テスト: レスポンシブデザイン
def test_responsive_design(browser):
    # モバイルサイズに設定
    browser.set_window_size(375, 812)  # iPhoneXサイズ
    
    # ログインページを表示
    browser.get(f"{BASE_URL}/login")
    
    # ログインフォームの要素が表示されることを確認
    email_input = browser.find_element(By.ID, "email")
    password_input = browser.find_element(By.ID, "password")
    login_button = browser.find_element(By.XPATH, "//button[contains(text(), 'ログイン')]")
    
    assert email_input.is_displayed()
    assert password_input.is_displayed()
    assert login_button.is_displayed()
    
    # デスクトップサイズに戻す
    browser.set_window_size(1280, 800)

if __name__ == "__main__":
    pytest.main(["-v", "test_e2e.py"])
