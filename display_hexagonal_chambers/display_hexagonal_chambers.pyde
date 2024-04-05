 # add_library('pLaunchControl')
# add_library('wellen')
# add_library('themidibus')
# Import the processing.py library
# from processing import *
import json
# import mido

# Load JSON data from the file
# with open("/home/paulo/QuantumItineraries/VQH/BookFactory_Data/Data_21/aggregate_data.json", "r") as file:
    # lines_data = json.load(file)



# Number of lines
num_lines = 6

# # Color array for each line
# line_colors = [
#     color(255, 0, 0),  # Red
#     color(0, 255, 0),  # Green
#     color(0, 0, 255),  # Blue
#     color(255, 255, 0),  # Yellow
#     color(255, 128, 0),  # Orange
#     color(128, 0, 255),   # Purple
#     color(255, 0, 255),  # Magenta
#     color(0, 255, 255)  # Cyan
# ]
line_colors = [
    color(255, 105, 90),  # Red
    color(0, 163, 153),  # Green
    color(72, 100, 171),  # Blue
    color(255, 201, 90),  # Yellow
    color(239, 84, 111),  # Orange
    color(157, 60, 167),   # Purple
    color(157, 60, 167),  # Magenta
    color(150, 228, 80)  # Cyan
]

darker_factor = 0.6
lighter_factor = 0.7
# darker_line_colors = [lerpColor(c, color(0, 0, 0), darker_factor) for c in line_colors]
darker_line_colors = [color(85, 85, 85) for c in line_colors]
# lighter_line_colors = [lerpColor(c, color(255, 255, 255), lighter_factor) for c in line_colors]
lighter_line_colors = [color(229,0,127) for c in line_colors]
# Yellow cursor properties
# cursor_color = color(255, 255, 0)  # Yellow
cursor_color = color(115)  # Yellow
cursor_width = 10
cursor_period = 5.0  # Adjust the speed as needed
cursor_speed = 1.0
cursor_height = 6
global last_execution_time
last_execution_time = 1.0
interval_time = 100.0 

# book_number = 50

global book
global triggers
global env
global t_index
global timetest
timetest = 30
global book_number
book_number = 36

# Setup function
def setup():
    global book, triggers, env, t_index
    global displayWidth
    global displayHeight
    # frameRate(30)
    t_index = 0
    size(displayWidth/2, displayHeight/2-10)  # Set the size of the canvas
    xml = loadXML("processing_data.xml")
#     selectFolder("Select a folder to process:", "folderSelected")
    book, triggers, env = update_xml()
    book_number = 36
    background(38)
    draw_states()
    draw_amps()
    draw_cursor()
      
    # nums = 5, 34
    
    # Writes the bytes to a file
    # saveBytes("/home/paulo/QuantumItineraries/VQH/display_hexagonal_chambers/data/time.dat", nums)
# def folderSelected(selection):
#     if selection == None:
#         print("Window was closed or the user hit cancel.")
#     else:
#         print("User selected " + selection.getAbsolutePath())
    # timetest = 0

# Draw function
def draw():
    global last_execution_time, timetest, book_number
    # background(50)  # Set the background to white
    background(38)
    # book = update_xml()
    # draw_states(book)
    # stroke(220)
    # draw_cursor()
    # draw_states()
    
    draw_amps()
    draw_cursor()
    # print(timetest)
    # current = millis()
    if millis() - last_execution_time > interval_time:
        update_time()
        last_execution_time = millis()
    
    # background(timetest)
    # Plot each line with a different color
    # for i in range(num_lines):
        # plot_line(i, line_colors[i])

def update_time():
    global timetest, t_index, book_number
    
    
    try: 
        b =loadBytes("/home/paulo/QuantumItineraries/VQH/display_hexagonal_chambers/data/time.dat")
        # c =loadBytes("/home/paulo/QuantumItineraries/VQH/display_hexagonal_chambers/test.dat")
        # Print each value, from 0 to 255
        for i in range(len(b)):
            # bytes are from -128 to 127, this converts to 0 to 255
            b[i] = b[i] & 0xff
            
        # for i in range(len(c)):
        #     # c[i] = c[i] & 0xff
        #     print("%i " % (c[i]))
        # # timetest = b[0]
        
        t_index = b2t(b)
        # print(b[1])
        if book_number != b[1]:
            # xml = loadXML("processing_data.xml")
            # book, triggers, env = update_xml()
            # print("book number changed")
            book_number = b[1]
            
        # Print a blank line at the end
        # print("")
    except:
        pass



# Function to plot a specific line with a given color
def plot_line(line_index, line_color):
    stroke(line_color)  # Set stroke color to the specified color

    # Begin drawing the line
    beginShape()

    # Iterate over each point in the line
    for j in range(len(lines_data)):
        x = map(j, 0, len(lines_data) - 1, 0, width)  # Map x-coordinate
        y = map(lines_data[j]["l" + str(line_index + 1)], 0, 1, height, 0)  # Map y-coordinate
        vertex(x, y)  # Add vertex to the shape

    # End drawing the line
    endShape()
    
