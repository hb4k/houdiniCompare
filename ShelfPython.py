filename = "PUT_THE_PATH_TO_THE_DOWNLOADED_.py_FILE_HERE"

with open(filename, "rb") as source_file:
    code = compile(source_file.read(), filename, "exec")
exec(code)
