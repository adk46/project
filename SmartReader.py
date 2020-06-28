# 2020-05-31 v1.2 allow block by registration date
# 2020-06-27 v1.3 update
from lxml import html
import requests
from os import path 
import re
#import sys
import tkinter as tk
import tkinter.font as tkFont
import base64
import urllib
from PIL import Image, ImageTk
import io

global show_num 
show_num = 10
global blocked_IDs
blocked_IDs=[]
msg = []
color = []
lz = []
post_num = []
global show_quote
show_quote = 1
main_page = []
pageNum = 1
show_pages = []
global bg_color
bg_color='#fbf4cd'
global owner_post
owner_post = 'purple'
global other_post
other_post = 'blue'
global font_size
font_size=14
global pic
pic=list()
global block_id_by_date
block_id_by_date = 0
global block_id_post_date
block_id_post_date='2099-12-31'

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

    def __init__(self, parent, top_panel):
        self.parent = parent
        self.labelframe = top_panel
        self.create_widgets()


        
    def create_widgets(self):
        global show_pages, show_num
        print('create widgets show_num = ', show_num)
        self.label = tk.Label(self.labelframe, text="Please enter post link here:", anchor = "e", width = 30).grid(row=0, column = 0)

        self.entry = tk.Entry(self.labelframe, width = 70)
        self.entry.grid(row=0, column = 1)

        self.button1 = tk.Button(self.labelframe, text="Load Page", command=self.get_input, width = 10).grid(row=0, column = 2, padx=(8,5))
        self.prev_btn = tk.Button(self.labelframe, text="<<", command=self.get_prev, width = 3 )
        self.prev_btn.grid(row=0, column = 3, padx=(10,5))
        show_pages = tk.StringVar()
        show_pages.set("Page: fr ~ to")
        self.curr_btn = tk.Label(self.labelframe, textvariable=show_pages, width = 12)
        self.curr_btn.grid(row=0, column = 4, padx=(5,5))
        self.next_btn = tk.Button(self.labelframe, text=">>", command=self.get_next, width = 3)
        self.next_btn.grid(row=0, column = 5, padx=(5,10))
        
        self.page_label = tk.Label(self.labelframe, text="Pages per load:", anchor = "e", width = 20)
        self.page_label.grid(row=0, column = 6)
        self.page_per_load = tk.IntVar()
        self.page_per_load.set(show_num)
        self.load_entry = tk.Entry(self.labelframe, textvariable=self.page_per_load, width = 3)
        self.load_entry.grid(row=0, column = 7)
        
        self.quote_btn = tk.Button(self.labelframe, text="Hide Quote", command=self.set_quote_flag, width = 10)
        self.quote_btn.grid(row=0, column = 8, padx=(15,10))

        self.textframe = tk.LabelFrame(self.parent)
        self.textframe.pack(fill="both", expand=True, side='bottom')   
        
        self.text = tk.Text(self.textframe, height=700, width=500)
        self.text.configure(bg = bg_color)
        self.text.tag_configure('owner', foreground='#e07b39', font=('Tempus Sans ITC', 12, 'bold'))
        self.text.tag_configure('poster', foreground='green', font=('Tempus Sans ITC', 12, 'bold'))
        self.text.tag_configure('other_post', foreground=other_post, font=('KaiTi', font_size))            
        self.text.tag_configure('owner_post', foreground=owner_post, font=('KaiTi', font_size)) 
        self.text.tag_configure('quote', foreground='grey', font=('Tempus Sans ITC', 10))  
        self.text.mark_set("refresh", "1.1")        

    def check_show_num(self):
        global show_num 
        try:
            update = self.page_per_load.get()
        except ValueError:
            print("expect an integer between 2-20")
        else:
            if ( update > 1 and update < 20):
                show_num = update
                
    def get_input(self):       
        value = self.entry.get()
        print('link:', value)
        self.get_link(value)  
        self.check_show_num()
    
    def get_prev(self):
        self.check_show_num()
        global pageNum, show_num             

        batch = int((pageNum-1)/show_num)
        if ((pageNum - 1)%show_num == 0):
            batch -= 1
        print("batch = ", batch, " page num", pageNum)
        if (batch > 0):           
            pageNum = (batch -1) * show_num +1
            print("prev page start from ", pageNum)
            self.show_page() 

        
    def get_next(self):
        self.check_show_num()      
        if (self.nextLoc > 0):
            self.show_page()
            
        
    def set_quote_flag(self):
    
        global show_quote
        if (self.quote_btn['text'] == 'Hide Quote'):
            self.quote_btn['text'] = 'Show Quote'
            show_quote = 0
            print("switch to show quote = ", show_quote)
        elif (self.quote_btn["text"] == "Show Quote"):
            self.quote_btn["text"] = "Hide Quote"
            show_quote = 1
            print("swtich to show_quote = ", show_quote)
        
            
    def find_lz(self, link):
        global main_page
        
        loc = link.find("page=")
        main_page = link[:loc-1]
        
        first_page = link[:loc] + 'page=1'
        
        print('first page link:', first_page)
        user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'}
        response = requests.get(first_page, headers=user_agent)
        pageStr = response.content.decode("utf-8")
        response.close()    
        #page = requests.get(first_page)
        #pageStr = page.content.decode("utf-8")
        tree = html.fromstring(pageStr)        
        poster = tree.xpath('//div[@class="name online" or @class="name offline"]/text()')        
        print(poster)
        return poster[0]       
        
        
    def get_link(self, link):
        global lz, pageNum
        
        self.text.delete('1.0', tk.END)
        loc = link.find("page=")
        
        if (loc == -1):
            link += '&page=1'
            loc = link.find("page=")

        lz = self.find_lz(link)
        
        print ('lz : ', lz)
        pageLoc = int(link[loc+5])
        print (pageLoc)

        main = link[:loc+5]
        pageNum = int(link[loc+5:])

        print ('main:', main)
        print ('page num = ', pageNum )
        
        self.show_page()        

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
            post.append(post1)
            pageStr = pageStr[loc_e+6:]
            #print(pageStr)
            match = re.search('<div class="wrap">', pageStr)

        return post
           
    def show_page(self):

        #global root
        global color, lz, pageNum, main_page, show_num
        global show_quote, blocked_IDs
        print('show_page:', pageNum)
        self.text.delete('1.0', tk.END)
        
        show_pages.set("Page: " + str(pageNum) + " ~ " + str(pageNum + show_num -1))

        pageCnt = 0
        self.nextLoc = 1
        while (self.nextLoc > 0 and pageCnt < show_num):
            print("loading page ", pageNum)           
            link = main_page + "&page=" + str(pageNum)
            user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'}
            response = requests.get(link, headers=user_agent)
            pageStr = response.content.decode("utf-8")
            response.close()
            pageStr = re.sub('<br>', '\n', pageStr)
            pageStr = re.sub('<blockquote>', '[quote_s]', pageStr)
            pageStr = re.sub('</blockquote>', '[quote_e]', pageStr)
            
            tree = html.fromstring(pageStr)  
                      
            poster = tree.xpath('//div[@class="name online" or @class="name offline"]/text()')
            
            post = tree.find_class("wrap")   
            #portrait = tree.xpath('//div/img/@src')
            #print('getting portaite')
            #print('portrait = ', portrait)
            #sys.exit()
            floor = re.findall('class="btn btn-link">(.*)<sup>#</sup>', pageStr)
            reg_date = re.findall('注册时间</label><span>@<!-- -->(.*)</span>', pageStr)

            print ('\n == page ',pageNum, ' ==\n')
            self.text.insert(tk.END, "\n === Page " + str(pageNum) + " ===\n", 'poster')
            
            msg = []
            for i in range(len(poster)):
                quote = []
                if (poster[i] in blocked_IDs) :
                    print(poster[i], 'found in blocked list')
                    self.text.insert(tk.END, "\n["+poster[i]+"] "+floor[i]+"# - blocked: find in blocked list\n", 'blocked')
                    color = 'blocked'
                elif block_id_by_date == 1 and reg_date[i] > block_id_post_date:
                    print(poster[i], 'blocked due to registration')
                    self.text.insert(tk.END, "\n["+poster[i]+"] "+floor[i]+"# - blocked: register date later than "+ block_id_post_date + "\n", 'blocked')
                    color = 'blocked'
                else:
                    if (poster[i] == lz):
                        color = 'owner_post'
                        self.text.insert(tk.END, "\n["+poster[i]+"] "+floor[i]+"# ", 'owner')
                    else:
                        color = 'other_post'
                        self.text.insert(tk.END, "\n["+poster[i]+"] "+floor[i]+"# ",'poster')                
                    msg = post[i].text_content()

                    quote_start = msg.find('[quote_s]')
               
                    if (quote_start>=0):                
                        quote_end = msg.rfind('[quote_e]') 
                        quote = msg[quote_start+9:quote_end]
                        msg = msg[:quote_start] + msg[quote_end+9:]
                        quote = quote.replace("[quote_s]", "{").replace("[quote_e]", "}").replace("\n\n", "\n")
                                                                         
                        if (show_quote == 0):
                            match = re.search('(\n.*$)', quote)              
                            if (match):
                                quote = "Re: ...." + match.group(0)
                            
                        self.text.insert(tk.END,quote, 'quote')     

                    print('quote:', quote)                
                    print('msg:', msg)

                    self.text.insert(tk.END,msg +"\n", color)
                
                    self.text.pack(side=tk.LEFT, pady = 15)
                    
                    postStr = str(html.tostring(post[i]))
                    quote_start = postStr.find('[quote_s]')
               
                    if (quote_start>=0):                
                        quote_end = postStr.rfind('[quote_e]') 
                        quote = postStr[quote_start+9:quote_end]
                        postStr = postStr[:quote_start] + postStr[quote_end+9:]
                     
                    #print(postStr)

                    img_loc = postStr.find('<img src')                  

                    if (img_loc >0):
                        tree1 = html.fromstring(postStr)
                        img_links = tree1.xpath('//img/@src')
                        print(postStr)
                        print('img links [', img_links, ']')
                        
                        global pic 
                        
                        for j in range(min(len(img_links),5)):
                            print("img url = [", img_links[j], "]")
                            try:
                                u1 = urllib.request.urlopen(img_links[j]) 
                                image_file = io.BytesIO(u1.read())
                                u1.close()
                                im = Image.open(image_file)
                                [imgWidth, imgHeight] = im.size
                                im = im.resize((int(imgWidth/2), int(imgHeight/2)), Image.ANTIALIAS)
                                img = ImageTk.PhotoImage(image=im)
                                self.text.image_create(tk.END, image=img)
                                self.text.pack(side=tk.LEFT)
                                pic.append(img)
                            except:
                                print('failed to open')
                            #else:

                            
            pageNum += 1
            pageCnt += 1
            nextPage = "page=" + str(pageNum)    
           # print("nextPage = ", nextPage)
            self.nextLoc = pageStr.find(nextPage) 
            
