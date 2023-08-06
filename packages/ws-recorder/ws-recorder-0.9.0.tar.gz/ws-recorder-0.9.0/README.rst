===========
WS Recorder
===========

Description
-----------

WSRecorder tool, which provides proxy for your webservices. Proxy allows recording and serving webservices' samples.
Proxy has form of function decorator. Samples are XSLT templates, which transform request to expected reply.
XSLT template is created as decision tree, where in each node is performed test against configured xpath, paths in
tree depends of value of xpath for each request.


Usage
-----

Example::

    params = {
        'request_msg_name': '//request/*',
        'reply_envelope_body': '//reply/*',
        'messages': {
            'msg1': [
                '//msg1/param1/text()',
                '//msg1/param2/text()'
            ],
        },
        'output_dir': '/tmp/tmpdir/,
    }

    recorder = WSRecorder(mode=WSRecorder.Mode.RECORD, **params)
    cls.record_service = staticmethod(recorder.decorator(web_service_mockup))

Documentation
-------------

Object of this class provide proxy for werbservices. To use proxy you need to create object of this class before.


WSRecorder.__init__(self, request_msg_name, reply_envelope_body, output_dir, mode=None, output_filename='{0}.output', messages={}):

:request_msg_name: xpath that indicates name of request message. Message name is afterward used to
    configure specific handler for each message and to save replies of different messages to different files.
:reply_envelope_body: xpath that indicates body of reply message. Reply body is that part of reply, which
    is meaningful and changes for every requests. Everything "above" the reply body is reused in every reply
    message.
:output_dir: - directory where recorded samples are stored and which is read to serve already recorded samples.
:mode: controls behaviour of WSRecorder. Default value: WSRecorder.Mode.TRANSPARENT. Available values:
    WSRecorder.Mode.RECORD - records samples according to configuration to output directory.
    WSRecorder.Mode.OVERRIDE - records sample according to configuration, if finds that such message was already
    recorded, overrides it.
    WSRecorder.Mode.SERVE - serves recorded samples, doesn't hit the webservices.
    WSRecorder.Mode.TRANSPARENT - serves recorded samples, just hit the webservices.
:output_filename: pattern for saved files. Default value {0}.output. To format function message name is passed.
:messages: dictionary of configured messages. Keys in dictionary are messages names, values are list of xpaths,
    which are sequential checked against request message.


WSRecorder.decorator(self, fn, mode=None):

Proxy for your webservice. It requires that decorated function as first argument takes request message
and return jest reply of message. Request and replies of messages must be Python string or lxml.etree._Element.

Example usage::

    @obj.decorator
    def webservice1(request):
        return {}

