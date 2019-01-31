# -*- coding: utf-8 -*-

from rules.rule import *


class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Component fields contain the correct information')

    def checkVisibility(self, field):
        return field['visibility'] == 'V'

    # return True if a field is empty else false
    def checkEmpty(self, field):
        if 'name' in field.keys():
            name = field['name']
            if name and name not in ['""', "''"] and len(name) > 0:
                return False
        return True

    def checkReference(self):

        fail = False

        ref = self.component.fields[0]

        if (not self.component.isGraphicSymbol()) and (not self.component.isPowerSymbol()):
            if not self.checkVisibility(ref):
                self.error("Ref(erence) field must be VISIBLE")
                fail = True
        else:
            if self.checkVisibility(ref):
                self.error("Ref(erence) field must be INVISIBLE in graphic symbols or power-symbols")
                fail = True

        return fail

    def checkValue(self):
        fail = False

        value = self.component.fields[1]

        name = value['name']

        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]

        if (not self.component.isGraphicSymbol()) and (not self.component.isPowerSymbol()):
            if not name == self.component.name:
                self.error("Value {val} does not match component name.".format(val=name))
                fail = True
            # name field must be visible!
            if not self.checkVisibility(value):
                self.error("Value field must be VISIBLE")
                fail = True
        else:
            if (not ('~'+name) == self.component.name) and (not name == self.component.name):
                self.error("Value {val} does not match component name.".format(val=name))
                fail = True

        if not isValidName(self.component.name, self.component.isGraphicSymbol(), self.component.isPowerSymbol()):
            self.error("Symbol name '{val}' contains invalid characters as per KLC 1.7".format(
                val=self.component.name))
            fail = True

        return fail

    def checkFootprint(self):
        # Footprint field must be invisible
        fail = False

        fp = self.component.fields[2]

        if self.checkVisibility(fp):
            self.error("Footprint field must be INVISIBLE")
            fail = True

        return fail

    def checkDatasheet(self):

        # Datasheet field must be invisible
        fail = False

        ds = self.component.fields[3]

        if self.checkVisibility(ds):
            self.error("Datasheet field must be INVISIBLE")
            fail = True

        # Datasheet field must be empty
        if not self.checkEmpty(ds):
            self.error("Datasheet field must be EMPTY")
            fail = True

        return fail

    def check(self):

        # Check for required fields
        n = len(self.component.fields)
        if n < 4:
            self.error("Component does not have minimum required fields!")

            if n < 1:
                self.errorExtra(" - Missing REFERENCE field")

            if n < 2:
                self.errorExtra(" - Missing VALUE field")

            if n < 3:
                self.errorExtra(" - Missing FOOTPRINT field")

            if n < 4:
                self.errorExtra(" - Missing DATASHEET field")

            return True

        # Check for extra fields!
        extraFields = False

        if n > 4:
            extraFields = True
            self.error("Component contains extra fields after DATASHEET field")

        return any([
            self.checkReference(),
            self.checkValue(),
            self.checkFootprint(),
            self.checkDatasheet(),
            extraFields
            ])

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("Fixing VALUE-field...")
        self.component.fields[1]['name'] = self.component.name
        # store datasheet field contents for later reuse
        if ((not self.component.documentation['datasheet']) or len(self.component.documentation['datasheet']) == 0) and (len(self.component.fields[3]['name']) > 2):
            ds = self.component.fields[3]['name']
            if ds[0] == '"' and ds[len(ds)-1] == '"':
                ds = ds[1:(len(ds)-1)]
            self.component.documentation['datasheet'] = ds
            self.info("Copying DATASHEET '{ds}' to DCM-file ...".format(ds=ds))

        self.info("Emptying DATASHEET-field ...")
        self.component.fields[3]['name'] = ""

        self.info("Setting default field visibilities ...")
        self.component.fields[0]['visibility'] = "V"
        self.component.fields[1]['visibility'] = "V"
        self.component.fields[2]['visibility'] = "I"
        self.component.fields[3]['visibility'] = "I"
        self.recheck()
