class MA(object):

    count = 0

class SimpleMA(MA):

    def __init__(self, n):
        self.n = int(n)
        self.lasts = []
        

    def compute(self, data, empty=0):

        self.count+=1
        self.lasts.append(float(data))

        if len(self.lasts) >= self.n:
            return (sum(self.lasts[-self.n:])) / self.n
        else:
            return empty

class EMA(MA):

    def __init__(self, a):
        self.a = a
        self.last = 0

    def compute(self, value):
        #data is list of ordered data wich is already clean and numerical
        if  self.count == 0 :
            self.last = float(value)
        else:
            self.last = self.a *float(value) + (1-self.a)*float(self.last)
        
        self.count = self.count+1
        return self.last

class NDayEMA(EMA):

    def __init__(self, n):
        self.n = n
        if n < 2:
            print "ATTENTION: N should probably be bigger thant 2"  
        try:
            print self.n
            a = 2.0000/(self.n + 1) # calculate a form n as explained on Wikipedia
            super(NDayEMA, self).__init__(a) # init the parent class with a
        except ZeroDivisionError:
            print "ERROR: N should not be equal to 1, ZeroDivisionError"
            exit()

# some simple EMA class, it should be dynamic! is it possible? EMA54() should be a dynamic class
class EMA20(NDayEMA):

    def __init__(self):
        super(EMA20, self).__init__(20)

class EMAW(NDayEMA):

    def __init__(self):
        super(EMA20, self).__init__(7)

class EMA7(NDayEMA):

    def __init__(self):
        super(EMA20, self).__init__(7)

class EMA5(NDayEMA):

    def __init__(self):
        super(EMA20, self).__init__(5)

