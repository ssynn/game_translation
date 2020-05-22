from __future__ import print_function
import os
import struct
import sys
import argparse

from scr.constants import *
from scr.public_function import *

furigana_enabled = False  # Untested, use not recommended


def shift_jis2unicode(charcode):
    # Shamelessly stolen from Stackoverflow
    if charcode <= 0xFF:
        shift_jis_string = chr(charcode)
    else:
        shift_jis_string = chr(charcode >> 8) + chr(charcode & 0xFF)

    return shift_jis_string


class ArgumentType(object):
    var = 0
    int = 1
    float = 2
    bool = 3
    string = 4

    byte = 100
    array = 101
    word = 102
    event = 103
    char = 104
    char_string = 105

    unknown = -1


class Script:
    filename = ""
    header = None
    body = None

    def __init__(self, filename="", header=None, body=None):
        self.filename = filename
        self.header = header
        self.body = body

    def write(self, indent=0):
        output = "\t" * indent + '<?xml version="1.0" encoding="Shift-JIS"?>'
        output += "\n"
        output += "\t" * indent + '<LMScript Name="%s">' % self.filename
        output += "\n"

        if self.header is not None:
            output += self.header.write(indent + 1) + "\n"

        if self.body is not None:
            output += self.body.write(indent + 1) + "\n"

        output += "\t" * indent + "</LMScript>"

        return output


class Header:
    script_version = 0
    unk1 = 1
    lm2_mode = False
    property_info = []
    property_field = []

    def __init__(self, script_version=0, unk1=1, property_info=None, property_field=None):
        self.script_version = script_version
        self.lm2_mode = script_version == 0x74

        if self.lm2_mode:
            print("LiveMaker 2 scripts may not work")

        self.unk1 = unk1

        if property_info is None:
            self.property_info = []
        else:
            self.property_info = property_info

        if property_field is None:
            self.property_field = []
        else:
            self.property_field = property_field

    def write(self, indent=0):
        output = "\t" * indent + '<Header Version="%d" Flag="%d">' % (self.script_version, self.unk1)
        output += "\n"
        indent += 1

        output += "\t" * indent + "<Properties>"
        output += "\n"
        indent += 1

        for i in range(0, len(self.property_info)):
            output += "\t" * indent + '<Property Id="%d">' % i
            indent += 1

            for x in range(0, len(self.property_info[i])):
                if x > 0:
                    output += " "
                output += "%02x" % self.property_info[i][x]

            indent -= 1
            output += "</Property>"
            output += "\n"

        indent -= 1
        output += "\t" * indent + "</Properties>"
        output += "\n"

        indent -= 1
        output += "\t" * indent + "</Header>"

        return output

    def write_function_flags(self, idx):
        print("Function %s (%02x):" % (opcode_names[idx], idx))

        for i in range(1, len(self.property_field[idx])):
            if self.property_field[idx][i]:
                print(properties[i])


class Body:
    commands = []

    def __init__(self, commands=None):
        if commands is None:
            self.commands = []
        else:
            self.commands = commands

    def write(self, indent=0):
        output = "\t" * indent + "<Body>"
        output += "\n"
        for command in self.commands:
            output += command.write(indent + 1) + "\n"
        output += "\t" * indent + "</Body>"
        return output


class Command:
    offset = 0
    opcode = -1
    name = ""
    indent = 0
    mute = 0
    not_update = 0
    line_number = 0
    line_number_diff = 0
    args = []

    def __init__(self, offset=0, opcode=-1, name="", indent=0, mute=0, not_update=0, line_number=0, line_number_diff=0,
                 args=None):
        self.offset = offset
        self.opcode = opcode
        self.name = name
        self.indent = indent
        self.mute = mute
        self.not_update = 0
        self.line_number = line_number
        self.line_number_diff = line_number_diff

        if args is None:
            self.args = []
        else:
            self.args = args

    def has_data(self):
        return len(self.args) > 0

    def write(self, indent=0):
        output = "\t" * indent + '<Item Command="%s" Indent="%d" Mute="%d" NotUpdate="%d" Color="0" Id="%d" Diff="%d">' % (
            opcode_names[self.opcode], self.indent, self.mute, self.not_update, self.line_number, self.line_number_diff)

        if self.has_data() != 0:
            output += "\n"

        for arg in self.args:
            output += arg.write(indent + 1) + "\n"

        if self.has_data() != 0:
            output += "\t" * indent

        output += "</Item>"

        # print output
        return output


