import sys

import requests
import json
import time
import subprocess
from urllib.parse import urlunparse
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_tiktok_live_data_from_pc(user_agent, pc_live_url):
    headers = {
        'User-Agent': user_agent
    }

    response = requests.get(pc_live_url, headers=headers)
    html_str = response.text

    soup = BeautifulSoup(html_str, 'html.parser')
    script = soup.find('script', id='SIGI_STATE', type='application/json')

    json_data = {}
    target_str = script.string.strip()
    if target_str is not None and "liveRoomUserInfo" in target_str:
        jsonObj = json.loads(target_str)

        if (('LiveRoom' not in jsonObj) or
                ('liveRoomUserInfo' not in jsonObj['LiveRoom']) or
                ('liveRoom' not in jsonObj['LiveRoom']['liveRoomUserInfo']) or
                'status' not in jsonObj['LiveRoom']['liveRoomUserInfo']['liveRoom']):
            return json_data

        print(target_str)

        live_status = jsonObj['LiveRoom']['liveRoomUserInfo']['liveRoom']['status']
        if live_status == 4:
            json_data['status'] = live_status
            print("直播已结束")
            return json_data

        stream_data = jsonObj['LiveRoom']['liveRoomUserInfo']['liveRoom']['streamData']['pull_data']['stream_data']
        print("origin stream_data: \n", stream_data)

        stream_data_jo = json.loads(stream_data)
        print("stream_data_jo:\n", stream_data)
        stream_data_url_data = stream_data_jo['data']

        origin_stream_url = stream_data_url_data['origin']['main']['flv']

        json_data['status'] = live_status
        json_data['record_url'] = origin_stream_url
        json_data['user_count'] = jsonObj['LiveRoom']['liveRoomUserInfo']['liveRoom']['liveRoomStats']['userCount']
        json_data['uniqueId'] = jsonObj['LiveRoom']['liveRoomUserInfo']['user']['uniqueId']
        json_data['nick_name'] = jsonObj['LiveRoom']['liveRoomUserInfo']['user']['nickname']
        json_data['room_title'] = jsonObj['LiveRoom']['liveRoomUserInfo']['liveRoom']['title']

        json_data['nick_avatar'] = jsonObj['LiveRoom']['liveRoomUserInfo']['user']['avatarLarger']

    return json_data


def save_video_slice(user_agent, record_url):
    print("record_url: \n", record_url)

    analyzeduration = "20000000"
    probesize = "10000000"
    bufsize = "8000k"
    max_muxing_queue_size = "1024"

    ffmpeg_command = [
        'ffmpeg', "-y",
        "-v", "verbose",
        "-rw_timeout", "30000000",
        "-loglevel", "error",
        "-hide_banner",
        "-user_agent", user_agent,
        "-thread_queue_size", "1024",
        "-analyzeduration", analyzeduration,
        "-probesize", probesize,
        "-fflags", "+discardcorrupt",
        "-i", record_url,
        "-bufsize", bufsize,
        "-sn", "-dn",
        "-reconnect_delay_max", "60",
        "-reconnect_streamed", "-reconnect_at_eof",
        "-max_muxing_queue_size", max_muxing_queue_size,
        "-correct_ts_overflow", "1",
    ]

    now = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    save_file_path = f"{now}_%03d.mp4"
    command = [
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0",
        "-f", "segment",
        "-segment_time", "20",
        "-segment_time_delta", "0.01",
        "-segment_format", "mp4",
        "-reset_timestamps", "1",
        "-pix_fmt", "yuv420p",
        save_file_path,
    ]

    ffmpeg_command.extend(command)
    print("开始拉取数据流...")

    result = ' '.join(ffmpeg_command)
    print("command: \n", result)
    _output = subprocess.check_output(ffmpeg_command, stderr=subprocess.STDOUT)
    # 以下代码理论上不会执行
    print(_output)


if __name__ == '__main__':
    url = input("tiktok直播的链接地址: ")
    parsed_url = urlparse(url)
    url_without_query = urlunparse(parsed_url._replace(query=""))

    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

    live_data = get_tiktok_live_data_from_pc(user_agent, url_without_query)

    print("live_data:")
    print(json.dumps(live_data, indent=4, ensure_ascii=False))

    if live_data['status'] == 4:
        # 直播已结束，直接退出
        sys.exit(-1)

    # 获取直播流并保存到本地目录
    save_video_slice(user_agent, live_data['record_url'])
