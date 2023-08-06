__author__ = 'jcorbett'


import configparser
import logging
import sys
import json
import time

from ..amqp import AMQPConnection

from slickqa import SlickConnection, AutomaticTestrunGroup, Testrun, MatchCriteria, ComparisonTypes, TestrunGroup
from slickqa import micromodels
from kombu import Consumer, Queue
from kombu.transport.base import Message

def get_dotted_attr(obj, attr_name):
    """
    Get the value of the attribute.  Unlike getattr this accepts nested or 'dotted' attributes.
    """
    if '.' not in attr_name:
        return getattr(obj, attr_name)
    else:
        L = attr_name.split('.', 1)
        return get_dotted_attr(getattr(obj, L[0]), L[1])

class AutomaticTestrunGroupPlugin(object):
    """The automatic testrun group plugin, that creates testrun groups and puts testruns into them, automatically!"""

    def __init__(self, configuration, amqpcon, slick):
        assert(isinstance(configuration, configparser.ConfigParser))
        assert(isinstance(amqpcon, AMQPConnection))
        assert(isinstance(slick, SlickConnection))
        self.configuration = configuration
        self.amqpcon = amqpcon
        self.logger = logging.getLogger('narc.plugins.testrungroup.AutomaticTestrunGroupPlugin')
        self.logger.debug("Automatic Testrun Group Plugin is gathering settings from slick.")
        self.slick = slick
        self.configured = False
        if self.configuration.has_option("AutomaticTestrunGroupPlugin", "disable"):
            self.logger.info("Automatic Testrun Group Plugin disabled")
            return
        else:
            self.configured = True

        self.channel = amqpcon.add_channel()
        self.queue = Queue('narc_auto_testrun_group', exchange=amqpcon.exchange, routing_key='create.Testrun', durable=True)
        self.consumer = Consumer(self.channel, queues=[self.queue,], callbacks=[self.testrun_created,])
        amqpcon.add_consumer(self.consumer)

    def matches(self, testrun, rule):
        """
        Does the testrun match the rule.
        """
        assert isinstance(testrun, Testrun)
        assert isinstance(rule, AutomaticTestrunGroup)
        matches = None
        for matcher in rule.matchers:
            matchValue = False
            assert isinstance(matcher, MatchCriteria)
            try:
                value = get_dotted_attr(testrun, matcher.propertyName)
                self.logger.debug("Checking testrun '{}' to see if {} {} {}, actual value is {}", testrun.name, matcher.propertyName, matcher.comparisonType, matcher.propertyValue, value)
                if matcher.comparisonType == ComparisonTypes.CONTAINS:
                    if matcher.propertyValue in value:
                        matchValue = True
                elif matcher.comparisonType == ComparisonTypes.EQUALS:
                    if matcher.propertyValue == value:
                        matchValue = True
                elif matcher.comparisonType == ComparisonTypes.EQUALS_IGNORE_CASE:
                    if matcher.propertyValue.lower() == value.lower():
                        matchValue = True
            except:
                self.logger.warn("Caught Exception while trying to check matcher: ", exc_info=sys.exc_info())
                return False
            if matchValue is False:
                return False
            if matchValue is True and matches is None:
                matches = True
        return matches is True

    def testrun_created(self, body, message):
        assert(isinstance(message, Message))
        if not message.acknowledged:
            message.ack()
        testrun = Testrun.from_dict(body)
        self.logger.debug("Recieved testrun with id {} and name '{}'", testrun.id, testrun.name)
        rules = self.slick.systemconfigurations(AutomaticTestrunGroup).find()
        self.logger.debug("Found {} rules to check testrun against.", len(rules))
        for rule in rules:
            assert isinstance(rule, AutomaticTestrunGroup)
            if self.matches(testrun, rule):
                try:
                    testrun_group_name = rule.template.format(testrun=testrun)
                    self.logger.debug("Trying to find a testrun group with name '{}'", testrun_group_name)
                    testrun_group = self.slick.testrungroups.findOne(q="eq(name,\"" + testrun_group_name + "\")", orderby="-created", limit=1)
                    if testrun_group is None:
                        self.logger.debug("Going to have to create testrun group.")
                        testrun_group = TestrunGroup()
                        testrun_group.name = testrun_group_name
                        testrun_group.groupType = rule.groupType
                        self.slick.testrungroups(testrun_group).create()
                    if rule.replaceSameBuild:
                        for trgtestrun in testrun_group.testruns:
                            if testrun.build.buildId == trgtestrun.build.buildId:
                                self.logger.debug("Found existing testrun '{}' with build '{}', removing it from the group.", trgtestrun.name, trgtestrun.build.name)
                                self.slick.testrungroups(testrun_group.id).remove_testrun(trgtestrun)
                    self.slick.testrungroups(testrun_group.id).add_testrun(testrun)
                    self.logger.info("Added testrun '{}' to testrun group '{}'.", testrun.name, testrun_group.name)
                except:
                    self.logger.warn("Had an issue with the rule: ", exc_info=sys.exc_info())


