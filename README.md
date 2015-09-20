# AndroidStringManager

You can manage android string resource files with tsv (Tab-separated values) file.

These files are tested only in python 2.7 version.

1. change the parameter DEFAULT_STRING_PATH in *.py files
2. run xml2tsv.py, then .tsv file will be created.
3. modify .tsv file
4. run tsv2xml.py, then changed values will be merged to .xml files
