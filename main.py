"""
  Demo interface MongoDB and Amadeus API using python and tkinter
  JLG 08/2021
"""
from datetime import datetime
from amadeus import Client, ResponseError
from pymongo import MongoClient
import tkinter as tk
import tkinter.font as tkfont
from ttkthemes import ThemedTk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from bson.json_util import dumps
from bson.json_util import loads
from bson.objectid import ObjectId
from bson.son import SON
import json

class CrearToolTip(object):
	def __init__(self,elemento,texto='Info del objeto'):
		self.espera = 500
		self.largo = 180
		self.objeto = elemento
		self.texto = texto
		self.objeto.bind("<Enter>",self.entrar)
		self.objeto.bind("<Leave>",self.salir)
		self.objeto.bind("<ButtonPress>",self.salir)
		self.id = None
		self.tw = None
	def entrar(self,event=None):
		self.asignar()
	def salir(self,event=None):
		self.liberar()
		self.ocultar_tip()
	def  asignar(self):
		self.liberar()
		self.id = self.objeto.after(self.espera,self.mostrar_tip)
	def  liberar(self):
		id = self.id
		self.id = None
		if id:
			self.objeto.after_cancel(id)
	def  mostrar_tip(self,event=None ):
		x = y = 0
		x,y,cx,cy = self.objeto.bbox("insert")
		x += self.objeto.winfo_rootx() + 25
		y += self.objeto.winfo_rooty() + 20
		self.tw = tk.Toplevel(self.objeto)
		self.tw.wm_overrideredirect(True)
		self.tw.wm_geometry("+%d+%d"%(x,y))
		label = tk.Label(self.tw,text=self.texto,justify="left",
					             background = "white",relief="solid",borderwidth=1,
								 wraplength = self.largo)
		label.pack(ipadx=1)
	def ocultar_tip(self):
		tw = self.tw
		self.tw = None
		if tw:
			tw.destroy()

def Search_Flight():
    global mycol,nflights
    AptDep=Dep_entry.get()
    AptArr=Arr_entry.get()
    FecVol=Date_entry.get()
    Adults=Adu_entry.get()
    Childs=Chl_entry.get()
    Infants=Inf_entry.get()
    Max=10;
    NonStop='false'
    mycol.drop() 
    nflights=0
    Flight_Offers_Search(AptDep,AptArr,FecVol,Adults,Childs,Infants,Max,NonStop) 
    FecVol=Date0_entry.get()
    Flight_Offers_Search(AptArr,AptDep,FecVol,Adults,Childs,Infants,Max,NonStop) 
    now = datetime.now() 
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    texto = tk.StringVar()
    texto.set(" Flights found: " + str(nflights) + " "*220 + date_time)
    statusbar1.config(textvariable=texto) 
    

# MongoDB
try:
  mymongo=MongoClient() 
  mydb   =mymongo.Amadeus
  mycol  =mydb.flight_offers
except  pymongo.errors.PyMongoError as e:
  messagebox.showwarning(title="Error", message="MongoDB error .." + str(e)) 
  
def Query(): 
  global mycol
  
  myqueryS = 'mycol.'+MDB_entry.get(1.0, tk.END)
  myqueryS = myqueryS.replace("\n", "")
  print (myqueryS)
  MDB_edit.delete('1.0', tk.END)
  try:
       mydoc = eval( myqueryS  ) 
  except  (SyntaxError, NameError, TypeError, ZeroDivisionError) as e:
       messagebox.showwarning(title="Error", message="Error executing MQL command ..." + str(e))  
       return 
  print (type(mydoc))
   
  json_str = dumps(mydoc, indent = 2)
  MDB_edit.insert(tk.INSERT,json_str)
  
