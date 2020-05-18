from lxml import html
import lxml.etree as et
import requests
import pandas as pd
import os 
import re
import sys
import tkinter as tk
import tkinter.font as tkFont

msg = []
root = []
color = []
lz = []
post_num = []

# --- classes ---

class ScrolledFrame(tk.Frame):

    def __init__(self, parent, vertical=True, horizontal=False):
        super().__init__(parent)

        # canvas for inner frame
        self._canvas = tk.Canvas(self)
        self._canvas.grid(row=0, column=0, sticky='news') # changed

        # create right scrollbar and connect to canvas Y
        self._vertical_bar = tk.Scrollbar(self, orient='vertical', command=self._canvas.yview)
        if vertical:
            self._vertical_bar.grid(row=0, column=1, sticky='ns')
        self._canvas.configure(yscrollcommand=self._vertical_bar.set)

        # create bottom scrollbar and connect to canvas X
        self._horizontal_bar = tk.Scrollbar(self, orient='horizontal', command=self._canvas.xview)
        if horizontal:
            self._horizontal_bar.grid(row=1, column=0, sticky='we')
        self._canvas.configure(xscrollcommand=self._horizontal_bar.set)

        # inner frame for widgets
        self.inner = tk.Frame(self._canvas, bg='red')
        self._window = self._canvas.create_window((0, 0), window=self.inner, anchor='nw')

        # autoresize inner frame
        self.columnconfigure(0, weight=1) # changed
        self.rowconfigure(0, weight=1) # changed

        # resize when configure changed
        self.inner.bind('<Configure>', self.resize)
        self._canvas.bind('<Configure>', self.frame_width)

    def frame_width(self, event):
        # resize inner frame to canvas size
        canvas_width = event.width
        self._canvas.itemconfig(self._window, width = canvas_width)

    def resize(self, event=None): 
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))

