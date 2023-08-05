# -*- mode: python; coding: utf-8 -*-

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


class Chrome(object):
    def __init__(self, left_open=False):
        self._left_open = left_open
        self.driver = webdriver.Chrome(
            service_log_path="/tmp/chromedriver.log")
        self._running = True

    def __del__(self):
        if self._left_open:
            return

        self.exit()

    # FIXME: move this to a WebPage (or Window) object
    @property
    def title(self):
        return self.driver.title

    def open(self, url, debug=False):
        self.driver.get(url)
        wait_that(self.is_ready, call_with().returns(True))

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
        if self._running:
            self.driver.quit()
            self._running = False

    ## FIXME!!!! this is wise specific!! it can not be here!
    def is_ready(self):
        status = self.driver.execute_script("return wiseReady;")
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

    def open_chrome_inspector(self):
        def open_js_console():
            try:
                from gexter import gext
            except ImportError:
                print "Warning: gexter is not available, could not open JS console"
                return 0

            # FIXME: why the need for this?
            import time
            time.sleep(0.5)

            gext.keyboard.generateKeyEvents("<Control_L><Shift_L>j")

        import threading
        threading.Thread(target=open_js_console).start()

        # FIXME: to avoid using gexter and sleep:
        # try the following:
        #  - open new tab with "chrome://inspect/#"
        #  - find link to explore the current tab
        #  - click on it
        # NOTE: this says: Not allowed to load local resource: chrome://inspect/

        # import time
        # time.sleep(5)

        # self.new_tab("chrome://inspect")
        # cmd = """
        #     var a = $('#pages');
        #     var b = a.children[0].lastChild;
        #     b.click();
        # """
        # self.driver.execute_script(cmd)
