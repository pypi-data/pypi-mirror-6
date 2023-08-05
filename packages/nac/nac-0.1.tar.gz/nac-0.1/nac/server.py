#!/usr/bin/python

import socket
import sys

import config
from game import Game

def main(args):
	try:
		s = socket.socket()
		try:
			s.bind((config.HOST, int(args[-1]) if args else config.PORT))
			s.listen(5)

			print 'Noughts and crosses, v1.0'
			print 'Server started! Waiting for clients...'

			c, addr = s.accept()
			print 'Got connection from', addr

			game = Game()
			game.display()
			while game.continues():
				pos = game.move()
				game.display()
				c.send(str(pos))
				if not game.continues():
					break
				print 'Waiting for opponent move'
				his_move = c.recv(1024)
				print 'Opponent >> ', his_move
				game._set(int(his_move))
				game.display()
			game.display_result()
		finally:
			s.close()
			print 'Connection closed'
	except KeyboardInterrupt, _err:
		print 'Finishing'
	except Exception, err:
		print 'Unexpected error occurred', err

if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))