def Query_MongoDB(): 
  global mycol
  global treev
  myqueryS = 'mycol.'+'find({ "$and":[ {"$expr":{"$gte":[{"$toDouble":"$price.grandTotal"}, '+low_price_entry.get()+'   ]}}, {"$expr":{"$lte":[{"$toDouble":"$price.grandTotal"}, '+hight_price_entry.get()+'    ]}} ]  } )'
  try:
       mydoc = eval( myqueryS  ) 
  except  (SyntaxError, NameError, TypeError, ZeroDivisionError) as e:
       messagebox.showwarning(title="Error", message="Error executing MQL command ..." + str(e))  
       return 
  
  i=0
  j=1
  treev.delete(*treev.get_children())
  for (flight ) in mydoc:
       du=flight['itineraries'][0]['duration'][2: ] 
       pr=flight['price']
       ac=flight['validatingAirlineCodes']
       
       treev.insert(parent='', index=i, iid=i, values=(str(j), ac[0] ,du, pr['total']  ) )
       i=i+1 
       j=j+1
       itine=flight['itineraries']
       for (it ) in itine:
             du=it['duration']
             segm=it['segments']
             for (seg) in segm:
                   dep  =seg['departure']['iataCode']
                   atdep=seg['departure']['at'].replace('T', ' ', 1)
                    
                   arr  =seg['arrival']['iataCode']
                   atarr=seg['arrival']['at'].replace('T', ' ', 1)
                   carrier=seg['carrierCode']
                   flight_n=seg['number']
                   dus=seg['duration']
                   treev.insert(parent='', index=i, iid=i, tags=('1'),values=('', '' ,'', '',carrier+'-'+flight_n,dep+ '-'+ arr,atdep,atarr,dus[2: ] ) )
                   i=i+1             
       tvp=flight['travelerPricings']
       for tv in tvp:
                 tvt=tv['travelerType']
                 tid=tv['travelerId']
                 tvdetail=tv['fareDetailsBySegment']
                 for tvd in tvdetail:
                     cabin=tvd['cabin']
                     clase=tvd['class']
       i=i+1
  texto = tk.StringVar()
  texto.set(" Flights found: " + str(j-1)        )
  statusbar2.config(textvariable=texto)

#Amadeus API 
amadeus = Client(
    client_id=<your client ID>,
    client_secret=< your secret key>  )
    
def Flight_Offers_Search(AptDep,AptArr,FecVol,Adults,Childs,Infants,Max,NonStop):
  global nflights
  try:
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode=AptDep,
        destinationLocationCode=AptArr,
        departureDate=FecVol,
        adults=Adults,
        children=Childs,
        infants=Infants,
        max=Max,
        nonStop=NonStop)
  except ResponseError as error:
    print('Error: ' ) ; print(error)
  txt_edit.insert(tk.INSERT,'\n'+AptDep+'-'+AptArr+'  ' + FecVol +'\n')
  if 'response' in locals():
    resp=response.data
    for flight in resp:
     try:
        mycol.insert_one(flight)
        nflights=nflights+1
     except  pymongo.errors.PyMongoError as e:
        messagebox.showwarning(title="Error", message="MongoDB error .." + str(e)) 
     du=flight['itineraries'][0]['duration'][2: ] 
     du=du.rjust(7)
     pr=flight['price']
     ac=flight['validatingAirlineCodes']
     txt_edit.insert(tk.INSERT,' Airline: '+ ac[0] + ' Duration: ' + du +
                                 ' Price: '+pr['total']+' ' +
                               ' Base: ' + pr['base'] + ' Others: ' + 
                               str(round(float(pr['total']) - float(pr['base']),2)) +  ' ' + pr['currency'] + '\n' )
                     

def center_window(w=1200, h=640):
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws/2) - (w/2)    
    y = (hs/2) - (h/2) - 40
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))

def conf(event):
    notebook.config(height=window.winfo_height(),width=window.winfo_width()-30) 
                               
# GUI
window = ThemedTk(theme='scidblue')
window.title("Amadeus API Demo")
center_window(880, 610)
style = ttk.Style(window)
window.bind("<Configure>",conf)


# create a notebook
s = ttk.Style()
s.configure('TNotebook.Tab', font=('Times','10' ) )
notebook = ttk.Notebook(window)
notebook.pack(padx=0,pady=0,  expand = 1, fill ="both")
# create frames
frame1 = ttk.Frame(notebook )
frame3 = ttk.Frame(notebook)
frame2 = ttk.Frame(notebook)
frame3 = ttk.Frame(notebook)
frame1.pack(fill='both', expand=True)
frame2.pack(fill='both', expand=True)
frame3.pack(fill='both', expand=True)
# add frames to notebook
notebook.add(frame1, text='  Search Amadeus  ')
notebook.add(frame3, text=' Query Mongo ')
notebook.add(frame2, text=' MQL Mongo ')
# End notebook section
 
#First Tab
statusbar1 = tk.Label(frame1, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, width=450,height=1,font=('Lucida', 9,'bold'), background = "#7F8F9A",foreground = "white")
statusbar1.pack(side=tk.BOTTOM, fill=tk.Y)

fr_search0 = tk.Frame(frame1, relief=tk.RAISED, bd=0 )
fr_search0.pack(side=tk.LEFT, fill=tk.Y)

fr_search = tk.Frame(fr_search0, relief=tk.RAISED, bd=0 )
fr_search.pack(side=tk.TOP, fill=tk.Y)

