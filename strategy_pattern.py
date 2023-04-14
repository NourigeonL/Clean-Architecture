class IQuackBehavior:
  def quack(self):
    raise NotImplementedError

class IFlyBehavior:
  def fly(self):
    raise NotImplementedError

class IDisplayBehavior:
  def display(self, name):
    raise NotImplementedError

class SimpleQuackBehavior(IQuackBehavior):
  def quack(self):
    print("I quack")

class NoQuackBehavior(IQuackBehavior):
  def quack(self):
    # do nothing
    pass

class SimpleFlyBehavior(IFlyBehavior):
  def fly(self):
    print("I fly")

class NoFlyBehavior(IFlyBehavior):
  def fly(self):
    # do nothing
    pass

class SimpleDisplayBehavior(IDisplayBehavior):
  def display(self, name):
    print(f"My name is {name}")

class NoDisplayBehavior(IDisplayBehavior):
  def display(self, name):
    # do nothing
    pass


class Duck:

  def __init__(self, name: str, quack_behavior : IQuackBehavior, fly_behavior : IFlyBehavior, display_behavior : IDisplayBehavior) -> None:
    self._quack_behavior = quack_behavior
    self._fly_behavior = fly_behavior
    self._display_behavior = display_behavior
    self.name = name

  def display(self):
    self._display_behavior.display(self.name)

  def quack(self):
      self._quack_behavior.quack()

  def fly(self):
      self._fly_behavior.fly()

duck1 = Duck("Billy", SimpleQuackBehavior(), NoFlyBehavior(), SimpleDisplayBehavior())
duck2 = Duck("Bob", NoQuackBehavior(), SimpleFlyBehavior(), SimpleDisplayBehavior())

for duck in [duck1, duck2]:
  duck.display()
  duck.fly()
  duck.quack()