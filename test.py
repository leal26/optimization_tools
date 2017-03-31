
key = 0
class test:
    def __init__(self):
        self.a = 0

    if key != 0:
        def b(self):
            return 11

        def load(self, original_test):
            for attribute in dir(original_test):
                var = getattr(original_test, attribute)
                setattr(self, attribute, var)


test1 = test()
test1.a = 100
print test1.a
# print test1.b()

key = 1
class test:
    def __init__(self):
        self.a = 0

    if key != 0:
        def b(self):
            return 11

        def load(self, original_test):
            for attribute in dir(original_test):
                var = getattr(original_test, attribute)
                setattr(self, attribute, var)
test2 = test()

test2.load(test1)
print test2.a
print test2.b()