class GetLink:

    def __init__(self, parent, link):
        self.parent = parent
        self.link = link
        self.create_widgets()

    def get_input(self):
        value = self.entry.get()
        print('link:', value)
        self.get_link(value)
    
    def load_more():
        return
        
    def create_widgets(self):
        self.labelframe = tk.LabelFrame(self.parent, text="Load huaren pages:                      ")
        self.labelframe.pack(fill="both", expand=True)

        self.label = tk.Label(self.labelframe, text=self.link)
        self.label.pack(expand=True, fill='both')

        self.entry = tk.Entry(self.labelframe)
        self.entry.pack()

        self.button = tk.Button(self.labelframe, text="Upload", command=self.get_input)
        self.button.pack()       
        
        self.text = tk.Text(self.labelframe, height=400, width=500, bg = "#fbf4cd")
        #self.text.insert(tk.END, "Test", 'color')
        #self.text.pack(side=tk.LEFT)
        #scroll = tk.Scrollbar(self.labelframe, command=self.text.yview)
        #self.text.configure(yscrollcommand=scroll.set)
        self.text.tag_configure('bold_italics', font=('Arial', 12, 'bold', 'italic'))
        self.text.tag_configure('big', font=('Verdana', 14, 'bold'))
        self.text.tag_configure('owner', foreground='#e07b39', font=('SimHei', 14, 'bold'))
        self.text.tag_configure('poster', foreground='green', font=('SimHei', 14, 'bold'))
        self.text.tag_configure('other_post', foreground='blue', font=('KaiTi', 14))            
        self.text.tag_configure('owner_post', foreground='purple', font=('KaiTi', 14)) 
        self.text.tag_configure('quote', foreground='grey', font=('Tempus Sans ITC', 10))            

    def get_link(self, link):
        self.text.delete('1.0', tk.END)
        loc = link.find("page=")
        
        if (loc == -1):
            link += '&page=1'
            loc = link.find("page=")

        print (loc)
        pageLoc = int(link[loc+5])
        print (pageLoc)

        main = link[:loc+5]
        pageNum = int(link[loc+5:])

        print ('main:', main)
        print ('page num = ', pageNum )
            
        oldSize = 0
        

        newSize = self.show_page(link, pageNum)

        #print('page size:', newSize)

        #while abs(newSize - oldSize) > 1:
        while newSize > 0:
            oldSize = newSize
            pageNum += 1
            newLink = main + str(pageNum)
            #print(newLink)
            newSize = self.show_page(newLink, pageNum)
           # print('page size:', newSize)

    def get_post(self, pageStr):
        post = []
        match = re.search('<div class="wrap">', pageStr)
        print (match)
        while (match ):
            pageStr = pageStr[match.span()[1]:]
            #print(pageStr)
            loc_e = pageStr.find('</div>')
            #print(loc_e)
            post1 = pageStr[:loc_e]
            #print(post)
            #post.append(clean_url(post1))
            post.append(post1)
            pageStr = pageStr[loc_e+6:]
            #print(pageStr)
            match = re.search('<div class="wrap">', pageStr)

        return post
           
    def show_page(self, link, pageNum):

        global root
        global color, lz
        
        page = requests.get(link)
        pageStr = page.content.decode("utf-8")
        #print(pageStr)
        print("============================")
        #pageStr = re.sub(r"<a.href[^>]*>|</a>", "", pageStr)
        #pageStr = re.sub('\<a href=.*?>(.*?)\</a>', '', pageStr)
        #pageStr = re.sub('<a href.*[.|"]>', '', pageStr)
        #pageStr = re.sub('<img src.*[.|"]>', '', pageStr)
        #pageStr = re.sub('</a>', '', pageStr)
        pageStr = re.sub('<br>', '\n', pageStr)
        pageStr = re.sub('<blockquote>', '[quote_s]', pageStr)
        pageStr = re.sub('</blockquote>', '[quote_e]', pageStr)
        if (pageNum==430):
            print(pageStr)

        #sys.exit()
        tree = html.fromstring(pageStr)  
                  
        poster = tree.xpath('//div[@class="name online" or @class="name offline"]/text()')        
        post = tree.find_class("wrap")      
        #post = self.get_post(pageStr)  
        
        #print(poster)
        if (pageNum == 1):
            title = tree.find_class("topic-title")
            print('** [title]  [', title[0].text_content(), ']')
            lz = poster[0]
        #post = tree.xpath('/div[@class="wrap"]/text()')

        print ('\n == page ',pageNum, ' ==\n')
        self.text.insert(tk.END, "\n === page " + str(pageNum) + "===\n", 'poster')
        #self.label = tk.Label(self.labelframe, font=fontStyle, justify=tk.LEFT, text="== page " + str(pageNum) + " ==", fg = "green").pack()
        msg = []
        for i in range(len(poster)):
            quote = []
            print('[', poster[i], ']')
            if (poster[i] == lz):
                color = 'owner_post'
                self.text.insert(tk.END, "\n["+poster[i]+"]", 'owner')
            else:
                color = 'other_post'
                self.text.insert(tk.END, "\n["+poster[i]+"]",'poster')

            msg = post[i].text_content()  

            #msg = re.sub('<br>', '\n', msg)
            
            loc0 = msg.find('[quote_s]')
       
            if (loc0>=0):
                loc = msg.find('[quote_e]')
                quote = msg[loc0+9:loc]
                if (loc0 == 0):
                    msg = msg[loc+9:]
                else:
                    msg = msg[:loc0]  
                    
                #quote = re.sub('<.*/.*>', '', quote)                               
                match = re.search('(\n.*$)', quote)
               
                if (match):
                    quote = "Re: ...." + match.group(0)
                    quote = re.sub('\n', '', quote)

                    
                self.text.insert(tk.END,quote, 'quote')     

                #msg = re.sub('<.*/.*>', '', msg)
            print('quote:', quote)                
            print('msg:', msg)

            self.text.insert(tk.END,msg +"\n", color)
        
            self.text.pack(side=tk.LEFT, pady = 15)
            
            if (i%5 == 0):
                self.button = tk.Button(self.labelframe, text="Load more", command=self.load_more)
           
        nextPage = "page=" + str(pageNum+1)    
       # print("nextPage = ", nextPage)
        nextLoc = page.text.find(nextPage) 
        #sys.exit()
       # print(nextLoc)
        if (nextLoc == -1):
            return nextLoc
        else:
            return len(page.text)
            
# --- main ---

root = tk.Tk()
root.title("Smart Reader")
root.geometry("1300x750")
fontStyle = tkFont.Font(family="Lucida Grande", size=14)

window = ScrolledFrame(root)
window.pack(expand=True, fill='both', pady=15)

GetLink(window.inner, "Please enter huaren link here: ")
    

root.mainloop()
