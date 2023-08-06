===========
WS Recorder
===========

Description
-----------

WSRecorder is a tool that provides proxy for your webservices. This tool allows to record and serve webservices samples.
The proxy is python function decorator. Samples are XSLT templates, which transform requests to expected replies.
Samples have a form of decision trees, where in each node a test against configured xpath is performed; tree paths
depend on an xpath value for each request.


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

Object of this class provides proxy for webservices. First you need to create an object of this class to use the proxy.

``WSRecorder.__init__(self, request_msg_name, reply_envelope_body, output_dir, mode=None, output_filename='{0}.output', messages={})``:

Initializes object of WSRecord.

**mode**:  parameter that controls behaviour of WSRecorder. Default value: ``WSRecorder.Mode.TRANSPARENT``.

Available values:

- ``WSRecorder.Mode.RECORD`` - records samples according to configuration into output directory.
- ``WSRecorder.Mode.OVERRIDE`` - records sample according to configuration, overrides already recorded message.
- ``WSRecorder.Mode.SERVE`` - serves recorded samples, doesn't hit the webservices.
- ``WSRecorder.Mode.TRANSPARENT`` - doesn't use recorded samples, just hit the webservices.

**request_msg_name**: xpath that indicates the name in the request message. Message name is afterwards used to configure
specific handler for each message and to save replies of different messages in different files.

**reply_envelope_body**: xpath that indicates body of reply message. Reply body is that part of a reply message, which
is meaningful and can change in replies. Everything "above" the reply body is constant and reused in every reply message.

**output_dir**: directory where recorded samples are stored in a ``RECORD``/``OVERRIDE`` modes and from which recorded
samples are read in a ``SERVE`` mode.

**output_filename**: pattern for saved files. Default value ``{}.output``. Message name is passed to ``string.format``
function.

**messages**: dictionary of configured messages. Keys in dictionary are messages names, values are list of xpaths,
which are sequential checked against request message.


``WSRecorder.decorator(self, fn, mode=None)``:

Proxy for your webservice. It requires that as a first argument the decorated function takes a request message
and returns a reply of message. Requests and replies of messages must be Python ``string`` or ``lxml.etree._Element``.

Example usage::

    @obj.decorator
    def webservice1(request):
        return reply

