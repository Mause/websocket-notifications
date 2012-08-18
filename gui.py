from Tkinter import *
from socket import *
import sys
import thread
import time

root = Tk()
root.resizable(width=FALSE, height=FALSE)

# client setup code
host = 'localhost'
port = 50012
buf = 1024
addr = (host, port)
clientsocket = socket(AF_INET, SOCK_STREAM)
clientsocket.connect(addr)


def insert(what):
	textbox.insert(END, (what+'\n'))
	text.delete(0,END)


class AutoScrollListBox_demo:
	def __init__(self, master):
		frame = Frame(master, width=1000, height=800, bd=1)
		frame.pack()

		self.listbox_log = Listbox(frame, height=30, width=100)
		self.scrollbar_log = Scrollbar(frame)

		self.scrollbar_log.pack(side=RIGHT, fill=Y)
		self.listbox_log.pack(side=LEFT,fill=BOTH)

		#self.listbox_log.grid(sticky=E+W)
		

		self.listbox_log.configure(yscrollcommand = self.scrollbar_log.set)
		self.scrollbar_log.configure(command = self.listbox_log.yview)

		#b = Button(text="Add", command=self.onAdd)
		#b.pack()

		#Just to show unique items in the list
		self.item_num = 0

	def onAdd(self, what):
		self.listbox_log.insert(END, str(what))       				  #Insert a new item at the end of the list

		self.listbox_log.select_clear(self.listbox_log.size() - 2)   #Clear the current selected item     
		self.listbox_log.select_set(END)                             	  #Select the new item
		self.listbox_log.yview(END)                                  	  #Set the scrollbar to the end of the listbox

		self.item_num += 1
	def prompt(self, what=''):
		self.listbox_log.delete(END, END)
		self.listbox_log.insert(END, str('>> '+what))					  #Insert a new item at the end of the list

		self.listbox_log.select_clear(int(self.listbox_log.size() - 2))   #Clear the current selected item     
		self.listbox_log.select_set(END)                             	  #Select the new item
		self.listbox_log.yview(END)                                  	  #Set the scrollbar to the end of the listbox

		self.item_num += 1


def update(clientsocket, host):
	x=1
	current_line = 0
	while x:
		data = clientsocket.recv(buf)
		if not data:
			pass
		else:
			print 'Recived: ', data
			#insert(data)
			for chunk in data.split('\n'):
				current_line =+ 1
				textbox.onAdd(chunk)
			textbox.onAdd('>> ')
			text.delete(0,END)
			#text.xscrollcommand=30.0
			text.see=current_line
			#print textbox.get(END)

def Button1(arg=1):
	text_contents = text.get()
	textbox.prompt(text_contents)
	print 'You entered: ', text_contents
	clientsocket.send(str(text_contents))
	#textbox.onAdd(text_contents)
	

frame = Frame(root)

button = Button(root, text="Go", command = Button1)
w = Label(frame, text=">>")
text = Entry(frame)
textbox = AutoScrollListBox_demo(root)

root.bind('<Return>', Button1)

button.pack(side=BOTTOM)
w.pack(side='left')
text.pack(side='left')
frame.pack(side=BOTTOM)

textbox.listbox_log.grid(row=0, column=0)
textbox.listbox_log.grid(sticky='nsew')
text.grid(row=1, column=0)
button.grid(row=1, column=1)
print 'packing and griding assignment finished'


textbox.onAdd('User type: ')
textbox.onAdd(textbox.listbox_log.size())
text.delete(0,END)

thread.start_new_thread(update, (clientsocket, host))

root.title("MUDINIC Client")
print 'title set, starting mainloop'
root.mainloop()
