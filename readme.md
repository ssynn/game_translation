# 一个用于把游戏封包内的文本抽取、翻译、替换的项目

## 功能
* 把需要翻译的文件放入input文件夹
* 输出的结果在output文件夹
* 中间的结果在intermediate_file文件夹，主要是日文-中文的字典

## 使用说明
* 函数使用方式参考test_py3.py
* ipynb内有翻译流程使用到的函数

## 流程说明
1. 打开ipynb
2. 运行第一个代码块，加载需要的模块和建立需要的三个文件夹
3. 抽取文本，如果input文件夹内是明文脚本，则使用第二个代码块抽取文本，对于特殊格式的文本自己修改get_scenario_from_origin函数
   * 如果脚本经过编译，则调用public_function内部的函数抽取，参考test_py3.py
4. 创建翻译字典
5. 检查翻译字典
6. 翻译字典，delete_func可以对翻译的文本进行简单的处理再提交给服务器翻译，翻译接口需要自己实现，baidufanyi、tencentfanyi我没有给出
7. 检查是否还有没翻译的文本
8. 创建中日对照文件在 intermediate_file/contrast.txt内
9. 替换文本，如果是明文脚本则直接使用ipynb内的替换文本代码块替换
   * 编译过的脚本使用public_function内部的函数抽取，参考test_py3.py

## 支持的引擎
* XFL
* LIVEMAKER (即将支持)
* YU_RIS
* PAC (有BUG)
* NEKOSDK
* SILKY
* MED
* ANIM
* Lilim
* RPM
* NScript

## 注意
* 只测试过我玩过的游戏
* 应该有大量的BUG
* 代码写的很随意
