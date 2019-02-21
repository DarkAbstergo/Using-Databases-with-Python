import json
import sqlite3

# Make connection to the sql and create a new sql file
conn = sqlite3.connect('rosterdb.sqlite')
cur = conn.cursor()

# Do some setup, create three tables
cur.executescript('''
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Member;
DROP TABLE IF EXISTS Course;

CREATE TABLE User (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name   TEXT UNIQUE
);

CREATE TABLE Course (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    title  TEXT UNIQUE
);

CREATE TABLE Member (
    user_id     INTEGER,
    course_id   INTEGER,
    role        INTEGER,
    PRIMARY KEY (user_id, course_id)
)
''')

fname = input('Enter file name: ')
if len(fname) < 1:
    fname = 'roster_data_sample.json'

# [
#   [ "Charley", "si110", 1 ],
#   [ "Mea", "si110", 0 ],
# Parse the json data

str_data = open(fname).read()
json_data = json.loads(str_data)

# This for loop runs throught the whole json data and get the user, course and Member
# tables that contain the user names, course titles and ids-and-role combination respectively
for entry in json_data:
    # entry is kinda like a list, use index to extract the string or int you want
    name = entry[0];
    title = entry[1];
    role = entry[2];

    print((name, title, role))

    # Insert into User, and get user id
    cur.execute('''INSERT OR IGNORE INTO User (name)
        VALUES ( ? )''', ( name, ) )
    cur.execute('SELECT id FROM User WHERE name = ? ', (name, ))
    user_id = cur.fetchone()[0]

    # Insert into Course, and get course id
    cur.execute('''INSERT OR IGNORE INTO Course (title)
        VALUES ( ? )''', ( title, ) )
    cur.execute('SELECT id FROM Course WHERE title = ? ', (title, ))
    course_id = cur.fetchone()[0]

    # put (user_id, course_id, role) to make sure that those three-combination is unique
    cur.execute('''INSERT OR REPLACE INTO Member
        (user_id, course_id, role) VALUES ( ?, ?, ? )''',
        ( user_id, course_id, role ) )


conn.commit()

# Now execute the JOIN statment and get the many-to-many relation
cur.execute('''SELECT hex(User.name || Course.title || Member.role ) AS X FROM
    User JOIN Member JOIN Course
    ON User.id = Member.user_id AND Member.course_id = Course.id
    ORDER BY X
    ''')

# Print out the result
result = cur.fetchone()
print("RESULT: " + str(result))
