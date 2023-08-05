import bubble


class Outer(bubble.Bubble):

    @bubble.switching
    def try_square(self, arg):
        inner = Inner()
        value = inner.square(arg)
        inner.kill(block=False)
        return value


class Inner(bubble.Bubble):

    @bubble.switching
    def square(self, arg):
        return arg * arg


bubble.bootstrap(True)
outer = Outer()
print outer.try_square(3)
outer.kill()
bubble.shutdown()
