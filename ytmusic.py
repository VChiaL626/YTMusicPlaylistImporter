from ytmusicapi import YTMusic
import argparse
from tqdm import tqdm
from zhconv import convert


class YTMusicPlaylistImporter:
    def __init__(self, args) -> None:
        self.playlist_file = args.file
        self.auth_file = args.auth
        self.play_list_id = args.playlist
        self.ytmusic = YTMusic(self.auth_file)
        self.songs_failed = {}
        self.songs_not_found = []


    def import_song(self, song: str, play_list_id: str):
        found_flag = False
        import_flag = False
        search_rets = self.ytmusic.search(song)
        for ret in search_rets:
            if 'title' not in ret:
                continue
            ret_song_title = ret['title']
            if ret['resultType'] == "song" and convert(ret_song_title, 'zh-cn') in convert(song, 'zh-cn'):
                found_flag = True
                response = self.ytmusic.add_playlist_items(play_list_id, [ret['videoId']])
                if 'status' in response and 'SUCCEEDED' in response['status']:
                    import_flag = True
                else:
                    error_msg = response['actions'][0]['addToToastAction']['item']['notificationActionRenderer']['responseText']['runs'][0]['text']
                break
        if not found_flag:
            self.songs_not_found.append(song)
        elif not import_flag:
            self.songs_failed[song] = error_msg


    def run(self):
        with open(self.playlist_file, encoding="utf-8") as ip:
            songs = [line.strip() for line in ip.readlines()]
        for song in tqdm(songs, ascii=True):
            self.import_song(song, self.play_list_id)
            
        if self.songs_not_found:
            print("Part of songs are not found:")
            for song in self.songs_not_found:
                print(song)
        print()
        if self.songs_failed:
            print("Part of songs are failed:")
            for song in self.songs_failed:
                print(song + ": " + self.songs_failed[song])
        else:
            print("All songs are successfully imported.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(f"Youtube Music Playlist Importer")
    parser.add_argument("-a", "--auth", help="headers auth file")
    parser.add_argument("-f", "--file", help="playlist file")
    parser.add_argument("-pl", "--playlist", help="playlist id")
    args = parser.parse_args()
    ytmusic_playlist_importer = YTMusicPlaylistImporter(args)

    ytmusic_playlist_importer.run()
