import re
import base64
import traceback
import json
from datetime import datetime, timedelta

START_COMMENT = '<!--START:starList-->'
END_COMMENT = '<!--END:starList-->'
listReg = f"{START_COMMENT}[\\s\\S]+{END_COMMENT}"


def readJsonFile(path):
    # print("开始")
    start = 0
#     markdown = '| 序号 |<div width="250px"> 仓库 </div>|<div width="900px"> 描述 </div>| 更新时间 | Star | Fork | 语言 | 许可证 |\n' + \
#                 '|:----:| ---- | ---- | ---- | ---- | ---- | ---- | ---- |\n'
    markdown = '| 序号 | 仓库 | 描述 | Star | 语言 |\n' + \
                '|:----:|:----:| ---- |:----:|:----:|\n'
    with open(path, "r", encoding='utf-8') as f:
        starList = list(f.readlines())
        for l in starList:
            for obj in json.loads(l):
                updated_at = datetime.strptime(obj["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
                is_hot = (datetime.utcnow() - updated_at).days < 3
                
                name_display = obj["name"]
                if is_hot:
                    name_display = f"🔥 {name_display}"
                start += 1
                name = ''
                license = ''
                desc = ''
                lang = ''
                if obj["name"] == None:
                    name = '无'
                elif len(obj["name"]) > 25:
                    name = obj["name"][0:25] + '...'
                else:
                    name = obj["name"]    
                if obj["description"] == None:
                    desc = '无'
                elif len(obj["description"]) > 200:
                    desc = obj["description"][0:200:] + '...'
                else:
                    desc = obj["description"][0:200:]
                star = "https://img.shields.io/github/stars/" + obj["name"] + "/" + "" + "?style=social"
                if obj["language"] == None:
                    lang = '无'
                else:
                    lang = obj["language"]
                if obj["license"] == None:
                    license = '无'
                else:
                    license = obj["license"]["name"]
                # | 序号 | 仓库 | 描述 | 更新时间 | Star | Fork | 语言 | 许可证 |
#                 markdown += '| ' + str(start) + ' | ' + '[' + obj["name"] + '](' + obj["html_url"] + ')' + ' | ' + desc.replace('|','').replace('\\', '') + ' | ' + \
#                     obj["updated_at"][0:9] + ' | ' + str(obj["stargazers_count"]) + ' | ' + str(obj["forks_count"]) + ' | ' + \
#                     lang + ' | ' + license + ' |\n'
                markdown += '| ' + str(start) + ' | ' + '[' + obj["name"][0:25] + '](' + obj["html_url"] + ')' + ' | ' + desc.replace('|','').replace('\\', '') + ' | ' + \
                    str(obj["stargazers_count"]) + ' | ' + lang + ' |\n'
    f.close()
    return markdown


def decode_readme(data: str):
    '''Decode the contents of old readme'''
    decoded_bytes = base64.b64decode(data)
    return str(decoded_bytes, 'utf-8')


def generate_new_readme(stats: str, readme: str):
    '''Generate a new Readme.md'''
    star_list_in_readme = f"{START_COMMENT}\n{stats}\n{END_COMMENT}"
    return re.sub(listReg, star_list_in_readme, readme)


if __name__ == '__main__':
    try:
        contents = ''
        with open('README.md', encoding='utf-8') as f:
            contents = str(f.readlines())
        f.close()
        markdown = readJsonFile('list.json')
        # rdmd = decode_readme(contents)
        if markdown !=  None:
            new_readme = generate_new_readme(stats=markdown, readme=contents)
            print(new_readme)
            print(type(new_readme))
            if new_readme != '':
                try:
                    with open('README.md', "w+", encoding='utf-8') as f:
                        f.writelines(new_readme.strip('[\'').strip('\']'))
                except:
                    print("写入README失败！")
                print("Readme updated")
    except Exception as e:
        traceback.print_exc()
        print("Exception Occurred " + str(e))
