"""
GUI script. Created a GUI using tkinter package.

1 window contains 4 entry  feilds, 2 listboxex to help the use correctly enter the source and destinations.
Date Entry box in the stict format (YYYY-MM-DD)
Number of passengers in the range of 1 - 9, a limit because of Google
A button to check for available flights.

2 window contains a table with the list of all available flights along with its number, depart time, arrival time,
duration and Price.
It contains a button when pressed after selecting a flight books the flight and add them to the booked table
in the database. All transactions occur through database.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import *
from FlightDatabase import makeurl, make_IATA_database
import sqlite3

database = sqlite3.connect('Flights')
db = database.cursor()
# make_IATA_database()
'''
print(scrape(makeurl('BOM', 'MAA', '2018-11-11', 11)))

'''


def on_keyrelease1(event):
    """
    Feeds the first list box based on the input in the entry box
    :param event:
    :return None:
    """
    # get text from entry
    value = event.widget.get()
    value = value.strip().lower()

    # get data from test_list
    if value == '':
        data = city_list
    else:
        data = []
        for item in city_list:
            if value in item.lower():
                data.append(item)

    # update data in listbox
    listbox1_update(data)


def listbox1_update(data):
    """
    Updates the first list box based on the input in the entry box
    :param data:
    :return None:
    """
    # delete previous data
    listbox1.delete(0, 'end')

    # sorting data
    data = sorted(data, key=str.lower)

    # put new data
    for item in data:
        listbox1.insert('end', item)


def on_keyrelease2(event):
    """
    Feeds the second list box based on the input in the entry box
    :param event:
    :return None:
    """

    # get text from entry
    value = event.widget.get()
    value = value.strip().lower()

    # get data from test_list
    if value == '':
        data = city_list
    else:
        data = []
        for item in city_list:
            if value in item.lower():
                data.append(item)

    # update data in listbox
    listbox2_update(data)


def listbox2_update(data):
    """
    Updates the second list box based on the input in the entry box
    :param event:
    :return None:
    """

    # delete previous data
    listbox2.delete(0, 'end')

    # sorting data
    data = sorted(data, key=str.lower)

    # put new data
    for item in data:
        listbox2.insert('end', item)


def searchflight():
    """
    Secomnd Window program. Collects the available flights and feed them in the table,
    :return:
    """
    origin = (entry1.get().lower(),)
    destination = (entry2.get().lower(),)
    date = entry3.get()
    passengers = int(entry4.get())
    ocode = db.execute("SELECT CODE from IATA WHERE CITY=? COLLATE NOCASE", origin).fetchall()[0][0]
    dcode = db.execute("SELECT CODE from IATA WHERE CITY=? COLLATE NOCASE", destination).fetchall()[0][0]
    if passengers > 0 and ocode in codes and dcode in codes:
        makeurl(ocode, dcode, date, passengers)
    elif passengers < 0:
        raise Exception("Passengers cannot be less than 1")
    elif ocode not in codes:
        raise Exception("Select valid Source")
    else:
        raise Exception("Select valid Destination")
    newWin = tk.Toplevel()
    newWin.title("Available Flights")
    table = Treeview(newWin)

    def selectItem(a):
        return

    def bookflight():
        curItem = table.focus()
        d = table.item(curItem)
        t = (str(d['text']).split(" ")[-1],)

        db.execute("CREATE TABLE if not exists BOOKED AS select * FROM FLIGHTS WHERE 0")
        t = db.execute('select * from FLIGHTS where FLIGHT_NUMBER=?', t).fetchall()[0]
        db.execute("INSERT OR REPLACE INTO BOOKED VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", t)

        database.commit()
        messagebox.showinfo(title="Success!", message="Flight booked succesfully!")
        newWin.destroy()

    #table creation
    table['columns'] = ['Departure', 'Arrival', 'Duration', 'Price']
    table.heading("#0", text="Flight Name", anchor='w')
    table.column("#0", anchor='w')
    table.heading("#0", text="Flight Name", anchor='w')
    table.heading('Departure', text='Departure')
    table.column('Departure', anchor='center', width=100)
    table.heading('Arrival', text='Arrival')
    table.column('Arrival', anchor='center', width=100)
    table.heading('Duration', text='Duration')
    table.column('Duration', anchor='center', width=100)
    table.heading('Price', text='Price')
    table.column('Price', anchor='center', width=100)
    table.grid(sticky=('N', 'S', 'W', 'E'))
    table.bind('<ButtonRelease-1>', selectItem)
    search = tk.Button(newWin, text="BOOK FLIGHT", justify='left', padx=2, width=20, command=bookflight)
    search.grid(sticky='s', row=1, column=1)

    flights = db.execute(
        "SELECT AIRLINE,FLIGHT_NUMBER,DEPART_TIME,ARR_TIME,DURATION,PRICE from FLIGHTS where DEPT_AIRPORT_CODE=? and ARR_AIRPORT_CODE=?",
        (ocode, dcode,)).fetchall()
    for x in flights:
        table.insert('', 'end', text=x[0] + " " + x[1], values=(x[2], x[3], x[4], x[5]))


# --- main ---#
#first window creation and operations
city_list = sorted([x[0] for x in db.execute('SELECT CITY from IATA ORDER BY CITY DESC').fetchall()])
codes = sorted([x[0] for x in db.execute('SELECT CODE from IATA ORDER BY CITY DESC').fetchall()])


root = tk.Tk()

Label1 = tk.Label(root, text="Source ")
Label1.grid(row=0, column=0)
entry1 = tk.Entry(root)
entry1.grid(row=0, column=1)
entry1.bind('<KeyRelease>', on_keyrelease1)

Label2 = tk.Label(root, text="Destination ")
Label2.grid(row=0, column=3)
entry2 = tk.Entry(root)
entry2.grid(row=0, column=4)
entry2.bind('<KeyRelease>', on_keyrelease2)

listbox1 = tk.Listbox(root)
listbox2 = tk.Listbox(root)
listbox1.grid(row=1, column=1)
listbox2.grid(row=1, column=4)

listbox1_update(city_list)
listbox2_update(city_list)

Label3 = tk.Label(root, text="Date of Journey\n(YYYY-MM-DD)")
Label3.grid(row=0, column=5)
entry3 = tk.Entry(root)
entry3.grid(row=0, column=6)

Label4 = tk.Label(root, text="Passengers")
Label4.grid(row=1, column=5, sticky='N')
entry4 = tk.Entry(root)
entry4.grid(row=1, column=6, sticky='N')

search = tk.Button(root, text="SEARCH FLIGHTS", justify='left', padx=2, width=20, command=searchflight)
search.grid(row=3, column=6, sticky='NW')
root.mainloop()
