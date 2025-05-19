import sqlite3

class DBOperation:
    def __init__(self, db_name="stewie_database.db"):
        self.db_name = db_name
        self.create_dialouge_stage_table()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_dialouge_stage_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS dialouge_stage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentence TEXT NOT NULL,
            character TEXT,
            image TEXT,
            image_search TEXT,
            audio_processed INTEGER DEFAULT 0,
            audio_process_retry INTEGER DEFAULT 0
        );
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            print("Table 'dialouge_stage' is ready.")
        except sqlite3.Error as e:
            print(f"SQLite error during table creation: {e}")
        finally:
            conn.close()


    def add_dialogues(self, dialogues):
            """
            Adds a list of dialogues to the dialouge_stage table.
            Each dialogue should be a dictionary with keys:
            - sentence
            - character
            - image
            - image_search
            - audio_processed (default 0)
            - audio_process_retry (default 0)
            """
            try:
                conn = self.connect()
                cursor = conn.cursor()

                # Prepare insert query
                query = """
                    INSERT INTO dialouge_stage (sentence, character, image, image_search, audio_processed, audio_process_retry)
                    VALUES (?, ?, ?, ?, ?, ?);
                """
                
                # Insert each dialogue in the list
                for dialogue in dialogues:
                    sentence = dialogue.get("dialogue")
                    character = dialogue.get("character", None)
                    image = dialogue.get("image", None)
                    image_search = dialogue.get("image_search", None)
                    audio_processed = dialogue.get("audio_processed", 0)  # Default to 0 if not provided
                    audio_process_retry = dialogue.get("audio_process_retry", 0)  # Default to 0 if not provided

                    cursor.execute(query, (sentence, character, image, image_search, audio_processed, audio_process_retry))

                conn.commit()
                print(f"Successfully added {len(dialogues)} dialogues.")
            except sqlite3.Error as e:
                print(f"SQLite error during insertion: {e}")
            finally:
                conn.close()


    def get_stage_and_unprocessed_dialogues(self):
        """
        Returns stage and up to 3 unprocessed dialogues (if exist):
        {
            "stage": 0 → table empty
                    1 → unprocessed dialogues exist
                    2 → table has data, but no eligible dialogues
            "dialogues": [...] or None
        }
            """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Check if table is empty
            cursor.execute("SELECT COUNT(*) FROM dialouge_stage;")
            total_rows = cursor.fetchone()[0]
            if total_rows == 0:
                return {"stage": 0, "dialogues": None}

            # Try to fetch up to 3 unprocessed dialogues
            cursor.execute("""
                SELECT id, sentence, character, image, image_search, audio_processed, audio_process_retry
                FROM dialouge_stage
                WHERE audio_processed = 0 AND audio_process_retry < 5
                ORDER BY id ASC
                LIMIT 3;
            """)
            rows = cursor.fetchall()
            if rows:
                dialogues = []
                for row in rows:
                    dialogues.append({
                        "id": row[0],
                        "sentence": row[1],
                        "character": row[2],
                        "image": row[3],
                        "image_search": row[4],
                        "audio_processed": row[5],
                        "audio_process_retry": row[6]
                    })
                return {"stage": 1, "dialogues": dialogues}

            # Table has data, but no unprocessed dialogue
            return {"stage": 2, "dialogues": None}

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return {"stage": -1, "dialogues": None}  # Error flag
        finally:
            conn.close()




    def get_raedy_assests(self):
  
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Check if table is empty
            cursor.execute("SELECT COUNT(*) FROM dialouge_stage;")
            total_rows = cursor.fetchone()[0]
            if total_rows == 0:
                None

            # Try to fetch up to 3 unprocessed dialogues
            cursor.execute("""
                SELECT id, sentence, character, image, image_search, audio_processed, audio_process_retry
                FROM dialouge_stage
                WHERE audio_processed = 1 ORDER BY id ASC;
            """)
            rows = cursor.fetchall()
            if rows:
                dialogues = []
                for row in rows:
                    dialogues.append({
                        "id": row[0],
                        "sentence": row[1],
                        "character": row[2],
                        "image": row[3],
                        "image_search": row[4],
                        "audio_processed": row[5],
                        "audio_process_retry": row[6]
                    })
                return dialogues

            # Table has data, but no unprocessed dialogue
            return None
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return {"stage": -1, "dialogues": None}  # Error flag
        finally:
            conn.close()



    def mark_processed(self, dialogue_id, flag):
            """
            Marks a dialogue as processed based on the flag:
            If flag is True, set audio_processed to 1 and increment audio_process_retry.
            If flag is False, just increment audio_process_retry.
            """
            try:
                conn = self.connect()
                cursor = conn.cursor()

                if flag:
                    # If flag is True, set audio_processed to 1 and increment retry count
                    cursor.execute("""
                        UPDATE dialouge_stage
                        SET audio_processed = 1, audio_process_retry = audio_process_retry + 1
                        WHERE id = ?;
                    """, (dialogue_id,))
                else:
                    # If flag is False, just increment retry count
                    cursor.execute("""
                        UPDATE dialouge_stage
                        SET audio_process_retry = audio_process_retry + 1
                        WHERE id = ?;
                    """, (dialogue_id,))

                conn.commit()
                print(f"Dialogue with ID {dialogue_id} has been updated.")
            except sqlite3.Error as e:
                print(f"SQLite error during update: {e}")
            finally:
                conn.close()


    def show_all_dialogues(self):
        """
        Fetches all dialogues from the dialouge_stage table and prints them in a neat format.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Fetch all rows from the dialouge_stage table
            cursor.execute("SELECT id, sentence, character, image, image_search, audio_processed, audio_process_retry FROM dialouge_stage;")
            rows = cursor.fetchall()

            # Check if the table is empty
            if not rows:
                print("No dialogues found in the database.")
                return

            # Print the table headers
            print(f"{'ID':<5} {'Sentence':<30} {'Character':<15} {'Image':<20} {'Image Search':<20} {'Audio Processed':<15} {'Retry Count':<10}")
            print("-" * 120)

            # Print each row
            for row in rows:
                print(f"{row[0]:<5} {row[1]:<30} {row[2]:<15} {row[3]:<20} {row[4]:<20} {row[5]:<15} {row[6]:<10}")
        except sqlite3.Error as e:
            print(f"SQLite error during fetching data: {e}")
        finally:
            conn.close()


    def truncate_dialouge_stage(self):
        """
        Deletes all rows from the dialouge_stage table and resets the auto-increment ID.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Delete all records
            cursor.execute("DELETE FROM dialouge_stage;")

            # Reset auto-increment ID
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='dialouge_stage';")

            conn.commit()
            print("Table 'dialouge_stage' has been truncated and ID reset.")
        except sqlite3.Error as e:
            print(f"SQLite error during truncate: {e}")
        finally:
            conn.close()




