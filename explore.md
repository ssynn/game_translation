
# YU-ris
幸仁 09 00 00 00 
ver 290:
    4Byte length 4Byte offset
    1. 0x14 4c6aa 0xfa
    2. 0x2c 4c6be 0x10e
    3. 0x50       0x13a
    4. 0x56       0x18a
    5. 0x54       0x1e0
    6. 0x22

    name 
    1. 0x08 0xab

# .aos
1. 表示文字列が不正です
2. 初回起動時はディスクが必要です。「風雷戦姫\u3000神夢」のオリジナルディスクを入れてください。

所有的中文都只拿了第一个字节
在复制完字符串后，还会对已经字符串继续处理

4BFBE0 记录文字地址
4bfee0 记录人名
sub_4541F0 
0. 2
1. sub_408600 应该是主循环
   1. sub_4356D0
      1. sub_4541F0 4568BE对上述地址写入文本，似乎是指令解释函数
         1. sub_453E80 hook后导致log不显示,现在几乎可以确定是这个函数负责记录log
            1. sub_458200
         2. sub_45C3F0
         3. sub_466b4a
   2. sub_435CD0
   3. #40875C sub_440D50() 这里会忽略人名，只输出对话，并将文字显示到画面上
      1. sub_442F20@<eax>(signed __int16 *a1@<eax>, unsigned __int8 *text@<edi>)
      2. sub_435180@<eax>(unsigned __int8 *text@<eax>, int a2@<ecx>, int a3, int a4)
      3. sub_410050@<eax>(int *a1@<edi>, int uchar, void *a3, int a4)
   4. sub_401EE0


## 选择支
[*(*4BFA84+4)+0x120]
1. 0
2. sub_42B0E0 int __thiscall sub_42B0E0(_DWORD *this)
3. sub_42B340 int __fastcall sub_42B340(int *a1, int a2)
4. sub_42CDE0 int __thiscall sub_42CDE0(_DWORD *this)
5. sub_42E0E0 int __usercall sub_42E0E0@<eax>(_DWORD *a1@<esi>)
6. sub_42E480 int __usercall sub_42E480@<eax>(_DWORD *a1@<eax>)
7. sub_42E950 int __usercall sub_42E950@<eax>(_DWORD *a1@<eax>)
8. sub_42F180 signed int __stdcall sub_42F180(_DWORD *a1)
9. sub_45DB00 signed int __cdecl sub_45DB00(int a1, int a2)
10. sub_4101E0 int __userpurge sub_4101E0@<eax>(void *text@<ecx>, int result@<eax>, int a3, int a4, int a5, int a6)
11. sub_410050
12. sub_40FDA0
13. sub_40F5A0
14. textouta

让exe基址固定
    createfontindirect 0x80 -> 0x86 三处最后一处决定文本
    textouta前           cmp al, 0xa0 -> cmp al,0xfe
    8179->A1BE
    817A->A1BF
    55 8B EC 83 EC 64 修改        cmp al, 0xa0 -> cmp al,0xfe

    ## 搜索特征AOS2
    1. 函数
        1. log函数 83 E4 F8 81 EC BC 010 00
        2. 选择支HOOK点 53 56 57 68 00 00 04 00 E8
    2. 边界
        1. 选择支边界检查 55 8B EC 83 EC 64
        2. 文字边界检查 8A 03 57 33 FF 3C 81
    3. 全局变量
        1. 文本 下面第二个 FF D5 68 00 00 01 00 6A 08 50 FF D6
        2. 人��� 下面  53 53 53 53 53 53 B9 02 00 00 00 E8
        3. 选择支 上面 83 C4 08 33 C9 39 37 74
    4. 字符集 88 5E 57 2B D0 8D 64 24 




# .gsc:
1. 0-4: 11fd1 文件大小
2. 4-8：24 head大小
3. 8-12：8c32 part2 大小
4. 12-16：c9c part3 大小
5. 16-20：4 part4 大小
6. 21-24：86c1 文本大小
7. 第一个文本地址：98f3


# med
1. 0-4 MED0
2. 4-6 entry_length
3. 6-8 entry_count

40e6f8 读取entry
\*(_DWORD \*)(dword_76CE14[\*(_DWORD \*)arglist] + 4 \* i) = *(_DWORD *)(handle + entry_offset + entry_length - 12);// int32 1
\*(_DWORD \*)(dword_76CDFC[\*(_DWORD \*)arglist] + 4 \* i) = *(_DWORD *)(entry_offset + handle + entry_length - 8);// int32 length
\*(_DWORD \*)(dword_76CDF0[\*(_DWORD \*)arglist] + 4 \* i) = *(_DWORD *)(handle + entry_offset + entry_length - 4);// int32 offset

