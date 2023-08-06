#############################################################################
# Author  : Jerome ODIER
#
# Email   : jerome.odier@cern.ch
#           jerome.odier@lpsc.in2p3.fr
#
# Version : 1.X.X for nEMD (2013-2014)
#
#############################################################################

import re, string, smtplib, nedm.config

#############################################################################

nedm_config_receivers = [email for email in re.split('[,;\s]+', nedm.config.receivers) if len(email) > 0]

#############################################################################

class NEDMException(Exception):
	#####################################################################

	def __init__(self, value):

		self.value = value

		body = string.join((
			'From: %s' % nedm.config.sender,
			'To: %s' % nedm.config.receivers,
			'Subject: %s' % 'nEDM metadata error (%s)' % nedm.config.current_site_name,
			'',
			value
		), '\r\n')

		try:
			smtp = smtplib.SMTP(nedm.config.smtp_server)

			if not nedm.config.smtp_login is None and len(nedm.config.smtp_login) > 0\
			   and                                                                   \
			   not nedm.config.smtp_passw is None and len(nedm.config.smtp_passw) > 0:

				smtp.login(nedm.config.smtp_login, nedm.config.smtp_passw)

			smtp.sendmail(nedm.config.sender, nedm.config.receivers, body)

			smtp.quit()

		except Exception as e:
			print('error: could not send emails (%s) !' % e)

	#####################################################################

	def __str__(self):
		return self.value

#############################################################################
