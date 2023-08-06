from distutils.core import setup
setup(name='uniprot_mapper',
		version='0.6',
		py_modules=['uniprot_mapper'],
		scripts=['uniprot_mapper'],

		requires=['urllib','urllib2','argparse'],

		author='Jan Rudolph',
		license='MIT license',
		author_email='jan.daniel.rudolph@gmail.com',
		description='Simple interface for uniprot.org/mapping',
		url='https://github.com/jdrudolph/uniprot_mapper',
		long_description=open('README').read(),
		)
