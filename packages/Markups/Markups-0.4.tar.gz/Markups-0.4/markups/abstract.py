# This file is part of python-markups module
# License: BSD
# Copyright: (C) Dmitry Shachnev, 2012

class AbstractMarkup(object):
	"""Abstract class for markup languages"""

	file_extensions = ()

	def __init__(self, filename=None):
		self.filename = filename
		self.enable_cache = False
		self.cache = {}

	def available():
		return True

	def get_document_title(self, text):
		return ''

	def get_document_body(self, text):
		raise NotImplementedError

	def get_stylesheet(self, text=''):
		return ''

	def get_javascript(self, text='', webenv=False):
		return ''

	def get_whole_html(self, text, custom_headers='', include_stylesheet=True,
	                   fallback_title='', webenv=False):
		self.enable_cache = True
		body = self.get_document_body(text)
		stylesheet = ('<style type="text/css">\n' + self.get_stylesheet(text)
			+ '</style>\n' if include_stylesheet else '')
		title = self.get_document_title(text)
		if not title:
			title = fallback_title
		title_string = ('<title>' + title + '</title>\n') if title else ''
		javascript = self.get_javascript(text, webenv)
		self.enable_cache = False
		self.cache = {}
		return (
		'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n'
		'<html>\n<head>\n'
		'<meta http-equiv="content-type" content="text/html; charset=utf-8">\n'
		+ custom_headers + title_string + stylesheet + javascript
		+ '</head>\n<body>\n' + body + '</body>\n</html>\n'
		)
