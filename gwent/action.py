#!/usr/bin/python3
from .common.logger import log
from .common import GameState
import random


class Action:
    def __init__(self, target=None):
        self.game = None
        self.source = None
        self.target = target
        self.times = 0
        self.next_choice = None
        self.callback_source = None
        self.callback = []

    def __mul__(self, other):
        self.times = other

    def trigger(self):
        rtn = []
        for time in range(self.times):
            rtn.append(self.do())
            self.game.queue_actions(self.callback_source, self.callback)
        if self.times == 0:
            rtn = self.do()
            self.game.queue_actions(self.callback_source, self.callback)
        return rtn

    def do(self):
        pass

    def then(self, source, actions):
        self.callback_source = source
        self.callback = actions


class Draw(Action):
    def do(self):
        rtn = None
        source = self.source
        if source.deck:
            log.info("%s 抽取了卡牌 %s", source, source.deck[0])
            rtn = source.deck[0]
            source.hand.append(source.deck[0])
            source.deck = source.deck[1:]
        else:
            log.info("%s 没有牌了, 无法抽牌", source)
        return rtn


class MulliganStart(Action):
    def do(self):
        self.source.state = GameState.MULLIGAN


class MulliganDone(Action):
    def do(self):
        self.source.state = GameState.MULLIGAN_DONE
        if self.source.state != GameState.MULLIGAN:
            self.game.queue_actions(self.game, TurnStart())


class TurnStart(Action):
    def do(self):
        game = self.game
        if not game.first_player:
            # 游戏还没开始
            game.first_player, game.second_player = game.queue_action(game, TossCoin())
        if game.turn % 2:
            game.current_player = game.first_player.opponent
        if game.state != GameState.GAME_OVER:
            game.state = GameState.PLAY
            game.current_player.state = GameState.PLAY
            game.current_player.oppenent.state = GameState.WAITING
            game.turn += 1
            log.info("第 %s 局开始", game.turn)
            log.info("当前是 %s 的回合", game.current_player)
        else:
            log.info("游戏已经结束了")


class TossCoin(Action):
    def do(self):
        game = self.game
        blue_coin = random.choice(game.players)
        red_coin = random.choice(game.players)
        log.info("%s 是蓝硬币, 获得了先手", blue_coin)
        log.info("%s 是红硬币, 获得了后手", red_coin)
        return blue_coin, red_coin


class Mulligan(Action):
    def do(self):
        source = self.source
        if source.state == GameState.MULLIGAN:
            self.next_choice = self
            source.choice = self
        else:
            log.warning("%s 无法调度", source)

    def choose(self, card):
        source = self.source
        deck = source.deck
        hand = source.hand
        if not card:
            log.info("%s 放弃了调度", self.source)
            self.next_choice = None
            source.state = GameState.MULLIGAN_DONE
        elif card in hand:
            index = hand.index(card)
            # 黑名单机制
            for i in range(len(deck)):
                if deck[i].id == card.id:
                    deck[i], deck[-1] = deck[-1], deck[i]
            deck.append(card)
            hand.remove(card)
            hand.insert(index, deck[0])
            deck.remove(deck[0])
            pass
        else:
            log.error("选择的牌%s不在手牌中", card)
            return
        source.choice = self.next_choice


class Play(Action):
    def do(self):
        # TODO 打出一张牌
        pass
