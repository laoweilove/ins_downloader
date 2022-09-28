import httpx
import pyaria2
import json
import re
import time
import logging
from tqdm import tqdm
import yaml

LOGO = '''

 _                     _                       _                    _               
(_)                   | |                     | |                  | |              
 _  ____    ___     _ | |  ___   _ _ _  ____  | |  ___    ____   _ | |  ____   ____ 
| ||  _ \  /___)   / || | / _ \ | | | ||  _ \ | | / _ \  / _  | / || | / _  ) / ___)
| || | | ||___ |  ( (_| || |_| || | | || | | || || |_| |( ( | |( (_| |( (/ / | |    
|_||_| |_|(___/    \____| \___/  \____||_| |_||_| \___/  \_||_| \____| \____)|_|    
                                                                                    

                                                                     by laowei
'''

rpc = pyaria2.Aria2RPC()

config_file = open("config.yaml")
config = yaml.load(config_file,Loader=yaml.Loader)
cookie = config['cookie']
app_id = config['app_id']
user_agent = config['user_agent']
proxy = config['proxy']

h = {
    'cookie': cookie,
    'user-agent': user_agent,
    'x-ig-app-id': app_id,
}
res = httpx.Client(http2=True, proxies=proxy, headers=h)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logfile = './log.txt'
file_handler = logging.FileHandler(logfile, mode='a')
file_handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def download(s, name):
    option = {'http-proxy': 'http://127.0.0.1:7890', 'https-proxy': 'https://127.0.0.1:7890',
              'out': f'ins/{v_name}/{name}'}
    rpc.addUri([s], option)


def get_start(username):
    url = f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}'
    s = res.get(url).json()['data']['user']
    x = s['edge_owner_to_timeline_media']['page_info']
    return x['end_cursor'], x['has_next_page'], s['id']


def get_after(user_id, end_cursor):
    table = {"id": user_id, "first": 50, "after": end_cursor}
    url = f'https://www.instagram.com/graphql/query/?query_hash=69cba40317214236af40e7efa697781d&variables={json.dumps(table)}'
    s = res.get(url).json()['data']['user']['edge_owner_to_timeline_media']
    for i in tqdm(s['edges'], colour="GREEN", desc="detail"):
        get_detail(i['node'])

    return s['page_info']['end_cursor'], s['page_info']['has_next_page']


def get_before(user_id, end_cursor):
    table = {"id": user_id, "first": 50, "before": end_cursor}
    url = f'https://www.instagram.com/graphql/query/?query_hash=69cba40317214236af40e7efa697781d&variables={json.dumps(table)}'
    s = res.get(url).json()['data']['user']['edge_owner_to_timeline_media']
    for i in tqdm(s['edges'][:-1], colour="GREEN", desc="detail"):
        get_detail(i['node'])


def get_video(s, name):
    video_url = s['video_url']
    download(video_url, name + '.mp4')


def get_pic(s, name):
    pic_url = s['display_resources'][-1]['src']
    download(pic_url, name + '.jpg')


def get_detail(s):
    try:
        text = re.sub('https://\S+', '',
                      s['edge_media_to_caption']['edges'][0]['node']['text'].replace("\n", "").replace(":",
                                                                                                       "").replace(
                          "\'", "").replace('\"', '').replace('/', ''))
    except Exception as err:
        logger.info(err)
        text = f'{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(s["taken_at_timestamp"]))}-No-{s["id"]}'

    if len(text) > 100 or len(text) < 5:
        name = f'{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(s["taken_at_timestamp"]))}-No-{s["id"]}'
    else:
        name = text

    if s['is_video']:
        get_video(s, name)
    else:
        try:
            pics = s['edge_sidecar_to_children']['edges']
            for i, j in enumerate(pics):
                get_pic(j['node'], f'{name}-{i}')
        except Exception as e:
            logger.info(e)
            get_pic(s, name)


def get_all(username):
    end_cursor, has_next_page, user_id = get_start(username)
    get_before(user_id, end_cursor)
    while has_next_page:
        end_cursor, has_next_page = get_after(user_id, end_cursor)
        logger.info(end_cursor)


if __name__ == '__main__':
    print(LOGO)
    v_name = input('输入要下载的账号\n')

    get_all(v_name)
