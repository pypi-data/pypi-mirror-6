# -*- coding: utf-8 -*-

from radish.exceptions import RadishError
from radish.config import Config

from getpass import getuser
from socket import gethostname
from re import compile


class ResultWriter(object):
    DEFAULT_FILENAME = "result.xml"

    def __init__(self, endResult, starttime, endtime):
        self._endResult = endResult
        self._starttime = starttime
        self._endtime = endtime

    def generate(self):
        try:
            from lxml import etree
        except:
            raise RadishError("No lxml support. Please install python-lxml")

        testrun_element = etree.Element(
            "testrun",
            starttime=self._starttime.strftime("%Y-%m-%dT%H:%M:%S"),
            endtime=self._endtime.strftime("%Y-%m-%dT%H:%M:%S"),
            duration=str((self._endtime - self._starttime).total_seconds()),
            agent="%s@%s" % (getuser(), gethostname())
        )

        for feature in self._endResult.get_features():
            feature_element = etree.Element(
                "feature",
                sentence=feature.get_sentence(),
                id=str(feature.get_id()),
                result=self._get_result_text(feature.has_passed()),
                starttime=feature.get_starttime().strftime("%Y-%m-%dT%H:%M:%S"),
                endtime=feature.get_endtime().strftime("%Y-%m-%dT%H:%M:%S"),
                duration=str(feature.get_duration()),
                testfile=feature.get_filename()
            )

            description_element = etree.Element("description")
            description_element.text = etree.CDATA(feature.get_description())

            scenarios_element = etree.Element("scenarios")

            for scenario in feature.get_scenarios():
                scenario_element = etree.Element(
                    "scenario",
                    sentence=scenario.get_sentence(),
                    id=str(scenario.get_id()),
                    result=self._get_result_text(scenario.has_passed()),
                    starttime=scenario.get_starttime().strftime("%Y-%m-%dT%H:%M:%S"),
                    endtime=scenario.get_endtime().strftime("%Y-%m-%dT%H:%M:%S"),
                    duration=str(scenario.get_duration())
                )

                for step in scenario.get_steps():
                    step_element = etree.Element(
                        "step",
                        sentence=step.get_sentence(),
                        id=str(step.get_id()),
                        result=self._get_result_text(step.has_passed()),
                        starttime=step.get_starttime().strftime("%Y-%m-%dT%H:%M:%S"),
                        endtime=step.get_endtime().strftime("%Y-%m-%dT%H:%M:%S"),
                        duration=str(step.get_duration())
                    )

                    if step.has_passed() is False:
                        failure_element = etree.Element(
                            "failure",
                            type=step.get_fail_reason().get_name(),
                            message=self._strip_ansi_text(step.get_fail_reason().get_reason())
                        )
                        failure_element.text = etree.CDATA(self._strip_ansi_text(step.get_fail_reason().get_traceback()))
                        step_element.append(failure_element)

                    scenario_element.append(step_element)
                scenarios_element.append(scenario_element)

            feature_element.append(description_element)
            feature_element.append(scenarios_element)
            testrun_element.append(feature_element)

        with open(Config().result_file or ResultWriter.DEFAULT_FILENAME, "w") as f:
            f.write(etree.tostring(testrun_element, pretty_print=True, xml_declaration=True, encoding="utf-8"))

    def _get_result_text(self, result):
        if result is True:
            return "passed"
        if result is False:
            return "failed"
        if result is None:
            return "skipped"

    # FIXME: register this methods somewhere as util
    def _strip_ansi_text(self, text):
        pattern = compile("(\\033\[\d+(?:;\d+)*m)")
        return pattern.sub("", text)
