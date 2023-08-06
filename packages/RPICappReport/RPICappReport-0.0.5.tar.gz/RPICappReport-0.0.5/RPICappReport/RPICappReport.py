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

def isAllCaps(string){
    for str in string:
        if str.islower():
           return False
    return True
}
   
def getCoursesTaken(html):
    parser = ParseCappReport()
    parser.feed(html)
    html_text = parser.data_stack
    courses = []
    for i in range(len(html_text)):
        if (len(html_text[i]) == 4 and isAllCaps(html_text[i]) and 
            len(html_text[i+1]) == 4 and html_text[i+1].isdigit() and 
            not html_text[i+5] in ("F", "NC", "U", "W")):
	    name = html_text[i]+" "+html_text[i+1]
            term = html_text[i+4]
            courses.append(Course(name, term))
    return courses
    