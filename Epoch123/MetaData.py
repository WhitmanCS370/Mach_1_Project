import sqlite3
import e123utils as eutils
import os
import logging
from PySide6.QtWidgets import QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView
from PySide6.QtCore import Qt

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')

class MetaDataDB:
    def __init__(self):
        try:
            self.db_path = eutils.get_main_sound_dir_path('Epoch123/DB') + '/metadata.db'
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            # Create audio_files table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS audio_files (
                    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    num_channels INTEGER,
                    sample_rate INTEGER,
                    file_size INTEGER,
                    duration REAL,
                    description TEXT
                )
            ''')

            # Create tags table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_name TEXT UNIQUE
                )
            ''')

            # Create file_tags table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_tags (
                    file_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (file_id, tag_id),
                    FOREIGN KEY (file_id) REFERENCES audio_files (file_id),
                    FOREIGN KEY (tag_id) REFERENCES tags (tag_id)
                )
            ''')

            self.conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Initialization Error", f"Database initialization error: {e}")
            logging.error(f"Database initialization error: {e}")
        finally:
            if self.conn:
                self.conn.close()

    def execute_query(self, query, params=()):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Query Error", f"Database query error: {e}")
            logging.error(f"Database query error: {e}")
            return None
        finally:
            if self.conn:
                self.conn.close()

    def file_already_exists(self, file_path):
        """Check if the file already exists in the database to avoid duplicates."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT 1 FROM audio_files WHERE file_path = ?", (file_path,))
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            logging.error(f"Error checking if file exists: {e}")
            return False
        finally:
            self.conn.close()

    def insert_metadata(self, file_name, file_path, num_channels, sample_rate, file_size, duration):
        """Insert metadata into the database, ignoring if it already exists."""
        if not self.file_already_exists(file_path):
            try:
                self.conn = sqlite3.connect(self.db_path)
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO audio_files (file_name, file_path, num_channels, sample_rate, file_size, duration)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (file_name, file_path, num_channels, sample_rate, file_size, duration))
                self.conn.commit()
            except sqlite3.Error as e:
                QMessageBox.critical(None, "Failed to Insert Metadata", f"Failed to insert metadata for {file_name}: {e}")
                logging.error(f"Failed to insert metadata for {file_name}: {e}")
            finally:
                self.conn.close()
        else:
            logging.info(f"Metadata for {file_path} already exists. Skipping insertion.")

    def write_metadata(self, file_path, num_channels=None, sample_rate=None, file_size=None, duration=None, description=None, tags=None):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            if self.file_already_exists(file_path):
                # Update the file metadata
                self.cursor.execute('''
                    UPDATE audio_files 
                    SET file_name = ?, num_channels = ?, sample_rate = ?, file_size = ?, duration = ?, description = ?
                    WHERE file_path = ?
                ''', (os.path.basename(file_path), num_channels, sample_rate, file_size, duration, description, file_path))

                file_id = self.cursor.execute("SELECT file_id FROM audio_files WHERE file_path = ?", (file_path,)).fetchone()[0]

                # Update the tags
                if tags is not None:
                    for tag in tags:
                        self.cursor.execute('''
                            INSERT OR IGNORE INTO tags (tag_name)
                            VALUES (?)
                        ''', (tag,))

                        self.cursor.execute('''
                            INSERT OR IGNORE INTO file_tags (file_id, tag_id)
                            VALUES (?, (SELECT tag_id FROM tags WHERE tag_name = ?))
                        ''', (file_id, tag))

            else:
                # Insert the file metadata
                self.cursor.execute('''
                    INSERT INTO audio_files (file_name, file_path, num_channels, sample_rate, file_size, duration, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (os.path.basename(file_path), file_path, num_channels, sample_rate, file_size, duration, description))

                file_id = self.cursor.lastrowid

                # Insert the tags
                if tags is not None:
                    for tag in tags:
                        self.cursor.execute('''
                            INSERT OR IGNORE INTO tags (tag_name)
                            VALUES (?)
                        ''', (tag,))

                        self.cursor.execute('''
                            INSERT INTO file_tags (file_id, tag_id)
                            VALUES (?, (SELECT tag_id FROM tags WHERE tag_name = ?))
                        ''', (file_id, tag))

            self.conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Error Writing Metadata", f"Error writing metadata: {e}")
            logging.error(f"Error writing metadata: {e}")
        finally:
            if self.conn:
                self.conn.close()

    def rename_file(self, old_path, new_path):
        new_name = os.path.basename(new_path)
        query = '''
            UPDATE audio_files
            SET file_path = ?, file_name = ?
            WHERE file_path = ?
        '''
        self.execute_query(query, (new_path, new_name, old_path))

    def delete_file(self, file_path):
        query = '''
            DELETE FROM audio_files
            WHERE file_path = ?
        '''
        self.execute_query(query, (file_path,))

    def get_metadata(self, file_path):
        query = '''
            SELECT * FROM audio_files
            WHERE file_path = ?
        '''
        result = self.execute_query(query, (file_path,))
        return result[0] if result else None

    def add_tag(self, tag_name):
        query = '''
            INSERT OR IGNORE INTO tags (tag_name)
            VALUES (?)
        '''
        self.execute_query(query, (tag_name,))

    def get_tags(self):
        query = '''
            SELECT tag_name FROM tags
        '''
        result = self.execute_query(query)
        return [tag[0] for tag in result] if result else []

    def get_files_by_tag(self, tag_name):
        query = '''
            SELECT file_path FROM audio_files
            WHERE file_id IN (
                SELECT file_id FROM file_tags
                WHERE tag_id = (SELECT tag_id FROM tags WHERE tag_name = ?)
            )
        '''
        result = self.execute_query(query, (tag_name,))
        return [file[0] for file in result] if result else []

    def remove_tag(self, tag_name):
        query = '''
            DELETE FROM tags
            WHERE tag_name = ?
        '''
        self.execute_query(query, (tag_name,))

    def remove_tag_from_file(self, file_path, tag_name):
        query = '''
            DELETE FROM file_tags
            WHERE file_id = (SELECT file_id FROM audio_files WHERE file_path = ?)
            AND tag_id = (SELECT tag_id FROM tags WHERE tag_name = ?)
        '''
        self.execute_query(query, (file_path, tag_name))

    def add_tag_to_file(self, file_path, tag_name):
        query = '''
            INSERT INTO file_tags (file_id, tag_id)
            VALUES ((SELECT file_id FROM audio_files WHERE file_path = ?), (SELECT tag_id FROM tags WHERE tag_name = ?))
        '''
        self.execute_query(query, (file_path, tag_name))

    def get_tags_for_file(self, file_path):
        query = '''
            SELECT tag_name FROM tags
            WHERE tag_id IN (
                SELECT tag_id FROM file_tags
                WHERE file_id = (SELECT file_id FROM audio_files WHERE file_path = ?)
            )
        '''
        result = self.execute_query(query, (file_path,))
        return [tag[0] for tag in result] if result else []

    def get_all_files(self):
        query = '''
            SELECT file_path FROM audio_files
        '''
        result = self.execute_query(query)
        return [file[0] for file in result] if result else []

class MetaDataWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.metadatadb = parent.metaDataDB
        self.layout = QVBoxLayout(self)
        self.setup_table()
        self.setLayout(self.layout)

    def setup_table(self):
        self.setRowCount(4)  # Assuming 6 metadata fields
        self.setColumnCount(4)  # Key and value columns
        self.setShowGrid(True)
        self.setStyleSheet("""
            QTableView {
                gridline-color: #ffffff;
                background-color: #151515;
                border: 1px;
                border-color: #ffffff;
                border-style: solid;

            }
        """)
        # have the table grid lines stretch to fill the table
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setStretchLastSection(True)

        # Set the table to be read-only
        self.setEditTriggers(QTableWidget.NoEditTriggers)

        # Set the table to be not selectable
        self.setSelectionMode(QTableWidget.NoSelection)

        # Hide the headers
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)

        # set the minimum height of the table
        self.setMinimumHeight(200)
        self.setMinimumWidth(300)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self)

    def update_metadata(self, file_path):
        self.file_path = file_path
        self.fetch_and_display_metadata()

    def fetch_and_display_metadata(self):
        try:
            metadata = self.metadatadb.get_metadata(self.file_path)
            if metadata:
                # Unpack the metadata based on how it's returned from your database
                file_id, file_name, file_path, num_channels, sample_rate, file_size, duration, description = metadata
                # Define tags
                tags = ', '.join(self.metadatadb.get_tags_for_file(file_path))

                data = [
                    ("File Name", file_name),
                    ("File Path", file_path),
                    ("Num of Channels", str(num_channels)),
                    ("Sample Rate", f"{sample_rate} Hz"),
                    ("File Size", f"{file_size} KB"),
                    ("Duration", f"{duration} seconds"),
                    ("Description", description),
                    ("Tags", tags)
                ]

                for i in range(4):
                    for j in range(2):
                        self.setItem(i, j*2, QTableWidgetItem(data[i*2+j][0]))
                        self.setItem(i, j*2+1, QTableWidgetItem(data[i*2+j][1]))
                        self.item(i, j*2+1).setTextAlignment(Qt.AlignCenter)

            else:
                QMessageBox.warning(None, "No Metadata Found", "No metadata found for this file path.")
                logging.warning("No metadata found for this file path.")
        except Exception as e:
            QMessageBox.critical(None, "Error Fetching Metadata", f"An error occurred while fetching and displaying metadata: {e}")
            logging.error(f"An error occurred while fetching and displaying metadata: {e}")