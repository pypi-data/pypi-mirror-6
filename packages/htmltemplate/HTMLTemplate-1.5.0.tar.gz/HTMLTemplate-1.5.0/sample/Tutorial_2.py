#!/usr/bin/env python

from HTMLTemplate import Template

html = """
<div node="-rep:section">
	<h2 node="con:title">section title</h2>
	<p node="con:desc">section description</p>
</div>
"""

def render_template(node, sections):
	node.section.repeat(render_section, sections)


def render_section(node, section):
	node.title.content, node.desc.content = section

template  = Template(render_template, html)


sections = [('title 1', 'description 1'), ('title 2', 'description 2'), ('title 3', 'description 3')]
print template.render(sections)