class Argument:
    name = ""
    type = ArgumentType.unknown
    data = None

    def __init__(self, name="", type=ArgumentType.unknown, data=None):
        self.name = name
        self.type = type
        self.data = data

    def has_data(self):
        return self.data is not None

    def write(self, indent=0):
        output = "\t" * indent + '<%s Name="%s">' % (type_table[self.type], self.name)

        if self.type == ArgumentType.string:
            output += self.data

        elif self.type == ArgumentType.int or self.type == ArgumentType.byte:
            output += "%d" % self.data

        elif self.type == ArgumentType.bool:
            output += ("FALSE", "TRUE")[self.data]

        elif self.type == ArgumentType.array:
            if self.data.has_data():
                output += "\n"

            output += self.data.write(indent + 1)

            if self.data.has_data():
                output += "\t" * indent

        elif self.type == ArgumentType.event:
            if self.data.has_data():
                output += "\n"

            output += self.data.write(indent + 1)

            if self.data.has_data():
                output += "\t" * indent

        elif self.type == ArgumentType.var:
            output += self.data

        elif self.type == ArgumentType.float:
            output += " ".join(["%02x" % ord(x) for x in self.data])

        else:
            output += self.data
            print("Unknown type: %s (%d)" % (type_table[self.type], self.type))
            exit(-1)

        output += '</%s>' % (type_table[self.type])

        return output


class Parameters:
    params = []

    def __init__(self, params=None):
        if params is None:
            self.params = []
        else:
            self.params = params

    def has_data(self):
        return len(self.params) > 0

    def write(self, indent=0):
        output = ""
        for param in self.params:
            output += "\t" * indent + '<Param Name="%s" Calc="%s" Type="%d">' % (
                param.param_name, calc_funcs[param.calc_function], param.param_type)
            output += "\n"

            output += param.write(indent + 1)

            output += "\t" * indent + '</Param>'
            output += "\n"
        return output


class Parameter:
    param_type = 0
    param_name = ""
    calc_function = -1
    args = []

    def __init__(self, param_type=0, param_name="", calc_function=-1, args=None):
        self.param_type = param_type
        self.param_name = param_name
        self.calc_function = calc_function

        if args is None:
            self.args = []
        else:
            self.args = args

    def has_data(self):
        return len(self.args) > 0

    def write(self, indent=0):
        # print "\tParameter Type: %s (%d), %s" % (type_table[self.param_type], self.param_type, self.param_name)

        output = ""

        # if self.calc_function != -1:
        # output += "\t" * indent + '<__CALCFUNC__ Function="%s">' % calc_funcs[self.calc_function]
        # output += "\n"
        # indent += 1

        for arg in self.args:
            output += arg.write(indent) + "\n"

        # if self.calc_function != -1:
        # indent -= 1
        # output += "\t" * indent + "</__CALCFUNC__>"
        # output += "\n"

        return output


class EventBlock:
    commands = []
    tpword = ""
    has_furigana = False

    def __init__(self, tpword="", has_furigana=False, commands=None):
        if commands is None:
            self.commands = []
        else:
            self.commands = commands

        self.tpword = tpword
        self.has_furigana = has_furigana

    def has_data(self):
        return len(self.commands) > 0

    def write(self, indent=0):
        output = "\t" * indent + '<EventBlock Name="%s" HasFurigana="%d">' % (self.tpword, self.has_furigana)
        output += "\n"
        for arg in self.commands:
            output += arg.write(indent + 1) + "\n"
        output += "\t" * indent + '</EventBlock>'
        output += "\n"
        return output


class EventCommand:
    opcode = -1
    args = []

    def __init__(self, opcode=-1, args=None):
        self.opcode = opcode

        if args is None:
            self.args = []
        else:
            self.args = args

    def has_data(self):
        return len(self.args) > 0

    def write(self, indent=0):
        output = "\t" * indent + '<Event Command="%s">' % (event_opcode_names[self.opcode])
        output += "\n"
        for arg in self.args:
            output += arg.write(indent + 1) + "\n"
        output += "\t" * indent + '</Event>'
        return output