光翼战姬1
「………………て……きて……
声が聞こえた。
聞き慣れた声が。

GB2312_CHARSET = 134
SHIFTJIS_CHARSET = 128


## 光翼战姬文字显示
0. 2
1. sub_42EAA8
2. sub_42F6D4

* 字体缓冲基址 *0x757A84
* 0x8140 12D7E004 +7E000
* 0x95B7 1377CB84 +A7CB80‬
* 偏移计算公式 ptr + 0xC0 * 0xA80 + (_wchar[1] - 0x40 + 0xBD * wchar_l[0] ) * 0xA80
* 字符在文件中的偏移要减去0x80才是在内存中的偏移
* 汉字计算方式 GBK ptr + 0xC0 * 0xA80 + (_wchar[1] - 0x40 + 0xBF * (_wchar[0]-0x81) ) * 0x540
* 汉字计算方式 GB2312 ptr + 0xC0 * 0xA80 + (_wchar[1] - 0x40 + 0x5E * (_wchar[0]-0xA0) ) * 0x1500
* 需要的汉字范围 0x8140-0xF7FE 第二字节从40开始 排除0x7f 每组BF个
* gb2312 编码范围 0xA0A0-0xF7FE 0xAA-0xAF为空   每组0x5E个
* 汉字字模生成

## TODO
1. 搞懂字符表格式 需要先解密，解密后4个字节表示一个像素，表示方式为RGBA
2. 生成字符表
3. 内存替换字符表
4. 改写字符指针计算方式

# RPS/YB图像
0-2：YB
2  ：FLAG
3  ：BPP（Byte）
4-8：PackedSize
12-14：width
14-16：height


# .MES
0-4 count
offset
data

白い肌をあらわにした彼女が、恥ずかしそうにブランケットの裾を引き寄せ身をすくめた。


# NEKOSDK
每块大小 
ea 开头
u32 长度
05 00 00 00 64 00 00 00 后 c0 为文本区

「 …これが新しい俺の家か』
まだ場所によっては雪の残る三月。

# .snl
0-4 0000
4-6 len unk1
6-8 len unk2
8-12 len str

每个字符串后有0000

# SILKY
D31000
ゲームがインストールされていません。実行するためには、ゲームをインストールして下さい。

# ANIM

## this
0-4 ?
4-8 句柄
8-12 文件长度
12-16 ？
16-20 数据地址

sub_45E720 应该在解密
## sce
0-4 00 00 00 01
4-20 key

## sce decoded
0-4 unk
4-8 str address
字符串以00结尾，长度似乎不影响结果

## exe
logfont -> createfontindirecta -> getglyphoutline

## 场景
やましい気持ちを隠しながら再びの食事
[181130][ANIM.teamMM] 僕ママ×友ママ交姦ハメップ性活
拡大·縮小は、カーソルの位置を基準にします。ボタンでの拡大·縮小は画面の中心が基準になります。
flow 【001 僕とエータと】·いつものようにエータが遊びに来た。エータはお母さんが気になる様子。そして今度は僕がエータの家に遊びに行って…
spFlowChartButton
extra【回想01 拓己:逃げ出した先でモミモミコスコス】二人の行為を見て飛び出した先で、おばさんと出会う。感極まった僕はおばさんのおっぱいを…。

* *
* 
* 402260
* 402080
* 4016f0


# LiveMaker

## File
(
    "version" / LsbVersionValidator(construct.Int32ul),
    "flags" / construct.Byte,
    "command_count" / construct.Int32ul,
    "param_stream_size" / construct.Int32ul,
    "command_params"
    / construct.Array(
        construct.this.command_count, _ParamStreamAdapter(construct.Bytes(construct.this.param_stream_size)),
    ),
    "commands" / construct.PrefixedArray(construct.Int32ul, construct.Select(*_command_structs)),
)

* version            0x0-0x4
* flags              0x4-0x5
* command_count      0x5-0x9
* param_stream_size  0x9-0xD
* command_params     0xD-
* commands           



## Command
(
    "type" / construct.Const(cls.type.name, construct.Enum(construct.Byte, CommandType)),
    "Indent" / construct.Int32ul,
    "Mute" / construct.Flag,
    "NotUpdate" / construct.Flag,
    "LineNo" / construct.Int32ul, construct.Embedded(cls._struct_fields)
)
 

