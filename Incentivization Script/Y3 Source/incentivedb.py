import json

class IncentiveDB():
    def __init__(self, opt, users, trades, comments):
        self.users = users
        self.trade = trades
        self.comments = comments
        self.opt = opt
        self.accumulate = True if opt["accumulation"] == "true" else False
        self.previous = self.getPrevious(opt)
        self.numwinners = opt["winners"]
        self.debug = opt["debug"]

    def getPrevious(self,opt):
        filename = opt["db"]
        json_data = open(filename)
        data = json.load(json_data)
        json_data.close()
        return data