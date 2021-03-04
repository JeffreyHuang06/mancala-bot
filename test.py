class Test:  
    def __init__(self, valmut):
        # valmut is some mutable value like a list
        self.valmut = valmut

    def bar(self, valmut, v):
        valmut[0] = v
        return valmut
    
    # NEVER PASS IN A MUTABLE VALUE WITHOUT MAKING A COPY, LEST THE FUNCTION HAVE SIDE EFFECTS
    def foo(self):
        lis = []
        for i in range(5):
            lis.append(self.bar(self.valmut, i))
        print(lis)

x = Test([0])
x.foo()