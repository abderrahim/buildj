{
	"project":
	{
		"name":    "CC Test",
		"version": "0.0.1",
		"url":     "http://www.codethink.co.uk"
	},
	"options":
	{
		"foo":
		{
			"description": "Sets the foo option",
			"default":     "True"
		}
	},
	"requires":
	{
		"glib-2.0": {
			"type":      "package",
			"mandatory": "True"
		},
		"gtk+-2.0":
		{
			"type":      "package",
			"version":   "2.14",
			"mandatory": "${foo}"
		}
	},
	"subdirs": ["cc"],
	"targets":
	{
		"my_cpp_program":
		{
			"type": "program",
			"tool": "c++",
			"path": "cpp",
			"input": ["cpprogram.cpp"],
			"uses": ["my_static_lib"]
		},
		"my_vala_program":
		{
			"type":     "program",
			"tool":     "vala",
			"input":    ["vala_program.vala"],
			"packages": ["gtk+-2.0"]
		},
		"my_vala_shared_lib":
		{
			"type": "sharedlib",
			"tool": "vala",
			"input": ["vala_library.vala"],
			"version": "12.4.5",
			"gir": "Bleh-1.0"
		},
		"my_vala_static_lib":
		{
			"type": "staticlib",
			"tool": "vala",
			"input": ["vala_library.vala"]
		},
		"my_cpp_program_data":
		{
			"tool": "data",
			"input": ["data/buildj.svg"]
		}
	}
}
