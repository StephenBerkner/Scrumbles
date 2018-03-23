import tkinter as tk
from tkinter import ttk
import ScrumblesFrames


class ItemManagerView(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller =  controller

		self.usernameLabel = tk.Label(self, text = "Item Manager", font = ("Verdana", 12))
		self.usernameLabel.pack(side = tk.TOP, fill = tk.X)

		self.tabButtons = ScrumblesFrames.STabs(self, controller, "Item Manager View")
		self.tabButtons.pack(side=tk.TOP, fill=tk.X)

		self.itemList = ScrumblesFrames.SList(self, "ITEMS")
		self.itemList.listbox.bind('<<ListboxSelect>>', lambda event: self.dynamicEventHandler(event))

		# self.grid(row = 1, column = 0)

		self.items = self.controller.dataBlock.items
		self.itemNames =[item.itemTitle for item in self.controller.dataBlock.items]

		self.itemList.importList(self.itemNames)
		self.itemList.pack(side = tk.LEFT, fill = tk.Y)



		self.commentField = ScrumblesFrames.commentsField(self)
		self.commentField.pack(side = tk.RIGHT, fill = tk.Y, padx = 20, pady = 20, ipadx = 5, ipady = 5)

		self.itemEditor = ScrumblesFrames.itemPicker(self)
		self.itemEditor.pack(side = tk.LEFT, fill = tk.BOTH, padx = 20, pady = 20, ipadx = 5, ipady = 5)

	def dynamicEventHandler(self, event):
		index = self.itemList.listbox.curselection()
		# print(self.itemList.listbox.get(index))
		# # print(self.itemList.listbox.get(index).itemTitle)
		# print(self.items[0].itemType)
		# print(self.items[0].getTitle())

		self.itemEditor.load_items(self.itemList.listbox.get(index), self.items[index[0]].getDescription(), self.items[index[0]].getStatus(), self.items[index[0]].getPriority() )


		print("item Selected")

		