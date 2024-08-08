# Transaction Server with RFID Terminal
Performs one primary check: whether `Origin` has a value or not.
1. If it does, the assumption is the user is exiting and thus has to have the corresponding fee deducted from their balance.
2. If it does not, the assumption is the user is entering a tollway and thus has to have the location of the client (RFID terminal) set as the origin for the user.

All logical and data operations are done server-side. The only information the client sends are the `UID`, `LOCATION_ID`, and `DEDUCTION_MATRIX`. The `UID` is expected to be unique for reach card and is an 8-character, uppercase hexadecimal number (`00`-`FF`). The `LOCATION_ID` is the location code of where the user is tapping their card. The `DEDUCTION_MATRIX` is a fare matrix that exists in every terminal, wherein they set the corresponding charge for wherever the user may be coming from. These information are not hardcoded into the server, so as long as the file format for each card record is correct, it will work with any terminal that sends the aforementioned information.

A separate application for "creating" cards is needed, and this application will only accept ones that have an existing record in a `db` folder. A card record has a text file bearing the `UID` of the card it is associated with. The server writes changes to these records directly.

Format for each card record:

> ``Balance  [INTEGER VALUE]`` *The value here must be an integer that is greater than or equal to 0*
> 
> ``Origin   [STRING VALUE or EMPTY]`` *The value here must be either a string or simply an empty space after the tab spaces*

A `server_log.txt` file is also created at the initial run of the server. All transactions and requests are logged into this file.

I have provided a sample terminal/client code (`sample_client.ino`)for MFRC522 and other RFID RC522-based modules as well as a sample `db` folder. Flash/upload the code to an appropriate System on a Chip (SoC) microcontroller with Wi-Fi capabilities, like an ESP32. You need to configure the server IP, port, and Wi-Fi credentials in the code beforehand, as well as downloading the necessary libraries.

There is also a Python client simulation included (`client_sim.py`). You may have to configure the server IP and port in the script before running as well as following the suggestiont to create multiple variations of the script to simulate multiple users from different locations. Simply run using `python client_sim.py`, `python3 client_sim.py`, or `py client_sim.py`.
