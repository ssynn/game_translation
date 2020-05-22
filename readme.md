# 文本翻译程序

## 功能
* 把需要翻译的文件放入input文件夹
* 输出的结果在output文件夹
* 中间的结果在intermediate_file文件夹，主要是日文-中文的字典


# YU-ris
幸仁 09 00 00 00 

# .aos
1. 表示文字列が不正です
2. 初回起動時はディスクが必要です。「風雷戦姫\u3000神夢」のオリジナルディスクを入れてください。

所有的中文都只拿了第一个字节
在复制完字符串后，还会对已经字符串继续处理

## 即指
x32dbg EC1000
IDA    401000


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

80- a0