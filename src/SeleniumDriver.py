from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
import threading

class SeleniumDriver:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")  
        chrome_options.add_argument("--disable-gpu")  
        chrome_options.add_argument("--window-size=1000,500")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.lock = threading.Lock()
        self.url = "https://programaredl.asp.gov.md/qwebbook/index.jsp?lang=ro"

    def select_dropdown_option(self, driver, dropdown_selector, option):
            WebDriverWait(driver, 10).until(
                lambda driver: len(driver.find_element(By.ID, dropdown_selector).find_elements(By.TAG_NAME, "option")) > 1
            )

            element = driver.find_element(By.ID, dropdown_selector)
            element.click()
            option_to_select = driver.find_element(By.XPATH, f"//select[@id='{dropdown_selector}']/option[text()='{option}']")
            option_to_select.click()
    
    def number_to_romanian_month(self, month_number):
        months = {
            1: "Ianuarie",
            2: "Februarie",
            3: "Martie",
            4: "Aprilie",
            5: "Mai",
            6: "Iunie",
            7: "Iulie",
            8: "August",
            9: "Septembrie",
            10: "Octombrie",
            11: "Noiembrie",
            12: "Decembrie",
        }

        return months.get(month_number, "Invalid month number")
    
    def find_correct_cell(self, date, fm_date_cells, lm_date_cells, dates):
        days_list = None
        month_year_key = f"{self.number_to_romanian_month(date.month)} {date.year}"
    
        if month_year_key in dates:
            days_list = dates[month_year_key]
            if str(date.day) in days_list:
                day_index = days_list.index(str(date.day))
        keys = list(dates.keys()) 
        
        if keys[0] == month_year_key:
            cell = fm_date_cells[day_index]
        elif keys[1] == month_year_key:
            cell = lm_date_cells[day_index]
        
        if days_list == None:
            return "Nu s-a găsit așa dată."
        
        return cell

    def fetch_select_options(self, dropdown_control, service = None, location = None, date = None):
        with self.lock:
            self.driver.get(self.url)
                       
            if(service != None):
                self.select_dropdown_option(self.driver, "firstSelectControl", service)

            if(location != None):
                self.select_dropdown_option(self.driver, "secondSelectControl", location)
            
            if date != None:
                fm_date_cells, lm_date_cells, dates = self.get_available_dates("dateControl", service, location, self.driver)
                date_cell = self.find_correct_cell(date, fm_date_cells, lm_date_cells, dates)
                date_cell.click() 
            
            WebDriverWait(self.driver, 10).until(
                lambda driver: len(driver.find_element(By.ID, dropdown_control).find_elements(By.TAG_NAME, "option")) > 1
            )

            dropdown = Select(self.driver.find_element(By.ID, dropdown_control))
            options = [option.text for option in dropdown.options[1:]]
            return options
        
    def get_available_dates(self, date_control, service, location, driver = None):
        if driver == None:
            with self.lock:
                self.driver.get(self.url)
                return self.fetch_available_dates(self.driver, date_control, service, location)
        else:
            return self.fetch_available_dates(driver, date_control, service, location)
                
    def fetch_available_dates(self, driver, date_control, service, location):
        self.select_dropdown_option(driver, "firstSelectControl", service)
        self.select_dropdown_option(driver, "secondSelectControl", location)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.ui-state-default.ui-state-active")))
        calendar = driver.find_element(By.ID, date_control)
        
        first_month_component = calendar.find_element(By.CLASS_NAME, "ui-datepicker-group-first")
        last_month_component = calendar.find_element(By.CLASS_NAME, "ui-datepicker-group-last")

        first_month_name = first_month_component.find_element(By.CLASS_NAME, "ui-datepicker-title").text
        last_month_name = last_month_component.find_element(By.CLASS_NAME, "ui-datepicker-title").text

        first_month_table = first_month_component.find_element(By.CLASS_NAME, "ui-datepicker-calendar")
        first_month_tablebody = first_month_table.find_element(By.TAG_NAME, "tbody")
        last_month_table = last_month_component.find_element(By.CLASS_NAME, "ui-datepicker-calendar")
        last_month_tablebody = last_month_table.find_element(By.TAG_NAME, "tbody")

        first_month_date_cells = first_month_tablebody.find_elements(By.CSS_SELECTOR, "td:not(.ui-datepicker-unselectable):not(.ui-state-disabled)")
        last_month_date_cells = last_month_tablebody.find_elements(By.CSS_SELECTOR, "td:not(.ui-datepicker-unselectable):not(.ui-state-disabled)")

        first_month_dates = [element.text for element in first_month_date_cells]
        last_month_dates = [element.text for element in last_month_date_cells]

        return first_month_date_cells, last_month_date_cells, {first_month_name:first_month_dates, last_month_name:last_month_dates}

    def close(self):
        self.driver.quit()
