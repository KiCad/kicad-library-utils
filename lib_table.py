import re

class LibTable:

    def __init__(self, filename):

        RE_NAME = r'\(name "?([^\)"]*)"?\)'
        RE_TYPE = r'\(type "?([^\)"]*)"?\)'
        RE_URI  = r'\(uri "?([^\)"]*)"?\)'
        RE_OPT  = r'\(options "?([^\)"]*)"?\)'
        RE_DESC = r'\(descr "?([^\)"]*)"?'

        self.entries = []
        self.errors = []

        with open(filename, 'r') as lib_table_file:

            for line in lib_table_file:

                # Skip lines that do not define a library
                if not '(lib ' in line:
                    continue

                re_name = re.search(RE_NAME, line)
                re_type = re.search(RE_TYPE, line)
                re_uri  = re.search(RE_URI,  line)
                re_opt  = re.search(RE_OPT,  line)
                re_desc = re.search(RE_DESC, line)

                if re_name and re_type and re_uri and re_opt and re_desc:
                    entry = {}
                    entry['name'] = re_name.groups()[0]
                    entry['type'] = re_type.groups()[0]
                    entry['uri']  = re_uri.groups()[0]
                    entry['opt']  = re_opt.groups()[0]
                    entry['desc'] = re_desc.groups()[0]

                    self.entries.append(entry)

                else:
                    self.errors.append(line)

    
