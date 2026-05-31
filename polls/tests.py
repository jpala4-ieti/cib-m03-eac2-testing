from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options


class MySeleniumTests(StaticLiveServerTestCase):
    # No creem una BD de test (comentem la linia)
    # fixtures = ['testdb.json',]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        # Mode headless: imprescindible per a GitHub Actions
        opts.add_argument('--headless=new')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        # Creem el superusuari (aixo SI per codi)
        user = User.objects.create_user('isard', 'isard@isardvdi.com', 'pirineus')
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_view_site_torna_codi_200(self):
        # 1) Anar a la pagina de login de l'admin
        self.selenium.get(f'{self.live_server_url}/admin/login/')

        # 2) Fer login simulant un usuari (Selenium, no per codi)
        username = self.selenium.find_element(By.NAME, 'username')
        password = self.selenium.find_element(By.NAME, 'password')
        username.send_keys('isard')
        password.send_keys('pirineus')
        self.selenium.find_element(By.XPATH, "//input[@type='submit']").click()

        # 3) Comprovar que hem entrat (existeix el boto 'Log out')
        self.selenium.find_element(By.XPATH, "//button[text()='Log out']")

        # 4) Localitzar l'enllac 'View site' i agafar la seva URL
        view_site = self.selenium.find_element(By.XPATH, "//a[text()='View site']")
        href = view_site.get_attribute('href')
        self.assertIsNotNone(href, 'No existeix el boto View site')

        # 5) Clicar 'View site'
        view_site.click()

        # 6) Comprovar que la pagina d'arrel es valida (codi 200).
        #    Selenium no exposa el codi HTTP directament, aixi que
        #    comprovem que el contingut esperat hi es i que no es una
        #    pagina d'error de Django.
        body = self.selenium.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Benvingut a Polls', body)
        self.assertNotIn('Page not found', body)
        self.assertNotIn('Server Error', body)
