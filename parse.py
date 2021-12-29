import threading
from parsers import *
from tqdm import trange

class Parser:
    def __init__(self):
        self.parsers = (tatler_parser, sobaka_parser, esquire_parser, kommersant_parser, rbc_parser, 
            dp_parsing, forbes_parser, sports_ru_parser, village_parser, flow_parser, elle_parser, 
            glamour_parser, afisha_parser, rtvi_parser, tvrain_parser)

    def parse(self, query:str) -> list:
        thread_list, results = [], []

        for func in self.parsers:
            thread = threading.Thread(target=func, args=(query,results))
            thread_list.append(thread,)
            thread.start()
        
        for i in trange(len(thread_list)):
            thread_list[i].join()

        return results

parser = Parser()
texts = parser.parse(input("Celebrity name: "))
print(texts)