def update_xml():
    
    xml = loadXML("processing_data.xml")
    iterations = xml.getChildren("iteration")
    book = []
    triggers = []
    env = []
    for i in range(len(iterations)):

        i_id = iterations[i].getInt("id")
        state = iterations[i].getChildren("state")[0].getChildren("qubit")
        amps = iterations[i].getChildren("amps")[0].getChildren("amp")
        
        # Get all content
        state_content = []
        amps_content = []
        val_content = iterations[i].getChildren("value")[0].getFloatContent()
        
        for k in range(len(state)):
            k_id = state[k].getString("id")
            qubit = state[k].getIntContent()
            amp = amps[k].getFloatContent()
            state_content.append(qubit)
            amps_content.append(amp)
        
        #val = 
        #print("%s %s" % (i_id, state_content))
        book.append(amps_content)
        triggers.append(state_content)
        env.append(val_content)
    # print("%s" % (book))
    return book, triggers, env

def draw_states():
    global book, triggers
    
    # print("%d %f %f" % (len(book), width, width/float(len(book))))
    r_width = width/float(len(triggers))
    r_height = height/float(len(triggers[0]))
    noStroke()
    for x in xrange(len(triggers)):
        for y in xrange(len(triggers[0])):
            # print("%d,%d => %d" % (x, y, triggers[x][y]))
            # stroke(triggers[x][y]*255)
            y_decr = len(triggers[0])-y-1
            fill(triggers[x][y]*lighter_line_colors[y_decr] + (1-triggers[x][y])*darker_line_colors[y_decr])
            # fill(triggers[x][y]*255)
            # stroke(0)
            noStroke()
            posx = r_width*x
            posy = r_height*y
            # rect(posx, posy, r_width, r_height)
            rect(posx,(1-book[x][y_decr])*height-4,r_width,20)
            
            
def draw_amps():
    global book
    
    # print("%d %f %f" % (len(book), width, width/float(len(book))))
    r_width = width/float(len(book))
    r_height = height/float(len(book[0]))
    pcolor = color(255, 0, 0)
    # stroke(pcolor)
    # point(0, book[0][0]*height)
    
    
    for x in xrange(len(triggers)-1):
        for y in xrange(len(triggers[0])):
            # print("%d,%d => %d" % (x, y, book[x][y]))
            # stroke(triggers[x][y]*255)
            # stroke(pcolor)
            stroke(line_colors[y])
            # fill(255)
            # noSmooth()
            
            # stroke(0)
            posx = r_width*(x+0.5)
            posx_n = (r_width)*(x+1.5)
            posy = r_height*y
            # rect(posx,posy,r_width,r_height)
            # point(posx, book[x][y]*height)
            line(posx, (1-book[x][y])*height, posx_n, (1-book[x+1][y])*height)
            # point(posx, 70)
            # print(book[x][y])

def draw_cursor():
    global triggers
    cursor_grid = len(triggers)
    
    # cursor_grid=30.0
    
    r_width = width/float(cursor_grid)
    r_height = height/float(len(triggers[0]))
    

    cursor_time = (millis() % (1000*cursor_period))/(1000.0*cursor_period)  # Normalize the time

    # print(cursor_x)
    # cursor_x = (((cursor_time*cursor_grid)//1)/cursor_grid)*width
    # x_index = int((cursor_time*cursor_grid)//1)
    x_index = t_index % cursor_grid
    # print(x_index)
    cursor_x = (float(x_index)/cursor_grid)*width

    # cursor_y = height - cursor_height  # Fixed position at the bottom
    stroke(cursor_color)
    noFill()
    # rect(cursor_x, 0, r_width, height)
    line(cursor_x+(r_width/2.0), 0, cursor_x+(r_width/2.0), height)


    for y in xrange(len(triggers[0])):
        # print("%d,%d => %d" % (x, y, triggers[x][y]))
        stroke((triggers[x_index][y])*color(229,0,127) + (1-triggers[x_index][y])*64)
        y_decr = len(triggers[0])-y-1
        fill(triggers[x_index][y]*lighter_line_colors[y_decr] + (1-triggers[x_index][y])*darker_line_colors[y_decr])

        posx = r_width*x_index
        posy = r_height*y
        # rect(posx, posy, r_width, 20)
        rect(posx,(1-book[x_index][y_decr])*height-4,r_width,20)

# def mousePressed():
#     global t_index, book_number
    
#     t_index += 1
#     t_bytes = t2b(t_index)
#     nums = t_bytes, book_number
#     saveBytes("/home/paulo/QuantumItineraries/VQH/display_hexagonal_chambers/data/time.dat", nums)
    
def keyPressed():
    global book, triggers, env
    #print(keyCode)
    if keyCode == 32:
        xml = loadXML("processing_data.xml")
        book, triggers, env = update_xml()
        
def t2b(t):
    return t
def b2t(b):
    # t = b[0]/8 + b[1]*16 + b[2]*127
    # t = b[0]/8 + b[1]*16 + b[2]*127
    # t = b[0]/8 + b[1]*16 + b[2]*127
    t = b[0]/8 + b[1]*16 + b[2]*127*16
    print(t)
    return t
