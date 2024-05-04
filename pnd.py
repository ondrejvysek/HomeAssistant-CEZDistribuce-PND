import appdaemon.plugins.hass.hassapi as hass
import time
import datetime
import os
import sys
import pandas as pd
from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_download(directory, timeout=30):
    """
    Wait for the first (newest) file to appear in the directory within the timeout period.
    Returns the path to the new file.
    """
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        files = sorted([os.path.join(directory, f) for f in os.listdir(directory)], key=os.path.getmtime)
        # Filter out incomplete downloads
        files = [f for f in files if not f.endswith('.crdownload')]
        if files:
            dl_wait = False
        seconds += 1
    if files:
        return files[-1]
    return None

class pnd(hass.Hass):
  def initialize(self):
    self.log(">>>>>>>>>>>> PND Initialize")
    
    self.username = self.args["PNDUserName"] 
    self.password = self.args["PNDUserPassword"]
    self.download_folder = self.args["DownloadFolder"]
    self.datainterval = self.args["DataInterval"]
    self.entity_id_consumption = 'sensor.pnd_consumption'
    self.entity_id_production = 'sensor.pnd_production'
    self.listen_event(self.run_pnd, "run_pnd")

  def terminate(self):
    self.log(">>>>>>>>>>>> PND Terminate")

  def run_pnd(self, event_name, data, kwargs):
    self.log(">>>>>>>>>>>> PND Run Event")
    self.set_state("binary_sensor.pnd_running", state="on")
    self.log("----------------------------------------------")
    self.log("Hello from AppDaemon for Portal Namerenych Dat")
    
    os.makedirs(self.download_folder, exist_ok=True)
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": self.download_folder,  # Set download folder
        "download.prompt_for_download": False,          # Disable download prompt
        "download.directory_upgrade": True,             # Manage download directory
        "plugins.always_open_pdf_externally": False      # Automatically open PDFs
    })
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--log-level=3")  # Disable logging
    #load service 
    service = Service('/usr/bin/chromedriver') 
    #load driver
    try:
      driver = webdriver.Chrome(service=service, options=chrome_options)
      self.log("Driver Loaded")
    except:
      self.error("Unable to initialize Chrome Driver - exitting")
      sys.exit()
    # Open a website
    try:
      driver.get("https://dip.cezdistribuce.cz/irj/portal/?zpnd=")  # Change to the website's login page
      self.log("Website Opened")
    except:
      self.error("Unable to open website - exitting")
      sys.exit()
    time.sleep(3)  # Allow time for the page to load
    # Locate the element that might be blocking the login button
    cookie_banner_close_button = driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowallSelection")

    # Click the close button or take other action to dismiss the cookie banner
    cookie_banner_close_button.click()
    time.sleep(3)  # Allow time for the page to load
    # Simulate login
    username_field = driver.find_element(By.XPATH, "//input[@placeholder='Uživatelské jméno / e-mail']")
    password_field = driver.find_element(By.XPATH, "//input[@placeholder='Heslo']")
    login_button = driver.find_element(By.XPATH, "//button[@type='submit' and @color='primary']")

    # Enter login credentials and click the button
    username_field.send_keys(self.username)
    password_field.send_keys(self.password) 

    # Wait until the login button is clickable
    wait = WebDriverWait(driver, 10)  # 10-second timeout
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @color='primary']")))
    login_button.click()

    # Allow time for login processing
    time.sleep(3)  # Adjust as needed

    wait = WebDriverWait(driver, 20)  # 10-second timeout

    #portal_title = wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Naměřená data')]"))).text
    # Check if the specified H1 tag is present
    h1_text = "Naměřená data"
    h1_element = wait.until(EC.presence_of_element_located((By.XPATH, f"//h1[contains(text(), '{h1_text}')]")))

    # Print whether the H1 tag with the specified text is found
    if h1_element:
        self.log(f"H1 tag with text '{h1_text}' is present.")
    else:
        self.error(f"H1 tag with text '{h1_text}' is not found.")
        sys.exit()
    # Wait for the button to be clickable
    wait = WebDriverWait(driver, 10)  # 10-second timeout
    tabulka_dat_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Tabulka dat']")))

    # Click the button
    tabulka_dat_button.click()


    # Use the label text to find the dropdown button
    dropdown_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Období')]")))
    dropdown_container = dropdown_label.find_element(By.XPATH, "./following-sibling::div//div[contains(@class, 'multiselect__select')]")
    dropdown_container.click()

    # Now, wait for the option labeled "Včera" to be visible and clickable, then click it
    option_vcera = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Včera') and contains(@class, 'multiselect__option')]")))
    option_vcera.click()


#-----------------------------------------------------------
#    # Locate the input field by its ID
#    input_field = driver.find_element(By.ID, "window-120274-interval")

#    # Clear the input field first if necessary
#    input_field.clear()

