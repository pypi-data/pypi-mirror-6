#!/usr/bin/env python

# Demonstrates how to:
# - generate multiple table cells within multiple table rows
# - assign strings as HTML elements' content
# - omit mocked-up HTML using 'del' directive
#
# Note how non-text types must be cast to string/unicode before assigning as content/attribute values. 


import calendar, time

from HTMLTemplate import Template


#################################################
# TEMPLATE
#################################################

html = """<html>
	<head>
		<title></title>
		<style type="text/css" media="all">
			.calendar td {text-align:center;}
		</style>
	</head>
	<body>
		<table class="calendar" width="50%">
			<caption node="con:caption">January 2004</caption>
			<thead>
				<tr>
					<th>Sunday</th>
					<th>Monday</th>
					<th>Tuesday</th>
					<th>Wednesday</th>
					<th>Thursday</th>
					<th>Friday</th>
					<th>Saturday</th>
				</tr>
			</thead>
			<tbody>
				<tr node="rep:week">
					<td node="rep:day"></td>
					<td node="del:">1</td>
					<td node="del:">2</td>
					<td node="del:">3</td>
					<td node="del:">4</td>
					<td node="del:">5</td>
					<td node="del:">6</td>
				</tr>
				<tr node="del:">
					<td>7</td>
					<td>8</td>
					<td>9</td>
					<td>10</td>
					<td>11</td>
					<td>12</td>
					<td>13</td>
				</tr>
				<tr node="del:">
					<td>14</td>
					<td>15</td>
					<td>16</td>
					<td>17</td>
					<td>18</td>
					<td>19</td>
					<td>20</td>
				</tr>
				<tr node="del:">
					<td>21</td>
					<td>22</td>
					<td>23</td>
					<td>24</td>
					<td>25</td>
					<td>26</td>
					<td>27</td>
				</tr>
				<tr node="del:">
					<td>28</td>
					<td>29</td>
					<td>30</td>
					<td>31</td>
					<td></td>
					<td></td>
					<td></td>
				</tr>
			</tbody>
		</table>
	</body>
</html>"""


def render_template(node):
	year, month = time.localtime()[0:2]
	node.caption.content = "%s %s" % (calendar.month_name[month], year)
	node.week.repeat(render_week,calendar.monthcalendar(year, month))

def render_week(node, week):
	node.day.repeat(render_day, week)

def render_day(node, day):
	if day != 0:
		node.content = str(day)


#################################################
# MAIN
#################################################

print Template(render_template, html).render()

