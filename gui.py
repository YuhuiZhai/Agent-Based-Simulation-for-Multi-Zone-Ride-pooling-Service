print("Importing library 1/4")
from importlib.resources import path
from tarfile import CompressionError
from tkinter import *
from tokenize import String
print("Importing library 2/4")
from taxi_simul.simulation import Simulation
print("Importing library 3/4")
from city import City 
print("Importing library 4/4")
from tkinter import filedialog
print("Welcome to simulation")
root = Tk()
root.title("Transit Simulation Demo")
root.geometry('500x700')
# Part of simulation type
frame1 = LabelFrame(root, text="Simulation type", padx=5, pady=5)
frame1.pack(padx=5, pady=5)
simul_type = StringVar()
simul_type.set("homogeneous")
Radiobutton(frame1, text="homogeneous", variable=simul_type, value="homogeneous").grid(row=0, column=0)
Radiobutton(frame1, text="heterogeneous", variable=simul_type, value="heterogeneous").grid(row=1, column=0)

# Part of fleet parameter
frame2 = LabelFrame(root, text="Fleet info", padx=5, pady=5)
frame2.pack(padx=5, pady=5)
Label(frame2, text="Enter fleet size / fleet matrix: ").grid(row=0, column=0, sticky=W)
e21 = Entry(frame2, width=10)
e21.grid(row=0, column=1)
def input_matrix(target_entry:Entry):
    top = Toplevel()
    Label(top, text="Enter row num: ").grid(row=0, column=0)
    Label(top, text="Enter col num: ").grid(row=1, column=0)
    e1, e2 = Entry(top), Entry(top)
    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)
    def generate_matrix():
        w = int(e1.get())
        h = int(e2.get())
        entrys = []
        for i in range(w):
            entrys.append([])
            for j in range(h):
                temp_e = Entry(top)
                temp_e.grid(row=i+3, column=j)
                entrys[i].append(temp_e)
        def output():
            string = ""
            for i in range(len(entrys)):
                for j in range(0, len(entrys[0])-1):
                    string += entrys[i][j].get()
                    string += ","
                string += entrys[i][-1].get()
                string += ";"
            target_entry.delete(0, END)
            target_entry.insert(0, string)
            top.destroy()
            return
        Button(top, text="Save", command=output, width=15).grid(row=w+3, column=0, columnspan=2)
        return 
    Button(top, text="Save", command=generate_matrix, width=15).grid(row=2, column=0, columnspan=2)
b1 = Button(frame2, text="Define fleet matrix", command=lambda:input_matrix(e21), width=15)
b1.grid(row=0, column=2)
def disable(btns:list):
    for b in btns:
        if simul_type.get() == "homogeneous":
            b.config(state="disabled")
        else:
            b.config(state="normal")

local_reallocation = IntVar()
local_reallocation.set(1)
Label(frame2, text="Allow local reallocation: ").grid(row=1, column=0, sticky=W)
Radiobutton(frame2, text="yes", variable=local_reallocation, value=1).grid(row=1, column=1)
Radiobutton(frame2, text="no", variable=local_reallocation, value=0).grid(row=1, column=2)

global_reallocation = IntVar()
global_reallocation.set(0)
Label(frame2, text="Allow global reallocation: ").grid(row=2, column=0, sticky=W)
Radiobutton(frame2, text="yes", variable=global_reallocation, value=1).grid(row=2, column=1)
Radiobutton(frame2, text="no", variable=global_reallocation, value=0).grid(row=2, column=2)

# Part of passenger parameter
frame3 = LabelFrame(root, text="Passengers info", padx=5, pady=5)
frame3.pack(padx=5, pady=5)
Label(frame3, text="Enter demand size / demand matrix: ").grid(row=0, column=0, sticky=W)
e31 = Entry(frame3, width=10)
e31.grid(row=0, column=1)
b2 = Button(frame3, text="Define demand matrix", command=lambda:input_matrix(e31))
b2.grid(row=0, column=2)
Label(frame3, text="Enter demand duration (hr): ").grid(row=1, column=0, sticky=W)
e32 = Entry(frame3, width=10)
e32.grid(row=1, column=1, sticky=E)
Button(frame1, text="Save", command=lambda:disable([b1, b2]), width=15).grid(row=3, column=0)

# Part of city parameter
frame4 = LabelFrame(root, text="City info", padx=5, pady=5)
frame4.pack(padx=5, pady=5)
city_type = StringVar()
city_type.set("Manhattan")
Label(frame4, text="Choose city type: ").grid(row=0, column=0, sticky=W)
Radiobutton(frame4, text="Euclidean-space", variable=city_type, value="Euclidean").grid(row=1, column=0)
Radiobutton(frame4, text="Manhattan-space", variable=city_type, value="Manhattan").grid(row=1, column=1)
Radiobutton(frame4, text="Real-world", variable=city_type, value="real-world").grid(row=2, column=0)

linkbtn = Button(frame4, text="Input link file", command=lambda:Input("link"), width=15)
linkbtn.grid(row=2, column=1)
nodebtn = Button(frame4, text="Input node file", command=lambda:Input("node"), width=15)
nodebtn.grid(row=2, column=2)
def Input(file_type:str):
    city_type.set("real-world")
    root.filename = filedialog.askopenfilename(
    initialdir="C:/", 
    title="Select A File", 
    filetypes=(("xls files", "*.xls"), ("all files", "*.*")))
    global linkfile
    global nodefile
    if file_type =="link":
        linkfile = root.filename
        filename = linkfile.split("/")[-1]
        linkbtn.config(text="file: " + filename)
    elif file_type == "node":
        nodefile = root.filename
        filename = nodefile.split("/")[-1]
        nodebtn.config(text="file: " + filename)
    local_reallocation.set(0) 
    global_reallocation.set(0)
    return 