Dep_label = tk.Label(fr_search,width=10,text="Departure:",font=('Lucida', 9,'bold'),anchor='e') 
Dep_label.grid(row=0, column=0,   padx=0, pady=(5,1))
Dep_entry = ttk.Entry(fr_search,width=4,font=('Lucida', 9,'bold')  )   ; Dep_entry.insert(0, "PMI") 
Dep_entry.grid(row=0, column=1,   padx=0, pady=(5,1))

Arr_label = tk.Label(fr_search,width=10,text="Arrival:",font=('Lucida', 9,'bold'),anchor='e') 
Arr_label.grid(row=1, column=0,   padx=5, pady=1)
Arr_entry = ttk.Entry(fr_search,width=4,font=('Lucida', 9,'bold'))    ; Arr_entry.insert(0, "BSL")   
Arr_entry.grid(row=1, column=1,   padx=0, pady=1)

Date_label = tk.Label(fr_search,width=10,text="Dep. Date:",font=('Lucida', 9,'bold'),anchor='e') 
Date_label.grid(row=2, column=0,   padx=5, pady=1)
Date_entry = ttk.Entry(fr_search,width=10,font=('Lucida', 9,'bold'))   ; Date_entry.insert(0, "2021-09-09")     
Date_entry.grid(row=2, column=1,   padx=(0,5), pady=1)

Date0_label = tk.Label(fr_search,width=10,text="Arr. Date:",font=('Lucida', 9,'bold'),anchor='e') 
Date0_label.grid(row=3, column=0,   padx=5, pady=1)
Date0_entry = ttk.Entry(fr_search,width=10,font=('Lucida', 9,'bold'))   ; Date0_entry.insert(0, "2021-09-11")     
Date0_entry.grid(row=3, column=1,   padx=(0,5), pady=1)

Adu_label = tk.Label(fr_search,width=10,text="Adults:",font=('Lucida', 9,'bold'),anchor='e') 
Adu_label.grid(row=4, column=0,   padx=5, pady=1)
Adu_entry = ttk.Entry(fr_search,width=3,font=('Lucida', 9,'bold'),justify='right' )   ; Adu_entry.insert(0, "2") 
Adu_entry.grid(row=4, column=1,   padx=0, pady=1)

Chl_label = tk.Label(fr_search,width=10,text="Childs:",font=('Lucida', 9,'bold'),anchor='e') 
Chl_label.grid(row=5, column=0,   padx=5, pady=1)
Chl_entry = ttk.Entry(fr_search,width=3 ,font=('Lucida', 9,'bold'),justify='right')   ; Chl_entry.insert(0, "1") 
Chl_entry.grid(row=5, column=1,   padx=0, pady=1)

Inf_label = tk.Label(fr_search,width=10,text="Infants:",font=('Lucida', 9,'bold'),anchor='e') 
Inf_label.grid(row=6, column=0,   padx=5, pady=1)
Inf_entry = ttk.Entry(fr_search,width=3,font=('Lucida', 9,'bold'),justify='right' )   ; Inf_entry.insert(0, "0") 
Inf_entry.grid(row=6, column=1,   padx=0, pady=1)

fr_search1 = tk.Frame(fr_search0, relief=tk.RAISED, bd=0 )
fr_search1.pack(side=tk.TOP, fill=tk.Y)
btn_open = tk.Button(fr_search1, text=" Search Amadeus ",font=('Lucida', 9,'bold'), command=Search_Flight)
btn_open.focus_set()
CrearToolTip(btn_open," Search flights in Amadeus ")
btn_open.grid(row=0, column=0,   padx=5, pady=10)

txt_edit = scrolledtext.ScrolledText(frame1,font=('Lucida console', 10), width = 90, height = 40,
           background = "#243642",foreground = "white",insertbackground="red")
txt_edit.pack(side=tk.LEFT, fill=tk.Y)

#End First Tab


#Second  tab

statusbar2 = tk.Label(frame3, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, width=450,height=1,font=('Lucida', 9,'bold'), background = "#7F8F9A",foreground = "white")
statusbar2.pack(side=tk.BOTTOM, fill=tk.Y)

fr_query = tk.Frame(frame3, relief=tk.RAISED, bd=0 )
fr_query.pack(side=tk.LEFT, fill=tk.Y)

fr_query0 = tk.Frame(fr_query, relief=tk.RAISED, bd=0 )
fr_query0.pack(side=tk.TOP, fill=tk.Y)

