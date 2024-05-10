class Test:
    def __init__(self,v):
        self.val = v
        self.val1 = None

    def sum(self, x):
        self.val1=self.val+x

if __name__ == "__main__":

    ogg = Test(5)

    ogg.sum(3)

    ogg = Test(0)

    print(ogg.val)
    print(ogg.val1)
