import random
'''
Machine Educable Blackjack Engine

This is inspired by the MENACE (Video about it here: https://www.youtube.com/watch?v=R9c-_neaxeU)

This version of MEBE is a decendent of MENACE, it will follow in the same logical steps as MENACE did.

The machine will have a large 'storage' where it will keep information on how viable a certain move (hit or stop) is
given its current running total.
When it finally decides to stop, or the machine's total is over 21, it will stop. Then the 'dealer' will take random cards until it
has amassed cards that total over 17. If the machine wins, it will be encouraged (given more options) to do the moves it did during
the game, if it lost it will be discouraged (removing more options) from doing the moves it did during the game.
'''
#Key-Value pair of numbers to cards, helps random card generation & readibility
maxDecisionArrayValue = 500 #maximum value for total tokens
minPercent = 0.001
nPercentChance = int(minPercent*maxDecisionArrayValue)
cards = {
    0: "Ace",
    1: "Two",
    2: "Three",
    3: "Four",
    4: "Five",
    5: "Six",
    6: "Seven",
    7: "Eight",
    8: "Nine",
    9: "Ten",
    10: "Jack",
    11: "Queen",
    12: "King"
}
values = {
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
    "Six": 6,
    "Seven": 7,
    "Eight": 8,
    "Nine": 9,
    "Ten": 10,
    "Jack": 10,
    "Queen": 10,
    "King": 10
}
decks = 1 #How many decks used in the blackjack game, defaulted to one
class MEBE:
    
    state = {
        "Ace": 0,
        "Two": 0,
        "Three": 0,
        "Four": 0,
        "Five": 0,
        "Six": 0,
        "Seven": 0,
        "Eight": 0,
        "Nine": 0,
        "Ten": 0,
        "Jack": 0,
        "Queen": 0,
        "King": 0
    }
    runningTotal = 0
    dealerTotal = 0
    decisionArray = [[7,10] for x in xrange(21)]
    stopped = False
    playHistory = [] #This will be an array representing the previous states
    #A 'state' will be in the form [Running total, 's' or 'h' for stopped or hit]
    def getDecisionArrayFromFile(self):
        decisionArrayFile = open("mebe1DecisionArray.txt", "r")
        index = 0
        for line in decisionArrayFile.readlines():
            argArray = line.split(" ")
            hitTokens = int(float(argArray[0]))
            totalTokens = int(float(argArray[1]))
            self.decisionArray[index] = [hitTokens, totalTokens]
            index+=1
    def __init__(self, start=True):
        self.state = {
            "Ace": 0,
            "Two": 0,
            "Three": 0,
            "Four": 0,
            "Five": 0,
            "Six": 0,
            "Seven": 0,
            "Eight": 0,
            "Nine": 0,
            "Ten": 0,
            "Jack": 0,
            "Queen": 0,
            "King": 0
        }
        self.runningTotal = 0
        self.stopped = False
        self.playHistory = []
        self.dealerTotal = 0
        if(start):
            self.getDecisionArrayFromFile()
    def takeACard(self, fordealer=False):
        randomCard = cards[random.randint(0,12)]
        while(self.state[randomCard]>4*decks):
            randomCard = cards[random.randint(0,12)] #This ensures that a card won't be delt if it is not available
        valueOfCard = 0
        if(randomCard == "Ace"):
            valueOfCard = 1 if (self.runningTotal>21) else 11
        else:
            valueOfCard = values[randomCard]
        self.state[randomCard] += 1
        if(not fordealer):
            self.runningTotal += valueOfCard
            self.stopped = (self.runningTotal >= 21)
        else:
            self.dealerTotal += valueOfCard
    def playGame(self):
        self.__init__(start=False)
        self.playRound()
        self.playRound()
        self.stopped = False
        self.takeACard(fordealer=True)
        while(self.runningTotal < 21 and (not self.stopped)):
            self.playRound()
        if(self.runningTotal>21):
            print("I lost :(")
            self.learn(won=False)
            return False
        while(self.dealerTotal < 17):
            self.takeACard(fordealer=True)
        if(self.dealerTotal>21 or (self.runningTotal > self.dealerTotal)):
            print("I won! :)")
            self.learn(won=True)
            return True
        else:
            print("I lost :(")
            self.learn(won=False)
            return False
    def playRound(self):
        nextPlayArray = self.decisionArray[self.runningTotal]
        probabilityOfHit = (float)(nextPlayArray[0])/nextPlayArray[1]
        rand = random.uniform(0, 1)
        if rand <= probabilityOfHit:
            self.playHistory.append([self.runningTotal, 'h'])
            self.takeACard()
        else:
            self.playHistory.append([self.runningTotal, 's'])
            self.stopped = True
    def learn(self, won=False):
        for x in range(0, len(self.playHistory)):
            totalAtTime = self.playHistory[x][0]
            actionAtTime = self.playHistory[x][1]
            hitTokens = self.decisionArray[totalAtTime][0]
            totalTokens = self.decisionArray[totalAtTime][1]
            if(won and actionAtTime == 'h'):
                incr = 0
                if(totalTokens + 10 < maxDecisionArrayValue):
                    incr = 10
                else:
                    diff = maxDecisionArrayValue - totalTokens
                    incr = diff
                self.decisionArray[totalAtTime][0] += incr
                self.decisionArray[totalAtTime][1] += incr
                #This 'adds' 10 hit tokens into the decisonArray when the total is totalAtTime
            elif((not won) and actionAtTime == 'h'):
                self.decisionArray[totalAtTime][0] = nPercentChance if hitTokens < nPercentChance+1 else hitTokens - 1
                self.decisionArray[totalAtTime][1] = 2 if totalTokens == 2 else totalTokens-1 #This ensures that there is always a miss token
            elif(won and actionAtTime == 's'):
                if(totalTokens + 10 < maxDecisionArrayValue):
                    incr = 10
                else:
                    incr = maxDecisionArrayValue - totalTokens
                self.decisionArray[totalAtTime][1] += incr
            else:
                hitTokens = nPercentChance if hitTokens < nPercentChance+1 else hitTokens #This prevents totalTokens from ever being 0
                self.decisionArray[totalAtTime][1] = hitTokens if (totalTokens==hitTokens) else totalTokens-1 
                #This ensures that the total tokens will never be less than the amount of hit tokens 

mebe = MEBE()
wins = 0
total = 0
for x in xrange(50000):
    wins = (wins + 1) if mebe.playGame() == True else wins
    total += 1
percent = ((float)(wins)/total)*100
print("Win percentage is " + (str)(percent))
decisionArrayFile = open("mebe1DecisionArray.txt", 'w')
for decision in mebe.decisionArray:
    decisionArrayFile.write("%f %f\n"%(decision[0], decision[1]))
decisionArrayFile.close()