class EventArgument:
    argument_type = ArgumentType.unknown
    data = None
    extra_data = None

    def __init__(self, argument_type=ArgumentType.unknown, data=None, extra_data=None):
        self.argument_type = argument_type
        self.data = data
        self.extra_data = extra_data

    def has_data(self):
        return self.data is not None

    def write(self, indent=0):
        if self.extra_data != None:
            output = "\t" * indent + '<EventArg Type="%s" ExtraData="%d">' % (type_table[self.argument_type], self.extra_data)
        else:
            output = "\t" * indent + '<EventArg Type="%s">' % (type_table[self.argument_type])
            
        # Byte string int word float
        if self.argument_type == ArgumentType.byte:
            output += "%d" % self.data
        elif self.argument_type == ArgumentType.char:
            output += "%s" % shift_jis2unicode(self.data)
        elif self.argument_type == ArgumentType.int:
            output += "%d" % self.data
        elif self.argument_type == ArgumentType.float:
            output += "%f" % self.data
        elif self.argument_type == ArgumentType.string:
            output += "%s" % self.data
        elif self.argument_type == ArgumentType.char_string:
            output += "%s" % self.data

        output += '</EventArg>'
        return output


class Furigana:
    data = None

    def __init__(self, tpword_version=0, text_commands=0, unk1=0, unk2=0, unk3=0, unk4=0, unk5=0, unk6=0, unk7=0,
                 unk8="", unk9="", unk10=0, unk11=0, data=None):
        self.data = data
        self.tpword_version = tpword_version
        self.text_commands = text_commands
        self.unk1 = unk1
        self.unk2 = unk2
        self.unk3 = unk3
        self.unk4 = unk4
        self.unk5 = unk5
        self.unk6 = unk6
        self.unk7 = unk7
        self.unk8 = unk8
        self.unk9 = unk9
        self.unk10 = unk10
        self.unk11 = unk11
    @staticmethod
    def has_data():
        return True

    def write(self, indent=0):
        output = "\t" * indent + '<Furigana Version="%d" TextCommands="%d" Unk1="%d" Unk2="%d" Unk3="%d" Unk4="%d" Unk5="%d" Unk6="%d" Unk7="%d" Unk8="%s" Unk9="%s" Unk10="%d" Unk11="%d" />' % (
            self.tpword_version, self.text_commands, self.unk1, self.unk2, self.unk3, self.unk4, self.unk5, self.unk6,
            self.unk7, self.unk8, self.unk9, self.unk10, self.unk11)
        return output


class Label:
    script = ""
    offset = 0

    def __init__(self, script="", offset=0):
        self.script = script
        self.offset = offset

    @staticmethod
    def has_data():
        return True

    def write(self, indent=0):
        output = "\t" * indent + '<Label Script="%s" Target="%d" />' % (self.script, self.offset)
        return output


class SetLabel:
    script = ""
    offset = 0

    def __init__(self, script=""):
        self.script = script

    @staticmethod
    def has_data():
        return True

    def write(self, indent=0):
        output = "\t" * indent + '<SetLabel>%s</SetLabel>' % (self.script)
        return output


