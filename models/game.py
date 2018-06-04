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

    @property
    def over(self):
        board = self.board
        return board.is_game_over()

    @property
    def over_reason(self):
        board = self.board
        side_won = ""
        if board.result()[-1] == '1':
            if self.my_side == "White":
                side_won = 'Zwart (tegenstander) heeft gewonnen'
            else:
                side_won = 'Zwart (u) heeft gewonnen'
        elif board.result()[0] == '1':
            if self.my_side == "White":
                side_won = 'Wit (u) heeft gewonnen'
            else:
                side_won = 'Wit (tegenstander) heeft gewonnen'
        else:
            side_won = 'Gelijkspel!'

        if not board.is_game_over():
            return ''
        if board.is_checkmate():
            return f"Schaakmat - {side_won}"
        elif board.is_stalemate():
            return "Gelijkspel!"
        elif board.is_insufficient_material():
            return f"Onvoldoende materiaal - {side_won}"
        elif board.is_seventyfive_moves():
            return f"75 zetten regel - {side_won}"
        elif board.is_fivefold_repetition():
            return f"5 voudig herhaalt regel - {side_won}"
