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
			"type":   "sharedlib",
			"tool":   "cc",
			"input":  "lib.c"
		},
		"my_static_lib":
		{
		}
	}
}
