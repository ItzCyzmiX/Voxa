import logging
import os
import random
import string
import time
from typing import Tuple, Optional

import mailslurp_client
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay import Display

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
#"82bb6ccc08cbb3a75126cead5370cc789bb92234bd77dea6e731e33a345c85fb"
MAILSLURP_API_KEY = os.getenv("MAILSLURP_API_KEY")
RANDOM_USER_API = "https://randomuser.me/api/"
JAMMABLE_SIGNUP_URL = "https://www.jammable.com/signup"
JAMMABLE_VOICE_URL = "https://www.jammable.com/custom-playboi-carti-deep-voice-2024"
WAIT_TIMEOUT = 20

class AccountGenerator:
    """Handles generation of temporary account credentials"""
    
    @staticmethod
    def generate_password(length: int = 10) -> str:
        """Generate a random password with letters, digits, and '@' symbol"""
        characters = string.ascii_letters + string.digits + "@"
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def get_temp_email() -> Optional[str]:
        """Generate a temporary email using MailSlurp"""
        try:
            configuration = mailslurp_client.Configuration()
            configuration.api_key['x-api-key'] = MAILSLURP_API_KEY
            
            with mailslurp_client.ApiClient(configuration) as api_client:
                inbox_controller = mailslurp_client.InboxControllerApi(api_client)
                inbox = inbox_controller.create_inbox()
                logger.info(f"Created temporary email: {inbox.email_address}")
                return inbox.email_address
        except Exception as e:
            logger.error(f"Failed to generate temporary email: {e}")
            return None

    @staticmethod
    def get_random_username() -> Optional[str]:
        """Generate a random username using randomuser.me API"""
        try:
            response = requests.get(RANDOM_USER_API)
            response.raise_for_status()
            username = response.json()['results'][0]['login']['username']
            logger.info(f"Generated username: {username}")
            return username
        except Exception as e:
            logger.error(f"Failed to generate username: {e}")
            return None

class FirefoxDriverSetup:
    """Handles Firefox WebDriver setup and configuration"""
    
    @staticmethod
    def create_driver() -> webdriver.Firefox:
        """Create and configure Firefox WebDriver"""
        display = Display(visible=0, size=(800, 600))  # Virtual display (headless)
        display.start()
        options = Options()
        # Configure audio settings
        # Headless mode for Chrome
        options.add_argument("--headless")

        # Disable sandbox (required in some environments)
        options.add_argument("--no-sandbox")

        # Disable /dev/shm usage (prevents crashes in some environments)
        options.add_argument("--disable-dev-shm-usage")

        # Fake media streams (similar to Firefox preferences)
        options.add_argument("--use-fake-ui-for-media-stream")  # Automatically grant media permissions
        options.add_argument("--use-fake-device-for-media-stream")  # Use fake devices (camera/mic)

        # Disable autoplay for media (similar to Firefox preferences)
        options.add_argument("--autoplay-policy=no-user-gesture-required")
        
        driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
        driver.set_page_load_timeout(30)  # Increase page load timeout
        driver.set_script_timeout(30)     # Increase script timeout 
        
        logger.info("Initializing Firefox Driver")
        return driver

