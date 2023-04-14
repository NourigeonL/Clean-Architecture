class ICommand:
  def execute(self) -> None:
    raise NotImplementedError

  def undo(self) -> None:
    raise NotImplementedError

class Remote:
  def __init__(self, on : ICommand, off : ICommand, increase : ICommand, decrease : ICommand) -> None:
    self._on = on
    self._off = off
    self._increase = increase
    self._decrease = decrease

  @property
  def on(self) -> ICommand:
    return self._on

  @property
  def off(self) -> ICommand:
    return self._off

  @property
  def increase(self) -> ICommand:
    return self._increase

  @property
  def decrease(self) -> ICommand:
    return self._decrease

class Light:
  def __init__(self, max) -> None:
    self._brightness_level : int = 0
    self._max_brightness = max
    self._is_on : bool = False

  @property
  def max_brightness(self):
    return self._max_brightness

  @property
  def brightness_level(self):
    return self._brightness_level

  @brightness_level.setter
  def brightness_level(self, val : int):
    self._brightness_level = max(0, min(self._max_brightness, val))

  @property
  def is_on(self):
      return self._is_on

  @is_on.setter
  def is_on(self, val : bool):
    self._is_on = val

class TurnLightOnCommand(ICommand):
  def __init__(self, light : Light) -> None:
    super().__init__()

  def execute(self) -> None:
    return super().execute()

  def undo(self) -> None:
    return super().undo()

class TurnLightOffCommand(ICommand):
  def __init__(self, light : Light) -> None:
    super().__init__()

  def execute(self) -> None:
    return super().execute()

  def undo(self) -> None:
    return super().undo()

class IncreaseLightBrightnessCommand(ICommand):
  def __init__(self, light : Light) -> None:
    super().__init__()

  def execute(self) -> None:
    return super().execute()

  def undo(self) -> None:
    return super().undo()

class DecreaseLightBrightnessCommand(ICommand):
  def __init__(self, light : Light) -> None:
    super().__init__()

  def execute(self) -> None:
    return super().execute()

  def undo(self) -> None:
    return super().undo()