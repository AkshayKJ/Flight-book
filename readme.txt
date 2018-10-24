Description
The program uses google flights information and collect the required information for the flights. The inputs are complete names of cities to be traveled. The GUI contains a list box that helps user in writing the correct name. The list box only shows the correct name, that cannot be selected from the list. The FULL NAMES ARE REQUIRED TO BE ENTERED MANUALLY. You can't select from the list box. It's just there for display and you have to write the city name as listed in the list box (case insensitive).

Executable
I have created an executable file from my python source code using pyinstaller. It is available in the Source/dist/GUI/. The name of the executable is GUI.exe. Please run and allow the required access to the file. All the dependencies are present and will run smoothly on any windows machine but will require network access. Kindly provide the reqired network access, thus allowing the program to run.

When running the program, after entering the cities and search , the window will become 'Not Responding', please do not panic as it isjust momentary.The results will be displaed in a selectable table with a book button, just select the flight of your choice and it will be transfered to the BOOKED table in the database.The results will be stored in Flights.db, which can be viewed in any database viewing program.

Source
Source containts the original python code which is also executable but will require dependencies to be install(selenium, lxml, sqlite, beautifulsoup). All the codes are well structured and documented and will be easy to understand.