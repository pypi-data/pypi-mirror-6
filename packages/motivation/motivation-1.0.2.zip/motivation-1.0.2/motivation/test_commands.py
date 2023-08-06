import six

from motivation import commands

def test_jm():
	res = commands.jm(None, None, "#inane", None, "")
	assert isinstance(res, six.text_type)
