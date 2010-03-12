import json
import re

WAF_TOOLS = {'cc':   'compiler_cc',
             'cxx':  'compiler_cxx',
             'vala': 'compiler_cc vala'}

# (Tool,Type) -> Waf features map
FEATURES_MAP = {('cc', 'program'):     'cc cprogram',
                ('cc', 'sharedlib'):   'cc cshlib',
                ('cc', 'staticlib'):   'cc cstaticlib',
                ('cxx', 'program'):    'cxx cprogram',
                ('cxx', 'sharedlib'):  'cxx cshlib',
                ('cxx', 'staticlib'):  'cxx cstaticlib',
                ('vala', 'program'):   'cc cprogram',
                ('vala', 'sharedlib'): 'cc cshlib',
                ('vala', 'staticlib'): 'cc cstaticlib'}

CC_TOOLCHAIN = {'ADDR2LINE': 'addr2line',
                'AS': 'as', 'CC': 'gcc', 'CPP': 'cpp',
                'CPPFILT': 'c++filt', 'CXX': 'g++',
                'DLLTOOL': 'dlltool', 'DLLWRAP': 'dllwrap',
                'GCOV': 'gcov', 'LD': 'ld', 'NM': 'nm',
                'OBJCOPY': 'objcopy', 'OBJDUMP': 'objdump',
                'READELF': 'readelf', 'SIZE': 'size',
                'STRINGS': 'strings', 'WINDRES': 'windres',
                'AR': 'ar', 'RANLIB': 'ranlib', 'STRIP': 'strip'}

DEFAULT_BUILDJ_FILE="project.js"

def normalize_package_name (name):
	name = name.upper ()
	nonalpha = re.compile (r'\W')
	return nonalpha.sub ('_', name)

class ProjectFile:
	def __init__ (self, project="project.js"):
		dec = json.decoder.JSONDecoder ()
		prj = open(project)
		self._json = prj.read ()
		self._project = dec.decode (self._json)
		prj.close ()

	def __repr__ (self):
		return str (self._json)
		
	def get_project_version (self):
		project = self._project
		
		if not "project" in project:
			#TODO: There must be a project name and a project 
			return

		project_node = project["project"]
		
		if "version" not in project_node:
			#TODO: There must be a version		
			pass		

		return str(project_node["version"])
		
	def get_project_name (self):
		project = self._project
		if "project" not in project:
			#TODO: There must be a project name and a project 
			return
			
		project_node = project["project"]		
		if "name" not in project_node:
			#TODO: There must be a name
			return

		return  str(project_node["name"])
		
		
	def get_targets (self):
		project = self._project
		if not "targets" in project:
			return
		
		project_list = []
		for target_name in project["targets"]:
			target_json = project["targets"][target_name]
			if not isinstance (target_json, dict):
				#TODO: Target object must be a dictionary
				continue
			if "tool" not in target_json:
				#TODO: Target object must have a tool
				continue
			#We instance the target class depending on the tool
			
			project_list.append (TOOL_CLASS_MAP[target_json["tool"]](target_name, target_json))
			
		return project_list
	
	def get_tools (self):
		tools = []
		
		for target in self.get_targets ():
			tool = target.get_tool ()
			if tool:
				tools.append (tool)
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

class ProjectTarget:
	def __init__(self, name, target):
		self._name   = name
		self._target = target
		if not isinstance (target, dict):
			raise ValueError, "Target %s: the target argument must be a dictionary" % (name,)

	def get_name (self):
		return str(self._name)
						
	def get_tool (self):
		if "tool" not in self._target:
			return None

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
	
	def get_defines (self):
		return self._get_string_list ("defines")
	
	def get_build_arguments (self):
		args = {"features": self.get_features (),
            "source":   self.get_input (),
            "target":   self.get_name ()}
		
		return args

class CcTarget (ProjectTarget):
	def get_build_arguments (self):
		args = ProjectTarget.get_build_arguments (self)

		uses = self.get_uses ()
		if uses:
			args["uselib_local"] = uses

		if self.get_type () == "sharedlib" and self.get_version ():
			args["vnum"] = self.get_version ()

		args["uselib"] = []
		for pkg in self.get_packages ():
			args["uselib"].append (normalize_package_name(pkg))
		
		defines = self.get_defines ()
		if defines:
			args["defines"] = defines

		return args

class ValaTarget (CcTarget):
	def get_vapi (self):
		if "vapi" in self._target:
			return str (self._target["vapi"])
		
	def get_gir (self):
		if "gir" in self._target:	
			gir = str(self._target["gir"])
			
			match = re.match (".*-.*", gir)
			if match:
				return gir
				
		return None

	def get_build_arguments (self):
			args = CcTarget.get_build_arguments (self)

			packages = self.get_packages ()
			if "glib-2.0" not in packages:
				packages.append ("glib-2.0")
				
			if "uselib" in args:
				args["uselib"].append (normalize_package_name("glib-2.0"))
			else:
				args["uselib"] = [normalize_package_name("glib-2.0")]
			
			args["packages"] = packages
			
			gir = self.get_gir ()
			if gir:
				args["gir"] = gir
			
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

#Mapping between tools and target classes
TOOL_CLASS_MAP = {'cc':   CcTarget,
                  'cxx':   CcTarget,
                  'vala': ValaTarget}
