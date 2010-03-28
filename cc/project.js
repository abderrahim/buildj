{
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
		}
	}
}
