{
	"project":
	{
		"name":    "CC Test",
	  "version": "0.0.1",
	  "url":     "http://www.codethink.co.uk"
	},
	"targets":
	{
		"my_program":
		{
			"type":    "program",
			"tool":    "cc",
			"input":   "program.c"
		},
		"my_shared_lib":
		{
			"type":    "sharedlib",
			"tool":    "cc",
			"input":   "lib.c",
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
			"input":   "program_with_lib.c",
			"uses":    ["my_static_lib"],
			"depends": []
		},
		"my_shared_program":
		{
			"type":  "program",
			"tool":  "cc",
			"input": "program_with_lib.c",
			"uses":  ["my_shared_lib"]
		}
	}
}