#form  of data that  db  accepts  ...


convo= [
    {
      "audio": "C:/path/to/audio/peter_audio_0.mp3",
      "image": "peter.png",
      "dialogue": "Peter: MongoDB is a NoSQL database, like a giant bookshelf for your data. No rigid tables!",
      "image_search": "mongodb noSQL bookshelf analogy",
      "character": "Peter"
    },
    {
      "audio": "C:/path/to/audio/stewie_audio_1.mp3",
      "image": "stewie.png",
      "dialogue": "Stewie: So, no tables? Are we just piling data on a shelf like a hoarder's dream?",
      "image_search": "mongodb data hoard shelf",
      "character": "Stewie"
    },
    {
      "audio": "C:/path/to/audio/peter_audio_2.mp3",
      "image": "peter.png",
      "dialogue": "Peter: Yep, MongoDB uses collections instead of tables. Think of them as folders of data.",
      "image_search": "mongodb collections folders",
      "character": "Peter"
    },
    {
      "audio": "C:/path/to/audio/stewie_audio_3.mp3",
      "image": "stewie.png",
      "dialogue": "Stewie: So I can store anything in a folder? Sounds like the tech version of a junk drawer!",
      "image_search": "mongodb junk drawer analogy",
      "character": "Stewie"
    },
    {
      "audio": "C:/path/to/audio/peter_audio_4.mp3",
      "image": "peter.png",
      "dialogue": "Peter: Exactly! Each document in MongoDB is like a sticky note with data—no fixed format.",
      "image_search": "mongodb document sticky note",
      "character": "Peter"
    },
    {
      "audio": "C:/path/to/audio/stewie_audio_5.mp3",
      "image": "stewie.png",
      "dialogue": "Stewie: So no columns? Just random data all over the place? Sounds messy.",
      "image_search": "mongodb no columns messy",
      "character": "Stewie"
    },
    {
      "audio": "C:/path/to/audio/peter_audio_6.mp3",
      "image": "peter.png",
      "dialogue": "Peter: It’s not messy, Stewie! MongoDB is flexible. You can add data as you need it.",
      "image_search": "mongodb flexible data addition",
      "character": "Peter"
    },
    {
      "audio": "C:/path/to/audio/stewie_audio_7.mp3",
      "image": "stewie.png",
      "dialogue": "Stewie: Flexible? Sounds like the database equivalent of an open bar at a wedding.",
      "image_search": "mongodb flexible open bar wedding",
      "character": "Stewie"
    },
    {
      "audio": "C:/path/to/audio/peter_audio_8.mp3",
      "image": "peter.png",
      "dialogue": "Peter: More like a buffet, Stewie! It lets you easily scale when the data gets huge.",
      "image_search": "mongodb scaling buffet analogy",
      "character": "Peter"
    }
  ]




# if __name__ == "__main__":
#     #db = DBOperation()
#     #db.truncate_dialouge_stage()
#    # db.add_dialogues(convo)
#     #print(db.get_stage_and_unprocessed_dialogue())
#     #db.show_all_dialogues()
#     ready_assests=db.get_raedy_assests()
#     print(ready_assests)
#     # for dic in  ready_assests:
#     #     print(dic)
#     #db.truncate_dialouge_stage()