class JammableAutomation:
    """Main automation class for Jammable website"""
    
    def __init__(self):
        self.driver = FirefoxDriverSetup.create_driver()
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)
        self.account_gen = AccountGenerator()
        self.email = self.account_gen.get_temp_email()
        self.password = self.account_gen.generate_password()
        self.username = self.account_gen.get_random_username()

    def create_account(self) -> Tuple[str, str, str]:
        """Create a new Jammable account"""
        # Generate credentials

        if not all([self.email, self.password, self.username]):
            raise ValueError("Failed to generate account credentials")

        # Navigate to signup page
        self.driver.get(JAMMABLE_SIGNUP_URL)
        logger.info("Loaded Jammable signup page")
        time.sleep(3)

        # Fill in signup form
        self._fill_signup_form(self.username, self.email, self.password)
        
        return self.email, self.password, self.username

    def _fill_signup_form(self, username: str, email: str, password: str):
        """Fill in the signup form with generated credentials"""
        # Locate form elements
        username_input = self.driver.find_element(By.XPATH, '//input[@name="username"]')
        email_input = self.driver.find_element(By.XPATH, '//input[@name="email"]')
        password_input = self.driver.find_element(By.XPATH, '//input[@name="password"]')
        terms_checkbox = self.driver.find_element(By.XPATH, '//button[@role="checkbox"]')
        submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')

        # Fill form with delays to avoid detection
        username_input.send_keys(username)
        time.sleep(1)
        email_input.send_keys(email)
        time.sleep(1)
        password_input.send_keys(password)
        time.sleep(1)
        terms_checkbox.click()
        time.sleep(3)

        logger.info('Completed form submission')
        submit_button.click()
        
        # Wait for successful signup
        self.wait.until(EC.url_to_be("https://www.jammable.com/"))
        logger.info('Successfully created account')

    def process_audio(self, input_path: str):
        """Process audio file using Jammable's voice conversion"""
        try:
            # Navigate to voice conversion page
            self.driver.get(JAMMABLE_VOICE_URL)
            time.sleep(5)
            logger.info('Loaded voice conversion page')

            # Start conversion process
            self._initiate_conversion(input_path)
            
            # Download converted audio
            self._download_converted_audio(input_path)

        except Exception as e:
            logger.error(f"Error during audio processing: {e}")
            raise

    def _initiate_conversion(self, input_path: str):
        """Start the voice conversion process"""
        create_cover_button = self.driver.find_element(
            By.XPATH, 
            '/html/body/div/div/main/div/div/div[2]/div[2]/div[1][@type="button"]'
        )
        create_cover_button.click()        
        time.sleep(3)
        
        logging.info('Clicked Create Cover')
        
        try:
            email_input_opened = self.driver.find_element(By.XPATH, '/html/body/div[3]/div/div/form/div[1]/div/input')
            password_input_opened = self.driver.find_element(By.XPATH, '/html/body/div[3]/div/div/form/div[2]/div/input')
            login_button = self.driver.find_element(By.XPATH, '/html/body/div[3]/div/div/form/button')
            
            email_input_opened.send_keys(self.email)
            time.sleep(2)
            password_input_opened.send_keys(self.password)
            time.sleep(2)
            login_button.click()
            time.sleep(3)
        except Exception as e:
            logging.info('No login confirmation needed')
            time.sleep(5)
        
        button_for_check = None
        
        try: 
            button_for_check = self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[3]/div/div/section/section/form/div/div[2]/input[@name="url"]')))
        except Exception as e:
            logging.info('Cover button wasnt clicked, retrying')
            create_cover_button.click()
        
        time.sleep(3)
        if button_for_check:
            # Handle file upload
            file_input = self.driver.find_element(
                By.XPATH, 
                '/html/body/div[3]/div/div/section/section/form/input'
            )
            file_input.send_keys(os.path.abspath(input_path))
            logger.info('Uploaded audio file')

            # Navigate through conversion steps
            time.sleep(3)
            next_button = self.driver.find_element(
                By.XPATH, 
                '/html/body/div[3]/div/div/div[3]/div[4]/div/button'
            )
            next_button.click()
            
            time.sleep(3)
            final_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[3]/div/div/div[3]/div/div[4]/button')
            ))
            final_button.click()
            logger.info('Started conversion process')
        else:
            logger.critical('Failed to open modal')
            exit(1)

    def _download_converted_audio(self, input_path: str):
        """Download the converted audio file"""
        self.wait.until(EC.url_contains("https://www.jammable.com/conversion"))
        time.sleep(3)
        
        # Wait for conversion to complete
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div/div/main/div/section/div[1]/div/div/div[4]/button[2]')
        ))

        # Get converted audio URL
        audio_element = self.driver.find_element(
            By.XPATH, 
            '/html/body/div/div/main/div/section/div[1]/div/div/div[5]/audio'
        )
        audio_url = audio_element.get_attribute('src')
        logger.info(f"Found converted audio URL: {audio_url}")

        # Prepare download request
        cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
        headers = {
            'User-Agent': self.driver.execute_script("return navigator.userAgent"),
            'Referer': 'https://www.jammable.com/',
            'Accept': '*/*'
        }

        # Download converted file
        output_path = input_path.replace('.wav', '_Cartied.wav')
        response = requests.get(audio_url, cookies=cookies, headers=headers, stream=True)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            logger.info(f"Successfully downloaded converted audio to {output_path}")
        else:
            raise Exception(f"Download failed with status code: {response.status_code}")

    def cleanup(self):
        """Clean up browser resources"""
        try:
            self.driver.quit()
            logger.info("Successfully cleaned up resources")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

