#!/usr/bin/env python

# Demonstrates how to:
# - generate multiple table rows
# - assign strings as HTML elements' content
# - assign strings to tag attributes.


from HTMLTemplate import Template

#################################################
# TEMPLATE
#################################################

html = '''<html>
	<head>
		<title node="con:title">TITLE</title>
	</head>
	<body>
	
		<table>
			<tr node="rep:client">
				<td node="con:name">Surname, Firstname</td>
				<td><a node="con:email" href="mailto:client@email.com">client@email.com</a></td>
			</tr>
		</table>
	
	</body>
</html>'''

def render_template(node, title, clients):
	node.title.content = title
	node.client.repeat(render_client, clients)

def render_client(node, client):
	node.name.content = client.surname + ', ' + client.firstname
	node.email.atts['href'] = 'mailto:' + client.email
	node.email.content =  client.email

template = Template(render_template, html)


#################################################
# MAIN
#################################################

class Client:
	def __init__(self, *args):
		self.surname, self.firstname, self.email = args

title = 'FooCo'
clients = [Client('Smith', 'K', 'ks@foo.com'), Client('Jones', 'T', 'tj@bar.org')]

print template.render(title, clients)