import socket
import threading
from socket import error
from tkinter import *
import tkinter as tk
from tkinter import ttk

from tkinter import filedialog

class Interface:

    connections = []
    users = []
    friends = []

    def __init__(self):
        self.counter = 0
        self.graph()

    def graph(self):
        root = tk.Tk()
        self.root = root
        self.root.geometry("800x600")

        #Label informativo
        self.lable1 = Label(root, bg="blue",fg="white", text="Chat grupal",padx=140,pady=10 ,width=20, height=1).grid(row=0,column=1)

        #Lugar donde se ven los mensajes 
        self.txt = Text(root, width=60)
        self.txt.grid(row=1, column=1, columnspan=2)
    
        #Barra de navegacion 
        scrollbar = Scrollbar(self.txt)
        scrollbar.place(relheight=1, relx=0.974)
    
        #Entrada de texto 
        self.e = Entry(root, bg="#BDBDBD", width=55)
        self.e.grid(row=2, column=1)
    
        #Boton de enviar 
        send = Button(root, text="Enviar", bg="blue",fg="white",command=self.send).grid(row=2, column=2)

        #Selector de privacidad
        self.comboSele = ttk.Combobox(root, state="readonly", values=["Público"]) 
        self.comboSele.set("Público")
        self.comboSele.place(y = 400, x = 630)

        #Usuarios conectados
        self.lable1 = Label(root,background="blue",fg="white" ,text="Usuarios conectados",pady=10, width=20, height=1).grid( row=0, column=0)
        self.lstconet = Listbox(root) 
        self.lstconet.grid(row=1, column=0)
      
        #Imagen xd
        self.img = tk.PhotoImage(file="imagen.png")
        lb_img = tk.Label(root,image= self.img).grid(column=3, row=1)

        #Definicion de Ip Servidor
        self.LabelIp = Label(root,background="blue",fg="white" ,text="Ingresa la IP",pady=7, width=15, height=1).place(y=460, x=10)
        self.Ip_IniS = Entry(root)
        self.Ip_IniS.place(y=500, x=10)

        #Definicion puerto Servidor
        self.LabelPort = Label(root,background="blue",fg="white" ,text="Ingresa el puerto",pady=7, width=15, height=1).place(y=460, x=150)
        self.Port_IniS = Entry(root)
        self.Port_IniS.place(y=500, x=150)

        #Confirmar boton
        self.cof_ippS = Button(root, text="Confirmar", bg="blue",fg="white",command=self.server)
        self.cof_ippS.place(x=280, y=460)

        #-------------------------------------------------------------------------------------------------------------------------
        #Definicion de Ip amigo
        self.LabelIpC = Label(root,background="blue",fg="white" ,text="Ingresa la IP",pady=7, width=15, height=1).place(y=460, x=420)
        self.Ip_IniC = Entry(root)
        self.Ip_IniC.place(y=500, x=420)

        #Definicion puerto amigo
        self.LabelPortC = Label(root,background="blue",fg="white" ,text="Ingresa el puerto",pady=7, width=15, height=1).place(y=460, x=550)
        self.Port_IniC = Entry(root)
        self.Port_IniC.place(y=500, x=550)

        #Confirmar agregar
        self.cof_ippC = Button(root, text="Agregar", bg="blue",fg="white",command=self.validateClient)
        self.cof_ippC.place(x=670, y=460)

        #Boton de envio de imagen
        self.BtnImg = Button(root, text="Enviar Imagen", bg="blue",fg="white",command=self.SendImg)
        self.BtnImg.grid(row= 2, column=3)

        
        self.root.mainloop()

    def send(self):
        send = self.e.get()
        friend = self.comboSele.current()
        if len(self.users) == 0:
          self.addTxt("Yo","Ingresa los datos del servidor")
        else:
          if len(self.connections) == 0:
            self.addTxt("Yo","No puedes hablar solo, por favor consigue amigos")
          else:
            self.addTxt("Yo", send)
            if friend == 0:
                for client in self.connections:
                    client.send(bytes(send, 'utf-8'))
            else:
                for client in range(len(self.connections)):
                    if friend == client + 1:
                        self.connections[client].send(bytes(send, 'utf-8'))

    def server(self):
        self.serverAddress = (self.Ip_IniS.get(), int(self.Port_IniS.get()))
        self.sockServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockServer.bind(self.serverAddress)
        self.sockServer.listen(1)
        print("Server running ...")
        self.users.append(self.serverAddress)
        cThread = threading.Thread(target = self.listenClients, args=())
        cThread.daemon = True
        cThread.start()
    
    def listenClients(self):
        while True:
            client, address = self.sockServer.accept()
            print(str(address[0]) + ':' + str(address[1]), "connected")
            self.usersConnected(client, address)
            lThread = threading.Thread(target=self.handler, args=(client, address))
            lThread.daemon = True
            lThread.start()

    def usersConnected(self, c, a):
        self.connections.append(c)
        values = list(self.comboSele["values"])
        self.comboSele["values"] = values + [a]
        self.lstconet.insert(len(self.connections), a)

    def handler(self, c, a):
            while True:
                try:
                    data = c.recv(2048)
                except:
                    print(str(a[0]) + ':' + str(a[1]), "disconnected")
                    self.removeClient(c,a)
                    c.close()
                    break
                if data == b'SgIMG':
                    self.reciveImg(c)
                    data = b'Se ha recibido un archivo'
                self.addTxt("%s:%s" % a, str(data.decode()))

                    
    def removeClient(self, connection, address):
        try:
            posicion = self.connections.index(connection)
            self.connections.remove(connection)
            self.lstconet.delete(posicion)
            values = list(self.comboSele["values"])
            values.remove(address)
            self.comboSele["values"] =values
            self.friends.remove(address)
        except:
            self.friends.remove(address)
            print("Se cierra el socket")

    
    def reciveImg(self,client):
        print("Recibo imagen")
        self.counter += 1
        msg = str(self.counter)
        f = open("recibido"+msg+".jpg", "wb")
        while True:
            try:
                input_data = client.recv(2048)
            except error:
                print("Error de lectura.")
                break
            else:
                if input_data:
                    f.write(input_data)
                if len(input_data) <2048:
                    break
        print("El archivo se ha recibido correctamente.")
        f.close()

    def addTxt(self, client, msg):
        self.txt.insert(END, "\n" + client + "->" + msg)

    def addClient(self, clientAddress):
        sockClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockClient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sockClient.connect(clientAddress)
        self.friends.append(clientAddress)

        iThread = threading.Thread(target = self.handler, args=(sockClient, clientAddress))
        iThread.daemon = True
        iThread.start()

    def validateClient(self):
      counter = 0
      clientAddress = (self.Ip_IniC.get(), int(self.Port_IniC.get()))
      if clientAddress == self.serverAddress:
        self.addTxt("Yo","No se agregue a si mismo como amigo")
      else:
        for friend in self.friends:
          if clientAddress == friend:
            self.addTxt("Yo","Ese amigo ya se encuentra agregado")
            counter = counter + 1
        if counter == 0:
          self.addClient(clientAddress)
        

    def SendImg(self):
        ruta = filedialog.askopenfilename(filetypes=[('image', '*.jpg')])
        friend = self.comboSele.current()
        if friend == 0:
            for client in self.connections:
                client.send(bytes("SgIMG", 'utf-8'))
        else:
            for client in range(len(self.connections)):
                if friend == client + 1:
                    self.connections[client].send(bytes("SgIMG", 'utf-8'))
        f = open(ruta, "rb")
        content = f.read(2048)
        while content:
            if friend == 0:
                for client in self.connections:
                    client.send(content)
                content = f.read(2048)
            else:
                for client in range(len(self.connections)):
                    if friend == client + 1:
                        self.connections[client].send(content)
                content = f.read(2048)
        f.close()
        self.addTxt("yo", "El archivo se ha enviado")
        print("El archivo se ha enviado")


            

def main():
    app = Interface()

if __name__ == '__main__':
    main()