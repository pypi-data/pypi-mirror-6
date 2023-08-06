import docutils
import docutils.core

def rst_formatter(text):
    return docutils.core.publish_parts(text, writer_name='html')['html_body']


def html_formatter(text):
    return text


FORMATTERS = {'rst': rst_formatter,
              'html': html_formatter}