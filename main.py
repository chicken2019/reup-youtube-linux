import os
import requests
import numpy as np
import time
import subprocess
import json
import re

np.seterr(over='ignore')
key_api = "AIzaSyAdO-hmFHLaRgiARrMRNdpN9RqgYx_ulB4"

pwd = os.getcwd()
pwd = pwd + '/'


def check_exist_chapt(id_series, id_chapt_new, stt_id):
    name_file = stt_id + "/save-data.txt"

    fo = open(name_file, "r")

    lines = fo.readlines()
    # format series:chapt,chapt\n
    for line in lines:
        arr_split = line.split(':')
        if (len(arr_split) > 1):
            series_current = arr_split[0]
            list_chapt_current = arr_split[1].replace('\n', '').split(',')

            if (str(series_current) == str(id_series)):
                if str(id_chapt_new) in list_chapt_current:
                    return False
    fo.close()
    return True


def save_to_file(id_series, id_chapt_new, stt_id):
    name_file = stt_id + "/save-data.txt"

    fo = open(name_file, "r")
    lines = fo.readlines()
    check = True
    i = 0
    len_lines = len(lines)
    n = '\n'
    # format series:chapt,chapt\n
    for line in lines:
        arr_split = line.split(':')
        if (len(arr_split) > 1):
            series_current = arr_split[0]
            list_chapt_current = arr_split[1].replace('\n', '')

            if (i == len_lines - 1):
                n = ''
            if (str(series_current) == str(id_series)):
                list_chapt_current = str(id_series) + ':' + str(list_chapt_current) + ',' + str(id_chapt_new) + n
                lines[i] = list_chapt_current
                check = False
        i = i + 1
    if (check):
        if (len(lines) > 0):
            lines[len(lines) - 1] = lines[len(lines) - 1] + '\n'
        lines.append(str(id_series) + ':' + id_chapt_new)
    fo.close()

    fo = open(name_file, "w")
    fo.writelines(lines)
    fo.close()
    return True


def upload_youtube_and_check_out_number(title, description, tags, file_name, playlist, stt_id):
    stdout = subprocess.check_output(['youtube-upload', '--title=' + str(title) + '', '--tags="' + str(tags) + '"',
                                '--description=' + str(description) + '', '--playlist=' + str(playlist),
                                      '--client-secrets=client_secrets.json',
                                '--credentials-file=' + str(stt_id) + '/credentials.json', str(file_name)])

    #'--thumbnail=' + thumbnail,
    # process = subprocess.Popen(['youtube-upload', '--title="' + str(title) + '"', '--tags="' + str(tags) + '"',
    #                             '--description="' + str(description) + '"', '--client-secrets=' + str(stt_id) + '/client_secrets.json',
    #                             '--credentials-file=' + str(stt_id) + '/credentials.json', str(file_name)],
    #                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # stdout, stderr = process.communicate()
    print(stdout)
    return len(str(stdout)) > 0



def isFirstUpload(stt_id):
    f = open(stt_id + '/credentials.json', 'r')
    lines = f.readlines()
    f.close()
    if(len(lines) == 0):
        return True

    return False


def get_file_upload():
    filelist = os.listdir('input')

    for fichier in filelist:
        if "input" in fichier:
            return fichier

    return False


def get_ffmpeg(file_video, file_ffmpeg, stt_id):
    path_file = 'ffmpeg-files/' + file_ffmpeg
    fo = open(path_file, "r")
    lines = fo.readlines()

    if len(lines) > 0:
        string_process = lines[0]
        string_process = string_process.replace("input.mp4", 'input/' + str(file_video))
        string_process = string_process.replace("output.mp4", "output/" + str(file_video))
        string_process = string_process.replace("temp/hh.png", str(stt_id) + "/hh.png")

        return string_process

    return False


def process_video(file_name, stt_id):
    string_ffmpeg = get_ffmpeg(file_name, 'text2.txt', stt_id)
    os.system(string_ffmpeg)

    return 'output/' + str(file_name)


def get_data_file(stt_id, file_name):
    path_file = str(stt_id) + '/' + file_name + '.txt'
    fo = open(path_file, "r")
    lines = fo.readlines()
    fo.close()
    stt_video = ''

    if len(lines) > 0:
        stt_video = lines[0]

    return stt_video


def update_stt_video(stt_id, stt_video):
    path_file = str(stt_id) + '/stt-video.txt'
    fo = open(path_file, "w")
    fo.write(str(stt_video))
    fo.close()


def replace_name_title(stt_id, stt_video):
    stt_video = get_data_file(stt_id, 'stt-video')
    title = get_data_file(stt_id, 'title')

    return title + ' #' + str(stt_video)


