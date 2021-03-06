import json
import urllib
import methods
import random
import HTMLParser
from Tkinter import *
import ttk
import profile
import methods
import platform

parser = HTMLParser.HTMLParser()
canvas = "";

scoreboardWindow=""
quizWindow = ""
rdioButtonsTmp = ""
submitBtn = "";

session_id = "0"

def on_configure(event):
    # update scrollregion after starting 'mainloop'
    # when all widgets are in canvas
    canvas.configure(scrollregion=canvas.bbox('all'))

def on_mousescroll(event):
    # enable scrolling; defined speed
    operating_system = platform.system()
    factor = 1
    if ( operating_system == "Windows" ) :
        factor = 120 
    canvas.yview_scroll( -1 * (event.delta / factor), "units")

def quizUI(category, number):
    global canvas,submitBtn,quizWindow,rdioButtonsTmp;

    # Retrieve the list of questions 
    questions = retrieve(category, number)
    answers={}

    height = 700
    if len(questions) == 1:
        height = 300

    quizWindow = Tk()
    quizWindow.title("AskTrivia")
    quizWindow.resizable(width=False, height=False)    

    # Creating a canvas to allow scrolling
    canvas = Canvas(quizWindow, width=520, height=height)
    canvas.pack(side=LEFT, padx=30)

    # Scrollbar
    scrollbar = Scrollbar(quizWindow, command=canvas.yview)
    scrollbar.pack(side=LEFT, fill='y')
    canvas.configure(yscrollcommand = scrollbar.set)
    canvas.bind('<Configure>', on_configure)
    canvas.bind_all('<MouseWheel>', on_mousescroll)

    frame = Frame(canvas, width=520)
    canvas.create_window((4,4), window=frame, anchor="nw")

    rdioButtonsTmp = {};

    for i in range(0, len(questions)):
        options = questions[i]["options"]

        Label(frame, 
          wraplength=450,
          text= parser.unescape(questions[i]["question"]),
          justify = LEFT,
          padx = 10).pack(side="top", pady=20, anchor=W)

        answers[i] = IntVar();
        rdioButtonsTmp[i] = []

        for j in range(0, len(options)):
            rdioButtonsTmp[i].insert(j, Radiobutton(frame, 
                        text=parser.unescape(options[j]),
                        padx = 10, 
                        variable=answers[i], 
                        value=j))
            rdioButtonsTmp[i][j].pack(side="top", anchor=W)
    
    submitBtn = Button(frame, text ="Submit", command = lambda: completed_quiz(questions, answers));
    submitBtn.pack(anchor=E)

    quizWindow.withdraw()
    quizWindow.update_idletasks()  # Update "requested size" from geometry manager

    x = (quizWindow.winfo_screenwidth() - quizWindow.winfo_reqwidth()) / 2
    y = (quizWindow.winfo_screenheight() - quizWindow.winfo_reqheight()) / 2
    quizWindow.geometry("+%d+%d" % (x, y))
    quizWindow.deiconify()
        
    mainloop()
   


def retrieve(category, quantity):
    url = "https://opentdb.com/api.php?amount="+ str(quantity) +"&category=" + str(category)
    # Read JSON data from url
    error = 0;
    try:
        response = urllib.urlopen(url)
        try:
            jsonData = json.loads(response.read())
        except ValueError:
            error = 1;
    except IOError:
        error = 1;

    if ( error == 1 ) :

        jsonData = methods.read_data("backup.json")
        results = jsonData[str(category)][str(quantity)]
    else: 
        results = jsonData["results"]
    
    questions = []
    for i in range(0, len(results)):
        data = results[i]
        # Place them all in their respective variables
        difficulty, category, question, correct_answer, incorrect_answers = data["difficulty"], data["category"], data["question"], data["correct_answer"], data["incorrect_answers"]
        
        # Append the incorrect_answers list to our options list
        options = []
        options.extend(incorrect_answers)

        # Calculate a random index to place our correct_answer in the options list
        random_index = random.randrange(len(options)+1);
        options.insert(random_index, correct_answer)

        # Append it in the form of an object/dictionary to our questions list
        questions.append({ "question" : question, "options" : options, "correct_answer" : random_index })

    # Shuffle our questions
    random.shuffle(questions, random.random)
    
    return questions
    

def close():
    global quizWindow, scoreboardWindow;
    try:
        quizWindow.destroy();
    except TclError:
        print ""
    try:
        scoreboardWindow.destroy();
    except TclError:
        print ""
    profile.session_id = session_id
    profile.show_window()


