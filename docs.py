#!/usr/bin/env python

import os,sys,re,glob,subprocess,shutil,datetime

path = list(sys.path)
#---connect to runner
sys.path.insert(0,'./runner')
#---excise functions without importing runner
from makeface import strip_builtins
from datapack import asciitree
from acme import read_config,read_inputs,get_input_files
sys.path = path

__all__ = ['docs','publish_docs']

#---magic for local import when you run from elsewhere
sys.path.insert(0,os.path.dirname(os.path.relpath(os.path.abspath(__file__),os.getcwd())))
from sphinx_auto import index_rst,makefile,conf_py,index_master_rst,conf_master_py
#---undo the magic
sys.path = list(sys.path[1:])

def write_rst_toctree(items,name,spacer='-',infotext=''):
	"""..."""
	text = "%s\n%s\n\n%s\n\n"%(name,spacer*len(name),infotext)
	text += ".. toctree::\n\t:maxdepth: 4\n\n"+''.join(["\t%s\n"%i for i in items])
	return text

def write_rst_automodule(title,name,spacer='-'):
	text = "%s\n%s\n\n"%(name,spacer*len(name))
	text += ".. automodule:: %s\n\t:members:\n\t:undoc-members:\n\t:show-inheritance:\n\n"%name
	return text

def docs_parents(dn):
	"""
	Search for all parent scripts in a submodule.
	"""
	#---definition of a parent function is here
	regexes = [r'^from amx import *',r'^import amx']
	parents,candidates = [],[]
	for rn,dns,fns in os.walk(dn):
		for fn in fns:
			if re.match('^.+\.py$',fn):
				candidates.append(os.path.join(rn,fn))
	for fn in candidates:
		with open(fn) as fp: text = fp.read()
		if any([re.search(regex,text,flags=re.M)
			for regex in regexes]):
			parents.append(fn)
	return parents

def docs_modules(dn,excludes=None):
	"""
	"""
	if excludes: excludes = list([os.path.relpath(i) for i in excludes])
	else: excludes = []
	#---definition for a module is here: any python script in the root folder for the extension
	candidates = [i for i in glob.glob(os.path.join(dn,'*.py')) 
		if i not in excludes and os.path.basename(i)!='__init__.py']
	return candidates

def docs_submodules(dn):
	"""
	"""
	#---definition for a submodule is here ...
	return [i for i in glob.glob(os.path.join(dn,'*')) 
		if os.path.isdir(i) and os.path.isfile(os.path.join(i,'__init__.py'))]

def docs_assemble():
	"""
	Get the locations for everything that must be documented.
	"""
	#---! previously got modules from inputlib but the config has the last word
	if False:
		inputlib = read_inputs()
		#---collect all directories that hold extensions referenced in the inputlib
		exts_dns = list(set([i for j in [[os.path.dirname(os.path.abspath(os.path.join(v['cwd'],w))) 
			for w in v['extensions']] for k,v in inputlib.items() if 'extensions' in v] for i in j]))
		exts = dict([(re.sub(os.sep,'-',os.path.relpath(i,os.getcwd())),i) for i in exts_dns])
		#---! need to fix exts to document bilayer with the scripts -- not just bilayer.codes
		#---! hacked for one example. fix the exts above
		exts = {'inputs-extras': {'path':'/run/media/rpb/store-omicron/test-acme6-bilayers/inputs/extras'}}
		for key,val in exts.items():
			exts[key]['path_rel'] = os.path.relpath(val['path'],os.getcwd())
			exts[key]['name'] = os.path.basename(exts[key]['path_rel']).capitalize()
		exts['inputs-extras']['submodules'] = ['amx_extras','GMXStructure','multiply']
	config = read_config()
	inputlib = read_inputs()
	#---exclude parameter files from modules
	#---note that all parameter files must be present in the inputs or they will be treated like modules
	param_files = [os.path.relpath(os.path.join(v['cwd'],v['params'])) 
		for k,v in inputlib.items() if 'params' in v and v['params']]
	input_files = [os.path.relpath(j) for j in get_input_files()]
	#---collect details for each code in a single bank, starting with the path and upstream git source
	bank = dict([('-'.join(c[1].split(os.sep)),{'path':c[1],'source':c[0]}) for c in config['modules']])
	for mod in bank:
		val = bank[mod]
		val['path_rel'] = os.path.relpath(val['path'],os.getcwd())
		val['name'] = os.path.basename(val['path_rel']).capitalize()
		val['scripts'] = docs_parents(val['path'])
		val['modules'] = docs_modules(val['path'],excludes=val['scripts']+param_files+input_files)
		#---add to the experiments by checking for paths that startwith our relative path
		val['experiments'] = [i for i in input_files if i.startswith(val['path'])]
		val['submodules'] = docs_submodules(val['path'])
	#---some modules might be experiments or mdp parameters so we filter them out here
	asciitree(bank)
	return bank

