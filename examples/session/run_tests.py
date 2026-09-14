"""Tiny fixture adapter; real projects should use their test runner's JUnit output."""

import sys
import unittest
import xml.etree.ElementTree as ET


class JUnitResult(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        self.case = ET.SubElement(suite_xml, "testcase", name=test.id())

    def addFailure(self, test, err):
        super().addFailure(test, err)
        ET.SubElement(self.case, "failure").text = self._exc_info_to_string(err, test)

    def addError(self, test, err):
        super().addError(test, err)
        ET.SubElement(self.case, "error").text = self._exc_info_to_string(err, test)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        ET.SubElement(self.case, "skipped", message=reason)


suite_xml = ET.Element("testsuite", name="session")
suite = unittest.defaultTestLoader.discover("tests")
result = unittest.TextTestRunner(resultclass=JUnitResult, verbosity=2).run(suite)
suite_xml.set("tests", str(result.testsRun))
suite_xml.set("failures", str(len(result.failures)))
suite_xml.set("errors", str(len(result.errors)))
suite_xml.set("skipped", str(len(result.skipped)))
ET.ElementTree(suite_xml).write("test-results.xml", encoding="utf-8", xml_declaration=True)
sys.exit(0 if result.wasSuccessful() and result.testsRun else 1)
