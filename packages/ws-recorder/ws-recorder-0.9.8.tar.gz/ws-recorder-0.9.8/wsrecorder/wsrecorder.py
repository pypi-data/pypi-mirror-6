"""
WSRecorder is a tool that provides proxy for your webservices. This tool allows to record and serve webservices samples.
The proxy is python function decorator. Samples are XSLT templates, which transform requests to expected replies.
Samples have a form of decision trees, where in each node a test against configured xpath is performed; tree paths
depend on an xpath value for each request.

.. author:: Kamil Kujawinski <kamil@kujawinski.net>
"""

import os
import os.path
import logging
from lxml import etree
from functools import wraps
from copy import deepcopy
from . import tools


log = logging.getLogger(__name__)


def is_proper_xpath(xpath):
    try:
        etree.XPath(xpath)
    except etree.XPathSyntaxError:
        return False
    return True


def is_proper_writeable_dir(dir_path):
    test_file_path = os.path.join(dir_path, 'test_writing_file')
    try:
        with open(test_file_path, 'w'):
            return True
    except IOError:
        return False
    finally:
        try:
            os.unlink(test_file_path)
        except OSError:
            pass


def is_mode_allowed(mode):
    return mode in WSRecorder.Mode.__all__


def is_node_empty(node):
    return tools.is_lxml_node_empty(node) or node.xpath('wsr:empty', namespaces=NAMESPACES)


def clear_node(node):
    for empty in node.xpath('wsr:empty', namespaces=NAMESPACES):
        node.remove(empty)
    tools.clear_lxml_node(node)