def hanlde(name_title, description, genres, stt_id):
    check = False

    file_name = get_file_upload()
    file_name = str(file_name)

    stt_video = get_data_file(stt_id, 'stt-video')
    stt_video = int(stt_video) + 1

    temp_file_name = str(file_name)
    file_name = process_video(file_name, stt_id)
    name_title = replace_name_title(stt_id, stt_video)
    description = name_title

    playlist = get_data_file(stt_id, 'playlist')

    if file_name:
        print("Uploading...")
        #isFirstUpload(stt_id)
        if isFirstUpload(stt_id):
            os.system('youtube-upload --title="' + str(
                name_title) + '" --description="' + description + '" --tags="' + genres +
                      '" --playlist="' + str(playlist) + '" --client-secrets="client_secrets.json" --credentials-file="' + str(stt_id) +
                      '/credentials.json" ' + str(file_name))

            check = True
        else:
            check = upload_youtube_and_check_out_number(name_title, description, genres, file_name, playlist, stt_id)

    os.remove('input/' + temp_file_name)
    os.remove('output/' + temp_file_name)

    if check:
        update_stt_video(stt_id, stt_video)

    return check


def download_video_from_youtube(id_video):
    number = get_number_video("https://www.youtube.com/watch?v=" + str(id_video))

    if number == False:
        return False

    print("Downloading...")
    url = "youtube-dl -f " + str(number) + " -o 'input/input.%(ext)s' https://www.youtube.com/watch?v=" + str(id_video)
    print(url)
    os.system(url)

    return True


def get_tags(id_video):
    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&key=" + key_api + "&id=" + str(id_video)

    req = requests.get(url)
    items = json.loads(req.content)
    tags = ''

    try:
        tags = items['items'][0]['snippet']['tags']
    except KeyError as e:
        print('I got a KeyError - reason "%s"' % str(e))

    list_tag = ','.join(tags)

    return list_tag


def update_max_video(stt_id):
    stt_video = get_data_file(stt_id, 'max-video')
    stt_video = int(stt_video) - 1

    path_file = str(stt_id) + '/max-video.txt'
    fo = open(path_file, "w")
    fo.write(str(stt_video))
    fo.close()


def get_list_video(channel_id, stt_id):
    print("Get list video..")
    max_result = 50

    url = "https://www.googleapis.com/youtube/v3/activities?part=snippet,contentDetails&key=" \
          + str(key_api) + "&channelId=" + str(channel_id) + "&maxResults=" + str(max_result)

    req = requests.get(url)

    list_item = json.loads(req.content)

    for item in list_item['items']:
        title = item['snippet']['title']
        description = title

        try:
            id_video = item['contentDetails']['upload']['videoId']
        except KeyError:
            id_video = item['contentDetails']['playlistItem']['resourceId']['videoId']

        stt_video = get_data_file(stt_id, 'max-video')

        if check_exist_chapt(channel_id, id_video, stt_id) and int(stt_video) > 0:
            tags = get_tags(id_video)
            check = False
            has_video = download_video_from_youtube(id_video)

            if has_video:
                check = hanlde(title, description, tags, stt_id)
            else:
                save_to_file(channel_id, id_video, stt_id)

            if check:
                save_to_file(channel_id, id_video, stt_id)

                update_max_video(stt_id)

                print("Done")
                time.sleep(150)


def get_source_links(stt_id):
    # read file get arr website avail
    fo = open(stt_id + "/source-links.txt", "r")
    arr_website_avail = []
    lines = fo.readlines()

    for line in lines:
        arr_website_avail.append(line.replace('\n', ''))
    fo.close()
    return arr_website_avail


def get_number_video(url):
    try:
        stdout = subprocess.check_output(['youtube-dl', '-F', url])
        # process = subprocess.Popen(['youtube-dl', url],
        #                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # stdout, stderr = process.communicate()

        arr = str(stdout).split('\\n')

        audio = ''

        for item in arr:
            if 'm4a' in item:
                audio = item.split(' ')[0]

        for item in arr:
            if '720p' in item and 'mp4' in item:
                return str(item.split(' ')[0]) + '+' + str(audio)

        for item in arr:
            if '480p' in item and 'mp4' in item:
                return str(item.split(' ')[0]) + '+' + str(audio)

        for item in arr:
            if '360p' in item and 'mp4' in item:
                return str(item.split(' ')[0]) + '+' + str(audio)

        for item in arr:
            if '240p' in item and 'mp4' in item:
                return str(item.split(' ')[0]) + '+' + str(audio)
    except:
        return False

    return True


if __name__ == '__main__':
    stt_id = str(input("Enter id: "))
    arr_website_avail = get_source_links(stt_id)

    for item_web in arr_website_avail:
        get_list_video(item_web, stt_id)
