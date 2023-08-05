class IncorrectNumberOfCells(Exception):

  def __str__(self):
    return "The amount of cells is icorrect"


class HeaderAlreadySet(Exception):

  def __str__(self):
    return "The number of columns can't be modified once a line has been added"