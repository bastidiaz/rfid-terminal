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

I have provided a sample terminal/client code for MFRC522 and other RFID RC522-based modules as well as a sample `db` folder.