## TextIns
(
   "Text" / construct.Prefixed(construct.Int32ul, TpWord._struct()),
   "Target" / LiveParser._struct(),
   "Hist" / LiveParser._struct(),
   "Wait" / LiveParser._struct(),
   "StopEvent" / construct.If(construct.this._._.version > 0x6A, LiveParser._struct()),
)

## TpWord
(
   "signature" / construct.Const(b"TpWord"),
   "version" / _TpWordVersionAdapter(construct.Bytes(3)),
   "decorators" / construct.PrefixedArray(construct.Int32ul, TDecorate._struct()),
   "conditions" / construct.If(construct.this.version >= 104, construct.PrefixedArray(construct.Int32ul, TWdCondition._struct()),),
   "links" / construct.If(construct.this.version >= 105, construct.PrefixedArray(construct.Int32ul, TWdLink._struct()),),
   "body" / construct.PrefixedArray(construct.Int32ul, construct.Select(*select_subcons))
)

## TDecorate
(
    "count" / construct.Int32ul,
    "unk2" / construct.Int32ul,
    "unk3" / construct.Int32ul,
    "unk4" / construct.Int32ul,
    "unk5" / construct.Byte,
    "unk6" / construct.Byte,
    "unk7" / construct.IfThenElse(construct.this._._.version < 100, construct.Byte, construct.Int32ul),
    "unk8" / construct.PascalString(construct.Int32ul, "cp932"),
    "unk9" / construct.PascalString(construct.Int32ul, "cp932"),
    "unk10" / construct.If(construct.this._._.version >= 100, construct.Int32ul,),
    "unk11" / construct.If(construct.this._._.version >= 100, construct.Int32ul,),
)

## TWdCondition
(
    "count" / construct.Int32ul, 
    "target" / construct.PascalString(construct.Int32ul, "cp932"),
)

## TWdLink
(
    "count" / construct.Int32ul,
    "event" / construct.PascalString(construct.Int32ul, "cp932"),
    "unk3" / construct.PascalString(construct.Int32ul, "cp932"),
)

## TWdChar
(
   "type" / construct.Const(b"\x01"),
   "condition" / construct.If(construct.this._._.version >= 104, construct.Int32sl),
   "link_name" / construct.If(construct.this._._.version < 105, construct.PascalString(constructInt32ul, "cp932")),
   "link" / construct.If(construct.this._._.version >= 105, construct.Int32sl),
   "text_speed" / construct.Int32ul,
   "ch" / _TWdCharAdapter(construct.Int16ul),
   "decorator" / construct.Int32sl,
)

## TWdOpeDiv
(
   "type" / construct.Const(b"\x02"),
   "condition" / construct.If(construct.this._._.version >= 104, construct.Int32sl),
   "align" / construct.Byte,
   "padleft" / construct.If(construct.this._._.version >= 105, construct.Int32sl),
   "padright" / construct.If(construct.this._._.version >= 105, construct.Int32sl),
   "noheight" / construct.If(construct.this._._.version >= 105, construct.Byte),

)

## TWdOpeReturn
(
   "type" / construct.Const(b"\x03"),
   "condition"  / construct.If(construct.this._._.version >= 104, construct.Int32sl),
   "break_type" / construct.Byte
)

## TWdOpeIndent
(
   "type" / construct.Const(b"\x04"),
   "condition" / construct.If(construct.this._._.version >= 104, construct.Int32sl),
)

## TWdOpeUndent
(
   "type" / construct.Const(b"\x05"),
   "condition" / construct.If(construct.this._._.version >= 104, construct.Int32sl),
)

## TWdOpeEvent
(
   "type" / construct.Const(b"\x06"),
   "condition" / construct.If(construct.this._._.version >= 104, construct.Int32sl),
   "event" / construct.PascalString(construct.Int32ul, "cp932"),
)


## TWdOpeVar
(
   "type" / construct.Const(b"\x07"),
   "condition" / construct.If(construct.this._._.version >= 104, construct.Int32sl),
   "decorator" / construct.Int32sl,
   "unk3" / construct.If(construct.this._._.version >= 100, construct.Int32ul),
   "link_name" / construct.If(100 <= construct.this._._.version < 105, construct.PascalString(construct.Int32ul, "cp932")),
   "link" / construct.If(construct.this._._.version >= 105, construct.Int32sl),
   "var_name_params" / construct.If(construct.this._._.version < 102, LiveParser._struct()),
   "var_name" / construct.If(construct.this._._.version >= 102, construct.PascalString(construct.Int32ul, "cp932")),
)

