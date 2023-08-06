import random, re, logging, ircformat

logging.basicConfig(level=logging.DEBUG)

fate_synonyms = ['F',"f","fate","fudge","Fate", "FATE", "Fudge"]
wod_synonyms = ["W", "w", "WW", "ww", "wod", "WoD"] 

def parse_roll(roll_expr):
        dienames = '|'.join(fate_synonyms+wod_synonyms)
        dice_regex = r'(\d+)d(\d+|[FfWw])'
        mod_regex = r'(\+|-)(\d+)'
        optional_mod = '('+mod_regex+')?'
        match = re.search(dice_regex+optional_mod, roll_expr)
        for index in range(5):
            if match.group(index) is None:
              print("Index "+str(index)+" is empty.")
            else:
              print("Index "+str(index)+":"+match.group(index))
        
        parsedroll = {'quantity': int(match.group(1)),
                      'faces': match.group(2),
                      'signedmod': match.group(3)}
        return parsedroll


class Die:
    def __init__(self, faces, number):
        self.faces = faces
        self.number = number
        logging.debug("faces = "+faces)
        #result is a list, to allow for standard coding and chains for WW die
        self.results = []
        if faces in fate_synonyms:
            logging.debug("recognized F")
            self.faces = "f"
            self.facelist = [-1, 0, 1]
            self.strversion = {-1: ircformat.color(u"\u2212", "red"  ), 
                                0: ircformat.color("0", "dark_grey" ), 
                                1: ircformat.color("+", "green")}

            self.values = {-1: -1,
                            0:  0,
                            1:  1}
        elif faces in wod_synonyms:
            self.faces = "w"
            self.facelist = range(1,11)
            self.successes = 0
            self.strversion = {1 : "1",
                               2 : "2",
                               3 : "3",
                               4 : "4",
                               5 : "5",
                               6 : "6",
                               7 : "7",
                               8 : ircformat.color("8" , "green" ),
                               9 : ircformat.color("9" , "green" ),
                               10: ircformat.color("10", "orange")}
            self.values = {1 : 0,
                           2 : 0,
                           3 : 0,
                           4 : 0,
                           5 : 0,
                           6 : 0,
                           7 : 0,
                           8 : 1,
                           9 : 1,
                           10: 1}
        else:
            self.facelist = range(1,int(faces)+1)
            self.strversion = {x: str(x) for x in range (1, int(faces)+1)}
            self.values = {x: x for x in range (1, int(faces)+1)}

    def __str__(self):
        return "d"+faces+": [ "+", ".join(self.history)+" ]"

    def roll(self):
        result = random.choice(self.facelist)
        result_arr = [result]
        if self.faces == "w" and result in [8, 9, 10]:
            result_arr+=self.roll()
        self.results = result_arr
        logging.debug("result = "+str(result_arr))
        return result_arr

    @property
    def total(self):
        return sum(self.values[result] for result in self.results)


    @property
    def result_string(self):
        return "!".join(self.strversion[result] for result in self.results)

class RollGroup:
    def __init__(self, rollexpression):
        parsed = parse_roll(rollexpression)
        quantity = parsed['quantity']
        faces = parsed['faces']
        self.modifier = parsed['signedmod']
        if self.modifier is None:
            self.modifier = 0
        self.dice = []
        self.rolled = False
        for die in range(1,quantity+1):
            self.dice.append(Die(faces, die))

    def roll(self):
        for die in self.dice:
            logging.debug("Rolling die #"+str(die.number))
            die.roll()
        self.rolled = True

    @property
    def total(self):
        return sum(die.total for die in self.dice)+int(self.modifier)

    @property
    def result_string(self):
        if self.rolled:
            die = ', '.join(str(die.result_string) for die in self.dice)
            total = "Total: "+ircformat.style(str(self.total), "bold") 
            return die+total
        else:
            return "Unrolled"
