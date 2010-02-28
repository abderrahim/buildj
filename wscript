import Utils
import json
import re
	
WAF_TOOLS = {'cc': 'compiler_cc'}
# (Tool,Type) -> Waf features map

FEATURES_MAP = {('cc', 'program'):    'cc cprogram',
                ('cc', 'sharedlib'):  'cc cshlib',
                ('cc', 'staticlib'):  'cc cstaticlib'}

class ProjectTarget:
	def __init__(self, name, target):
		self._name   = name
		self._target = target
		if not isinstance (target, dict):
			raise ValueError, "Target class: the target argument must be a dictionary"

	def get_name (self):
		return str(self._name)
			
	def has_tool (self):
		return "tool" in self._target
			
	def get_tool (self):
		if not self.has_tool():
			return
		return str(self._target["tool"])
	
	def get_name (self):
		return str(self._name)
		
	def get_type (self):
		if "type" not in self._target:
			return
		return str(self._target["type"])
		
	def get_features (self):
		tool = self.get_tool ()
		output_type = self.get_type ()
		if not tool or not output_type:
			#TODO: Report tool and target type needed
			return
			
		if (tool, output_type) in FEATURES_MAP:
			return FEATURES_MAP[(tool, output_type)]
		else:
			#TODO: Report lack of support for this combination
			return
	
	def _get_string_list (self, key):
		if key not in self._target:
			return []
		target_input = self._target[key]
		
		if isinstance (target_input, unicode):
			return [str(target_input),]
		elif isinstance (target_input, list):
			#TODO: Check if everything is str
			return [str(t) for t in target_input]

		#TODO: Report warning, empty input
		return []
		
	def get_input (self):
		return self._get_string_list ("input")
		
	def get_uses (self):
		return self._get_string_list ("uses")
	
	def get_version (self):
		if "version" not in self._target:
			return None
		return str(self._target["version"])
		
	def get_packages (self):
		return self._get_string_list ("packages")
		
	def get_build_arguments (self):
		args = {"features": self.get_features (),
            "source":   self.get_input (),
            "target":   self.get_name (),
            "uselib_local": self.get_uses ()}

		if self.get_type () == "sharedlib":
			args["vnum"] = self.get_version ()

		args["uselib"] = []
		for pkg in self.get_packages ():
			args["uselib"].append (normalize_package_name(pkg))
			
		return args
			

class ProjectRequirement:
	def __init__ (self, name, requirement):
		self._name = name
		self._requirement = requirement

	def get_name (self):
		return str(self._name)
	
	def get_type (self):
		if "type" not in self._requirement:
			#TODO: Type is required
			return

		return str(self._requirement["type"])
		
	def get_version (self):
		if "version" not in self._requirement:
			return
		return str(self._requirement["version"])
		
	def is_mandatory (self):
		if "mandatory" not in self._requirement:
			return False
			
		mandatory = self._requirement["mandatory"]
		if "True" == mandatory:
			return True
		elif "False" == mandatory:
			return False
		else:
			#TODO: Warn about wrong mandatory 
			pass
		
		
	def get_check_pkg_args (self):
		args = {"package": self.get_name ()}
		
		#Correctly sets the version
		if self.get_version():
			version = self.get_version()
			if version.startswith ("= "):
				args["exact_version"] = str(version[2:])
			if version.startswith ("== "):
				args["exact_version"] = str(version[3:])
			elif version.startswith (">= "):
				args["atleast_version"] = str(version[3:])
			elif version.startswith ("<= "):
				args["max_version"] = str(version[3:])
			else:
				#FIXME: < and > are supported as an argument but not by waf
				#TODO: Warn that >= is recommended
				args["atleast_version"] = str(version)
				pass
				
		if self.get_type () == "package":
			args["mandatory"] = self.is_mandatory ()
			
		args["args"] = "--cflags --libs"
		
		args["uselib_store"] = normalize_package_name (self.get_name ())

		return args


class ProjectFile:
	def __init__ (self, project="project.js"):
		dec = json.decoder.JSONDecoder ()
		prj = open(project)
		self._json = prj.read ()
		self._project = dec.decode (self._json)
		prj.close ()

	def __repr__ (self):
		return str (self._json)
		
	def get_targets (self):
		project = self._project
		if not "targets" in project:
			return
		
		return [ProjectTarget (target_name,
		                       project["targets"][target_name])
		          for target_name in project["targets"]]

	def get_tools (self):
		tools = []
		
		for target in self.get_targets ():
			if target.has_tool ():
				tools.append (target.get_tool ())
		return tools
	
	def get_requires (self):
		project = self._project
		if not "requires" in project:
			return
		
		return [ProjectRequirement(require, project["requires"][require])
		          for require in project["requires"]]
	
	def get_packages_required (self):
		requires = self.get_requires ()
		return [require for require in requires if require.get_type () == "package"]
	
	def get_check_pkg_arg_list (self):
		return [package.get_check_pkg_args ()
		          for package in self.get_packages_required ()]


####### Utils ##################################################################

def parse_project_file (project_file="project.js"):
	try:
		project = ProjectFile (project_file)
	except ValueError, e:
		raise Utils.WscriptError (str(e), project_file)
	
	return project

def normalize_package_name (name):
	name = name.upper ()
	nonalpha = re.compile (r'\W')
	return nonalpha.sub ('_', name)

################################################################################
## WAF TARGETS 
################################################################################

#TODO: Cache json values? Worth it?
#TODO: Allow definition of different json filename

def set_options (opt):
	project = parse_project_file ()
	
	for tool in project.get_tools ():
		opt.tool_options (WAF_TOOLS[tool])

def configure (conf):
	project = parse_project_file ()
	
	for tool in project.get_tools ():
		conf.check_tool (WAF_TOOLS[tool])
		
	for args in project.get_check_pkg_arg_list ():
		conf.check_cfg (**args)
		
def build(bld):
	project = parse_project_file ()
	
	print bld.env

	try:
		project = ProjectFile ()
	except ValueError, e:
		raise Utils.WscriptError (str(e), "project.js")

	for target in project.get_targets ():
		args = target.get_build_arguments ()
		bld (**args)
