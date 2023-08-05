"""

"""
import unittest
import os

import mock
from nose.plugins import PluginTester
from fresher.noseplugin import FresherNosePlugin

import holmium.core
from tests import utils


support = os.path.join(os.path.dirname(__file__), "support")

class TestFresherIntegration(PluginTester, unittest.TestCase):
    activate = "--with-holmium"
    args = ['--holmium-environment=development'
        , '--holmium-browser=firefox'
        , '--with-fresher'
    ]
    suitepath = os.path.join(support, 'cucumber')
    plugins = [holmium.core.HolmiumNose(), FresherNosePlugin()]
    def setUp(self):
        self.old_mapping = holmium.core.config.browser_mapping
        holmium.core.config.browser_mapping = utils.build_mock_mapping("firefox")
        self.driver = holmium.core.config.browser_mapping["firefox"]
        self.driver.return_value.title = "test"
        e1 = mock.Mock()
        e1.text = "e"
        self.driver.return_value.find_elements.return_value = [e1] * 100
        e1.find_element.return_value.text = "e"
        self.driver.return_value.find_element.return_value.find_element.return_value.text = "e"
        self.driver.return_value.find_element.return_value.text = "e"
        mock_section_element = mock.Mock()
        mock_section_element.text = "e"
        self.driver.return_value.find_element.return_value.find_elements.return_value = [mock_section_element]
        self.sleep_patcher = mock.patch("time.sleep")
        self.sleep_mock = self.sleep_patcher.start()

        super(TestFresherIntegration,self).setUp()
    def runTest(self):
        assert "Ran 8 tests" in self.output, self.output
        assert "FAILED (errors=6)" in self.output, self.output
        assert "KeyError: u'moo'" in self.output, self.output
        assert "TestPage does not contain an element named not_existent" in self.output
        assert "page object FooPage not found. did you import it?" in self.output
        assert "'TestSection' object has no attribute 'moo'" in self.output
        assert "page object TestPage does not contain a method noop" in self.output
        assert "do_stuff() takes exactly 3 arguments (4 given)" in self.output
        assert self.driver.call_count == 1, self.driver.call_count
        self.driver.return_value.get.assert_any_call("http://www.google.com")
        self.driver.return_value.get.assert_any_call("http://www.google.com/login")
        assert self.driver.return_value.delete_all_cookies.call_count == 8, self.driver.return_value.delete_all_cookies.call_count
    def tearDown(self):
        holmium.core.config.browser_mapping = self.old_mapping
        self.sleep_patcher.stop()

