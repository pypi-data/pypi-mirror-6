#!/usr/bin/env python

# Demonstrates how to:
# - generate alternately coloured table rows.


from HTMLTemplate import Template

#######
# Support

def alternator(*items):
	"""A generator that yields the supplied items as a repeating sequence."""
	i = 0
	while 1:
		yield items[i % len(items)]
		i += 1

#######
# Template

html = """<table>
<tr node="rep:row" bgcolor="lime"><td>...</td></tr>
</table>"""

def render_template(node, rows):
	node.row.repeat(render_row, rows, alternator('lime', 'cyan'))

def render_row(node, row, colors):
	node.atts['bgcolor'] = colors.next()

#######
# Test

print Template(render_template, html).render(range(10))

