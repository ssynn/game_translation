opcode_names = {
    0x00: "If",           0x01: "Elseif",       0x02: "Else",
    0x03: "Label",        0x04: "Jump",         0x05: "Call",
    0x06: "Exit",         0x07: "Wait",         0x08: "BoxNew",
    0x09: "ImgNew",       0x0a: "MesNew",       0x0b: "Timer",
    0x0c: "Movie",        0x0d: "Flip",         0x0e: "Calc",
    0x0f: "VarNew",       0x10: "VarDel",       0x11: "GetProp",
    0x12: "SetProp",      0x13: "ObjDel",       0x14: "TextIns",
    0x15: "MovieStop",    0x16: "ClrHist",      0x17: "Cinema",
    0x18: "Caption",      0x19: "Menu",         0x1a: "MenuClose",
    0x1b: "Comment",      0x1c: "TextClr",      0x1d: "CallHist",
    0x1e: "Button",       0x1f: "While",        0x20: "WhileInit",
    0x21: "WhileLoop",    0x22: "Break",        0x23: "Continue",
    0x24: "ParticleNew",  0x25: "FireNew",      0x26: "GameSave",
    0x27: "GameLoad",     0x28: "PCReset",      0x29: "Reset",
    0x2a: "Sound",        0x2b: "EditNew",      0x2c: "MemoNew",
    0x2d: "Terminate",    0x2e: "DoEvent",      0x2f: "ClrRead",
    0x30: "MapImgNew",    0x31: "WaveNew",      0x32: "TileNew",
    0x33: "SliderNew",    0x34: "ScrollbarNew", 0x35: "GaugeNew",
    0x36: "CGCaption",    0x37: "MediaPlay",    0x38: "PrevMenuNew",
    0x39: "PropMotion",   0x3a: "FormatHist",   0x3b: "SaveCabinet",
    0x3c: "LoadCabinet",  0x3d: "IFDEF",        0x3e: "IFNDEF",
    0x3f: "ENDIF",
}
opcode_names_inv = {v: k for k, v in opcode_names.items()}

