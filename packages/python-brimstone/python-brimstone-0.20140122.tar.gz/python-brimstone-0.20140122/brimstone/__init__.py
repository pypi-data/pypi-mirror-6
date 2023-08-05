# -*- mode: python; coding: utf-8 -*-

import warnings

warnings.filterwarnings("once", category=DeprecationWarning)


import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidElementStateException

from commodity.testing import wait_that, call_with

import logging
logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
logger.setLevel(logging.WARNING)


class ExtendedWebElement:
    def __init__(self, browser, element):
        self._browser = browser
        self._element = element

    def __getattr__(self, name):
        return getattr(self._element, name)

    def get_children(self, selector):
        return self._element.find_elements_by_css_selector(selector)

    def set_attribute(self, key, value):
        self._browser.set_attribute(self._element, key, value)

    def get_value(self):
        return self._element.get_attribute('value')

    def set_value(self, value):
        try:
            self._element.clear()
            self._element.send_keys(str(value))
        except InvalidElementStateException:
            self._browser.set_attribute(self._element, "value", value)

    def set_bool_state(self, state):
        self._browser.set_attribute(self._element, "checked", state)


class Browser(object):
    def __init__(self, left_open=False):
        self._left_open = left_open
        self._running = True

    # FIXME: move this to a WebPage (or Window) object
    @property
    def title(self):
        return self.driver.title

    def open(self, url, debug=False):
        self.driver.get(url)
        wait_that(self.is_ready, call_with().returns(True))

        # wait = WebDriverWait(self.driver, 10)
        # wait.until(EC.element_to_be_clickable((By.Id,'someid')))


        if debug:
            self.open_chrome_inspector()

    def new_tab(self, url):
        cmd = """
            a = document.createElement('a');
            a.setAttribute("href", "{}");
            a.setAttribute("target", "_blank");
            a.click();
        """.format(url)

        self.driver.execute_script(cmd)
        self.driver.switch_to_window(self.driver.window_handles[-1])
        wait_that(self.is_ready, call_with().returns(True))

    def exit(self):
        warnings.warn("Browser.exit() is deprecated. Use Browser.quit()",
                      DeprecationWarning)
        self.quit()

    def quit(self):
        if self._running:
            self.driver.quit()
            self._running = False

    ## FIXME!!!! this is wise specific!! it can not be here!
    def is_ready(self):
        status = self.driver.find_element_by_id('wiseReady')
        return bool(status)

    def find_element(self, query):
        try:
            element = self.driver.find_element_by_css_selector(query)
            return ExtendedWebElement(self, element)
        except NoSuchElementException:
            return None

    def find_elements(self, query):
        retval = []
        try:
            for e in self.driver.find_elements_by_css_selector(query):
                retval.append(ExtendedWebElement(self, e))
        except NoSuchElementException:
            pass

        return retval

    def set_attribute(self, node, key, value):
        if node is None:
            raise TypeError("node could not be None")

        if isinstance(value, bool) and not value:
            cmd = 'removeAttribute("{}")'.format(key)
        else:
            value = json.dumps(value)
            cmd = 'setAttribute("{}", {})'.format(key, value)

        script = 'arguments[0].{};'.format(cmd)
        self.driver.execute_script(script, node)

    def js(self, script):
        return self.driver.execute_script(script)


class Chrome(Browser):
    def __init__(self, *args, **kargs):
        self.driver = webdriver.Chrome()
        super(Chrome, self).__init__(*args, **kargs)


class PhantomJS(Browser):
    def __init__(self, *args, **kargs):
        self.driver = webdriver.PhantomJS()
        super(PhantomJS, self).__init__(*args, **kargs)
