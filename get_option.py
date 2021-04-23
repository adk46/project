from urllib.request import urlopen
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import requests
from lxml import html
import pandas as pd
import subprocess

class OptionPrice:
  def __init__(self, price, df_call, df_put):
     self.price = price
     self.df_call = df_call
     self.df_put = df_put

  
def get_table(link, user_agent, idx):
    response = requests.get(link, headers=user_agent)
    pageStr = response.content
    df_list = pd.read_html(pageStr)
  
    df_call = df_list[0]
    df_call = df_call[df_call['Volume'] >10]
    df_put = df_list[1]
    df_put = df_put[df_put['Volume'] >10]    
    
    #print(df.head())
    response.close()
    
    return df
    '''
    i = 8
    print(len(df_list[8].columns))
    while len(df_list[i].columns) == 5:
        print(df_list[i])
        i += 1
    #tree = html.fromstring(pageStr)  
    #print(tree)
    #topic = tree.find_class(  
    #print(topic) 
    response.close()
    '''
    
def get_data(link, user_agent, ttl_pages, tbl_loc):

    response = requests.get(link, headers=user_agent)
    pageStr = response.content.decode("utf-8")
    #print(pageStr)

        
    df_list = pd.read_html(pageStr)
  
    df_call = df_list[0]
    #df_call = df_call[df_call['Last Price'] >0.5]
    #df_call = df_call.nlargest(5, 'Volume')
    #df_call = df_call['Volume'].sort_values(ascending=False).head(5)
    df_put = df_list[1]
    #df_put = df_put.nlargest(5, 'Volume')
    #df_put = df_put[df_put['Last Price'] >0.5]    
    
    fname = 'call.csv'
    df_call.to_csv(fname, index=False)
    fname = 'put.csv'
    df_put.to_csv(fname, index=False)
    #print(df.to_string())

    
    pricePrefix = 'data-reactid="50">'
    loc = pageStr.find(pricePrefix)
    pageStr = pageStr[loc:loc+100]
    #print(pageStr)
    loc_e = pageStr.find('</span>')
    #print(loc_e)
    price = float(pageStr[len(pricePrefix):loc_e])
    
    result = subprocess.run(['date', '+"%Y-%m-%d %X"'], capture_output=True, text=True)
    timestamp = result.stdout
    timestamp = timestamp.replace('"', '')
    print(timestamp)    
 
    print(timestamp, 'Price ', price)    
    
    df_call = df_call[df_call['Strike'] < price+2]
    
    df_call = df_call[df_call['Strike'] > price -3]
    df_call = df_call.drop(df_call.columns[[0, 1, 4,5]], axis=1)
    df_call = df_call.sort_values(by=['Strike'], ascending=True)
    
    df_put = df_put[df_put['Strike'] > price-2]
    
    df_put = df_put[df_put['Strike'] < price+3]
    df_put = df_put.drop(df_put.columns[[0, 1, 4,5]], axis=1)
    df_put = df_put.sort_values(by=['Strike'], ascending=True)

    
    print('call\n', df_call.to_string())
    print('put\n', df_put.to_string())
    
    return OptionPrice(price, df_call, df_put)


def refresh():
    print('refresh')
    user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'}

    #link_overview = "https://finviz.com/screener.ashx?v=111&f=geo_usa&ft=4"
    ticker = 'viac'
    link = 'https://finance.yahoo.com/quote/'+ticker+'/options?p='+ticker
        #link = 'https://finviz.com/screener.ashx?v=' + k + '&f=geo_usa,ind_stocksonly,sh_curvol_o5000'
    option = get_data(link, user_agent, 16, 14)    
    show_data(option)


def show_data(option):

    cols = list(option.df_call.columns)
    result = subprocess.run(['date', '+"%Y-%m-%d %X"'], capture_output=True, text=True)
    timestamp = result.stdout
    timestamp = timestamp.replace('"', '')
    label = tk.Label(width = 57, height = 1, text = timestamp + "Price" + str(option.price))
    label.pack()
    
    show_df(option.df_call, "Call")
    show_df(option.df_put, "Put")
    
def show_df(df, type):
    label = tk.Label(width = 17, height = 1, text = type )
    label.pack()

    tree = ttk.Treeview(root)
    tree.pack()
    cols = list(df.columns)
    tree["columns"] = cols
    for i in cols:
        tree.column(i, anchor="w")
        tree.heading(i, text=i, anchor='w')

    for index, row in df.iterrows():
        tree.insert("",0, values=list(row))
    
root = tk.Tk()
        
        
root.title("VIAC Option")
root.geometry("1600x500")

labelframe = tk.LabelFrame(root, text="Load option values:")
labelframe.pack(fill="both", expand=False, side = 'top')  
#button = tk.Button(labelframe, text="Refresh", command=refresh(), width = 10).grid(row=0, column = 2, padx=(8,5))
button = tk.Button(text="Refresh", command=refresh, width = 10)
button.pack()
refresh()
root.mainloop()
  

