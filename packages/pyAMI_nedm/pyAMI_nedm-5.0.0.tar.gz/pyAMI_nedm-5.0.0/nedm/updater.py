#############################################################################
# Author  : Jerome ODIER
#
# Email   : jerome.odier@cern.ch
#           jerome.odier@lpsc.in2p3.fr
#
# Version : 1.X.X for nEMD (2013-2014)
#
#############################################################################

import time, nedm.run, nedm.config, nedm.run_finder, nedm.exception

#############################################################################

class NEDMUpdater:
	#####################################################################

	def __init__(self, client):
		self.client = client

		import pyAMI.exception

		pyAMI.exception.Error = nedm.exception.NEDMException

	#####################################################################

	def prepare(self):

		try:
			#####################################################
			# INSERT RUN TYPES                                  #
			#####################################################

			for nedm_run_type in nedm.config.nedm_run_types:

				result = self.client.execute([
					'SearchQuery',
					'-project=NEDM',
					'-processingStep=metadata',
					'-sql="SELECT type, subType FROM metadata_run_type WHERE type=\'%s\' and subType=\'%s\'"' % (nedm_run_type['type'], nedm_run_type['subType'])
				], 'dict_object')

				if len(result.rowsets) == 0:

					self.client.execute([
						'AddElement',
						'-project=NEDM',
						'-processingStep=metadata',
						'-entity=metadata_run_type',
						'-@type=%s' % nedm_run_type['type'],
						'-@subType=%s' % nedm_run_type['subType']
					], 'dict_object')

			#####################################################
			# INSERT SITES                                      #
			#####################################################

			for nedm_site in nedm.config.nedm_sites:

				result = self.client.execute([
					'SearchQuery',
					'-project=NEDM',
					'-processingStep=metadata',
					'-sql="SELECT name, path FROM metadata_site WHERE name=\'%s\'"' % (nedm_site['name'])
				], 'dict_object')

				if len(result.rowsets) == 0:

					self.client.execute([
						'AddElement',
						'-project=NEDM',
						'-processingStep=metadata',
						'-entity=metadata_site',
						'-name="%s"' % nedm_site['name'],
						'-path="%s"' % nedm_site['path']
					], 'dict_object')

			#####################################################
			# INSERT COMPONENTS & PARAMETERS                    #
			#####################################################

			for nedm_component in nedm.config.nedm_component_parameters:

				result = self.client.execute([
					'SearchQuery',
					'-project=NEDM',
					'-processingStep=metadata',
					'-sql="SELECT name FROM cond_component WHERE name=\'%s\'"' % (nedm_component)
				], 'dict_object')

				if len(result.rowsets) == 0:

					self.client.execute([
						'AddElement',
						'-project=NEDM',
						'-processingStep=metadata',
						'-entity=cond_component',
						'-name="%s"' % nedm_component,
					], 'dict_object')

				for nedm_parameter in nedm.config.nedm_component_parameters[nedm_component]:

					result = self.client.execute([
						'SearchQuery',
						'-project=NEDM',
						'-processingStep=metadata',
						'-sql="SELECT name FROM cond_parameter WHERE name=\'%s\'"' % (nedm_parameter)
					], 'dict_object')
		
					if len(result.rowsets) == 0:

						self.client.execute([
							'AddElement',
							'-project=NEDM',
							'-processingStep=metadata',
							'-entity=cond_parameter',
							'-cond_component.name="%s"' % nedm_component,
							'-cond_parameter.name="%s"' % nedm_parameter,
							'-@type="%d"' % 0,
							'-unit="%s"' % 'none',
						], 'dict_object')

			#####################################################

		except nedm.exception.NEDMException as e:
			print(e)
			return False

		return True

	#####################################################################

	def update(self):
		#############################################################
		# LOOKFOR RUNS                                              #
		#############################################################

		runs = nedm.run_finder.runs_finder(nedm.config.current_site_path)

		print('%s runs found for site `%s` in `%s`...' % (len(runs), nedm.config.current_site_name, nedm.config.current_site_path))

		for run in runs:
			print('  -> %06d' % int(run))

		print('')

		#############################################################
		# PROCESS RUNS                                              #
		#############################################################

		result = True

		for run in runs:
			t1 = time.time()

			try:
				RUN = nedm.run.NEDMRun(self.client, int(run), runs[run])

				RUN.read()
				RUN.dump()
				RUN.save()
				RUN.cond()

			except nedm.exception.NEDMException as e:
				print(e)
				result = False

			t2 = time.time()

			print('%.2f seconds\n' % (t2 - t1))

		#############################################################

		return result

#############################################################################