low_price_label = tk.Label(fr_query0,width=10,text="Low Price:",font=('Lucida', 9,'bold'),anchor='e') 
low_price_label.grid(row=0, column=0,   padx=5, pady=1)
low_price_entry = ttk.Entry(fr_query0,width=7,font=('Lucida', 9,'bold') )     ; low_price_entry.insert(0, '50') 
low_price_entry.grid(row=0, column=1,   padx=5, pady=(5,1))

hight_price_label = tk.Label(fr_query0,width=10,text="Hight Price:",font=('Lucida', 9,'bold'),anchor='e') 
hight_price_label.grid(row=1, column=0,   padx=5, pady=1)
hight_price_entry = ttk.Entry(fr_query0,width=7 ,font=('Lucida', 9,'bold'))   ; hight_price_entry.insert(0, '10000') 
hight_price_entry.grid(row=1, column=1,   padx=5, pady=1)

fr_query1 = tk.Frame(fr_query, relief=tk.RAISED, bd=0 )
fr_query1.pack(side=tk.TOP, fill=tk.Y)
btn_MDB = tk.Button(fr_query1, text=" Query MongoDB ", command=Query_MongoDB,font=('Lucida', 9,'bold'))
btn_MDB.focus_set()
CrearToolTip(btn_MDB," Query flights in MongoDB ")
btn_MDB.grid(row=0, column=0,   padx=15, pady=5)

###

tree_frame = tk.Frame(frame3, bd=0, relief=tk.SOLID)
tree_frame.pack(side=tk.LEFT, fill=tk.Y)
treev = ttk.Treeview(tree_frame, columns=(1,2,3,4,5,6,7,8,9), show='headings', height=25 )
 
header_font = tkfont.Font(family='TimesNewRoman', size=9,weight="bold") 
s0 = ttk.Style()
s0.configure("Treeview.Heading", font=header_font, rowheight=int(12*2.5)) 
treev.tag_configure('0', background='#E8E8E8')
treev.tag_configure('1', background='#DFDFDF')
 
treev.pack(side=tk.LEFT, fill=tk.Y)
treev.heading(1, text="ID")       ; treev.column(1, minwidth=0, width=25,  stretch=tk.YES)
treev.heading(2, text="Airline")  ; treev.column(2, minwidth=0, width=45,  stretch=tk.YES)
treev.heading(3, text="Duration") ; treev.column(3, minwidth=0, width=70,  stretch=tk.NO)
treev.heading(4, text="Price")    ; treev.column(4, minwidth=0, width=70,  stretch=tk.NO)
treev.heading(5, text="Flight")   ; treev.column(5, minwidth=0, width=70,  stretch=tk.NO)
treev.heading(6, text="Route")    ; treev.column(6, minwidth=0, width=75,  stretch=tk.NO)
treev.heading(7, text="Time Dep "); treev.column(7, minwidth=0, width=120, stretch=tk.NO)
treev.heading(8, text="Time Arr") ; treev.column(8, minwidth=0, width=120, stretch=tk.NO)
treev.heading(9, text="Duration") ; treev.column(9, minwidth=0, width=80,  stretch=tk.NO)

sb = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
sb.pack(side=tk.RIGHT, fill=tk.Y)
treev.config(yscrollcommand=sb.set)
sb.config(command=treev.yview)

#End second tab

#Third tab

fr_mdb = tk.Frame(frame2, relief=tk.RAISED, bd=0 )
fr_mdb.pack(side=tk.TOP, fill=tk.Y)

MDB_entry = scrolledtext.ScrolledText(fr_mdb, font=('Lucida console', 10), width = 106, height = 4,
           background = "#243642",foreground = "white",insertbackground="red",bd=1)
MDB_entry.insert(tk.INSERT, 'find({"$expr":{"$lte":[{"$toDouble":"$price.grandTotal"},350.0]}},{"_id":0})') 
MDB_entry.grid(row=0, column=0,   padx=0, pady=5)
 
btn_MDB0 = tk.Button(fr_mdb, text=" Exec MQL MongoDB ", command=Query,font=('Lucida', 9,'bold'))
btn_MDB0.focus_set()
CrearToolTip(btn_MDB0," Execute MQL in MongoDB ")
btn_MDB0.grid(row=1, column=0,   padx=5, pady=5)

MDB_edit = scrolledtext.ScrolledText(frame2,font=('Lucida console', 10), width = 106, height = 40,
           background = "#243642",foreground = "white",insertbackground="red")
MDB_edit.pack(side=tk.TOP, fill=tk.Y)

#End Third Tab
 
window.mainloop()
