class Wordle:

  def __init__(self, solution):
    self.solution = solution
    self.n_guesses = 0
    self.guesses = list()

  def guess(self, word):
    if len(word) != len(self.solution):
      raise Exception(f"word is of invalid length. guesses must be length {len(self.solution)}")
    
    result = [0]*len(self.solution)
    for i in range(len(self.solution)):
      if word[i] == self.solution[i]:
        result[i] = 2
      elif word[i] in self.solution:
        result[i] = 1

    self.guesses.append((word, result))
    return result

