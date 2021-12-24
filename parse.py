import threading
from parsers import *

parsers  = [tatler_parser, sobaka_parser, esquire_parser, kommersant_parser, rbc_parser, 
            dp_parsing, forbes_parser, sports_ru_parser, village_parser, flow_parser, elle_parser]

def parse(query:str) -> list:
    global parsers

    thread_list, results = [], []

    for func in parsers:
        thread = threading.Thread(target=func, args=(query,results))
        thread_list.append(thread,)
        thread.start()
    
    for i in range(len(thread_list)):
        thread_list[i].join()

    return results

texts = parse(input())
print(texts)