def LoadConfig(cfgFile):
    global show_num, blocked_IDs, show_quote, bg_color, owner_post, other_post
    global block_id_by_date, block_id_post_date,font_size
    block_id_by_date = 0
    f = open(cfgFile, 'r', encoding="utf8")
    for x in f:
        key,value = x.split("=")
        print ('[',key, "],[", value,']')
        if key == "blocked_list":
            blocked_IDs = value.rstrip().split(",")
            print('blocked IDs:', blocked_IDs)
        elif key == "pages_per_load":
            show_num = int(value)
        elif key == "show_quote":
            show_quote = value
        elif key == "background_color":
            bg_color=value.rstrip()
        elif key == 'owner_post':
            owner_post = value.rstrip()
        elif key == 'other_post':
            other_post = value.rstrip()
        elif key == 'font_size':
            font_size = int(value)
        elif key == 'block_id_reg_date':
            if value < '2099-12-31' :
                block_id_by_date = 1
                block_id_post_date = value
 
                
    
# --- main ---

cfgFile = 'Reader.ini'
if (path.exists(cfgFile)):
    LoadConfig(cfgFile)

root = tk.Tk()
root.title("Smart Reader")
root.geometry("1300x750")
fontStyle = tkFont.Font(family="Lucida Grande", size=14)

labelframe = tk.LabelFrame(root, text="Load huaren pages:")
labelframe.pack(fill="both", expand=False, side = 'top')  
        
window = ScrolledFrame(root)
window.pack(expand=True, fill='both', pady=15)

GetLink(window.inner, labelframe)
    

root.mainloop()
