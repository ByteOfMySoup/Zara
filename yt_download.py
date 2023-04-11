import os
import sys
from pytube import YouTube

def download_video(url, download_path=None):
    if download_path is None:
        download_path = os.path.join(os.path.expanduser("~"), "Downloads")
    yt = YouTube(url)
    video = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
    video.download(output_path=download_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python yt_download.py <URL> [download_path]")
        sys.exit(1)

    url = sys.argv[1]
    download_path = sys.argv[2] if len(sys.argv) > 2 else None
    download_video(url, download_path)
    print(f"Video downloaded successfully to: {download_path}")