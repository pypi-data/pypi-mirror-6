"""
Here you can create samples of your widgets by providing default parameters,
inserting them in a container widget, mixing them with other widgets, etc...
These samples will appear in the WidgetBrowser

See http://toscawidgets.org/documentation/WidgetBrowser for more information
"""

import widgets


class DemoPygmentize(widgets.Pygmentize):
    # Provide default parameters, value, etc... here
    # default = <some-default-value>
    formatter_args = dict(
        linenos='table',
        lineanchors='line',
        linespans='line',
        anchorlinenos=True,
    )
    lexer_name = 'Python'
    filename = 'hello.py'
    source = u'''
#!/usr/bin/python

import sys

for line in sys.stdin:
    print int(line)**2
'''
