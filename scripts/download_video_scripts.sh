# download clip in mp4 format, send to data dir
yt-dlp --download-sections "*01:30-02:00" --merge-output-format mp4 'https://www.youtube.com/watch?v=8835heTiSAk' -o '/Users/treyshanks/data_science/Court_Vision/data/inputs/lebron.%(ext)s'
# Use specific video size and quality -f
yt-dlp -o '/Users/treyshanks/data_science/Court_Vision/data/%(title)s.%(ext)s' -f 397 'https://www.youtube.com/watch?v=8835heTiSAk'

yt-dlp -f 606 -o '/Users/treyshanks/data_science/Court_Vision/data/lebron.%(ext)s' 'https://www.youtube.com/watch?v=oBKeZSSS9qM'

yt-dlp -f "(bestvideo+bestaudio/best)[protocol!*=dash]" --external-downloader ffmpeg --external-downloader-args "ffmpeg_i:-ss 3263 -to 3274" "https://www.youtube.com/watch?v=S9HdPi9Ikhk"

yt-dlp -f "(bestvideo+bestaudio/best)[protocol!*=dash]" --external-downloader ffmpeg --external-downloader-args "ffmpeg_i:-ss 90 -to 110" -o '/Users/treyshanks/data_science/Court_Vision/data/lebron.%(ext)s' 'https://www.youtube.com/watch?v=oBKeZSSS9qM' 

yt-dlp --external-downloader ffmpeg --external-downloader-args "ffmpeg_i:-ss 90 -to 100" --merge-output-format mp4 -o '/Users/treyshanks/data_science/Court_Vision/data/lebron_1.%(ext)s' 'https://www.youtube.com/watch?v=oBKeZSSS9qM' 