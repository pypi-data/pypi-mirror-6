from distutils.core import setup
setup( name             = 'csh-webnews'
	 , version          = '0.1.1'
	 , description      = 'A CSH webnews API wrapper'
	 , author           = 'Matt Gambogi'
	 , author_email     = 'matt.gambogi@gmail.com'
	 , url              = 'http://www.github.com/gambogi/pywebnews'
	 , py_modules       = ['Webnews']
	 , license          = 'MIT'
	 , install_requires = ['requests']
	 )
