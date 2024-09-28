from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoAlertPresentException, StaleElementReferenceException
from selenium.webdriver.common.alert import Alert
import time

# 크롬 드라이버 경로 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def login(driver, username, password):
    url = "https://www.letskorail.com/korail/com/login.do"
    driver.get(url)
    driver.find_element(By.ID, "txtMember").send_keys(username)
    driver.find_element(By.ID, "txtPwd").send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="loginDisplay1"]/ul/li[3]/a/img').click()

def search_ticket(driver, start, end, year, month, day, hour):
    # 버튼 나올 때까지 암시적 대기(10초 대기를 하나 버튼이 로드될 경우 대기하는 것을 멈춤)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="res_cont_tab01"]/form/div/fieldset/p/a/img')))
    
    # 버튼 클릭
    driver.find_element(By.XPATH, '//*[@id="res_cont_tab01"]/form/div/fieldset/p/a/img').click()
    
    # KTX 선택하는 라디오 버튼이 나오기까지 대기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'selGoTrainRa00')))
    
    # KTX 버튼 클릭
    radio_button = driver.find_element(By.ID, "selGoTrainRa00")
    radio_button.click()
    # 출발지 입력
    driver.find_element(By.ID, "start").clear()
    driver.find_element(By.ID, "start").send_keys(start)
    # 도착지 입력
    driver.find_element(By.ID, "get").clear()
    driver.find_element(By.ID, "get").send_keys(end)
    # Select 년 
    select_year = Select(driver.find_element(By.ID, 's_year'))
    select_year.select_by_value(year)
    # Select 월
    select_month = Select(driver.find_element(By.ID, 's_month'))
    select_month.select_by_value(month)
    # Select 일
    select_day = Select(driver.find_element(By.ID, 's_day'))
    select_day.select_by_value(day)
    # Select 시간
    select_hour = Select(driver.find_element(By.ID, 's_hour'))
    select_hour.select_by_value(hour)

    # 조회 버튼 클릭
    driver.find_element(By.XPATH, '//*[@id="center"]/div[3]/p/a/img').click()

def check_normal(driver):
    # 테이블 나올 때까지 대기
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
    table = driver.find_element(By.CSS_SELECTOR, "table")  # 실제 CSS 선택자에 맞게 변경

    # 테이블의 헤더를 확인하여 "일반실" 열의 인덱스를 찾기
    headers = table.find_elements(By.CSS_SELECTOR, "thead th")  # 헤더 셀을 찾기 위한 선택자
    general_room_column_index = None
    for index, header in enumerate(headers):
        if "일반실" in header.text:  # 열 헤더 텍스트에 따라 변경
            general_room_column_index = index
            break

    if general_room_column_index is None:
        raise Exception("General Room column not found!")
    
    return general_room_column_index

def book_ticket(driver):
    while True:
        try:
            general_room_column_index = check_normal(driver)  # 헤더 인덱스를 확인
            
            # 테이블 및 행을 다시 찾아서 사용
            table = driver.find_element(By.CSS_SELECTOR, "table")
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) > general_room_column_index:
                    cell = cells[general_room_column_index]
                    buttons = cell.find_elements(By.XPATH, ".//a/img")  # "예약하기" 버튼을 찾기 위한 XPath
                    for button in buttons:
                        if "예약하기" in button.get_attribute("alt"):  # 버튼의 alt 속성을 확인
                            button.click()
                            print("일반실 예매 완료!")
                            
                            # 예매 성공 시 팝업 모달 닫기
                            close_all_alerts(driver)
                            
                            return True  # 예매 완료 후 함수 종료
            break
        except StaleElementReferenceException:
            print("StaleElementReferenceException 발생, 테이블을 다시 로드합니다.")
            time.sleep(1)  # 잠시 대기 후 다시 시도
            continue  # while 루프를 재시도

    return False  # 예매할 수 있는 버튼이 없는 경우

def go_to_next_page(driver):
    try:
        # 다음 페이지 버튼 찾기
        next_button = driver.find_element(By.XPATH, '//a/img[@alt="다음"]')
        next_button.click()
        return True
    except Exception:
        return False

def go_to_previous_page(driver):
    try:
        # 이전 페이지 버튼 찾기
        prev_button = driver.find_element(By.XPATH, '//a/img[@alt="이전"]')
        prev_button.click()
        return True
    except Exception:
        return False

def close_all_alerts(driver):
    # 팝업 모달 닫기 로직
    while True:
        try:
            alert = Alert(driver)
            alert.accept()
            print("팝업 모달 확인 완료")
            time.sleep(1)  # 팝업 모달이 여러 개 뜨는 경우 대기 시간 추가
        except NoAlertPresentException:
            break  # 팝업 모달이 없으면 루프 종료

# 실행 예제
login(driver, "1576724729", "@dlaxotmd12")
search_ticket(driver, "서울", "부산", "2024", "09", "14", "10")

moving_forward = True

while True:
    try:
        # 매 페이지마다 예매 시도
        if book_ticket(driver):
            print("예매 성공! 루프를 종료합니다.")
            break
        
        # 다음 페이지로 이동
        if moving_forward:
            if not go_to_next_page(driver):
                print("마지막 페이지 도달. 이전 페이지로 돌아갑니다.")
                moving_forward = False
        else:
            if not go_to_previous_page(driver):
                print("첫 페이지에 도달했습니다. 다시 앞으로 이동합니다.")
                moving_forward = True
            else:
                print("이전 페이지로 이동합니다.")
        
        time.sleep(2)  # 페이지 로드 대기 후 다시 시도
    except Exception as e:
        print(f"오류 발생: {e}. 다시 시도합니다.")
        time.sleep(10)  # 오류가 발생한 경우 10초 대기 후 다시 시도
