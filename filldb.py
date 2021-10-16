import sqlite3
con = sqlite3.connect('alldb.sqlite3')
cur = con.cursor()
# Insert a row of data
inline = []
with open("mass_media.txt", 'r') as f:
    inline = f.read().split()

con.execute("INSERT INTO queue (url) VALUES ('" +
            "') ,('".join(inline) + "')")

# Save (commit) the changes
con.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
con.close()
