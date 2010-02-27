import json
	
WAF_TOOLS = {'cc': 'compiler_cc'}
# (Tool,Type) -> Waf features map

FEATURES_MAP = {('cc', 'program'):    'cc cprogram',
                ('cc', 'sharedlib'):  'cc cshlib',
                ('cc',  'staticlib'): 'cc cstaticlib'}


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
		
	def get_input (self):
		if "input" not in self._target:
			return
		target_input = self._target["input"]
		
		if isinstance (target_input, unicode):
			print target_input
			return [str(target_input),]
		elif isinstance (target_input, list):
			#TODO: Check if everything is str
			return [str(t) for t in target_input]
		else:
			#TODO: Report warning, empty input
			return []
		
	def get_build_arguments (self):
		return {"features": self.get_features (),
            "source":   self.get_input (),
            "target":   self.get_name ()}


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
			
		return [ProjectTarget (target_name, project["targets"][target_name])
		          for target_name in project["targets"]]

	def get_tools (self):
		tools = []
		
		for target in self.get_targets ():
			if target.has_tool ():
				tools.append (target.get_tool ())

		return tools		             

################################################################################
## WAF TARGETS 
################################################################################

#TODO: Decorator to open the project file
#TODO: Cache json values
#TODO: Allow definition of different json filename

def set_options (opt):
	try:
		project = ProjectFile ()
	except ValueError, e:
		conf.fatal ("project.js: "+e)
		
	for tool in project.get_tools ():
		opt.tool_options (WAF_TOOLS[tool])

def configure (conf):
	try:
		project = ProjectFile ()
	except ValueError, e:
		conf.fatal ("project.js: "+e)
		
	for tool in project.get_tools ():
		conf.check_tool (WAF_TOOLS[tool])

def build(bld):
	try:
		project = ProjectFile ()
	except ValueError, e:
		conf.fatal ("project.js: "+e)

	for target in project.get_targets ():
		args = target.get_build_arguments ()
		bld (**args)
