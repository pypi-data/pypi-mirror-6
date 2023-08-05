#!/usr/bin/python

import socket
import sys

import config
from game import Game

def main(args):
	try:
		host = args[0] if len(args) > 1 else config.HOST
		port = int(args[-1]) if args else config.PORT

		print 'Noughts and crosses, v1.0'
		print 'Connecting to', host, port
		s = socket.socket()
		try:
			s.connect((host, port))

			game = Game()
			game.display()
			while game.continues():
				print 'Waiting for opponent move'
				his_move = s.recv(1)
				print 'Opponent >>', his_move
				game._set(int(his_move))
				game.display()
				if not game.continues():
					break
				pos = game.move()
				game.display()
				s.send(str(pos))
			game.display_result()
		finally:
			s.close()
			print 'Connection closed'
	except KeyboardInterrupt, err:
		print 'Finishing'
	except Exception, err:
		print 'Unexpected error occurred', err

if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))