def completed_quiz(questions, answers):
    submitBtn.config(text="Back to profile",command = close);
    calculate_results(questions, answers);

def calculate_level(correct, level = 1):
    correct -= (5 + 2*level)
    if correct <= 0:
        return level
    else:
        return calculate_level(correct, level+1)

def calculate_results(questions, answers):
    global scoreboardWindow,rdioButtonsTmp,submitBtn;

    correct = 0
    incorrect = []
    for i in range(0, len(questions)):
        correct_answer = questions[i]["correct_answer"]
        selected_answer = answers[i].get()
        if ( selected_answer == correct_answer ) :
            correct += 1
        else: 
            incorrect.append(i)
        
        rdioButtonsTmp[i][correct_answer].config(bg = "#8cff9f")
        for j in range(0, len(questions[i]["options"])):
            if ( j != correct_answer ) :
                rdioButtonsTmp[i][j].config(bg="#ff8e8e")
    
            

    # Calculate percentage based on the no. of corrects over the no. of questions
    percentage = (float(correct) / float(len(questions))) * 100


    #The new window and the expcalculator starts here
    scoreboardWindow = methods.define_window("Scoreboard","700x400")

    def update_locally(exp):
        users = methods.read_data("users.json")
        user = users[str(session_id)]
        user["exp"] += exp
        user["weekly_exp"] += exp     
        user["level"] = calculate_level(user["exp"] / 25)    
        methods.write_data(users, "users.json")

    def expadder(correct):   
        exp = correct * 25
        # Read JSON data from url
        '''
        error = 0;
        try:
            response = urllib.urlopen(url)
            try:
                users = json.loads(response.read())
            except ValueError:
                error = 1;
        except IOError:
            error = 1;
        '''

        usersRemote = methods.read_remote_json("public")

        if ( usersRemote == False ) :
            update_locally(exp)
        else:
            user = usersRemote[str(session_id)]
            newexp = exp + int(user["exp"])
            level = calculate_level(user["exp"] / 25)  
            methods.post_remote("updateExp", { "id" : session_id, "exp" : newexp, "weekly_exp" : newexp, "level" : level})
            update_locally(exp)
            
        return exp 





    label = Label(scoreboardWindow, text= "Score for this round:" + "\n" +str(percentage) + "%" )
    label.pack(side='top',pady=50)
    label.config(font=("Courier", 40))

    expgain = Label(scoreboardWindow, text = "Experience for this round:" + "\n" + str(expadder(correct)))
    expgain.pack()
    expgain.config(font=("Courier",30))

    scoreboardWindow.mainloop();
    

    
def selection():
    global master;
    categorynum = {"Random":9,"Books":10,"Film":11,"Music":12,"Musicals & Theatres":13,"Television":14,"Video Games":15,"Board Games":16,
               "Science & Nature":17,"Computers":18,"Mathematics":19,"Mythology":20,"Sports":21,"Geography":22,"History":23,"Politics":24,"Art":25,
               "Celebrities":26,"Animals":27,"Vehicles":28,"Comics":29,"Gadgets":30,"Japanese Anime & Manga":31,"Cartoon & Animations":32}
               
    master = methods.define_window("Pick your choice","400x300")
    

    category_var = StringVar(master)
    category_var.set("Random") #default value
    category = ttk.Combobox(master, state = "readonly", textvariable = category_var, values = ["Random","Books","Film","Music","Musicals & Theatres","Television","Video Games","Board Games",
                                                                           "Science & Nature","Computers","Mathematics","Mythology","Sports","Geography","History","Politics","Art",
                                                                           "Celebrities","Animals","Vehicles","Comics","Gadgets","Japanese Anime & Manga","Cartoon & Animations"])
    category.pack()
    category.place(relx=.5,rely=.4, anchor="center")
    
    number_var = StringVar(master)
    number_var.set("5") #default value
    num = ttk.Combobox(master, state = "readonly", textvariable = number_var, values=["5","10","15","20"])
    num.pack()
    num.place(relx=.5,rely=.5,anchor="center")

    def getinput():
        category = category_var.get()
        if category == "Random":
            category = random.randint(9,32)
        else:
            category = categorynum[category]
        number = number_var.get()
        master.destroy();
        quizUI(category, number)

    def back():
        master.destroy()
        profile.show_window()

    Button(master, text = "Back", command = back).pack(side=BOTTOM, pady = 10)
    Button(master, text = "Play!", command = getinput).pack(side=BOTTOM, pady=50)
    master.mainloop()