## TWdImg
(
   "type" / construct.Const(b"\x09"),
   "condition" / construct.If(construct.this._._.version >= 104, construct.Int32sl),
   "link_name" / construct.If(construct.this._._.version < 105, construct.PascalString(constructInt32ul, "cp932")),
   "link" / construct.If(construct.this._._.version >= 105, construct.Int32sl),
   "text_speed" / construct.Int32ul,
   "src" / construct.PascalString(construct.Int32ul, "cp932"),
   "align" / construct.Byte,
   "hoversrc" / construct.If(construct.this._._.version >= 103, construct.PascalString(construct.Int32ul, "cp932")),
   "mgnleft" / construct.If(construct.this._._.version >= 105, construct.Int32sl,),
   "mgnright" / construct.If(construct.this._._.version >= 105, construct.Int32sl,),
   "mgntop" / construct.If(construct.this._._.version >= 105, construct.Int32sl,),
   "mgnbottom" / construct.If(construct.this._._.version >= 105, construct.Int32sl,),
   "downsrc" / construct.If(construct.this._._.version >= 105, construct.PascalString(construct.Int32ul, "cp932")),
)

## OpeData
(
   "type" / construct.Enum(construct.Byte, OpeDataType),
   "name" / construct.PascalString(construct.Int32ul, "cp932"),
   "count" / construct.Int32ul,
   "func" / construct.Switch(construct.this.type, {"Func": construct.Enum(construct.Byte, OpeFuncType)}),
   "operands" / construct.Array(construct.this.count, Param._struct()),
)

## TWdOpeHistChar
(
   "type" / construct.Const(b"\x0A"),
   "condition" / construct.If(construct.this._._.version >= 104, construct.Int32sl),
   "decorator" / construct.Int32sl,
   "unk3" / construct.If(construct.this._._.version >= 100, construct.Int32ul),
   "link_name" / construct.If(100 <= construct.this._._.version < 105, construct.PascalString(construct.Int32ul, "cp932")),
   "link" / construct.If(construct.this._._.version >= 105, construct.Int32sl),
   "var_name_params" / construct.If(construct.this._._.version < 102, LiveParser._struct()),
   "var_name" / construct.If(construct.this._._.version >= 102, construct.PascalString(construct.Int32ul, "cp932")),
)

* type         0x00-0x01   0x14
* Indent       0x01-0x05   0x0000
* Mute         0x05-0x06   
* NotUpdate    0x06-0x07
* LineNo       0x07-0x0B
* size         0x0B-0x0F      
* signature    0x0F-0x15   TpWord
* version      0x15-0x18
* decorators   0x
* conditions
* links
* body

## 需要提取
1. 人名NAMELABEL
   (
      "type" / construct.Const(b"\x06"),
      "condition"  / construct.If(construct.this._._.version >= 104, construct.Int32sl),
      "size" / construct.Int32ul,
      "name" / construct.Const(b"NAMELABEL\r\n"),
      "vlaue" / onstruct.PascalString(construct.Int32ul-0xB, "cp932")
   )  
2. 文本 01 00 00 00 00 00 00 00 00 32 00 00 00 42 81 00 00 00 00
   (
      "type" / construct.Const(b"\x01"),
      "condition" / construct.If(construct.this._._.version >= 104, construct.Int32sl),
      "link_name" / construct.If(construct.this._._.version < 105, construct.PascalString(constructInt32ul, "cp932")),
      "link" / construct.If(construct.this._._.version >= 105, construct.Int32sl),
      "text_speed" / construct.Int32ul,
      "ch" / _TWdCharAdapter(construct.Int16ul),
      "decorator" / construct.Int32sl,
   )
3. <PG> 03 00 00 00 00 01
   (
      "type" / construct.Const(b"\x03"),
      "condition"  / construct.If(construct.this._._.version >= 104, construct.Int32sl),
      "break_type" / construct.Const(b"\x01"),
   )
4. <BR> 03 00 00 00 00 00
   (
      "type" / construct.Const(b"\x03"),
      "condition"  / construct.If(construct.this._._.version >= 104, construct.Int32sl),
      "break_type" / construct.Const(b"\x00"),
   )
5. <STYLE></STYLE>  文本的decorator=0x01