Label(frame4, text="Enter city length (mile): ").grid(row=3, column=0, sticky=W)
e41 = Entry(frame4, width=15)
e41.grid(row=3, column=1, columnspan=5, sticky=E)
Label(frame4, text="Enter maximum velocity (mph): ").grid(row=4, column=0, sticky=W)
e42 = Entry(frame4, width=15)
e42.grid(row=4, column=1, columnspan=5, sticky=E)

frame5 = LabelFrame(root, text="Serving type", padx=5, pady=5)
frame5.pack(padx=5, pady=5)
Label(frame5, text="Choose your serving type: ").grid(row=0, column=0, sticky=E)
serving_function = StringVar()
serving_function.set("simple serve")
Radiobutton(frame5, text="simple serve", variable=serving_function, value="simple serve").grid(row=1, column=0)
Radiobutton(frame5, text="batch serve", variable=serving_function, value="batch serve").grid(row=1, column=1)
Radiobutton(frame5, text="sharing serve", variable=serving_function, value="sharing serve").grid(row=1, column=2)
def click_sf():
    top = Toplevel()
    Label(top, text="Enter resolution (s): ").grid(row=0, column=0)
    e1 = Entry(top, width=5)
    e1.grid(row=0, column=1)
    if serving_function.get() == "batch serve":
        Label(top, text="Enter batch gap (s): ").grid(row=1, column=0)
        e2 = Entry(top, width=5)
        e2.grid(row=1, column=1)
    elif serving_function.get() == "sharing serve":
        Label(top, text="Enter detour percentage (%): ").grid(row=1, column=0)
        e2 = Entry(top, width=5)
        e2.grid(row=1, column=1)
    def save():
        global res
        global dt
        global detour_percentage
        res = float(e1.get()) if e1.get() != "" else -1
        if serving_function.get() == "batch serve":
            dt = float(e2.get()) if e2.get() != "" else -1
        elif serving_function.get() == "sharing serve":
            detour_percentage = float(e2.get()) if e2.get() != "" else -1
        top.destroy()
    Button(top, text="Save", command=save, width=15).grid(row=2, column=0, columnspan=2)
Button(frame5, text="Define parameters", command=click_sf, width=15).grid(row=2, column=0, columnspan=3)


elist = [e21, e31, e32, e41, e42]
varlist = [simul_type, local_reallocation, global_reallocation, city_type, serving_function]
def simulate():
    global s
    global res
    global dt
    global detour_percentage
    ct, cl, v = city_type.get(), float(e41.get()) if e41.get() != "" else -1, float(e42.get())
    if ct == "real-world":
        global linkfile
        global nodefile
        city = City(type_name=ct, length=cl, max_v=v, node_file=nodefile, link_file=linkfile)
    else:
        city = City(type_name=ct, length=cl, max_v=v)
    T = float(e32.get())
    lr = local_reallocation.get()
    gr = global_reallocation.get()
    sf = serving_function.get()
    st = simul_type.get() 
    if st == "homogeneous":
        m = int(e21.get()) if e21.get() != "" else -1 
        lbd = int(e31.get()) if e21.get() != "" else -1
        s = Simulation(city, T, simul_type=st, lmd=lbd, fleet_size=m, lr=lr)
    elif st == "heterogeneous":
        def convert(string:str):
            matrix = []
            rows = string.split(";")
            for row_idx in range(len(rows)-1):
                matrix.append([])
                cols = rows[row_idx].split(",")
                for col in cols:
                    matrix[row_idx].append(int(col))
            return matrix
        m_map = convert(e21.get())
        lbd_map = convert(e31.get())
        s = Simulation(city, T, simul_type=st, lmd_map=lbd_map, fleet_map=m_map, 
                lr=lr, gr=gr)
    if sf == "simple serve":
        s.simple_serve(res/3600)
    elif sf == "batch serve":
        s.batch_serve(res/3600, dt/3600)
    elif sf == "sharing serve":
        s.sharing_serve(res/3600, detour_percentage/100)
    Label(root, text="Simulation finished").pack()
simul_button = Button(root, text="Run simulation", command=simulate, width=15)
simul_button.pack()


def export():
    root.directory  = filedialog.askdirectory()
    global s
    s.export(path=root.directory)
    Label(root, text="Simulation exported").pack()
    return 
Button(root, text="Export to csv", command=export, width=15).pack()

def animate():
    global savepath
    savepath = ""
    top = Toplevel()
    Label(top, text="Enter compression factor: ").grid(row=0, column=0)
    Label(top, text="Enter fps: ").grid(row=1, column=0)
    e1 = Entry(top)
    e1.grid(row=0, column=1)
    e2 = Entry(top)
    e2.grid(row=1, column=1)
    Label(top, text="Choose address to save animation: ").grid(row=2, column=0)
    comp = int(e1.get()) if e1.get() != "" else 50
    fps = int(e2.get()) if e2.get() != "" else 15
    def open():
        global savepath
        savepath = filedialog.askdirectory()
        Button(top, text=savepath, command=open).grid(row=2, column=1)
    def animate_helper():
        s.make_animation(compression=comp, fps=fps, path=savepath)
        Label(root, text="Animation is saved to " + savepath).pack()
    Button(top, text="...", command=open, width=15).grid(row=2, column=1)
    Button(top, text="Run animation", command=animate_helper, width=15).grid(row=3, column=0)
Button(root, text="Make animation", command=animate, width=15).pack()

root.mainloop()