#!/usr/bin/python
from ncsdaemon.server import Server

# Run the server if this file is run directly
if __name__ == '__main__':
    server = Server()
    server.run('localhost', 5000)
