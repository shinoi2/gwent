#!/usr/bin/python3
from .action import *


class Player:
    def __init__(self, leader, deck):
        # 这里没有做卡组合法性校验
        self.state = GameState.READY
        self.game = None
        self.opponent = None
        self.start_leader = leader
        self.leader = leader
        self.deck = random.shuffle(deck)
        self.hand = []
        self.rows = [[], [], []]
        self.choice = None
        self.score = []
        self.total_score = 0
        self.graveyard = []
        self.removed = []

    def passed(self):
        if self.state == GameState.PLAY:
            log.info("%s 放弃出牌", self)
            self.state = GameState.PASS
        else:
            log.error("不是 %s 的回合", self)

    def play(self, card):
        if self.state == GameState.PLAY:
            if (card is self.leader) or (card in self.hand):
                self.game.queue_action(self, Play(card))
            else:
                log.error("你选择的牌%s 无法打出", card)
        else:
            log.error("不是 %s 的回合", self)

    @property
    def point(self):
        return self.melee_point + self.range_point + self.siege_point

    @property
    def melee(self):
        return self.rows[0]

    @property
    def range(self):
        return self.rows[1]

    @property
    def siege(self):
        return self.rows[2]

    @property
    def melee_point(self):
        rtn = 0
        for unit in self.melee:
            rtn += unit.point
        return rtn

    @property
    def range_point(self):
        rtn = 0
        for unit in self.range:
            rtn += unit.point
        return rtn

    @property
    def siege_point(self):
        rtn = 0
        for unit in self.siege:
            rtn += unit.point
        return rtn

    def draw(self, num=1):
        return self.game.queue_action(self, Draw(self) * num)

    def mulligan(self, num=1):
        self.game.queue_actions(self, [MulliganStart(), Mulligan() * num])
