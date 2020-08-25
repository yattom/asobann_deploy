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


@pytest.mark.parametrize('param', DEPLOYMENTS, ids=[p['id'] for p in DEPLOYMENTS])
def test_alive(browser, param):
    browser.get(param['url'])
    WebDriverWait(browser, 5).until(
        expected_conditions.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'asobann'))
    assert re.match('^.*/tables/[0-9a-z]+$', browser.current_url)
    WebDriverWait(browser, 5).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'div.component')))

    browser.close()  # do not close on failure


NON_SSLS = [p for p in DEPLOYMENTS if 'no_ssl' in p['id']]

@pytest.mark.parametrize('param', NON_SSLS, ids=[p['id'] for p in NON_SSLS])
def test_no_ssl_should_be_redirected(browser, param):
    browser.get(param['url'])
    WebDriverWait(browser, 5).until(
        expected_conditions.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'asobann'))
    assert browser.current_url.startswith('https')
    WebDriverWait(browser, 5).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'div.component')))

    browser.close()  # do not close on failure