def docs(refresh=False,clean=False):
	"""
	The current documentation method identifies three components of extensions:
	1. Submodules: scripts containing functions used by automacs procedures, in the root directory of the extension. These are the core of the extension, and hold functions which are typically exposed to the "global" [note that nothing is global] automacs namespace.
	2. Codes: sub-submodules in the extension's root directory that might be imported by the submodules. These are more generic, and don't necessarily have to use the wordspace (hence making them easy to poach for other applications, and less tied to the automacs ecosystem by variables like the ``state``).
	3. Experiments: experiment specificatiojns 
	"""
	if refresh: 
		docs_refresh()
		return

	docs_dn = 'build_all'
	build_dn = os.path.join(os.path.dirname(__file__),docs_dn)
	#---style directory holds custom themes
	style_dn = os.path.join(os.path.dirname(__file__),'style')

	#---cleanup
	if clean and os.path.isdir(build_dn):
		print('[NOTE] cleaning docs')
		shutil.rmtree(build_dn)
		return 
	elif clean:
		print('[NOTE] no docs to clean')
		return

	if not os.path.isdir(build_dn): os.mkdir(build_dn)
	else: raise Exception('build directory already exists %s. try `make docs clean` first'%build_dn)

	#---catalog the documentation targets
	exts = docs_assemble()
	components_master = {}

	#---compile sphinx documentation for each separate documentation target
	for name,spec in exts.items():
		dn = spec['path']
		#---create a new directory
		spot = os.path.join(build_dn,name)
		### if os.path.isdir(spot): raise Exception('docs directory exists: %s'%spot)
		os.mkdir(spot)
		spec_rst = {'name':spec['name'],'path_rel':spec['path_rel'],'git_source':spec['source']}
		spec_rst['index_toc_items'] = []
		#---LIST SCRIPTS and EXPERIMENTS as literals
		#---! development idea: part-out the experiments automatically from their parent files
		lits = ['scripts','experiments']
		for lit in lits:
			if spec.get(lit,False):
				text = '%s\n%s\n\n'%(lit.capitalize(),len(lit)*'=')
				for sn in spec[lit]:
					script_name = os.path.relpath(sn,spec['path_rel'])
					script_fn = os.path.splitext('-'.join(sn.split(os.sep)))[0]+'.rst'
					script_rel_path = os.path.relpath(os.path.join(os.getcwd(),sn),spot)
					#---use the full path as the title
					text += '%s\n%s\n\n'%(sn,'-'*len(sn))
					text += ".. literalinclude:: %s\n\n"%script_rel_path
				#---combine the listing into a single scripts.rst
				with open(os.path.join(spot,'%s.rst'%lit),'w') as fp: fp.write(text)
				spec_rst['index_toc_items'].append(lit)
		#---LIST MODULES
		if spec['modules']:
			#---modules must be directly in the extensions folder (otherwise they are submodules)
			modules = [os.path.splitext(os.path.relpath(s,dn))[0] for s in spec['modules']]
			spec_rst['modules'] = write_rst_toctree(modules,'Modules')
			text = "%s\n%s\n\n"%('Modules','='*len('Modules'))
			for mod in modules:
				text += write_rst_automodule(mod,mod,spacer='-')
			#---combine the listing into a single scripts.rst
			with open(os.path.join(spot,'modules.rst'),'w') as fp: fp.write(text)
			spec_rst['index_toc_items'].append('modules')
		#---LIST SUBMODULES
		submods = [os.path.relpath(s,spec['path']) for s in spec['submodules']]
		if submods:
			#---index will point to submodules.rst
			text = "%s\n%s\n\n"%('Submodules','='*len('Submodules'))
			for subname,route in zip(submods,spec['submodules']):
				text += write_rst_automodule(subname,subname,spacer='-')
				#---submodules can only be level down from modules
				#---manually pick up the codes in this submodule
				#---! note this is all that is documented in the submodule
				#---! ...there is no recursion without a specific tool e.g. sphinx-apidoc
				for fn in glob.glob(os.path.join(route,'*.py')):
					if os.path.basename(fn) != '__init__.py':
						subsubname = os.path.splitext(os.path.basename(fn))[0]
						text += write_rst_automodule(subsubname,subname+'.'+subsubname,spacer='~')
			#---combine the listing into a single scripts.rst
			with open(os.path.join(spot,'submodules.rst'),'w') as fp: fp.write(text)
			spec_rst['index_toc_items'].append('submodules')
		path_for_imports = os.path.relpath(spec['path_rel'],spot)
		#---prepare items for the index.rst for this extension
		spec_rst['index_toc'] = write_rst_toctree(spec_rst['index_toc_items'],'Contents',spacer='-')
		fns = [('index.rst',index_rst%spec_rst),('Makefile',makefile),('conf.py',conf_py%path_for_imports)]
		#---make the root file
		for fn,text in fns:
			with open(os.path.join(spot,fn),'w') as fp: fp.write(text)
		shutil.copytree(style_dn,os.path.join(spot,'_static/'))
		proc = subprocess.check_call('make html',shell=True,cwd=spot)
		#---save the presence of scripts, experiments, modules, etc for the master listing
		components_master[name] = spec_rst['index_toc_items']
	#---copy the walkthrough files
	for fn in glob.glob(os.path.join(os.path.dirname(__file__),'walkthrough','*')): shutil.copy(fn,build_dn)
	#---overwrite the index.rst with a master listing of the components
	exts_name_sort = sorted(exts.keys())
	components_text = '\n\n'.join([write_rst_toctree([
		'%s.rst'%(os.path.join('-'.join(exts[name]['path_rel'].split(os.sep)),i)) 
		for i in components_master[name]],os.path.basename(exts[name]['path_rel']),
		spacer='-',infotext=(
			"The ``%(name)s`` extension is a component of automacs located "+
			"at ``%(path_rel)s`` and sourced from ``%(git_source)s``.")%dict(
				name=exts[name]['name'],
				path_rel=exts[name]['path_rel'],
				git_source=exts[name]['source'],
				)) 
		for name in exts_name_sort if components_master[name]])
	#---write the master index
	with open(os.path.join(build_dn,'index.rst'),'w') as fp:
		fp.write(index_master_rst%{'components':components_text})
	#---write the master configuration
	master_import_text = 'import os,sys\n'
	#---hard-coded the amx imports
	master_import_text += '\nsys.path.insert(0,"../../../")'+\
		'\nimport amx\nimport runner'+\
		'\nsys.path.insert(0,"../../../amx")'+\
		'\nsys.path.insert(0,"../../../runner")'+\
		'\n'
	#---automatically detect imports from other modules
	master_import_text += '\n'.join(['sys.path.insert(0,"%s")'%os.path.relpath(spec['path_rel'],build_dn) 
		for name,spec in exts.items()])
	with open(os.path.join(build_dn,'conf.py'),'w') as fp:
		fp.write(conf_master_py%master_import_text)
	master_dn = 'DOCS'
	shutil.copytree(style_dn,os.path.join(build_dn,'_static/'))
	proc = subprocess.check_call('sphinx-build . %s'%master_dn,shell=True,cwd=build_dn)
	print('[NOTE] documentation available at "file://%s"'%
		os.path.join(build_dn,master_dn,'index.html'))

