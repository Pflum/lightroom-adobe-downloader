# lightroom-adobe-downloader
Downloader to download images and videos from shared adobe lightroom

# Usage
Get the URL and use the ID at the end: https://lightroom.adobe.com/shares/<SHARE-ID>
Clone the repo and start the skript with the ID from the URL
```bash
git clone https://github.com/Pflum/lightroom-adobe-downloader
cd https://github.com/Pflum/lightroom-adobe-downloader
chmod +x ./lightroom-adobe-downloader.py
./lightroom-adobe-downloader.py <SHARE-ID>
```

# Notice
I write the script to download the images from a singel share, so I don't now if this still works or is a good way to do this. I also not have a good error handling. If you have improvements feel free to create pull request.
