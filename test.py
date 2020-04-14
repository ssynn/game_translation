import json
import re
# with open('E:/Tools/VNR/jp_chs_split.json', 'r') as f:
#     jp_chs = json.loads(f.read())

a = '【亮介】あ、お疲れさまですゲンさん。'

a = a.replace('\n', '')
a = a.replace('　', '')
print re.