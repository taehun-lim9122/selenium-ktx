from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert

import time

driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()))

url = "https://www.letskorail.com/korail/com/login.do"
driver.get(url)
driver.find_element(By.ID, "txtMember").send_keys("1576724729")
driver.find_element(By.ID, "txtPwd").send_keys("@dlaxotmd12")
driver.find_element(By.XPATH, '//*[@id="loginDisplay1"]/ul/li[3]/a/img').click()

time.sleep(1)

driver.find_element(By.XPATH, '//*[@id="res_cont_tab01"]/form/div/fieldset/p/a/img').click()

time.sleep(1)
driver.find_element(By.ID, 'selGoTrainRa00').click()
# 출발지 입력
driver.find_element(By.ID, "start").clear()
driver.find_element(By.ID, "start").send_keys("부산")
# 도착지 입력
driver.find_element(By.ID, "get").clear()
driver.find_element(By.ID, "get").send_keys("서울")
# 출발 날짜 Select
# 년
select = Select(driver.find_element(By.ID, 's_year'))
select.select_by_value("2024")
# 월
select = Select(driver.find_element(By.ID, 's_month'))
select.select_by_value("09")
# 일
select = Select(driver.find_element(By.ID, 's_day'))
select.select_by_value("17")

#조회 버튼 클린
driver.find_element(By.XPATH, '//*[@id="center"]/div[3]/p/a/img').click()


time.sleep(4)
# train_list = driver.find_elements(By.ID, "tableResult")
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

# 테이블 본문에서 버튼을 찾고 클릭
rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")  # 테이블의 행을 찾기 위한 선택자
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) > general_room_column_index:
        cell = cells[general_room_column_index]
        buttons = cell.find_elements(By.XPATH, ".//a/img")  # "예약하기" 버튼을 찾기 위한 XPath
        for button in buttons:
            if "예약하기" in button.get_attribute("alt"):  # 버튼의 alt 속성을 확인
                button.click()
                end = False
                break  # 첫 번째 버튼 클릭 후 반복 종료
            else:
                next_button = driver.find_element(By.XPATH, '//img[@alt="다음"]')
                before_button = driver.find_element(By.XPATH, '//img[@alt="이전"]')
                if next_button:
                    next_button.click()
                else:
                    before_button.click()
                    

                              
        if end == False:
            break

while True:
    try:
        da = Alert(driver)
        da.accept()
    except Exception as e:
        print(f"예외 발생: {e}")
        break  # 예외가 발생하면 루프 종료

# 테이블 나오는거 대기 -> 테이블에서 일반실에 해당하는 컬럼 인덱스 찾기 -> 일반실 인덱스를 가지고 예약하기 가능한 버튼 찾기 -> 있으면 예약하기, 없으면 다음 페이지 찾기
                

time.sleep(5)