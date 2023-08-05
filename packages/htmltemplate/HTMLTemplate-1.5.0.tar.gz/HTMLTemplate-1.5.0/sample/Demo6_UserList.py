#!/usr/bin/env python

# Demonstrates how to:
# - insert HTML markup as a node's raw (unescaped) content
# - get, modify and re-insert an element's attribute value (or content); mixes Python string substitutions with HTML templates
# - compose multiple templates to produce a complete HTML document.


from HTMLTemplate import Template

#######
# PAGE TEMPLATE

pagehtml = '''<html>
	<head>
		<title node="con:title1">TITLE</title>
	</head>
	<body>
		<h1 node="con:title2">TITLE</h1>
		<div node="-con:body">...</div>
	</body>
</html>'''

def render_page(node, title, body):
	node.title1.content = node.title2.content = title
	node.body.raw = body

pagetemplate = Template(render_page, pagehtml)


#######
# BODY TEMPLATE

bodyhtml = '''<table cellpadding="3" border="0" cellspacing="1" width="100%">
	<thead>
		<tr>
			<th>Id</th>
			<th>Name</th>
			<th>Email</th>
			<th>Banned</th>
		</tr>
	</thead>
	<tbody>
		<tr node="rep:user">
			<td node="con:id">123</td>
			<td node="con:name">John Doe</td>
			<td><a href="mailto:%s" node="con:email">j.doe@foo.com</a></td>
			<td node="con:banned">&nbsp;</td>
		</tr>
	</tbody>
</table>'''

def render_body(node, users):
	node.user.repeat(render_user, users)

def render_user(node, user):
	node.id.content = user['id']
	node.name.content = user['name']
	node.email.atts['href'] = node.email.atts['href'] % user['email']
	node.email.content = user['email']
	if user['banned']:
		node.banned.content = 'X'

bodytemplate = Template(render_body, bodyhtml)


#######
# TEST

users = [
	{'id': '1', 'name': 'Jane Brown', 'email': 'j.brown@foo.com', 'banned': False},
	{'id': '2', 'name': 'Sam Jones', 'email': 's.jones@foo.com', 'banned': True},
	{'id': '3', 'name': 'Fred Smith', 'email': 'f.smith@foo.com', 'banned': False},
]

print pagetemplate.render('User List', bodytemplate.render(users))

