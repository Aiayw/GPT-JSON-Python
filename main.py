import http.client
import hashlib
import urllib
import random
import json
import chardet

def translate(file_path):
    # 百度appid和密钥需要通过注册百度【翻译开放平台】账号后获得
    appid = ''  # 填写你的appid
    secretKey = ''  # 填写你的密钥

    fromLang = 'en'  # 原文语种
    toLang = 'zh'  # 译文语种
    salt = random.randint(32768, 65536)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = json.load(f)

    count = 0  # 计数器

    def translate_value(value):
        nonlocal count  # 使用nonlocal关键字引用外层函数变量
        if isinstance(value, str):
            sign = appid + value + str(salt) + secretKey
            sign = hashlib.md5(sign.encode()).hexdigest()

            url = '/api/trans/vip/translate'
            url = url + '?appid=' + appid + '&q=' + urllib.parse.quote(value) + '&from=' + fromLang + \
                '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

            try:
                httpClient = http.client.HTTPConnection('fanyi-api.baidu.com')
                httpClient.request('GET', url)
                response = httpClient.getresponse()
                result_all = response.read().decode("utf-8")
                result = json.loads(result_all)
                translated_value = result['trans_result'][0]['dst']
            except Exception as e:
                print(e)
                translated_value = value
            count += 1  # 计数器加1
            print(f"已翻译{count}/{total}个字符串值，完成进度：{count/total:.1%}")
            return translated_value
        elif isinstance(value, dict):
            return {k: translate_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [translate_value(v) for v in value]
        else:
            return value

    total = count_json_str(content)  # 统计需要翻译的字符串值的总数
    trans_content = translate_value(content)

    result_file_path = file_path.replace('.json', '_zh.json')
    with open(result_file_path, 'w', encoding='utf-8') as f:
        json.dump(trans_content, f, ensure_ascii=False, indent=2)

def count_json_str(obj):
    count = 0
    if isinstance(obj, str):
        return 1
    elif isinstance(obj, dict):
        for k, v in obj.items():
            count += count_json_str(k)
            count += count_json_str(v)
    elif isinstance(obj, list):
        for v in obj:
            count += count_json_str(v)
    return count

if __name__ == '__main__':
    file_path = 'example.json'
    translate(file_path)