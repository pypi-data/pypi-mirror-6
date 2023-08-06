#!/usr/bin/python
"""
Print out a line-by-line list of basic tag info from all comics
"""

"""
Copyright 2012  Anthony Beville

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import os

from comictaggerlib.comicarchive import *
from comictaggerlib.settings import *
import comictaggerlib.utils

def main():
	utils.fix_output_encoding()
	settings = ComicTaggerSettings()

	style = MetaDataStyle.CIX

	if len(sys.argv) < 2:
		print >> sys.stderr, "usage:  {0} comic_folder ".format(sys.argv[0])
		return
	
	filelist = utils.get_recursive_filelist( sys.argv[1:] )
			
	#first read in info from all files
	comic_list = []	
	max_name_len = 2
	for filename in filelist:
		ca = ComicArchive(filename, settings.rar_exe_path )
		if ca.seemsToBeAComicArchive():
			comic_list.append( ca )
	
			max_name_len = max ( max_name_len, len(filename))
			fmt_str = u"{{0:{0}}}".format(max_name_len)
			print >> sys.stderr, fmt_str.format( filename ) + "\r",
			sys.stderr.flush()

	print >> sys.stderr, fmt_str.format( "" ) + "\r",
	print "-----------------------------------------------"
	print "Found {0} comics".format( len(comic_list))
	print "-----------------------------------------------"

	# now, figure out column widths	
	w0 = 4
	for ca in comic_list: 
		w0 = max( len((os.path.split(ca.path)[1])), w0)
	w0 += 2
	
	# build a format string
	fmt_str = u"{0:" + str(w0) + "} {1}"
		
	# now print
	for ca in comic_list:
		name = ca.getPageName(ca.getScannerPageIndex())
		if name is not None:
			name = os.path.split( name )[1]
		print fmt_str.format(os.path.split(ca.path)[1]+":", name)

if __name__ == '__main__':
	main() 
