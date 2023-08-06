#! /usr/bin/env python
# -*- coding: utf-8 -*-

from time import time
import OpenDiscovery as od
import OpenDiscovery.screen as ODScreen
import glob
import os
import shutil

if __name__ == '__main__':

	t = time()

	options                   = {}
	options['directory']      = '~/Desktop/od2/'
	options['exhaustiveness'] = 1

	directory = os.path.abspath(os.path.expanduser(options['directory']))
	receptor_folder = directory + "/receptor/*.pdbqt"

	for receptor in glob.glob(receptor_folder):
		receptor_name, receptor_extension = os.path.splitext(os.path.basename(os.path.normpath(receptor)))

		s = ODScreen.Screen(
			parse 			= False,
			directory 		= options['directory'],
			exhaustiveness 	= options['exhaustiveness'],
			receptor 		= receptor_name,
			verbose 		= False
		)

		s.run()

	s.writeCompleteSummary()
	#s.plot()

	od.logHeader('Time Taken: {0:.2f} seconds\n'.format(time() - t))



