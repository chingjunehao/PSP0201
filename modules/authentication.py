from Tkinter import *
import tkMessageBox
import json
import os
import methods
import profile
import urllib
import urllib2
import hashlib

def password_hash(string):
        hash_obj = hashlib.sha256(string.encode())
        return hash_obj.hexdigest()

def submit(username,password,password_confirmation):

      
      if len(username) <6:
         tkMessageBox.showerror("Error","Minimum length of username is 6")
         return
      if len(password)<6:
         tkMessageBox.showerror("Error","Minimum length of password is 6")
         return
      if password_confirmation != password:
         tkMessageBox.showerror("Error","Both Passwords did not match. Try Again")
         return

      data = methods.read_remote_json("usernames")
      # If connection to remote server failed due to internet failure or error in request
      if ( data == False ) :
         tkMessageBox.showinfo("Error","Internet connection/Server down")
      else:
        error = 0;

        # If there are users currently existing in the remote database, check:
        if ( data != None ) : 
          users = data["users"]
          for i in users:
            if username == i :
              error = 1;
              break;
          if ( error == 1 ) :
            print "username has been taken"
            tkMessageBox.showerror("Error","Username: "+username+" has been taken")
        if ( error == 0 ):
          # Send a POST request to addUser/ with parameters: name, password, description. These parameters will be stored in the remote database.
          newUser = methods.post_remote("addUser", { "name" : username, "password" : password_hash(password), "description" : "Set your description" })
          # Save users profile locally as well
          save_user_locally(json.loads(newUser)["id"], username, password, "Set your description", 0, 0, 1)
          tkMessageBox.showinfo("Done","Register Successfully!")
          Back();

def save_user_locally(userId, username, password, description, exp, weekly_exp, level):
  # Save users profile locally as well
  users = methods.read_data("users.json")
  users[str(userId)] = {"name" : username, "password" : password_hash(password), "description" : description, "exp" : exp, "weekly_exp" : weekly_exp, "level" : level}
  methods.write_data(users, "users.json")

def Back():
    RegWindow.withdraw()
    LogWindow.deiconify()

def Register():
    RegWindow.deiconify()
    LogWindow.withdraw()
        
def login(username, password):
   
   print "sending request"
   request = methods.post_remote("loginUser", { "name" : username })

   print request

   # If request did not fail: 
   if ( request != None ):
      data = json.loads(request);
      # If there are errors ( caused by non-existing username ) and password does not match the password stored in the database:
      if ( ( "error" in data and data["error"] == True ) or data["password"] != password_hash(password) ):
         tkMessageBox.showerror("Error","Please Try Again!")
      else:
            tkMessageBox.showinfo("Done","Login Successfully!")
            save_user_locally(data["id"], username, password, data["description"], data["exp"], data["weekly_exp"], data["level"])
            LogWindow.destroy()
            RegWindow.destroy()
            profile.session_id = data["id"]
            profile.show_window()
   else:
      # If request to remote server failed, log in locally
      print "logging in locally"
      users = methods.read_data("users.json") 
      counter = 0;
      for i in users:
         counter = counter + 1
         if users[str(i)]["name"] == username and users[str(i)]["password"]== password_hash(password):
            tkMessageBox.showinfo("Done","Login Successfully!")
            LogWindow.destroy()
            RegWindow.destroy()
            profile.session_id = str(i)
            profile.show_window()
            break
         else:
            if (counter == len(users)) :
               tkMessageBox.showerror("Error","Please Try Again!")
               break;
            else:
               continue;

def show_window():
  try:
        global LogWindow, RegWindow
        #First Window
        LogWindow = methods.define_window("AskTrivia","500x300")
        FrameColor = "light blue"
        LogWindow.configure(bg=FrameColor)
        Welcome = Label(LogWindow,text = "Welcome to\n AskTrivia",bg=FrameColor,font="Arial")

        LogUser = Label(LogWindow,text = "Username:",bg=FrameColor,font="Arial")
        log_username = Entry(LogWindow)
        LogPass = Label (LogWindow,text="Password:",bg=FrameColor,font="Arial")
        log_password = Entry(LogWindow,show = "*")

        #SecondWindow
        RegWindow = methods.define_window("Register", "500x300")
        RegWindow.configure(bg = FrameColor)
        RegWord = Label (RegWindow,text="REGISTER",font = "Arial",bg=FrameColor)

        RegUser = Label (RegWindow,text="Username: ",bg=FrameColor,font="Arial")
        reg_username = Entry(RegWindow)
        RegPass = Label(RegWindow,text="Password: ",bg=FrameColor,font="Arial")
        reg_password = Entry(RegWindow,show="*")
        ConfirmationPass = Label(RegWindow,text="Password Confirmation: ",bg=FrameColor,font="Arial")
        confirmation_pass = Entry(RegWindow,show="*")
        RegWindow.withdraw()
        users = {}                
        
        #Button
        ButtonColor = "light green"

        submitButton = Button (RegWindow,text = "    Submit    ",command= lambda: submit(reg_username.get(), reg_password.get(), confirmation_pass.get()), bg="Pink",activebackground = "white",activeforeground ="black")
        backButton=Button(RegWindow,text ="    Back    ",command=Back,bg=ButtonColor,activebackground = "white",activeforeground ="black")
        registerButton=Button(LogWindow,text="    Register    ",command= Register,bg=ButtonColor,activebackground = "white",activeforeground="black")
        loginButton = Button(LogWindow,text = "    Login    ",command= lambda: login(log_username.get(), log_password.get()),bg="Pink",activebackground = "white",activeforeground="black")        

        #Adjust Lining LogWindow
        LogSpaceX1 = Label (LogWindow,text="                                 ",bg=FrameColor).grid(row=0,column=0)
        LogSpaceY1 = Label (LogWindow,text=" ",bg=FrameColor).grid(row=1,column=0)
        LogSpaceY2 = Label (LogWindow,text=" ",bg=FrameColor).grid(row=4,column=0)
        Welcome.grid(row=0,column=4)
        LogUser.grid(row=2,column=3)
        log_username.grid(row=2,column=4)
        LogPass.grid(row=3,column=3)
        log_password.grid(row=3,column=4)

        loginButton.grid(row=5,column=3)
        registerButton.grid(row=5,column=4)

        #Adjust Lining RegWindow
        RegSpaceX1 = Label (RegWindow,text="            ",bg=FrameColor).grid(row=0,column=0)
        RegSpaceY1 = Label (RegWindow,text=" ",bg=FrameColor).grid(row=1,column=0)
        RegSpaceY2 = Label (RegWindow,text=" ",bg=FrameColor).grid(row=4,column=0)
        RegSpaceY3 = Label (RegWindow,text=" ",bg=FrameColor).grid(row=5,column=0)
        RegWord.grid(row=0,column=4)
        RegUser.grid(row=2,column=3)
        reg_username.grid(row=2,column=4)
        RegPass.grid(row=3,column=3)
        reg_password.grid(row=3,column=4)
        ConfirmationPass.grid(row=4,column=3)
        confirmation_pass.grid(row=4,column=4)
        submitButton.grid(row=6,column=3)
        backButton.grid(row=6,column=4)

        LogWindow.bind('<Return>',lambda x: login(log_username.get(), log_password.get())); 
        RegWindow.bind('<Return>',lambda x: submit(reg_username.get(), reg_password.get(), confirmation_pass.get()));
        LogWindow.mainloop()

  except:
    return False;
