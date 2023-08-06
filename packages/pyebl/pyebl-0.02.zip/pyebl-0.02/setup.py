from distutils.core import setup
setup(
	name = "pyebl",
	packages = ["pyebl"],
	version = "0.02",
	description = "Scripting interface for .ely files",
	author = "Eric R. J. Edwards",
	author_email = "eric.edwards@physik.uni-halle.de",
	url = "http://www.github.com/erje/pyebl",
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
		"Operating System :: OS Independent"
		],
	long_description = """\
                        pyebl implements a simply scripting interface for
creating .ely files. Syntax and function is reminiscent of matplotlib's pyplot.
See docs/examples for usage. It may be useful for quickly tuning
highly-repetitive structures, arrays where some parameter should be varied over
each structure in the array, and approximations of smooth curves using the
polygon primitive. pyebl requires python 3, there is no python 2 version.
			"""
)


