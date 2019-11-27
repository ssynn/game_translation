# 汉化程序入口
# 首先查看是否有三个必要文件夹

# 读入input内的文件
# 提取所有日文到中间jp.txt
# 生产需要翻译日文的空value字典, 保存到jp-chs.json
# 把jp-chs.json字典使用翻译君翻译，翻译失败的写入failed.txt
# 把input内所有日文文件使用jp-chs.json翻译写入output.txt，翻译失败的写入failed.txt
# 产生中日对照文件


if __name__ == "__main__":
    ...