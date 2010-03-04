{
	"project":
	{
		"name":    "CC Test",
		"version": "0.0.1",
		"url":     "http://www.codethink.co.uk"
	},
	"requires":
	{
		"glib-2.0": {
			"type": "package",
			"mandatory": "True"
		},
		"gtk+-2.0": 
		{
			"type":      "package",
			"version":   "2.14",
			"mandatory": "True"
		}
	},
	"targets":
	{
		"my_program":
		{
			"type":    "program",
			"tool":    "cc",
			"input":   ["program.c"]
		},
		"my_shared_lib":
		{
			"type":    "sharedlib",
			"tool":    "cc",
			"input":   ["lib.c"],
			"version": "1.2.3"
		},
		"my_static_lib":
		{
			"type":  "staticlib",
			"tool":  "cc",
			"input": ["lib.c"]
		},
		"my_static_program":
		{
			"type":    "program",
			"tool":    "cc",
			"input":   ["program_with_lib.c"],
			"uses":    ["my_static_lib"]
		},
		"my_shared_program":
		{
			"type":  "program",
			"tool":  "cc",
			"input": ["program_with_lib.c"],
			"uses":  ["my_shared_lib"]
		},
		"my_gtk_program":
		{
			"type":     "program",
			"tool":     "cc",
			"input":    ["gtk_program.c"],
			"packages": ["gtk+-2.0"]
		},
		"my_program_with_defines":
		{
			"type":     "program",
			"tool":     "cc",
			"input":    ["program_with_defines.c"],
			"defines":  ["FOO", "BAR=\"123\""]
		},
		"my_vala_program":
		{
			"type":     "program",
			"tool":     "vala",
			"input":    ["vala_program.vala"],
			"packages": ["gtk+-2.0"]
		},
		"my_vala_library":
		{
			"type": "sharedlib",
			"tool": "vala",
			"input": ["vala_library.vala"],
			"version": "12.4.5"
		}
	}
}
