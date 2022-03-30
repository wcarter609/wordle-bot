import pytest

from wordle_bot.wordle import Wordle


def test_wordle_api():
  wdl = Wordle("snail")
  assert wdl.solution == "snail"

  results = wdl.guess("arose")
  assert results == [1,0,0,1,0]
  
  results = wdl.guess("stamp")
  assert results == [2,0,2,0,0]

  results = wdl.guess("snail")
  assert results == [2,2,2,2,2]
  assert wdl.guesses == [
    ("arose", [1,0,0,1,0]),
    ("stamp", [2,0,2,0,0]),
    ("snail", [2,2,2,2,2])
  ]

def test_wordle_invalid_guess():
  wdl = Wordle("wordle")
  assert wdl.solution == "wordle"

  with pytest.raises(Exception) as exc_info:
    wdl.guess("abc")

  assert exc_info.value.args[0] == 'word is of invalid length. guesses must be length 6'