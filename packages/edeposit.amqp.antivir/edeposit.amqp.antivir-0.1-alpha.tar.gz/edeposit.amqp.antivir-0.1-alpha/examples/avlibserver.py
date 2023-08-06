#! /usr/bin/env python
# -*- coding: utf-8 -*-

from edeposit.amqp.antivir import amqpav

'''AVServer usage example.'''


def main():
    
    print('AV Service')
    print('-' * 10)

    avc = amqpav.AVServer()
    print('Listening...')
    avc.run()

    
if __name__ == '__main__':

    main()
