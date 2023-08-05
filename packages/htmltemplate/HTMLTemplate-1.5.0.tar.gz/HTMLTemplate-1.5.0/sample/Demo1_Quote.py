#!/usr/bin/env python

# Demonstrates how to:
# - assign strings as HTML elements' content.


from HTMLTemplate import Template

#################################################
# TEMPLATE
#################################################

html = '''<html>
    <head>
        <title node="con:pagetitle">Page Title</title>
    </head>
    <body>
        <h1 node="con:h1title">Page Title </h1>
        <p node="con:quote">Some Text</p>
    </body>
</html>''' # the html template

def render_template(node, title, quote): # the template's controller
	node.pagetitle.content = title # set page title
	node.h1title.content = title # set h1 title
	node.quote.content = quote # set quote text

template = Template(render_template, html) # compile template

#################################################
# MAIN
#################################################

print template.render('Quote of the Day', '"God does not play dice." Albert Einstein')