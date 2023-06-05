import tkinter as tk
import hypixel_helper

class App:
    def __init__(self, master):
        master.geometry("1000x325")
        self.label = tk.Label(root, text="API Key")
        self.label.pack()
        self.entry = tk.Entry(root,width=30)
        self.entry.pack()
        self.button = tk.Button(root, text = 'Enter',command = lambda: self.helperMethod(self.entry.get()))
        self.button.pack()

    def helperMethod(self,apiKey):
        frame=tk.Frame(root, width=1000, height=325)
        frame.pack()
        self.v=tk.Scrollbar(frame, orient='vertical')
        self.h=tk.Scrollbar(frame, orient='horizontal')
        self.text=tk.Text(frame,  wrap= "none")
        self.text.place(x=0, y=0, height=325, width=1000)
        self.v.config(command=self.text.yview)
        self.h.config(command=self.text.xview)
        self.label.destroy()
        self.entry.destroy()
        self.button.destroy()
        self.p1 = hypixel_helper.Player(apiKey)
        self.Refresher()

    def Refresher(self): 
        a = self.p1.formatNicerLol()
        if a != None:
            self.text.config(state= tk.NORMAL)
            self.text.delete("1.0","end")
            self.text.insert(tk.END, a)
            root.title(self.p1.getServer())
        self.text.config(state= tk.DISABLED)
        root.after(2000, self.Refresher)

root = tk.Tk()
app = App(root)
root.mainloop()
