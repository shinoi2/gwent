#!/usr/bin/python3
from .action import *


class Game:
    def __init__(self, players):
        self.players = players
        self.player1 = players[0]
        self.player2 = players[1]
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1
        for player in players:
            player.game = self
            player.draw(10)
        self.first_player = None
        self.second_player = None
        self.current_player = None
        self.state = GameState.READY
        self.turn = 0

    def start_game(self):
        # 先调度, 第一轮调度3张牌
        if self.state == GameState.READY:
            self.state = GameState.MULLIGAN
            log.info("双方开始调度...")
            self.queue_actions(self.player1, [MulliganStart(), Mulligan() * 3, MulliganDone()])
        else:
            log.error("游戏已经开始过了")

    def queue_action(self, source, action):
        return self.queue_actions(source, [action])[0]

    def queue_actions(self, source, actions):
        rtn = []
        for action in actions:
            action.game = self
            action.source = source
            rtn.append(action.trigger())
        return rtn

    @property
    def score(self):
        return self.player1.score, self.player2.score