XSLT_TEMPLATE_TPL = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/"></xsl:template>
</xsl:stylesheet>'''
XSLT_CHOOSE_TPL = '<xsl:choose xmlns:xsl="http://www.w3.org/1999/XSL/Transform"></xsl:choose>'
XSLT_OTHERWISE_TPL = '<xsl:otherwise xmlns:xsl="http://www.w3.org/1999/XSL/Transform"></xsl:otherwise>'
XSLT_WHEN_TPL = '<xsl:when xmlns:xsl="http://www.w3.org/1999/XSL/Transform"></xsl:when>'
DUMMY_WHEN_TEST = 'false()'
EMPTY_ELEMENT = '<wsr:empty xmlns:wsr="http://kjw.pt/ws-recorder"/>'
XSLT_OTHERWISE_WITH_EMPTY = '''<xsl:otherwise xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
                               <wsr:empty xmlns:wsr="http://kjw.pt/ws-recorder"/></xsl:otherwise>'''
NAMESPACES = {'xsl': 'http://www.w3.org/1999/XSL/Transform', 'wsr': 'http://kjw.pt/ws-recorder'}
xml_parser = etree.XMLParser(remove_blank_text=True)


def prepare_XSLT_WHEN(test_expression):
    out = etree.fromstring(XSLT_WHEN_TPL, xml_parser)
    out.attrib['test'] = test_expression
    return out


class ConfigurationException(Exception):
    pass


class NotRecordedException(Exception):
    pass


class WSRecorder(object):
    """
    Object of this class provides proxy for webservices. First you need to create an object of this class to use the
    proxy.
    """

    class Mode(object):
        TRANSPARENT = 'TRANSPARENT'
        RECORD = 'RECORD'
        OVERRIDE = 'OVERRIDE'
        SERVE = 'SERVE'
        SERVE_TRANSPARENT = 'SERVE_TRANSPARENT'
        SERVE_RECORD = 'SERVE_RECORD'

        __all__ = [TRANSPARENT, RECORD, OVERRIDE, SERVE, SERVE_TRANSPARENT, SERVE_RECORD]

    def __init__(self, request_msg_name, reply_envelope_body, output_dir,
                 mode=None, output_filename='{}.output', messages={},
                 pretty_print=False):
        """
        Initializes object of WSRecord.

        :mode: parameter that controls behaviour of WSRecorder. Default value: WSRecorder.Mode.TRANSPARENT.
            Available values:
            WSRecorder.Mode.RECORD - records samples according to configuration into output directory.
            WSRecorder.Mode.OVERRIDE - records sample according to configuration, overrides already recorded message.
            WSRecorder.Mode.SERVE - serves recorded samples, doesn't hit the webservices, if fails raise
                NotRecordedException.
            WSRecorder.Mode.TRANSPARENT - doesn't use recorded samples, just hit the webservices.
            WSRecorder.Mode.SERVE_TRANSPARENT - try to use recorded samples, if fails just hit the webservices.
            WSRecorder.Mode.SERVE_RECORD - try to use recorded samples, if fails just hit the webservices and
                record replies.
        :request_msg_name: xpath that indicates the name in the request message. Message name is afterwards used to
            configure specific handler for each message and to save replies of different messages in different files.
        :reply_envelope_body: xpath that indicates body of reply message. Reply body is that part of a reply message,
            which is meaningful and can change in replies. Everything "above" the reply body is constant and reused in
            every reply message.
        :output_dir: directory where recorded samples are stored in a RECORD mode and from which recorded samples are
            read in a SERVE mode.
        :output_filename: pattern for saved files. Default value {}.output. Message name is passed to string.format
            function.
        :messages: dictionary of configured messages. Keys in dictionary are messages names, values are list of xpaths,
            which are sequential checked against request message.
        :pretty_print: boolean param determines whether output file should be pretty printed. Default value: ``False``.

        Exceptions:
        - ConfigurationException: raised when:
            - Request message name is not proper xpath,
            - Reply envelope body is not proper xpath,
            - Chosen mode is not allowed,
            - Any xpath for message is not proper xpath,
            - Output directory path is not proper.

        """
        self.mode = mode or mode.TRANSPARENT
        self.request_msg_name = request_msg_name
        if not is_proper_xpath(self.request_msg_name):
            raise ConfigurationException('Request message name is not proper xpath')
        self.reply_envelope_body = reply_envelope_body
        if not is_proper_xpath(self.reply_envelope_body):
            raise ConfigurationException('Reply envelope body is not proper xpath')
        if not is_mode_allowed(self.mode):
            raise ConfigurationException('Chosen mode "%s" is not allowed' % self.mode)
        self.messages = messages
        for msg, paths in self.messages.items():
            for path in paths:
                if not is_proper_xpath(path):
                    raise ConfigurationException('Path <%s> for message %s is not proper xpath' % (path, msg))
        self.output_dir = output_dir
        if not is_proper_writeable_dir(self.output_dir):
            raise ConfigurationException('Given output directory path: <%s> is not proper' % self.output_dir)
        self.output_filename = output_filename
        self.pretty_print = pretty_print

    def decorator(self, fn, mode=None):
        """
        Proxy for your webservice. It requires that as a first argument the decorated function takes a request message
        and returns a reply of message. Requests and replies of messages must be Python string or lxml.etree._Element.

        Exceptions:
        - NotRecordedException - raised in SERVE mode if sample doesn't have reply for given request.
        - ConfigurationException - in proxy function, raised when:
            - configured xpaths doesn't match those saved in recorded sample, raise in modes: RECORD, OVERRIDE,
                SERVE_RECORD,
            - given mode is not allowed.
            - XPath with reply envelope body is not proper for given message reply.

        Example usage:
        @obj.decorator
        def webservice1(request):
            return reply
        """
        if mode is not None and not is_mode_allowed(mode):
            raise ConfigurationException('Chosen mode "%s" is not allowed' % mode)
        mode = mode or self.mode

        @wraps(fn)
        def wrapped(request, *args, **kwargs):
            if isinstance(request, etree._Element):
                request_lxml = request
            else:
                request_lxml = etree.fromstring(request, xml_parser)
            msg_name = self._get_msg_name(request_lxml)
            file_name = self.output_filename.format(msg_name)
            file_path = os.path.join(self.output_dir, file_name)

            def _handle_record_reply():
                log.info("Hitting webservice %s" % msg_name)
                rec_reply = fn(request, *args, **kwargs)
                if isinstance(rec_reply, etree._Element):
                    rec_reply_lxml = rec_reply
                else:
                    rec_reply_lxml = etree.fromstring(rec_reply, xml_parser)
                self._dump_reply(request=request_lxml,
                                 reply=rec_reply_lxml,
                                 file_path=file_path,
                                 msg_name=msg_name)
                return rec_reply

            if msg_name not in self.messages or mode in WSRecorder.Mode.TRANSPARENT:
                log.info("Hitting webservice %s" % msg_name)
                return fn(request, *args, **kwargs)
            elif mode in (WSRecorder.Mode.RECORD, WSRecorder.Mode.OVERRIDE):
                return _handle_record_reply()
            else:  # SERVE
                try:
                    try:
                        with open(file_path, 'r+') as f:
                            transform = etree.XSLT(etree.parse(f))
                            reply_lxml = transform(request_lxml)
                            if reply_lxml.xpath(self.reply_envelope_body)[0].xpath('wsr:empty', namespaces=NAMESPACES):
                                raise NotRecordedException()
                            log.info("Serving webservice %s" % msg_name)
                            return etree.tostring(reply_lxml)
                    except IOError:
                        raise NotRecordedException()
                except NotRecordedException:
                    log.info("Reply sample not found for given request")
                    if mode == WSRecorder.Mode.SERVE_TRANSPARENT:
                        log.info("Hitting webservice %s" % msg_name)
                        return fn(request, *args, **kwargs)
                    elif mode == WSRecorder.Mode.SERVE_RECORD:
                        return _handle_record_reply()
                    else:
                        raise
        return wrapped

    def _get_msg_name(self, request_lxml):
        msg_name_element = request_lxml.xpath(self.request_msg_name)
        if msg_name_element:
            return msg_name_element[0].tag
        raise ConfigurationException('XPath with request msg name doesn\'t return any node for given message.')

    def _reply_new_file_content(self, reply):
        reply = deepcopy(reply)
        try:
            reply_body = reply.xpath(self.reply_envelope_body)[0]
        except IndexError:
            raise ConfigurationException('XPath with reply envelope body doesn\'t return any node for given message.')

        clear_node(reply_body)

        output = etree.fromstring(XSLT_TEMPLATE_TPL, xml_parser)
        output.xpath('//xsl:template[@match="/"]', namespaces=NAMESPACES)[0].append(reply)
        return output

    def _get_output_content(self, file_path, reply):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if content:
                    return etree.fromstring(content, xml_parser)
        except IOError:
            content = None
        if not content:
            return self._reply_new_file_content(reply)

    def _traverse_and_update_reply(self, msg_name, request, reply, reply_base):
        msg_xpaths = self.messages[msg_name] or []

        reply_base_body = reply_base.xpath('//xsl:template' + self.reply_envelope_body,
                                           namespaces=NAMESPACES)[0]
        xsl_chosen_option = reply_base_body
        xpath_tests = []

        for xpath in msg_xpaths:
            xpath_value = request.xpath(xpath)
            xsl_choose = xsl_chosen_option.xpath('./xsl:choose', namespaces=NAMESPACES)
            if xsl_choose:
                xsl_choose = xsl_choose[0]
            else:
                xsl_choose = etree.fromstring(XSLT_CHOOSE_TPL, xml_parser)
                clear_node(xsl_chosen_option)
                xsl_chosen_option.append(xsl_choose)
            otherwise_option = xsl_choose.xpath('./xsl:otherwise', namespaces=NAMESPACES)
            if xpath_value:
                conflict_nodes = []
                when_option = []
                when_nodes = xsl_choose.xpath('./xsl:when', namespaces=NAMESPACES)
                value = xpath_value[0] if isinstance(xpath_value, list) else xpath_value
                when_test_expr = "{xpath}='{xpath_value}'".format(xpath=xpath, xpath_value=value)
                xpath_tests.append(when_test_expr)
                for node in when_nodes:
                    test_attr = node.attrib['test']
                    if test_attr != DUMMY_WHEN_TEST and not test_attr.startswith(xpath):
                        conflict_nodes.append(node)
                    elif test_attr == when_test_expr:
                        when_option.append(node)

                if conflict_nodes:
                    conflicted_xpaths = [n.attrib['test'] for n in conflict_nodes]
                    error_msg = 'There is a conflict between recorded sample vs current configuration. Expected ' + \
                                'test against %s, but found tests: %s''' % (xpath, ', '.join(conflicted_xpaths))
                    raise ConfigurationException(error_msg)

                # should be one value, if more means the it is not the best conf xpath
                if when_option:
                    when_option = when_option[0]
                else:
                    dummy_option = xsl_choose.xpath('./xsl:when[@test="%s"]' % DUMMY_WHEN_TEST, namespaces=NAMESPACES)
                    if dummy_option:
                        dummy_option[0].getparent().remove(dummy_option[0])
                    when_option = prepare_XSLT_WHEN(when_test_expr)
                    xsl_choose.insert(0, when_option)
                xsl_chosen_option = when_option
                if not otherwise_option:
                    otherwise_empty_option = etree.fromstring(XSLT_OTHERWISE_WITH_EMPTY, xml_parser)
                    xsl_choose.append(otherwise_empty_option)
            else:
                xpath_tests.append('otherwise')
                if otherwise_option:
                    otherwise_option = otherwise_option[0]
                else:
                    dummy_when_option = prepare_XSLT_WHEN(DUMMY_WHEN_TEST)
                    xsl_choose.insert(0, dummy_when_option)
                    otherwise_option = etree.fromstring(XSLT_OTHERWISE_TPL, xml_parser)
                    xsl_choose.append(otherwise_option)
                xsl_chosen_option = otherwise_option

        if xsl_chosen_option.tag == '{http://www.w3.org/1999/XSL/Transform}otherwise':
            if tools.is_lxml_node_empty(xsl_chosen_option):
                xsl_chosen_option.append(etree.fromstring(EMPTY_ELEMENT, xml_parser))

        try:
            reply_body = reply.xpath(self.reply_envelope_body)[0]
        except IndexError:
            raise ConfigurationException('XPath with reply envelope body is not proper for this message.')

        log.debug('Decision path for given reply: %s', ' > '.join(xpath_tests))
        if not is_node_empty(xsl_chosen_option):
            if self.mode == WSRecorder.Mode.OVERRIDE:
                log.info("Overriding saved reply sample.")
                clear_node(xsl_chosen_option)
                for element in reply_body.iterchildren():
                    xsl_chosen_option.append(element)
            else:
                log.info("There is reply sample for given reply, sample is not overridden.")
        else:
            log.info("Recording reply sample.")
            clear_node(xsl_chosen_option)
            for element in reply_body.iterchildren():
                xsl_chosen_option.append(element)

    def _dump_reply(self, request, reply, file_path, msg_name):
        content = self._get_output_content(file_path, reply)
        if content is None:
            content = self._reply_new_file_content(reply)

        with open(file_path, 'w+') as f:
            self._traverse_and_update_reply(msg_name=msg_name,
                                            request=request,
                                            reply=reply,
                                            reply_base=content)
            f.write(etree.tostring(content, pretty_print=self.pretty_print))
