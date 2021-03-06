import smtplib
import os
import jinja2
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Emailer(object):

	def __init__(self, server, port, username, password):
		self.serverUrl = server
		self.port = port
		self.username = username
		self.password = password

	def generateEmailFromTemplate(self, templateFile, data):
		path, filename = os.path.split(templateFile)
		return jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(data)

	def sendEmail(self, recipient, subject, templateFile, data):
		server = smtplib.SMTP(self.serverUrl, self.port)
		server.ehlo()
		server.starttls()
		server.login(self.username, self.password)

		html = self.generateEmailFromTemplate(templateFile, data)
		text = html

		message = MIMEMultipart('alternative')
		message['Subject'] = subject
		message['From'] = self.username
		message['To'] = recipient

		plainTextMessage = MIMEText(text, 'plain')
		htmlMessage = MIMEText(html, 'html')

		message.attach(plainTextMessage)
		message.attach(htmlMessage)

		server.sendmail(self.username, recipient, message.as_string())
		server.quit()