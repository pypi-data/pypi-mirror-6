import HTMLParser
import re

class ParseCappReport(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.data_stack=[]
    def handle_data(self, data):
        self.data_stack.append(data)

class Course:
    def __init__(self, name, term):
        self.name = name
	self.term = term

def isAllCaps(string):
    for letter in string:
        if letter.islower():
           return False
    return True
   
def getCoursesTaken(html):
    parser = ParseCappReport()
    parser.feed(html)
    html_text = parser.data_stack
    courses = []
    for i in range(len(html_text)):
        if (len(html_text[i]) == 4 and isAllCaps(html_text[i]) and 
            len(html_text[i+1]) == 4 and html_text[i+1].isdigit() and not
            set([html_text[i+5], html_text[i+6]]) <= set(["F", "NC", "U", "W"])):
	    name = html_text[i]+" "+html_text[i+1]
            if len(html_text[i+4]) == 6:
                term = html_text[i+4]
            else:
                term = html_text[i+5]
            taken = False
            for course in courses:
                if course.name == name and course.term == term:
                    taken = True
            if not taken:
            	courses.append(Course(name, term))
    return courses
    
