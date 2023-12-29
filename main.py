import os
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from tqdm import tqdm
from p_tqdm import p_map
import pickle
import sqlite3

musicDir = "/home/pablo//Music"
cachePath = "cache.pkl"
sqliteConn = sqlite3.connect("output.db")

acceptableID3Tags = [
  # 'APIC*', Handled specially later, as I want to keep all APIC tags
  'TALB', # Album
  'TCOM', # Composer
  'TCON', # Genre 
  'TDRC', # RecordingTime
  'TDRL', # ReleaseTime
  'TIT1', # Grouping
  'TIT2', # Title
  'TIT3', # Subtitle
  'TLAN', # Language
  'TLEN', # Length
  'TPE1', # Artist
  'TPE2', # Band (=Album Artist)
  'TRCK', # Track
  'TXXX:replaygain_album_peak',
  'TXXX:replaygain_album_gain',
  'TXXX:replaygain_track_gain',
  'TXXX:replaygain_track_peak',
]

acceptableOtherTags = [
  "WM/AlbumArtist",
  "replaygain_track_peak",
  "©alb",
  "trkn",
  "replaygain_album_gain",
  "replaygain_album_peak",
  "Author",
  "Title",
  "aART",
  "©day",
  "©wrt",
  "WM/Year",
  "WM/AlbumTitle",
  "WM/TrackNumber",
  "replaygain_track_gain",
  "©ART",
  "©nam",
  "disk",
  "covr",
  "©gen",
]

class MusicFile:
  def __init__(self, path, info):
    self.path = path
    self.info = info

try:
  musicFiles = pickle.load(open(cachePath, 'rb'))
except:
  filePaths = []
  for root, subdirs, files in os.walk(musicDir):
    for file in files:
      path = os.path.join(root, file)
      filePaths.append(path)

  musicFiles = []
  for path in tqdm(filePaths, "Reading info"):
    info = mutagen.File(path)
    if info:
      musicFiles.append(MusicFile(path, info))

  pickle.dump(musicFiles, open(cachePath, 'wb'))


# Cleanup files
deletedTags = set()
for mf in tqdm(musicFiles, "Cleaning files"):
  isMp3 = mf.path.lower().endswith(".mp3")
  if isMp3:
    acceptableTags = acceptableID3Tags
  else:
    acceptableTags = acceptableOtherTags
  
  for tag in list(mf.info.keys()):
    if isMp3 and tag.startswith("APIC"):
      pass
    elif tag in acceptableTags:
      pass
    else:
      mf.info.pop(tag)
      mf.info.save()
      deletedTags.add(tag)

f = open("deleted-tags.txt", "w")
for deletedTag in deletedTags:
  f.write(deletedTag.replace("\n","\\n"))
  f.write("\n")
f.close()

# sqliteCursor = sqliteConn.cursor()
# # Create table
# columns = ["\"" + tag + "\" TEXT NULLABLE DEFAULT NULL" for tag in nonMp3Tags]
# columns = ", ".join(columns)
# sqliteCursor.execute("DROP TABLE IF EXISTS tags")
# sqliteCursor.execute("CREATE TABLE tags(path, " + columns + ")")
# # Add data
# for mf in tqdm(nonMp3Files, "Adding to db"):
#   tags = list(mf.info.tags.keys())

#   cols = ["path"] + tags
#   cols = ["\"" + col + "\" " for col in cols]
#   cols = ", ".join(cols)

#   vals = [mf.path] + [mf.info.tags[tag] for tag in tags]
#   vals = [str(val).replace("'", "''") for val in vals]
#   vals = [val.replace("\x00", "\\NUL") for val in vals]
#   vals = ["'" + val + "'" for val in vals]
#   vals = ", ".join(vals)

#   query = "INSERT INTO tags (" + cols + ") VALUES(" + vals +");"
#   f = open("temp.txt", "w")
#   f.write(query)
#   f.close()
#   sqliteCursor.execute(query)
# sqliteConn.commit()

