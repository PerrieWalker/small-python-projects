import ttkbootstrap as ttkb
import tkinter
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.dialogs import Querybox
from tkinter import filedialog

import os
import sqlite3
import eyed3
import shutil

# THE UI WAS DESIGNED ON MAN. WILL LOOK DIFFERENT ON WINDOWS

class Mp3_App_Organiser():
    """Uses Mp3 Meta data to organise Mp3's into folders sorted by Artist and Album,
     will organise files into folders in the source folder unless a new target location is selected.
      When the Organise button is pressed a top level window displays a table showing Mp3 Meta Data,
       the original file location, and where it has been moved to."""
    def __init__(self):
        super().__init__()
        # THEME
        self.theme = 'darkly'

        # WINDOW SETUP
        self.window = ttkb.Window(themename=self.theme)
        self.window.title('Mp3 Organiser')
        self.width = 425
        self.height = 170
        self.center_window(self.window, self.width, self.height)
        self.window.protocol('WM_DELETE_WINDOW', self.close_app)

        self.frame = tkinter.Frame(self.window, padx=10, pady=10)
        self.frame.grid(row=0, column=0)

        self.app_label = ttkb.Label(self.frame, text="Mp3 Organiser", font=("", 40), padding=(10, 10))
        self.app_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.source_directory_name = None
        self.target_directory_name = None

        # BUTTONS
        self.button_1 = ttkb.Button(self.frame, text="Select Folder", width=10, bootstyle=PRIMARY,
                                    command=self.select_source_directory_name)
        self.button_1.grid(row=1, column=0, padx=10, pady=10)
        self.button_2 = ttkb.Button(self.frame, text="Move to", width=10, bootstyle=PRIMARY,
                                    command=self.select_target_directory)
        self.button_2.grid(row=1, column=1, padx=10, pady=10)
        self.button_3 = ttkb.Button(self.frame, text="ORGANISE", width=10, bootstyle=SUCCESS, command=self.organise)
        self.button_3.grid(row=1, column=2, padx=10, pady=10)

    def data_table(self):
        """Data Table - Shows Mp3 Meta Data, where files are and where they are moved to """

        self.data_table_window_width = 1400
        self.data_table_window_height = 700

        self.data_table_window = tkinter.Toplevel()
        self.data_table_window.title('Files Organised')
        self.data_table_window.resizable(False, False)
        self.center_window(self.data_table_window, self.data_table_window_width, self.data_table_window_height)
        self.data_table_window.transient(self.window)

        # TABLE
        column_data = [
            {"text": "Track Number", "stretch": False, "minwidth": 100, "width": 100},
            {"text": "Track Name", "stretch": False, "minwidth": 100, "width": 250},
            {"text": "Artist", "stretch": False, "minwidth": 100, "width": 100},
            {"text": "Album", "stretch": False, "minwidth": 100, "width": 100},
            {"text": "Moved From", "stretch": False, "minwidth": 100, "width": 350},
            {"text": "Moved To", "stretch": False, "minwidth": 100, "width": 475},
        ]

        try:
            conn = sqlite3.connect('mp3_tags.db')
            c = conn.cursor()

            c.execute(
                "SELECT track_number, album_artist, album, filename, filepath, destination_path, COUNT(*) as track_count "
                "FROM mp3_tags "
                "GROUP BY  album_artist, album, title "
                "ORDER BY  album_artist, album, track_number, title ")

            # gets the data stores it as a variable
            rows = c.fetchall()

            row_data = [(row[0], row[3], row[1], row[2], row[4], row[5]) for row in rows]

            conn.commit()
            conn.close()

        except:
            row_data = [(

            )]

        self.table = Tableview(master=self.data_table_window, height=35,
                               pagesize=35,
                               coldata=column_data,
                               rowdata=row_data,
                               paginated=True,
                               searchable=True,
                               bootstyle=SUCCESS,
                               # stripecolor=(self.colors.dark, None)
                               )

        self.table.grid(row=2, column=0, padx=10, pady=5)

    def center_window(self, window, width, height):
        """Centers Window On Screen"""
        # Get the screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculate the position of the window to center it on the screen
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the geometry of the window
        window.geometry(f"{width}x{height}+{x}+{y}")

    def select_source_directory_name(self):
        """Prompts user to choose source directory"""
        program_directory = os.path.dirname('')
        self.source_directory_name = filedialog.askdirectory(initialdir=program_directory, title="Select A Folder")

    def select_target_directory(self):
        """Prompts user for target directory"""
        program_directory = os.path.dirname('')
        self.target_directory_name = filedialog.askdirectory(initialdir=program_directory, title="Select A Folder")

    def toast_pop(self, title, message, duration=2000, bootstyle='light', alert=False, inoffset_x=0, inoffset_y=30):
        """Pop up for when organise button is pressed but source directory is chosen"""
        offset_x = inoffset_x
        offset_y = inoffset_y
        toast = ToastNotification(icon="",
                                  alert=alert,
                                  bootstyle=bootstyle,
                                  title=title,
                                  message=message,
                                  duration=duration,
                                  position=(self.window.winfo_x() + offset_x, self.window.winfo_y() + offset_y, 'nw',
                                            )
                                  )
        toast.show_toast()

    def organise(self):
        """Organises Mp3's - uses Meta data to sort by artist and album"""

        if self.source_directory_name is not None:
            if self.target_directory_name is None:
                self.target_directory_name = self.source_directory_name

            conn = sqlite3.connect('mp3_tags.db')
            c = conn.cursor()

            c.execute('''CREATE TABLE IF NOT EXISTS mp3_tags (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            filename TEXT,
                            artist TEXT,
                            album TEXT,
                            album_artist TEXT,
                            title TEXT,
                            track_number INTEGER,
                            composer TEXT,
                            comment TEXT,
                            filepath TEXT,
                            destination_path TEXT,
                            UNIQUE(title, artist, album)  -- Composite unique constraint on multiple columns
                        )''')

            # iterates through files in source directory
            for filename in os.listdir(self.source_directory_name):

                if filename.endswith('.mp3'):
                    # for each file with the .mp3 extension it constructs the full file path
                    file_path = os.path.join(self.source_directory_name, filename)
                    # and uses eyed.load() to load the mp3 file and extract the ID3 tag information
                    audiofile = eyed3.load(file_path)

                    # if the ID3 tag exists for the file audiofile.tag retrieves the artist, album, genre information
                    if audiofile.tag:
                        artist = audiofile.tag.artist if audiofile.tag.artist else None
                        album = audiofile.tag.album if audiofile.tag.album else None
                        # genre = audiofile.tag.genre if audiofile.tag.genre else None

                        title = audiofile.tag.title if audiofile.tag.title else None
                        # year = audiofile.tag.getBestDate()
                        track_number = audiofile.tag.track_num[0] if audiofile.tag.track_num else None
                        # duration = audiofile.info.time_secs  # Extracts the duration of the song in seconds
                        album_artist = audiofile.tag.album_artist if audiofile.tag.album_artist else None
                        composer = audiofile.tag.composer if audiofile.tag.composer else None
                        comment = audiofile.tag.comments[0].text if audiofile.tag.comments else None
                        lyrics = audiofile.tag.lyrics[0].text if audiofile.tag.lyrics else None
                        file_path = os.path.join(self.source_directory_name, filename)

                        # MOVING FILES
                        if album and album_artist:
                            # creates paths for both artist and album folders
                            artist_folder = os.path.join(self.target_directory_name, album_artist)
                            album_folder = os.path.join(artist_folder, album)

                            # if the artist folder does not exist it create ons
                            if not os.path.exists(artist_folder):
                                os.makedirs(artist_folder)
                            # if the album folder doesn't exist it creates one
                            if not os.path.exists(album_folder):
                                os.makedirs(album_folder)
                            # creates a destination path for the file to be moved to
                            destination_path = os.path.join(album_folder, filename)
                            # moves file to the new location
                            shutil.move(file_path, destination_path)

                        # Insert tag information into the database
                        c.execute('''INSERT OR IGNORE INTO mp3_tags (filename, artist, album, title, track_number,
                         album_artist, composer, comment, filepath, destination_path) 
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (filename, artist, album,
                                                                                title, track_number, album_artist,
                                                                                composer,
                                                                                comment, file_path, destination_path))

                    else:
                        c.execute("SELECT track_number, album_artist, album, title, filename, COUNT(*) as track_count "
                                  "FROM mp3_tags "
                                  "GROUP BY  album_artist, album, title "
                                  "ORDER BY  album_artist, album, track_number, title ")
                        rows = c.fetchall()

                        number = 0
                        number_pre = 0
                        existing = False
                        for row in rows:
                            row1 = str(row[2])

                            unknown = row1[0:7]
                            if unknown == "unknown":
                                number_pre = int(row1[7])

                            if number_pre >= 0:
                                number = number_pre + 1
                                existing = True

                        unknown = f"unknown{number}"
                        file_path = os.path.join(self.source_directory_name, filename)

                        unknown_folder = os.path.join(self.target_directory_name, "Unknown")
                        if not os.path.exists(unknown_folder):
                            os.makedirs(unknown_folder)
                        destination_path = os.path.join(unknown_folder, filename)
                        shutil.move(file_path, destination_path)

                        c.execute('''INSERT OR IGNORE INTO mp3_tags (filename, artist, album, title, track_number, filepath, destination_path)
                                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                  (filename, unknown, unknown, unknown, unknown, file_path, destination_path))

                        if existing == False:
                            number += 1

            conn.commit()
            conn.close()

            self.data_table()

        else:
            self.toast_pop("No Directory", "Select a folder with Mp3's to be organised")

    def close_app(self):
        """Opens Dialogue Box to Ask User If They Want To Close App"""
        screen_width = self.window.winfo_x() + self.width // 2 - (self.width // 4) - 60
        screen_height = self.window.winfo_y() + self.height // 2 - 50

        close_app_message = ttkb.dialogs.Messagebox.show_question('Are you sure you want to close'
                                                                  ' the App?', 'Close App?',
                                                                  buttons=['Yes:success', 'No:danger'],
                                                                  position=(screen_width, screen_height))
        if close_app_message == 'Yes':
            self.window.quit()
            self.window.destroy()
            try:
                os.remove("mp3_tags.db")
            except FileNotFoundError:
                pass



def main():
    app = Mp3_App_Organiser()
    app.window.mainloop()


if __name__ == "__main__":
    main()
