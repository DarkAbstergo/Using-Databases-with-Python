# If you run the program multiple times in testing or with different files, make sure to empty out the data before each run.
# You can use this code as a starting point for your application: http://www.py4e.com/code3/tracks.zip.
# The ZIP file contains the Library.xml file to be used for this assignment.
# You can export your own tracks from iTunes and create a database, but for the database that you turn in for this assignment, only use the Library.xml data that is provided.
#

#PART 1: PREPARING THE DATABASE
import xml.etree.ElementTree as ET
import sqlite3

conn = sqlite3.connect('trackdb2.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
# Getting sure it is empty
# We can use "executescript" to execute several statements at the same time
cur.executescript('''

    DROP TABLE IF EXISTS Artist;
    DROP TABLE IF EXISTS Genre;
    DROP TABLE IF EXISTS Album;
    DROP TABLE IF EXISTS Track;

    CREATE TABLE Artist (
        id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name    TEXT UNIQUE
    );
    CREATE TABLE Genre (
        id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name    TEXT UNIQUE
    );
    CREATE TABLE Album (
        id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        artist_id  INTEGER,
        title   TEXT UNIQUE
    );
    CREATE TABLE Track (
        id  INTEGER NOT NULL PRIMARY KEY
            AUTOINCREMENT UNIQUE,
        title TEXT  UNIQUE,
        artist_id INTEGER,
        genre_id  INTEGER,
        album_id  INTEGER
    );
''')

# PART 2: INSERTING THE DATA
# Getting the data and parsing it
fname = input('Enter file name: ')
if ( len(fname) < 1 ) : fname = 'Library.xml'

# <key>Track ID</key><integer>369</integer>
# <key>Name</key><string>Another One Bites The Dust</string>
# <key>Artist</key><string>Queen</string>
def lookup(d, key):
    found = False
    for child in d:
        if found : return child.text
        if child.tag == 'key' and child.text == key :
            found = True
    return None

stuff = ET.parse(fname)

# Obtaining every tag with track data
all = stuff.findall('dict/dict/dict')
print('Dict count:', len(all))

# Getting the values of the fields we'll insert
for entry in all:
    if ( lookup(entry, 'Track ID') is None ) : continue
    name = lookup(entry, 'Name')
    artist = lookup(entry, 'Artist')
    genre = lookup(entry, 'Genre')
    album = lookup(entry, 'Album')

    if name is None or artist is None or genre is None or album is None :
        continue

    print(name, artist, genre, album)

    # Artist
    cur.execute('''INSERT OR IGNORE INTO Artist (name)
        VALUES ( ? )''', ( artist, ) )
    cur.execute('SELECT id FROM Artist WHERE name = ? ', (artist, ))
    artist_id = cur.fetchone()[0]

    # Genre
    cur.execute('''INSERT OR IGNORE INTO Genre (name)
        VALUES ( ? )''', ( genre, ) )
    cur.execute('SELECT id FROM Genre WHERE name = ? ', (genre, ))
    genre_id = cur.fetchone()[0]

    # Album
    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id)
        VALUES ( ?, ? )''', ( album, artist_id ) )
    cur.execute('SELECT id FROM Album WHERE title = ? ', (album, ))
    album_id = cur.fetchone()[0]

    # Inserting data
    cur.execute('''INSERT OR REPLACE INTO Track
        (title, artist_id, genre_id, album_id)
        VALUES ( ?, ?, ?, ? )''',
        ( name, artist_id, genre_id, album_id ) )
    conn.commit()
