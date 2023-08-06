#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random


class generator(object):

    def __init__(self, context = None):
        self.context = context

    def cards(self, numbersPerCard, minNum, maxNum, cards, lot):
        ''' Method that will create a given number of bingo
        cards from a given grid size, it will return a matrix
        of unique numbers.

        >>> import bingo
        >>> batch = bingo.generator().cards(15, 1, 90, 11, 1)
        >>> type(batch) is dict
        True

        @param numbersPerCard: The size of the grid, this number will
                        be used to create a squared grid, this
                        means that the resulting matrix will have
                        a size of ``gridSize`` x ``gridSize``
        @param minNum: This is the smallest number that will appear
                      on the bingo cards.
        @param maxNum: This is the biggest number that will appear
                      on the bingo cards.
        @param cards: The quantity of cards that will be created
                     on the created lot.
        @param lot: A externally generated number to identify The
                    to identify wich lot will the cards belong to.
        '''
        cardsPerStrip = 6 #TODO Dear future me, please unwire this when you have time
        already_raffled = []
        batch = {}
        card = []
        mod = cards % cardsPerStrip
        diff = cardsPerStrip - mod
        cards_rounded = diff + cards
        for h in range(cards_rounded):
            card = []
            for n in range(numbersPerCard):
                number = random.randint(minNum, maxNum)
                while number in already_raffled:
                    number = random.randint(minNum, maxNum)
                already_raffled.append(number)
                card.append(number)
                if h % cardsPerStrip:
                    already_raffled = []
            batch[h] = card
            batch['lot'] = lot
            batch['numbersPerCard'] = numbersPerCard
        return batch

    def raffle_all(self, minNum, maxNum, lot):
        ''' Method that will run the game, it will trow an
        array of mumbers, it means that all the game will be
        trown when them method is called.

        >>> import bingo
        >>> batch = bingo.generator().raffle_all(1, 90, 1)
        >>> type(batch) is dict
        True

        @param gridSize: The size of the grid, this number will
                        be used to create a squared grid, this
                        means that the resulting matrix will have
                        a size of ``gridSize`` x ``gridSize``
        @param minNum: This is the smallest number that will appear
                      on the bingo cards.
        @param maxNum: This is the biggest number that will appear
                      on the bingo cards.
        @param cards: The quantity of cards that will be created
                     on the created lot.
        @param lot: A externally generated number to identify The
                    to identify wich lot will the cards belong to.
        '''
        batch = {}
        randRange = range(minNum, maxNum, lot)
        card_list = random.sample(randRange, maxNum-1)
        batch['lot'] = lot
        batch['card_list'] = card_list
        return batch

    def raffle_one(self, minNum, maxNum, raffled, lot):
        ''' Method that will run the game, it will trow a
        number based on raffled ones, it means this Method
        will take already raffled numbers to not trow any
        repeared one

        >>> import bingo
        >>> lot = 1
        >>> minNum = 1
        >>> maxNum = 90
        >>> raffled = [1, 4, 6, 43]
        >>> batch = bingo.generator().raffle_one(minNum, maxNum, raffled, lot)
        >>> type(batch) is dict
        True

        @param minNum: This is the smallest number that will appear
                      on the bingo cards.
        @param maxNum: This is the biggest number that will appear
                      on the bingo cards.
        @param raffled: List of numbers that are already raflled
        '''
        batch = {}
        number = random.randint(minNum, maxNum)
        while number in raffled or len(raffled) == maxNum:
            number = random.randint(minNum, maxNum)
        if len(raffled) != maxNum:
            batch['number'] = number
            batch['lot'] = lot
        return batch


if __name__ == "__main__":
    import doctest
    doctest.testmod()
