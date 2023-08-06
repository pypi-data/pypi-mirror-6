homepage="http://www.ratemyprofessors.com"

from HTMLParser import HTMLParser
import itertools
import urllib2
import string

class LinkExtractor(HTMLParser):

    def __init__(self, data_to_find, word_part):
        HTMLParser.__init__(self)
        self.data_to_find=data_to_find
        self.word_part=word_part
        self.possible_link=""
        self.link=""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
           for name, value in attrs:
               if name == "href" and self.word_part in value:
                   self.possible_link=value

    def handle_data(self, data):
        if (self.data_to_find+",") in data:
            self.link=self.possible_link
            self.possible_link=""

def getProfessorUrl(professor):
        extractor= LinkExtractor(professor, "ShowRatings")
        letter=professor[0]
        for count in itertools.count(1):
            teacher_listing= homepage+"/SelectTeacher.jsp?sid=795&letter="+letter+"&pageNo="+str(count)
            extractor.feed(urllib2.urlopen(teacher_listing).read())
            try:
                if extractor.link!="":
                    return homepage+"/"+extractor.link
            except:       
                break
           
def getProfessorDifficulty(professor):
    professor_page= urllib2.urlopen(getProfessorUrl(professor)).read()
    return professor_page.split("</strong><span>Easiness</span></a>",1)[0][-3:]