calc_funcs = {
    0x00: "IntToStr",           0x01: "IntToHex",           0x02: "GetProp",
    0x03: "SetProp",            0x04: "GetArraySize",       0x05: "Length",
    0x06: "JLength",            0x07: "Copy",               0x08: "JCopy",
    0x09: "Delete",             0x0a: "JDelete",            0x0b: "Insert",
    0x0c: "JInsert",            0x0d: "CompareStr",         0x0e: "CompareText",
    0x0f: "Pos",                0x10: "JPos",               0x11: "Trim",
    0x12: "JTrim",              0x13: "Exists",             0x14: "Not",
    0x15: "SetArray",           0x16: "FillMem",            0x17: "CopyMem",
    0x18: "GetCheck",           0x19: "SetCheck",           0x1a: "Random",
    0x1b: "GetSaveCaption",     0x1c: "ArrayToString",      0x1d: "StringToArray",
    0x1e: "IndexOfStr",         0x1f: "SortStr",            0x20: "ListCompo",
    0x21: "ToClientX",          0x22: "ToClientY",          0x23: "ToScreenX",
    0x24: "ToScreenY",          0x25: "Int",                0x26: "Float",
    0x27: "Sin",                0x28: "Cos",                0x29: "Tan",
    0x2a: "ArcSin",             0x2b: "ArcCos",             0x2c: "ArcTan",
    0x2d: "ArcTan",             0x2e: "Hypot",              0x2f: "IndexOfMenu",
    0x30: "Abs",                0x31: "Fabs",               0x32: "VarExists",
    0x33: "EncodeDate",         0x34: "EncodeTime",         0x35: "DecodeDate",
    0x36: "DecodeTime",         0x37: "GetYear",            0x38: "GetMonth",
    0x39: "GetDay",             0x3a: "GetHour",            0x3b: "GetMin",
    0x3c: "GetSec",             0x3d: "GetWeek",            0x3e: "GetWeekStr",
    0x3f: "GetWeekJStr",        0x40: "FixStr",             0x41: "GetDisplayMode",
    0x42: "AddArray",           0x43: "InsertArray",        0x44: "DeleteArray",
    0x45: "InPrimary",          0x46: "CopyArray",          0x47: "FileExists",
    0x48: "LoadTextFile",       0x49: "LowerCase",          0x4a: "UpperCase",
    0x4b: "ExtractFilePath",    0x4c: "ExtractFileName",    0x4d: "ExtractFileExt",
    0x4e: "IsPathDelimiter",    0x4f: "AddBackSlash",       0x50: "ChangeFileExt",
    0x51: "IsDelimiter",        0x52: "StringOfChar",       0x53: "StringReplace",
    0x54: "AssignTemp",         0x55: "HanToZen",           0x56: "ZenToHan",
    0x57: "DBCreateTable",      0x58: "DBSetActive",        0x59: "DBAddField",
    0x5a: "DBSetRecNo",         0x5b: "DBInsert",           0x5c: "DBDelete",
    0x5d: "DBGetInt",           0x5e: "DBSetInt",           0x5f: "DBGetFloat",
    0x60: "DBSetFloat",         0x61: "DBGetBool",          0x62: "DBSetBool",
    0x63: "DBGetStr",           0x64: "DBSetStr",           0x65: "DBRecordCount",
    0x66: "DBFindFirst",        0x67: "DBFindLast",         0x68: "DBFindNext",
    0x69: "DBFindPrior",        0x6a: "DBLocate",           0x6b: "DBLoadTsvFile",
    0x6c: "DBDirectGetInt",     0x6d: "DBDirectSetInt",     0x6e: "DBDirectGetFloat",
    0x6f: "DBDirectSetFloat",   0x70: "DBDirectGetBool",    0x71: "DBDirectSetBool",
    0x72: "DBDirectGetStr",     0x73: "DBDirectSetStr",     0x74: "DBCopyTable",
    0x75: "DBDeleteTable",      0x76: "DBInsertTable",      0x77: "DBCopy",
    0x78: "DBClearTable",       0x79: "DBSort",             0x7a: "DBGetActive",
    0x7b: "DBGetRecNo",         0x7c: "DBClearRecord",      0x7d: "SetWallPaper",
    0x7e: "Min",                0x7f: "Max",                0x80: "Fmin",
    0x81: "Fmax",               0x82: "GetVarType",         0x83: "GetEnabled",
    0x84: "SetEnabled",         0x85: "AddDelimiter",       0x86: "ListSaveCaption",
    0x87: "OpenUrl",            0x88: "Calc",               0x89: "SaveScreen",
    0x8a: "StrToIntDef",        0x8b: "StrToFloatDef",      0x8c: "GetVisible",
    0x8d: "SetVisible",         0x8e: "GetHistoryCount",    0x8f: "GetHistoryMaxCount",
    0x90: "SetHistoryMaxCount", 0x91: "GetGroupIndex",      0x92: "GetSelected",
    0x93: "SetSelected",        0x94: "SelectOpenFile",     0x95: "SelectSaveFile",
    0x96: "SelectDirectory",    0x97: "ExtractFile",        0x98: "Chr",
    0x99: "Ord",                0x9a: "InCabinet",          0x9b: "PushVar",
    0x9c: "PopVar",             0x9d: "DeleteStack",        0x9e: "CopyFile",
    0x9f: "DBGetTableCount",    0xa0: "DBGetTable",         0xa1: "CreateObject",
    0xa2: "DeleteObject",       0xa3: "GetItem",            0xa4: "UniqueArray",
    0xa5: "TrimArray",          0xa6: "GetImeOpened",       0xa7: "SetImeOpened",
    0xa8: "Alert",

    -1: "",
}
calc_funcs_inv = {v: k for k, v in calc_funcs.items()}

type_table = {
    0x00: "Var",
    0x01: "Int",
    0x02: "Float",
    0x03: "Flag",
    0x04: "Str",

    100: "Byte",  # Not part of the engine's spec, added for my convenience
    101: "Array",
    102: "Word",
    103: "Event",
    104: "Char",
    105: "CharString",
    106: "Param",
}
type_table_inv = {v: k for k, v in type_table.items()}
type_table_inv_lower = {v.lower(): k for k, v in type_table.items()}

