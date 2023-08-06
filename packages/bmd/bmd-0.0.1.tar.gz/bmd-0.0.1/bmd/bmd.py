"""

    bmd
    ---------------
    Baidu 320k Music Downloader

    :license: MIT, see LICENSE for more details.
"""


import argparse
import glob
import logging
import multiprocessing
import os
import os.path
import requests
import shutil
import threading
import uuid

MUSIC_INFO_URL = "http://play.baidu.com/data/music/songlink"

logging.basicConfig(format="%(asctime)s[%(process)d] %(message)s",
                    level=logging.INFO)
logger = logging.getLogger('bmd')

logging.getLogger("requests").setLevel(logging.ERROR)


class Worker(threading.Thread):
    """
    worker thread for downloading music data chunk
    """
    def __init__(self, rng, song, uid):
        self._range = rng
        self._song = song
        self._uid = uid

        super(Worker, self).__init__()

    def run(self):
        headers = {
            'Range': 'bytes={}-{}'.format(*self._range)
        }
        res = requests.get(self._song["song_link"], headers=headers)

        i, buf = 0, []
        with open("part-{}-{}".format(self._uid, self._range[0]), 'wb') as f:
            for chunk in res.iter_content(1024):
                buf.append(chunk)
                i += len(chunk)

                if i >= 524288:
                    f.write(b''.join(buf))
                    i, buf = 0, []
            if buf:
                f.write(b''.join(buf))


def music_info(songid):
    """
    Get music info from baidu music api
    """
    if isinstance(songid, list):
        songid = ','.join(songid)
    data = {
        "hq": 1,
        "songIds": songid
    }
    res = requests.post(MUSIC_INFO_URL, data=data)
    info = res.json()
    music_data = info["data"]

    songs = []
    for song in music_data["songList"]:
        song_link, size = _song_link(song, music_data["xcode"])
        songs.append({
            "name": song["songName"],
            "singer": song["artistName"],
            "lrc_link": song["lrcLink"],
            "song_link": song_link,
            "size": size
        })
    return songs


def download_music(song, thread_num=4):
    """
    process for downing music with multiple threads
    """
    filename = "{}.mp3".format(song["name"])

    if os.path.exists(filename):
        os.remove(filename)

    part = int(song["size"] / thread_num)
    if part <= 1024:
        thread_num = 1

    _id = uuid.uuid4().hex

    logger.info("downloading '{}'...".format(song["name"]))

    threads = []
    for i in range(thread_num):
        if i == thread_num - 1:
            end = ''
        else:
            end = (i + 1) * part - 1
        thread = Worker((i * part, end), song, _id)
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    fileParts = glob.glob("part-{}-*".format(_id))
    fileParts.sort(key=lambda e: e.split('-')[-1])

    logger.info("'{}' combine parts...".format(song["name"]))
    with open(filename, "ab") as f:
        for part in fileParts:
            with open(part, "rb") as d:
                shutil.copyfileobj(d, f)
            os.remove(part)
    logger.info("'{}' finished".format(song["name"]))


def _song_link(songinfo, xcode=None):
    rates = list(songinfo["linkinfo"].keys())
    rates.sort(reverse=True)
    target = rates[0]
    song = songinfo["linkinfo"][target]

    song_link = song["songLink"]
    if "xcode" not in song_link:
        song_link = "{}?xcode={}".format(song_link, xcode)
    return song_link, song["size"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("song_ids", nargs='+', help="song ids")
    args = parser.parse_args()

    pfs = glob.glob("part-*")
    for p in pfs:
        os.remove(p)

    songs = music_info(args.song_ids)

    pool = multiprocessing.Pool()
    pool.map(download_music, songs)


if __name__ == "__main__":
    main()
