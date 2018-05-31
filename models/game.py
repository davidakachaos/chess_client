class Game(object):
    """A game of chess."""

    def __init__(self, guid, net):
        # super(Game, self).__init__()
        self.guid = guid
        self.net = net

    def __eq__(self, other):
        return self.guid == other.guid

    @property
    def state(self):
        return self.net.game_state(self.guid)

    @property
    def board(self):
        return self.net.get_board(self.guid)

    @property
    def my_turn(self):
        return self.net.is_it_my_turn(self.guid)

    @property
    def my_opponent(self):
        return self.net.opponent_name(self.guid)

    def make_move(self, move):
        return self.net.make_move(self.guid, move)

    @property
    def my_side(self):
        return self.net.my_side(self.guid)