properties = {
    0x01: "PR_NAME",                 0x02: "PR_PARENT",               0x03: "PR_SOURCE",
    0x04: "PR_LEFT",                 0x05: "PR_TOP",                  0x06: "PR_WIDTH",
    0x07: "PR_HEIGHT",               0x08: "PR_ZOOMX",                0x09: "PR_COLOR",
    0x0a: "PR_BORDERWIDTH",          0x0b: "PR_BORDERCOLOR",          0x0c: "PR_ALPHA",
    0x0d: "PR_PRIORITY",             0x0e: "PR_OFFSETX",              0x0f: "PR_OFFSETY",
    0x10: "PR_FONTNAME",             0x11: "PR_FONTHEIGHT",           0x12: "PR_FONTSTYLE",
    0x13: "PR_LINESPACE",            0x14: "PR_FONTCOLOR",            0x15: "PR_FONTLINKCOLOR",
    0x16: "PR_FONTBORDERCOLOR",      0x17: "PR_FONTHOVERCOLOR",       0x18: "PR_FONTHOVERSTYLE",
    0x19: "PR_HOVERCOLOR",           0x1a: "PR_ANTIALIAS",            0x1b: "PR_DELAY",
    0x1c: "PR_PAUSED",               0x1d: "PR_VOLUME",               0x1e: "PR_REPEAT",
    0x1f: "PR_BALANCE",              0x20: "PR_ANGLE",                0x21: "PR_ONPLAYING",
    0x22: "PR_ONNOTIFY",             0x23: "PR_ONMOUSEMOVE",          0x24: "PR_ONMOUSEOUT",
    0x25: "PR_ONLBTNDOWN",           0x26: "PR_ONLBTNUP",             0x27: "PR_ONRBTNDOWN",
    0x28: "PR_ONRBTNUP",             0x29: "PR_ONWHEELDOWN",          0x2a: "PR_ONWHEELUP",
    0x2b: "PR_BRIGHTNESS",           0x2c: "PR_ONPLAYEND",            0x2d: "PR_INDEX",
    0x2e: "PR_COUNT",                0x2f: "PR_ONLINK",               0x30: "PR_VISIBLE",
    0x31: "PR_COLCOUNT",             0x32: "PR_ROWCOUNT",             0x33: "PR_TEXT",
    0x34: "PR_MARGINX",              0x35: "PR_MARGINY",              0x36: "PR_HALIGN",
    0x37: "PR_BORDERSOURCETL",       0x38: "PR_BORDERSOURCETC",       0x39: "PR_BORDERSOURCETR",
    0x3a: "PR_BORDERSOURCECL",       0x3b: "PR_BORDERSOURCECC",       0x3c: "PR_BORDERSOURCECR",
    0x3d: "PR_BORDERSOURCEBL",       0x3e: "PR_BORDERSOURCEBC",       0x3f: "PR_BORDERSOURCEBR",
    0x40: "PR_BORDERHALIGNT",        0x41: "PR_BORDERHALIGNC",        0x42: "PR_BORDERHALIGNB",
    0x43: "PR_BORDERVALIGNL",        0x44: "PR_BORDERVALIGNC",        0x45: "PR_BORDERVALIGNR",
    0x46: "PR_SCROLLSOURCE",         0x47: "PR_CHECKSOURCE",          0x48: "PR_AUTOSCRAP",
    0x49: "PR_ONSELECT",             0x4a: "PR_RCLICKSCRAP",          0x4b: "PR_ONOPENING",
    0x4c: "PR_ONOPENED",             0x4d: "PR_ONCLOSING",            0x4e: "PR_ONCLOSED",
    0x4f: "PR_CARETX",               0x50: "PR_CARETY",               0x51: "PR_IGNOREMOUSE",
    0x52: "PR_TEXTPAUSED",           0x53: "PR_TEXTDELAY",            0x54: "PR_HOVERSOURCE",
    0x55: "PR_PRESSEDSOURCE",        0x56: "PR_GROUPINDEX",           0x57: "PR_ALLOWALLUP",
    0x58: "PR_SELECTED",             0x59: "PR_CAPTUREMASK",          0x5a: "PR_POWER",
    0x5b: "PR_ORIGWIDTH",            0x5c: "PR_ORIGHEIGHT",           0x5d: "PR_APPEARX",
    0x5e: "PR_APPEARY",              0x5f: "PR_PARTMOTION",           0x60: "PR_PARAM",
    0x61: "PR_PARAM",                0x62: "PR_TOPINDEX",             0x63: "PR_READONLY",
    0x64: "PR_CURSOR",               0x65: "PR_POSZOOMED",            0x66: "PR_ONPLAYSTART",
    0x67: "PR_PARAM",                0x68: "PR_ONMOUSEIN",            0x69: "PR_ONMAPIN",
    0x6a: "PR_ONMAPOUT",             0x6b: "PR_MAPSOURCE",            0x6c: "PR_AMP",
    0x6d: "PR_WAVELEN",              0x6e: "PR_SCROLLX",              0x6f: "PR_SCROLLY",
    0x70: "PR_FLIPH",                0x71: "PR_FLIPV",                0x72: "PR_ONIDLE",
    0x73: "PR_DISTANCEX",            0x74: "PR_DISTANCEY",            0x75: "PR_CLIPLEFT",
    0x76: "PR_CLIPTOP",              0x77: "PR_CLIPWIDTH",            0x78: "PR_CLIPHEIGHT",
    0x79: "PR_DURATION",             0x7a: "PR_THUMBSOURCE",          0x7b: "PR_BUTTONSOURCE",
    0x7c: "PR_MIN",                  0x7d: "PR_MAX",                  0x7e: "PR_VALUE",
    0x7f: "PR_ORIENTATION",          0x80: "PR_SMALLCHANGE",          0x81: "PR_LARGECHANGE",
    0x82: "PR_MAPTEXT",              0x83: "PR_GLYPHWIDTH",           0x84: "PR_GLYPHHEIGHT",
    0x85: "PR_ZOOMY",                0x86: "PR_CLICKEDSOURCE",        0x87: "PR_ANIPAUSED",
    0x88: "PR_ONHOLD",               0x89: "PR_ONRELEASE",            0x8a: "PR_REVERSE",
    0x8b: "PR_PLAYING",              0x8c: "PR_REWINDONLOAD",         0x8d: "PR_COMPOTYPE",
    0x8e: "PR_FONTSHADOWCOLOR",      0x8f: "PR_FONTBORDER",           0x90: "PR_FONTSHADOW",
    0x91: "PR_ONKEYDOWN",            0x92: "PR_ONKEYUP",              0x93: "PR_ONKEYREPEAT",
    0x94: "PR_HANDLEKEY",            0x95: "PR_ONFOCUSIN",            0x96: "PR_ONFOCUSOUT",
    0x97: "PR_OVERLAY",              0x98: "PR_TAG",                  0x99: "PR_CAPTURELINK",
    0x9a: "PR_FONTHOVERBORDER",      0x9b: "PR_FONTHOVERBORDERCOLOR", 0x9c: "PR_FONTHOVERSHADOW",
    0x9d: "PR_FONTHOVERSHADOWCOLOR", 0x9e: "PR_BARSIZE",              0x9f: "PR_MUTEONLOAD",
    0xa0: "PR_PLUSX",                0xa1: "PR_PLUSY",                0xa2: "PR_CARETHEIGHT",
    0xa3: "PR_REPEATPOS",            0xa4: "PR_BLURSPAN",             0xa5: "PR_BLURDELAY",
    0xa6: "PR_FONTCHANGEABLED",      0xa7: "PR_IMEMODE",              0xa8: "PR_FLOATANGLE",
    0xa9: "PR_FLOATZOOMX",           0xaa: "PR_FLOATZOOMY",           0xab: "PR_CAPMASKLEVEL",
}
properties_inv = {v: k for k, v in properties.items()}

event_opcode_names = {
    0x01: "Char",   0x02: "Align",  0x03: "Return",
    0x04: "Indent", 0x05: "Undent", 0x06: "Event",
    0x07: "Var",    0x09: "Img",    0x0a: "HistChar",
    -1: "String"
}
event_opcode_names_inv = {v: k for k, v in event_opcode_names.items()}


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
    param = 106

    unknown = -1