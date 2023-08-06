#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys,os,shutil

if sys.version_info.major==2:
	other_version = 3
else:
	other_version = 2

pysite_command = 'pysite-%d.%d' % (sys.version_info.major,sys.version_info.minor)

readme = changes = ''
if os.path.exists('README.rst'):
	readme = open('README.rst').read()
if os.path.exists('CHANGES.rst'):
	changes = open('CHANGES.rst').read()

install_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(install_dir,'scripts')
shutil.rmtree(scripts_dir,ignore_errors=True)
if not os.path.exists(scripts_dir):
	os.makedirs(scripts_dir)
f_pysite_temp = open(os.path.join(install_dir,'script','templates','pysite'))
f_pysite_cmd = open(os.path.join(scripts_dir,pysite_command),'w')
f_pysite_cmd.write(f_pysite_temp.read().replace('<INTERPRETER>',sys.executable))
f_pysite_cmd.close()
f_pysite_temp.close()

VERSION = '0.2.0'

SHORT_DESC = "Create simple yet powerful WSGI based sites, utilizing Jinja2 and Qt's TS-file format for localization"

def walk_dir(dirname):
	files = []
	def detect_svn(fname):
		return fname.find('.svn')==-1
	for f in filter(detect_svn ,map(lambda fname: os.path.join(dirname,fname),os.listdir(dirname))):
		files += [f]
	return files

def packages(basedir):
	p = []
	for base,dirs,files in os.walk(basedir):
		if base.find('.svn')==-1:
			p+=['.'.join(base.split(os.path.sep)[1:])]
	return p

data_files= [
	('script/templates',walk_dir('script/templates')),
	('resources/init/static/css',walk_dir('resources/init/static/css')),
	('resources/init/static/images',walk_dir('resources/init/static/images')),
	('resources/init/templates',walk_dir('resources/init/templates'))]

print(data_files)
setup(
	name='pysite',
	packages=packages('src/pysite'),
	package_dir={'':'src'},
	version=VERSION,
	description=SHORT_DESC,
	long_description='\n\n'.join([readme, changes]),
	classifiers=[
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Operating System :: OS Independent',
		'Natural Language :: English',
		'Intended Audience :: Developers',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',       
	],
	keywords= ['wsgi', 'website', 'www', 'website', 'framework'],
	author='Jakob Simon-Gaarde',
	author_email='jakob@simon-gaarde.dk',
	maintainer = 'Jakob Simon-Gaarde',
	maintainer_email = 'jakob@simon-gaarde.dk',
	install_requires=['jinja2'],
	requires=['jinja2'],
	provides=['pysite'],
	license='LGPL3',
	scripts=['scripts/%s' % pysite_command],
	data_files= data_files,
	zip_safe=False
)
