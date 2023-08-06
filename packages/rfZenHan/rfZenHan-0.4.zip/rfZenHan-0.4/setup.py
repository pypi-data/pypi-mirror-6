from distutils.core import setup;
setup(
	name="rfZenHan",
	version="0.4",
	description="Translate full-width to half-width, and other in Japanese.",
	url="https://github.com/hATrayflood/rfZenHan",
	author="hATrayflood",
	author_email="h.rayflood@gmail.com",
	license="The MIT License (MIT)",
	long_description="Detail is needed to written in Japanese. visit github. https://github.com/hATrayflood/rfZenHan",
	classifiers=(
		"Development Status :: 4 - Beta",
		"Environment :: Console",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: Japanese",
		"Programming Language :: Python :: 2 :: Only",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Text Processing :: Filters",
	),
	py_modules=["rfZenHan"],
	scripts=['rfzenhan', 'rfzenhan.bat', 'rfZenHanCmd.py'],
)
