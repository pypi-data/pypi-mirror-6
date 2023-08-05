#!/usr/bin/env python

import HTMLTemplate


# 1. Define HTML template:

html = """
<html>
	<head>
		<title node="con:title">TITLE</title>
	</head>
	<body>
		<ul>
			<li node="rep:item">
				<a href="" node="con:link">LINK</a>
			</li>
		</ul>
	</body>
</html>
"""


# 2. Define functions to control template rendering:

def render_template(tem, pagetitle, linksinfo):
	tem.title.content = pagetitle
	tem.item.repeat(render_item, linksinfo)


def render_item(item, linkinfo):
	URI, name = linkinfo
	item.link.atts['href'] = URI
	item.link.content = name


# 3. Compile template:

template = HTMLTemplate.Template(render_template, html)


# 4. Render template:

title = "Site Map"
links = [('index.html', 'Home'), ('products/index.html', 'Products'), ('about.html', 'About')]
print template.render(title, links)