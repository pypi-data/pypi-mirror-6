CHANGES
=======	

	
0.4.0a3
=======

2013-12-11  Whit  <whit@surveymonkey.com>
	* update docs
	* deprecate process based concurrency until a better way is found
	* add a way to config different callables for naming an upload

	
0.4.0a2
=======

2013-03-21  Whit  <whit@surveymonkey.com>

	* thread and process concurrency via futures for index building
	* optional pip cache syncing
	* option to not write index.html (for use with servers w/ directory list ala nginx)
	* various performance improvements (thanks @bbinet!)


0.2a1
=====

2012-10-31  whit  <whit@surveymonkey.com>:

 * Filter non-source distribution downloads from pypi
 * Fixed bug with index.json generation for add packages via pypi
 * Index regeneration is now package by package
 * initial work on unified 'datafile' handling via transaction
 * Make 'regenerate_all' rebuild the datafile (albeit inefficiently)

	
0.1a1
=====

Initial alpha release.

Development Log
---------------

2012-01-09  whit  <whit@surveymonkey.com>:
 * Recursive download of requirements files and dependencies
 * Search of pypi and download of files
 * Improved test coverage
 * Initialization of index on start up
 * Basic read-only API for index
 * Broader event support
 * Documentation improvements

2011-12-21  whit  <whit@surveymonkey.com>:
 * Individual leaf update via event on upload
 * Refactor to use pkginfo 

2011-12-01  whit  <whit@surveymonkey.com>:
 * Housekeeping: add static fileserving for index for developments,
   more use of path.py
 * Port over emporium readme.

2011-11-07  whit  <whit@surveymonkey.com>:
 * Get app basically serving

2011-11-07  whit  <whit@surveymonkey.com>:
 * Setup initial package structure  