#    # Enter the date range into the input field
#    date_range = datainterval
#    input_field.send_keys(date_range)

#    # Optionally, you can send ENTER or TAB if needed to process the input
#    input_field.send_keys(Keys.ENTER)  # or Keys.TAB if you need to move out of the input field
#    self.log(f"Data Interval Entered - '{datainterval}'")
#-----------------------------------------------------------    
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), 'Vyhledat data')]")))
    button.click()

    time.sleep(5)

    # Wait for the page and elements to fully load
    wait = WebDriverWait(driver, 10)  # Adjust timeout as necessary

    # Find and click the link by its exact text
    #print(driver.page_source)
    link_text = "07 Profil spotřeby za den (+A)"
    link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, link_text)))
    link.click()

    # Wait for the dropdown toggle and click it using the button text
    wait = WebDriverWait(driver, 10)
    toggle_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Exportovat data')]")))
    toggle_button.click()

    # Wait for the CSV link and click it
    csv_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='CSV']")))
    self.log(f"Downloading CSV file for {link_text}")
    csv_link.click()
    # Wait for the download to complete
    downloaded_file = wait_for_download(self.download_folder)
    # Rename the file if it was downloaded
    if downloaded_file:
        new_filename = os.path.join(self.download_folder, "daily-consumption.csv")
        os.remove(new_filename) if os.path.exists(new_filename) else None
        os.rename(downloaded_file, new_filename)
        self.log(f"File downloaded and saved as: {new_filename}")
    else:
        self.error(f"No file was downloaded for {link_text}")

    wait = WebDriverWait(driver, 10)  # Adjust timeout as necessary

    # Find and click the link by its exact text
    #print(driver.page_source)
    link_text = "08 Profil výroby za den (-A)"
    link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, link_text)))
    link.click()

    # Wait for the dropdown toggle and click it using the button text
    wait = WebDriverWait(driver, 10)
    toggle_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Exportovat data')]")))
    toggle_button.click()

    # Wait for the CSV link and click it
    csv_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='CSV']")))
    self.log(f"Downloading CSV file for {link_text}")
    csv_link.click()
    # Wait for the download to complete
    downloaded_file = wait_for_download(self.download_folder)
    # Rename the file if it was downloaded
    if downloaded_file:
        new_filename = os.path.join(self.download_folder, "daily-production.csv")
        os.remove(new_filename) if os.path.exists(new_filename) else None
        os.rename(downloaded_file, new_filename)
        self.log(f"File downloaded and saved as: {new_filename}")
    else:
        self.error(f"No file was downloaded for {link_text}")

    self.log("All Done - DAILY DATA DOWNLOADED")
    date_format = "%d.%m.%Y %H:%M"
    data_consumption = pd.read_csv(self.download_folder + '/daily-consumption.csv', delimiter=';', encoding='latin1')
    latest_consumption_entry = data_consumption.iloc[-1]  # Get the last row, assuming the data is appended daily
    data_production = pd.read_csv(self.download_folder + '/daily-production.csv', delimiter=';', encoding='latin1')
    latest_production_entry = data_production.iloc[-1]  # Get the last row, assuming the data is appended daily

    # Extract date and consumption values
    date_consumption_str = latest_consumption_entry.iloc[0]
    date_consumption_str = date_consumption_str.replace("00:00", "23:59")
    date_consumption_obj = datetime.datetime.strptime(date_consumption_str, date_format)
    yesterday_consumption = date_consumption_obj - datetime.timedelta(days=1)
    date_production_str = latest_production_entry.iloc[0]
    date_production_str = date_production_str.replace("00:00", "23:59")
    date_production_obj = datetime.datetime.strptime(date_production_str, date_format)
    yesterday_production = date_production_obj - datetime.timedelta(days=1)
    
    consumption_value = latest_consumption_entry.iloc[1]
    production_value = latest_production_entry.iloc[1]

    self.log(f"Latest entry: {date_consumption_str} - {yesterday_consumption} - {consumption_value} kWh")
    self.log(f"Latest entry: {date_production_str} - {yesterday_production} - {production_value} kWh")

    self.set_state(self.entity_id_consumption, state=consumption_value, attributes={
      "friendly_name": "PND Consumption",
      "device_class": "energy",
      "unit_of_measurement": "kWh",
      "date": yesterday_consumption.isoformat()
    })
    self.set_state(self.entity_id_production, state=production_value, attributes={
      "friendly_name": "PND Production",
      "device_class": "energy",
      "unit_of_measurement": "kWh",
      "date": yesterday_production.isoformat()
    })
    
    self.log("All Done - DAILY DATA PROCESSED")

    #------------------INTERVAL-----------------------------
    ## Use the label text to find the dropdown button
    dropdown_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Období')]")))
    dropdown_container = dropdown_label.find_element(By.XPATH, "./following-sibling::div//div[contains(@class, 'multiselect__select')]")
    dropdown_container.click()

    ## Now, wait for the option labeled "Včera" to be visible and clickable, then click it
    option_vcera = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Vlastní') and contains(@class, 'multiselect__option')]")))
    option_vcera.click()
    # Locate the input field by its ID
    input_field = driver.find_element(By.ID, "window-120274-interval")

    # Clear the input field first if necessary
    input_field.clear()

    # Enter the date range into the input field
    date_range = self.datainterval
    input_field.send_keys(date_range)

    # Optionally, you can send ENTER or TAB if needed to process the input
    input_field.send_keys(Keys.ENTER)  # or Keys.TAB if you need to move out of the input field

    # Confirmation output (optional)
    self.log(f"Data Interval Entered - '{self.datainterval}'")
    #-----------------------------------------------

    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), 'Vyhledat data')]")))
    button.click()

    time.sleep(5)

    # Wait for the page and elements to fully load
    wait = WebDriverWait(driver, 10)  # Adjust timeout as necessary

    # Find and click the link by its exact text
    #print(driver.page_source)
    link_text = "07 Profil spotřeby za den (+A)"
    link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, link_text)))
    link.click()

    # Wait for the dropdown toggle and click it using the button text
    wait = WebDriverWait(driver, 10)
    toggle_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Exportovat data')]")))
    toggle_button.click()

    # Wait for the CSV link and click it
    csv_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='CSV']")))
    csv_link.click()

    # Wait for the download to complete
    downloaded_file = wait_for_download(self.download_folder)

    # Rename the file if it was downloaded
    if downloaded_file:
        new_filename = os.path.join(self.download_folder, "range-consumption.csv")
        os.remove(new_filename) if os.path.exists(new_filename) else None
        os.rename(downloaded_file, new_filename)
        print(f"File downloaded and saved as: {new_filename}")
    else:
        print("No file was downloaded.")
    #----------------------------------------------
    # Wait for the page and elements to fully load
    wait = WebDriverWait(driver, 10)  # Adjust timeout as necessary

    # Find and click the link by its exact text
    #print(driver.page_source)
    link_text = "08 Profil výroby za den (-A)"
    link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, link_text)))
    link.click()

    # Wait for the dropdown toggle and click it using the button text
    wait = WebDriverWait(driver, 10)
    toggle_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Exportovat data')]")))
    toggle_button.click()

    # Wait for the CSV link and click it
    csv_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='CSV']")))
    csv_link.click()

    # Wait for the download to complete
    downloaded_file = wait_for_download(self.download_folder)

    # Rename the file if it was downloaded
    if downloaded_file:
        new_filename = os.path.join(self.download_folder, "range-production.csv")
        os.remove(new_filename) if os.path.exists(new_filename) else None
        os.rename(downloaded_file, new_filename)
        print(f"File downloaded and saved as: {new_filename}")
    else:
        print("No file was downloaded.")
    self.log("All Done - INTERVAL DATA DOWNLOADED")
    data_consumption = pd.read_csv(self.download_folder + '/range-consumption.csv', delimiter=';', encoding='latin1', parse_dates=[0],dayfirst=True)
    data_production = pd.read_csv(self.download_folder + '/range-production.csv', delimiter=';', encoding='latin1', parse_dates=[0],dayfirst=True)

    data_consumption.iloc[:, 0] = pd.to_datetime(data_consumption.iloc[:, 0], format="%d.%m.%Y %H:%M")
    date_str = [dt.isoformat() for dt in data_consumption.iloc[:, 0]]

    consumption_str = data_consumption.iloc[:, 1].to_list()
    production_str = data_production.iloc[:, 1].to_list()

    now = dt.now()
    self.set_state("sensor.pnd_data", state=now.strftime("%Y-%m-%d %H:%M:%S"), attributes={"pnddate": date_str, "consumption": consumption_str, "production": production_str})
    total_consumption = "{:.2f}".format(data_consumption.iloc[:, 1].sum())
    total_production = "{:.2f}".format(data_production.iloc[:, 1].sum())
    self.set_state("sensor.pnd_total_interval_consumption", state=total_consumption,attributes={
      "friendly_name": "PND Total Interval Consumption",
      "device_class": "energy",
      "unit_of_measurement": "kWh"
    })
    self.set_state("sensor.pnd_total_interval_production", state=total_production,attributes={
      "friendly_name": "PND Total Interval Production",
      "device_class": "energy",
      "unit_of_measurement": "kWh"
    })
    #----------------------------------------------
    self.log("All Done - INTERVAL DATA PROCESSED")


    # Close the browser
    driver.quit()
    self.log("All Done - BROWSER CLOSED")
    self.set_state("binary_sensor.pnd_running", state="off")
    self.log("Sensor State Set to OFF")