def docs_refresh():
	"""
	Refresh the documentation if it already exists.
	This is mostly meant to make the documentation development faster.
	"""
	docs_dn = 'build_all'
	master_dn = 'DOCS'
	build_dn = os.path.join(os.path.dirname(__file__),docs_dn)
	if not os.path.isdir(build_dn): raise Exception('[ERROR] cannot find build directory %s. '%build_dn+
		'make the docs from scratch instead, with `make docs`.')
	subprocess.check_call('rsync -ariv ../walkthrough/* ./',cwd=build_dn,shell=True)
	subprocess.check_call('sphinx-build . %s'%master_dn,shell=True,cwd=build_dn)

def publish_docs(to=''):
	"""
	Prepare documentation for push to github pages. Administrator usage only.
	WARNING! Make sure you compile the docs manually before you run this!

	NOTES:
	-----
	This function will clean then make the docs, and set up the repo to track the github repo.
	We used a similar procedure to update the docs, and eventually replaced it with the current
	set of commands to handle the newer versions of git.	
	The first commit to the repo was created as follows (saved here for posterity):
		git init .
		git commit -m 'initial commit' --allow-empty
		git branch gh-pages
		git checkout gh-pages
		touch .nojekyll
		git add .
		git commit -am 'added files'
		git remote add origin <destination>
		git push -u origin gh-pages
	"""
	html_source_path = 'build_all/DOCS'
	if not to: raise Exception('send destination for documentation via the "to" argument to make')
	dropspot = os.path.join(os.path.dirname(__file__),html_source_path,'')
	print('[WARNING] you must make sure the docs are up-to-date before running this!')
	timestamp = '{:%Y.%m.%d.%H%M}'.format(datetime.datetime.now())
	cmds = [
		'git init .',
		'git checkout -b new_changes',
		'git add .',
		'git commit -m "refreshing docs"',
		'git remote add origin "%s"'%to,
		'git fetch origin gh-pages',
		'git checkout gh-pages',
		('git merge -X theirs -m "refreshing docs" new_changes',
			'git merge -X theirs --allow-unrelated-histories -m "refreshing docs" new_changes'),
		'git commit -m "refreshing docs"',
		'git push --set-upstream origin gh-pages',
		][:-1]
	for cmd in cmds: 
		if type(cmd)==tuple: run_cmds = cmd
		else: run_cmds = [cmd]
		for try_num,this_cmd in enumerate(run_cmds):
			try: subprocess.call(this_cmd,cwd=dropspot,shell=True)		
			except: 
				if try_num==0: continue 
				else: raise Exception('[ERROR] both command options failed!')
	print('[NOTE] tracking github pages from "%s"'%dropspot)
	print('[NOTE] admins can push from there to publish documentation changes')
	print('[NOTE] run "git push --set-upstream origin gh-pages" from there')
