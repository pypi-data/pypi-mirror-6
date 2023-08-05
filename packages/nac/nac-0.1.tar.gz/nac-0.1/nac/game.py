
class Game():
    '''Game class implements Noughts and Crosses game logic'''

    X = 'X'
    O = 'O'

    COMBINATIONS = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))

    def __init__(self):
        self.fields = [None, None, None, None, None, None, None, None, None]
        self.turn = self.X
        self.winner = None

    def _check_winner(self):
        for c in self.COMBINATIONS:
            sign = self.fields[c[0]]
            if sign is not None and self.fields[c[1]] == sign and self.fields[c[2]] == sign:
                self.winner = sign
                break

    def _set(self, position):
        if position < 0 or position >= 9:
            raise ValueError('Position must be between 0 and 8')
        if self.fields[position] is not None:
            raise ValueError('Cell %s is already taken' % position)
        self.fields[position] = self.turn
        self._check_winner()
        self.turn = self.O if self.turn == self.X else self.X

    def move(self):
        result = None
        while result is None:
            try:
                pos = int(raw_input('Your input: '))
                self._set(pos)
                result = pos
            except ValueError, err:
                print str(err)
        return result

    def continues(self):
        return None in self.fields and self.winner is None 

    def display(self):
        fn = lambda pos: ' ' + self.fields[pos] + ' ' \
                if self.fields[pos] is not None else '(' + str(pos) + ')'
        print '%s|%s|%s\n---+---+---\n%s|%s|%s\n---+---+---\n%s|%s|%s\n' % \
                tuple(fn(pos) for pos in xrange(9))

    def display_result(self):
        print self.winner if self.winner else 'Nobody', 'has won!'
