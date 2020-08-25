from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import re
import pytest

from .deployment_config_local import DEPLOYMENTS


@pytest.fixture
def browser():
    options = Options()
    # options.headless = True
    browser = webdriver.Firefox(options=options)
    browser.delete_all_cookies()
    yield browser


@pytest.mark.parametrize('testcase', DEPLOYMENTS.items())
def test_alive(browser, testcase):
    case_name, param = testcase
    browser.get(param['url'])
    WebDriverWait(browser, 5).until(
        expected_conditions.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'asobann'))
    assert re.match('^.*/tables/[0-9a-z]+$', browser.current_url)

    browser.close()  # do not close on failure


@pytest.mark.parametrize('testcase', [e for e in DEPLOYMENTS.items() if 'no_ssl' in e[0]])
def test_no_ssl_should_be_redirected(browser, testcase):
    case_name, param = testcase
    browser.get(param['url'])
    WebDriverWait(browser, 5).until(
        expected_conditions.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'asobann'))
    assert browser.current_url.startswith('https')

    browser.close()  # do not close on failure
