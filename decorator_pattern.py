
class Number():
    def write_val(self, val : int) -> None:
        raise NotImplementedError

    def read_val(self) -> int:
        raise NotImplementedError

class SimpleNumber(Number):
  def __init__(self) -> None:
      self.val : int = 0

  def write_val(self, val : int) -> None:
        self.val = val

  def read_val(self) -> int:
      return self.val


class NumberDecorator(Number):
    def __init__(self, number : Number) -> None:
        self._number = number

    @property
    def number(self) -> Number:
      return self._number

    def write_val(self, val : int) -> None:
      self.number.write_val(val)

    def read_val(self) -> int:
      return self.number.read_val()

class DoubleDecorator(NumberDecorator):
    def write_val(self, val: int) -> None:
        self.number.write_val(2*val)

    def read_val(self) -> int:
        return self.number.read_val()

class PlusOneDecorator(NumberDecorator):
    def write_val(self, val: int) -> None:
        self.number.write_val(val + 1)

    def read_val(self) -> int:
        return self.number.read_val()

number1 = SimpleNumber()
number1 = DoubleDecorator(number1)
number1 = PlusOneDecorator(number1)

number2 = SimpleNumber()
number2 = PlusOneDecorator(number2)
number2 = DoubleDecorator(number2)

number1.write_val(5)
number2.write_val(5)
print(number1.read_val())
print(number2.read_val())