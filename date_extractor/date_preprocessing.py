import re
import traceback
import regex
try:
    from pattern.en import number
except ImportError:
    from pattern3.en import number
from dateutil.parser import _timelex

class PreProcess(object):
    """
    This class converts alphabetic numbers to numeric.
    """

    def __init__(self):
        self.num_list = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                         "zero", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                         "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty",
                         "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
        self.sim_list = ["hundred", "thousand"]

    def word2nummain(self, query):
        """
        This function splits te string based on certain words
        and calls the the other functions.
        Params:
            Input:
                query - str
            Output:
                output_query - str
        """
        try:
            query = self.preprocess(query)
            reg1 = regex.compile(r"""\b(month|year|january|jan|february|feb|march|mar|april|apr|may|
                              june|jun|july|jul|august|aug|september|sept|sep|october|oct|november|
                              nov|december|dec|for|to|th|nd|st|rd|of|
                              (?<!hundred\s|thousand\s)and)\b|(\.|:)""")
            reg1 = reg1.pattern.replace('\n', '').replace(' ', '')
            sent_list = [x for x in regex.split(reg1, query, flags=re.I) if isinstance(x, str)]
            new_sent_list = self.convertword2num(sent_list)
            output_query = " ".join(new_sent_list)
            output_query = ' '.join([x for x in list(_timelex(output_query)) if x != ' '])
            return output_query
        except Exception as exc:
            print("the error in main is>>>", traceback.format_exc(), exc)

    def preprocess(self, query):
        """
        This function preprocesses the string based on certain rules
        Params:
            Input:
                query - str
            Output:
                query - str
        """
        query = " " + query + " "
        reg = r"([a-zA-Z]+)\s?(-)\s?([a-zA-Z]+)"
        srch = re.search(reg, query, re.I)
        while srch:
            query = re.sub(reg, r"\1 \3", query, flags=re.I)
            srch = re.search(reg, query, re.I)
        query = query.replace('tieth ', 'ty th ')
        query = query.replace(' first ', ' one st ')
        query = query.replace(' second ', ' two nd ')
        query = query.replace(' third ', ' three rd ')
        query = regex.sub(r"(?<!mon|\s|wi)th\s", " th ", query, 0, flags=re.I)
        query = query.replace(' eigh ', ' eight ').replace(' fif ', ' five ').replace(' twelf ', ' twelve ')

        return query

    def convertword2num(self, sent_list):
        """
        This is the main function where numbers are extracted from
        their alphabetic equivalents
        Params:
            Input:
                sent_list - list of broken sentences
            Output:
                new_list - same list of sentences, but with numbers
        """
        new_list = []
        print(sent_list)
        for sent in sent_list:
            is_a_part = False
            words = []
            temp_sent = [x for x in list(_timelex(sent)) if x != ' ']
            for ind, wrd in enumerate(temp_sent):
                word = ''
                if wrd in self.num_list + self.sim_list:
                    if not is_a_part:
                        is_a_part = True
                        if wrd in self.sim_list:
                            if ind == 0:
                                sent = sent.replace(wrd, u'one ' + wrd)
                                wrd = u'one ' + wrd
                                words.append(wrd)
                            elif number(temp_sent[ind-1]) == 0:
                                sent = sent.replace(wrd, u'one ' + wrd)
                                wrd = u'one ' + wrd
                                words.append(wrd)
                        if ind != len(temp_sent) - 1 and \
                        number(temp_sent[ind]) in range(1, 21) and \
                        temp_sent[ind+1] in self.num_list and \
                        number(temp_sent[ind+1]) > 9:
                            sent = sent.replace(wrd, wrd + u' hundred')
                            wrd = wrd + u' hundred'
                            words.append(wrd)
                        elif wrd not in words:
                            words.append(wrd)
                    else:
                        if ind != len(temp_sent)-1 and \
                        number(temp_sent[ind]) in range(1, 21) and \
                        temp_sent[ind+1] in self.num_list and \
                        number(temp_sent[ind+1]) > 9:
                            sent = sent.replace(wrd, wrd + u' hundred')
                            wrd = wrd + u' hundred'
                            words.append(wrd)
                        else:
                            words.append(wrd)
                elif wrd == 'and' and temp_sent[ind - 1] in self.sim_list:
                    if is_a_part:
                        try:
                            if temp_sent[ind+1] in self.num_list:
                                words.append(wrd)
                        except:
                            pass
                else:
                    is_a_part = False

            word = " ".join([word for word in words])
            word = list(_timelex(word))
            word = ' '.join([x for x in word if x != ' '])
            try:
                num = number(word)
                print(num)
            except Exception:
                num = word
            else:
                if word:
                    sent = sent.replace(word, str(num))
            new_list.append(sent)

        return new_list

if __name__ == '__main__':
    OBJ = PreProcess()
    while True:
        QUERY = input("\nEnter: ")
        if QUERY == 'exit':
            break
        QUERY = OBJ.word2nummain(QUERY)
        print(QUERY)
