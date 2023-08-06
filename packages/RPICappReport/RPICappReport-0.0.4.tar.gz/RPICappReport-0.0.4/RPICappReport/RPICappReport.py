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
   
def getCoursesTaken(html):
    parser = ParseCappReport()
    parser.feed(html)
    html_text = parser.data_stack
    courses = []
    for i in range(len(html_text)):
        if ((html_text[i] == "Grd" or re.match(r"^((^[A-F](-|\+))|P|(NC)|(AP)|(Reg))$", html_text[i]))
        and len(html_text[i+1])==4 and html_text[i+2].isdigit() and not html_text[i+6] in ("F", "NC", "U", "W")):
	    name = html_text[i+1]+" "+html_text[i+2]
            term = html_text[i+5]
            courses.append(Course(name, term))
    return courses
    