class Disassembler:
    file = None
    data = None
    idx = 0
    lm2_mode = False
    script_version = 0
    opcode_extra_info = None
    script = None
    input_filename = ""
    last_id = 0

    def __init__(self, input_filename, internal_filename=None):
        self.file = None
        self.data = None
        self.idx = 0
        self.lm2_mode = False
        self.script_version = 0
        self.opcode_extra_info = None
        self.script = None
        self.input_filename = ""
        self.last_id = 0
        self.strings = []

        if not os.path.isfile(input_filename):
            print("Could not find %s, exiting..." % (input_filename))
            exit(-1)

        print("Opening %s..." % input_filename)

        if internal_filename is not None:
            self.input_filename = internal_filename
        else:
            self.input_filename = input_filename

        self.data = open(input_filename, 'rb').read()

    def disassemble(self):
        print("Disassembling %d bytes of data..." % len(self.data))

        header = self.parse_header()
        body = self.parse_body()
        save_json('text.json', self.strings)
        self.script = Script(self.input_filename, header, body)

    def write(self, output_filename):
        output = ""

        if self.script is not None:
            output = self.script.write()

        try:
            output_path = os.path.dirname(output_filename)
            os.makedirs(output_path)
        except:
            pass

        file = open(output_filename, "w")
        file.write(output)
        file.close()

    def parse_header(self):
        self.script_version = self.read_int()
        self.lm2_mode = self.script_version == 0x74

        if self.script_version < 0x67:
            print("Invalid LSB file")
            exit(-2)

        unk1 = self.read_byte()
        object_count = self.read_int()
        object_size = self.read_int()
        object_size_overflow = 0

        if object_size > 0x580:
            object_size_overflow = object_size - 0x580
            object_size = 0x580

        # An entry exists for all opcodes in the virtual machine.
        # It says what parameters/fields are available to the opcode.
        # I don't think there will ever be a need to change it.
        self.opcode_extra_info = []
        property_data = {}
        for i in range(0, object_count):
            if i > 0x40:
                # This should never get hit I think
                object_size_overflow += object_size

            property_count = 0xab
            if self.lm2_mode:
                property_count = 0xa5

            properties = bytearray(self.read(object_size))
            properties_bool = [False]

            for x in range(0, len(properties)):
                for bitshift in range(0, 8):
                    prop_exists = (properties[x] & (1 << bitshift)) != 0
                    properties_bool.append(prop_exists)

                    if len(properties_bool) > property_count:
                        break

            self.opcode_extra_info.append(properties_bool)
            property_data[i] = properties

            # Skip extra data
            if object_size_overflow > 0:
                self.idx += object_size_overflow

        # Skip extra data at end if needed
        if object_size_overflow > 0:
            self.idx += object_size_overflow

        header = Header(self.script_version, unk1, property_data, self.opcode_extra_info)
        return header

    def parse_body(self):
        def read_params(command):
            output = Parameters()

            num_of_params = self.read_int()
            for i in range(0, num_of_params):
                param_type = self.read_byte()
                param_name = self.read_string()
                num_of_arguments = self.read_int()

                param = Parameter(param_type=param_type, param_name=param_name)

                # print "offset[%08x] %d %s %d" % (self.idx, param_type, param_name, num_of_arguments)

                # TODO: Add operators

                if param_type == 0x0b:
                    # Calc
                    calc_function = self.read_byte()
                    param.calc_function = calc_function

                    if calc_function not in calc_funcs:
                        print("Unknown calc function: %02x" % calc_function)
                        exit(-3)

                for i in range(0, num_of_arguments):
                    argument_type = self.read_byte()

                    if argument_type == 0x01:
                        # TParamInt
                        val = self.read_int()
                    elif argument_type == 0x02:
                        # TParamFloat
                        # 1 float = 0x0a bytes
                        val = self.read(10)
                    elif argument_type == 0x03:
                        # TParamFlag
                        val = self.read_byte()
                    elif argument_type == 0x04:
                        # TParamStr
                        val = self.read_string()
                    else:
                        # TParamVar
                        val = self.read_string()

                    argument = Argument(type=argument_type, data=val)
                    param.args.append(argument)

                    # print "[arg %d/%d] %s =" % (i + 1, num_of_arguments, type_table[argument_type]),
                    # print val

                output.params.append(param)

            return output

        def read_function_prologue(command):
            command.indent = self.read_int()
            command.mute = self.read_byte()
            command.not_update = self.read_byte()
            command.line_number = self.read_int()

        def TComIf(command):
            read_function_prologue(command)
            command.args.append(Argument("Calc", ArgumentType.array, read_params(command)))

        def TComTerminate(command):
            # Checked
            read_function_prologue(command)

        def TComLabel(command):
            # Checked
            # TODO: Make new SetLabel type
            read_function_prologue(command)
            command.args.append(SetLabel(self.read_string()))

        def TComJump(command):
            # Checked
            read_function_prologue(command)
            page = self.read_string()
            target_label = self.read_int()
            command.args.append(Label(page, target_label))

            command.args.append(Argument("Calc", ArgumentType.array, read_params(command)))

        def TComCall(command):
            # Checked
            read_function_prologue(command)
            page = self.read_string()
            target_label = self.read_int()
            command.args.append(Label(page, target_label))

            result = self.read_string()
            command.args.append(Argument("Result", ArgumentType.string, result))

            command.args.append(Argument("Calc", ArgumentType.array, read_params(command)))

            params = Parameter()
            count = self.read_int()
            for i in range(0, count):
                params.args.append(Argument("__ARG_%d__" % i, ArgumentType.array, read_params(command)))
            command.args.append(Argument("Params", ArgumentType.array, params))

        def TComExit(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("Calc", ArgumentType.array, read_params(command)))

        def TComWait(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("Calc", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Time", ArgumentType.array, read_params(command)))

            if self.script_version >= 0x6b:
                # Version difference?
                command.args.append(Argument("StopEvent", ArgumentType.array, read_params(command)))

        def TComImgNew(command):
            read_function_prologue(command)

            for i in range(0, len(self.opcode_extra_info[command.opcode])):
                if self.opcode_extra_info[command.opcode][i]:
                    command.args.append(Argument("__ARG_%d__" % i, ArgumentType.array, read_params(command)))

        def TComFlip(command):
            # CHecked
            read_function_prologue(command)
            command.args.append(Argument("Wipe", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Time", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Reverse", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Act", ArgumentType.array, read_params(command)))

            targets = Parameter()
            count = self.read_int()
            for i in range(0, count):
                targets.args.append(Argument("__ARG_%d__" % i, ArgumentType.array, read_params(command)))
            command.args.append(Argument("Targets", ArgumentType.array, targets))

            command.args.append(Argument("Delete", ArgumentType.array, read_params(command)))

            param = Parameter()
            param.args.append(Argument("Item", ArgumentType.array, read_params(command)))
            param.args.append(Argument("Item", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Param", ArgumentType.array, param))

            if self.script_version >= 0x65:
                command.args.append(Argument("Source", ArgumentType.array, read_params(command)))
            if self.script_version >= 0x6b:
                command.args.append(Argument("StopEvent", ArgumentType.array, read_params(command)))
            if self.script_version >= 0x75:
                command.args.append(Argument("DifferenceOnly", ArgumentType.array, read_params(command)))

        def TComVarNew(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("Name", ArgumentType.string, self.read_string()))
            command.args.append(Argument("Type", ArgumentType.byte, self.read_byte()))
            command.args.append(Argument("InitVal", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Scope", ArgumentType.byte, self.read_byte()))

        def TComVarDel(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("Name", ArgumentType.string, self.read_string()))

        def TComGetProp(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("ObjName", ArgumentType.array, read_params(command)))
            command.args.append(Argument("ObjProp", ArgumentType.array, read_params(command)))
            command.args.append(Argument("VarName", ArgumentType.string, self.read_string()))

        def TComSetProp(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("ObjName", ArgumentType.array, read_params(command)))
            command.args.append(Argument("ObjProp", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Value", ArgumentType.array, read_params(command)))

        def TComObjDel(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("Name", ArgumentType.array, read_params(command)))

        def ParseEventBlock(command):
            block_end = self.idx + self.read_int()

            tpword = self.read(6)  # TpWord
            tpword_version_str = self.read(3)
            tpword_version = int(tpword_version_str)

            event_block = EventBlock(tpword + tpword_version_str)

            variable_count = self.read_int()
            for i in range(0, variable_count):
                text_commands = self.read_int()
                unk1 = self.read_int()
                unk2 = self.read_int()
                unk3 = self.read_int()
                unk4 = self.read_byte()
                unk5 = self.read_byte()

                unk6 = 0
                if tpword_version < 0x64:
                    unk6 = self.read_byte()

                unk7 = self.read_int()
                unk8 = self.read_string()
                unk9 = self.read_string()

                unk10 = 0
                unk11 = 0
                if tpword_version >= 0x64:
                    unk10 = self.read_int()
                    unk11 = self.read_int()

                if furigana_enabled:
                    event_block.commands.append(
                        Furigana(tpword_version, text_commands, unk1, unk2, unk3, unk4, unk5, unk6, unk7, unk8, unk9,
                                 unk10, unk11))
                event_block.has_furigana = True

            expected_command_count = self.read_int()
            command_count = 0
            str = ""
            found_str = False
            extra_data = None
            while command_count < expected_command_count: #and self.idx < block_end:
                data = []
                op = self.read_byte()
                command_count += 1

                if op != 0x01 and str != "":
                    data.append(EventArgument(ArgumentType.char_string, str, extra_data))
                    event_block.commands.append(EventCommand(-1, data))
                    str = ""
                    found_str = False
                    data = []

                if op == 0x01:
                    # TWdChar
                    # s, f, and i are always the same every command so they can be ignored in order to combine
                    # a bunch of Char commands into a single string
                    # s = self.read_string()
                    # f = self.read_int()
                    # w = self.read_word()
                    # i = self.read_int()

                    # data.append(EventArgument(ArgumentType.string, s))
                    # data.append(EventArgument(ArgumentType.int, f)) # How does this work?
                    # data.append(EventArgument(ArgumentType.char, w))
                    # data.append(EventArgument(ArgumentType.int, i))

                    s = self.read_string()
                    extra_data = self.read_int()
                    str += shift_jis2unicode(self.read_word())
                    i = self.read_int()
                    found_str = True
                    
                elif op == 0x02:
                    # TWdOpeAlign
                    data.append(EventArgument(ArgumentType.byte, self.read_byte()))

                elif op == 0x03:
                    # TWdOpeReturn
                    data.append(EventArgument(ArgumentType.byte, self.read_byte()))
                    
                elif op == 0x04:
                    # TWdOpeIndent
                    # No data
                    pass
                    
                elif op == 0x05:
                    # TWdOpeUndent
                    # No data
                    pass

                elif op == 0x06:
                    # TWdOpeEvent
                    event = self.read_string()

                    if event[0] == '\x01':
                        event = "[\\x01]" + event[1:]
                    event = event.replace('\r\n', '|')

                    data.append(EventArgument(ArgumentType.string, event))

                elif op == 0x07:
                    # TWdOpeVar
                    data.append(EventArgument(ArgumentType.int, self.read_int()))
                    
                    if self.script_version >= 0x65:
                        data.append(EventArgument(ArgumentType.int, self.read_int()))
                        data.append(EventArgument(ArgumentType.string, self.read_string()))
                    
                    if self.script_version >= 0x66:
                        data.append(EventArgument(ArgumentType.string, self.read_string()))
                    else:
                        # Untested
                        self.idx -= 4
                        data.append(EventArgument(ArgumentType.string, self.read_string()))
                        data.append(EventArgument(ArgumentType.int, self.read_int()))                        
                    
                elif op == 0x09:
                    # TWdImg
                    data.append(EventArgument(ArgumentType.string, self.read_string()))
                    data.append(EventArgument(ArgumentType.int, self.read_int()))
                    data.append(EventArgument(ArgumentType.string, self.read_string()))
                    data.append(EventArgument(ArgumentType.byte, self.read_byte()))

                elif op == 0x0a:
                    # TWdOpeHistChar
                    data.append(EventArgument(ArgumentType.string, self.read_string()))
                    data.append(EventArgument(ArgumentType.int, self.read_int()))
                    data.append(EventArgument(ArgumentType.int, self.read_int()))
                    data.append(EventArgument(ArgumentType.string, self.read_string()))

                else:
                    print("unknown opcode: %02x @ %08x" % (op, self.idx - 1))
                    exit(1)

                if op != 0x01:
                    event_block.commands.append(EventCommand(op, data))

            if found_str:
                data = [EventArgument(ArgumentType.char_string, str)]
                event_block.commands.append(EventCommand(-1, data))

            return event_block

        def TComTextIns(command):  # Event??
            read_function_prologue(command)
            # block = self.read_string()

            command.args.append(ParseEventBlock(command))

            command.args.append(Argument("__UNK_1__", ArgumentType.array, read_params(command)))
            command.args.append(Argument("__UNK_2__", ArgumentType.array, read_params(command)))
            command.args.append(Argument("__UNK_3__", ArgumentType.array, read_params(command)))

            if self.script_version >= 0x6b:
                # Version difference?
                command.args.append(Argument("__UNK_4__", ArgumentType.array, read_params(command)))

        def TComGameSave(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("No", ArgumentType.array, read_params(command)))

            if self.script_version >= 0x69:
                page = self.read_string()
                target_label = self.read_int()
                command.args.append(Label(page, target_label))
            else:
                command.args.append(Argument("Page", ArgumentType.string, self.read_string()))

            command.args.append(Argument("Caption", ArgumentType.array, read_params(command)))

        def TComMenuClose(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("Target", ArgumentType.array, read_params(command)))

        def TComMovieStop(command):
            # No examples of the second parameter available
            read_function_prologue(command)
            command.args.append(Argument("Target", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Time", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Wait", ArgumentType.array, read_params(command)))

            if self.script_version >= 0x6b:
                # Version difference?
                command.args.append(Argument("__UNK__", ArgumentType.array, read_params(command)))

        def TComTextClr(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("Target", ArgumentType.array, read_params(command)))

        def TComCallHist(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("Target", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Index", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Count", ArgumentType.array, read_params(command)))
            command.args.append(Argument("CutBreak", ArgumentType.array, read_params(command)))

            if self.script_version >= 0x6f:
                # Version difference?
                command.args.append(Argument("FormatName", ArgumentType.array, read_params(command)))

        def TComWhile(command):
            # Different format than original scripting
            read_function_prologue(command)
            command.args.append(Argument("__UNK__", ArgumentType.array, read_params(command)))
            command.args.append(Argument("__UNK_2__", ArgumentType.int, self.read_int()))

        def TComWhileInit(command):
            # Different format than original scripting
            read_function_prologue(command)
            command.args.append(Argument("__UNK__", ArgumentType.array, read_params(command)))

        def TComWhileLoop(command):
            # Different format than original scripting
            read_function_prologue(command)
            command.args.append(Argument("__UNK__", ArgumentType.array, read_params(command)))
            command.args.append(Argument("__UNK_2__", ArgumentType.int, self.read_int()))

        def TComBreak(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("Calc", ArgumentType.array, read_params(command)))
            command.args.append(Argument("__UNK__", ArgumentType.int, self.read_int()))

        def TComContinue(command):
            # No examples of the second parameter available
            read_function_prologue(command)
            command.args.append(Argument("Calc", ArgumentType.array, read_params(command)))
            command.args.append(Argument("__UNK__", ArgumentType.int, self.read_int()))

        def TComGameLoad(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("No", ArgumentType.array, read_params(command)))

        def TComPCReset(command):
            # Checked
            read_function_prologue(command)
            page = self.read_string()
            target_label = self.read_int()
            command.args.append(Label(page, target_label))

            command.args.append(Argument("AllClear", ArgumentType.byte, self.read_byte()))

        def TComMediaPlay(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("Target", ArgumentType.array, read_params(command)))

        def TComPropMotion(command):
            # Checked
            read_function_prologue(command)
            command.args.append(Argument("Name", ArgumentType.array, read_params(command)))
            command.args.append(Argument("ObjName", ArgumentType.array, read_params(command)))
            command.args.append(Argument("ObjProp", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Value", ArgumentType.array, read_params(command)))
            command.args.append(Argument("Time", ArgumentType.array, read_params(command)))
            command.args.append(Argument("MoveType", ArgumentType.array, read_params(command)))

            if self.script_version >= 0x6c:
                command.args.append(Argument("Paused", ArgumentType.array, read_params(command)))

        def TComCabinetSave(command):
            # Checked
            TComImgNew(command)
            command.args.append(Argument("Name", ArgumentType.array, read_params(command)))

            targets = Parameter()
            count = self.read_int()
            for i in range(0, count):
                targets.args.append(Argument("__ARG_%d__" % i, ArgumentType.array, read_params(command)))
            command.args.append(Argument("Targets", ArgumentType.array, targets))

        def TComEntryHist(command):
            # No examples of the second parameter available
            read_function_prologue(command)
            command.args.append(Argument("Name", ArgumentType.array, read_params(command)))

            if self.script_version >= 0x6f:
                # Version difference?
                command.args.append(Argument("__UNK__", ArgumentType.array, read_params(command)))

        function_count = self.read_int()
        body = Body()
        for i in range(0, function_count):
            opcode = self.read_byte()

            opcode_table = {
                0x00: TComIf, 0x01: TComIf, 0x02: TComTerminate,
                0x03: TComLabel, 0x04: TComJump, 0x05: TComCall,
                0x06: TComExit, 0x07: TComWait, 0x08: TComImgNew,
                0x09: TComImgNew, 0x0a: TComImgNew, 0x0b: TComImgNew,
                0x0c: TComImgNew, 0x0d: TComFlip, 0x0e: TComIf,
                0x0f: TComVarNew, 0x10: TComVarDel, 0x11: TComGetProp,
                0x12: TComSetProp, 0x13: TComObjDel, 0x14: TComTextIns,
                0x15: TComMovieStop, 0x16: TComTerminate, 0x17: TComImgNew,
                0x18: TComImgNew, 0x19: TComImgNew, 0x1a: TComMenuClose,
                0x1b: TComLabel, 0x1c: TComTextClr, 0x1d: TComCallHist,
                0x1e: TComImgNew, 0x1f: TComWhile, 0x20: TComWhileInit,
                0x21: TComWhileLoop, 0x22: TComBreak, 0x23: TComContinue,
                0x24: TComImgNew, 0x25: TComImgNew, 0x26: TComGameSave,
                0x27: TComGameLoad, 0x28: TComPCReset, 0x29: TComPCReset,
                0x2a: TComImgNew, 0x2b: TComImgNew, 0x2c: TComImgNew,
                0x2d: TComTerminate, 0x2e: TComTerminate, 0x2f: TComTerminate,
                0x30: TComImgNew, 0x31: TComImgNew, 0x32: TComImgNew,
                0x33: TComImgNew, 0x34: TComImgNew, 0x35: TComImgNew,
                0x36: TComImgNew, 0x37: TComMediaPlay, 0x38: TComImgNew,
                0x39: TComPropMotion, 0x3a: TComEntryHist, 0x3b: TComCabinetSave,
                0x3c: TComCabinetSave, 0x3d: TComTerminate, 0x3e: TComTerminate,
                0x3f: TComTerminate,
                # 0x3a Should be named "FormatHist", check to make sure all opcodes have the correct names
            }

            max_opcode = 0x3f
            if self.lm2_mode:
                max_opcode = 0x3c

            if opcode > max_opcode:
                print("Illegal command: %02x @ %08x" % (opcode, self.idx - 1))
                exit(-3)

            elif not opcode in opcode_table:
                print("Unknown command: %s (%02x) @ %08x" % (opcode_names[opcode], opcode, self.idx - 1))
                exit(1)

            # print "[%08x] Opcode: %s (%02x)" % (self.idx - 1, opcode_names[opcode], opcode)

            command = Command(offset=self.idx - 1, opcode=opcode, name=opcode_names[opcode])
            opcode_table[opcode](command)
            # print "Line Number: %08x" % command.line_number
            # print ""

            command.line_number_diff = int(command.line_number) - self.last_id
            self.last_id = int(command.line_number)

            body.commands.append(command)

        return body

    def read(self, length):
        val = self.data[self.idx:self.idx + length]
        self.idx += length
        return val

    def read_byte(self):
        # val = struct.unpack('<B', self.read(1))[0]
        return from_bytes(self.read(1))

    def read_word(self):
        # val = struct.unpack('<H', self.read(2))[0]
        return from_bytes(self.read(2))

    def read_int(self):
        # try:
        #     t = self.read(4)
        #     val = struct.unpack('<I', t)[0]
        # except Exception as e:
        #     print(t, self.idx, hex(self.idx))
        #     print(e)
        #     raise Exception()
        return from_bytes(self.read(4))

    def read_float(self):
        val = struct.unpack('<f', self.read(4))[0]
        return val

    def read_string(self):
        length = self.read_int()
        string = self.read(length)
        self.strings.append(string.decode('cp932', errors='ignore'))
        return string


def main():
    parser = argparse.ArgumentParser(
        description='Disassmble LiveMaker 2/3 scripts into a modifiable plain-text script file.')
    parser.add_argument('--input', required=True, dest='input_filename', help='Input LSB file')
    parser.add_argument('--output', required=True, dest='output_filename', help='Output XML file')
    args = parser.parse_args(sys.argv[1:])

    dis = Disassembler(args.input_filename)
    dis.disassemble()
    dis.write(args.output_filename)


if __name__ == "__main__":
    main()