#!/usr/bin/env python

# Demonstrates how to:
# - view Template object model's structure for diagnostic purposes
# - generate multiple table rows
# - assign strings as HTML elements' content
# - assign strings to tag attributes
# - insert separators between repeating blocks
# - omit tags from compiled nodes using 'minus tags' modifier (-).
#
# Also note how duplicate nodes are automatically omitted from compiled Template.

import urllib

from HTMLTemplate import Template

#################################################
# TEMPLATE
#################################################

html = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<title node="con:title">Some Title</title>
</head>
<body>
	<!-- side navbar -->
	<ul>
		<li node="rep:sidenav"><a href="#" node="con:link">Home</a></li>
		<li node="rep:sidenav"><a href="#">Services</a></li>
		<li node="rep:sidenav"><a href="#">Blah-Blah</a></li>
	</ul>


	<!-- footer navbar -->
	<p>
		<a href="#" node="rep:footernav">Home</a>
		<span node="-sep:footernav"> | </span>
		<a href="#" node="rep:footernav">Blah-Blah</a>
	</p>
</body>
</html>'''


def render_template(node, title, names):
	node.title.content = title
	node.sidenav.repeat(render_sidenav, names)
	node.footernav.repeat(render_footernav, names)
		
def render_sidenav(node, name):
	node.link.atts['href'] = urllib.quote(name.lower()) + '.html'
	node.link.content = name
		
def render_footernav(node, name):
	node.atts['href'] = urllib.quote(name.lower()) + '.html'
	node.content = name


template = Template(render_template, html)


#################################################
# MAIN
#################################################

print '******* TEMPLATE STRUCTURE *******\n'
print template.structure()
print
print '******* SAMPLE RENDERED PAGE *******\n'
print template.render('Fantastic Foo Inc', ['Home', 'Products', 'Services', 'About Us', 'Contact Us', 'Help'])
