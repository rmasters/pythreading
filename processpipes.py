# -*- coding: utf-8 -*-
"""
A basic Python threading learning experiment.

Learning to use the threading and multiprocessing modules by putting
calls to the random.org random number generator in a separate process.

"""

from multiprocessing import Process, Pipe
import urllib2
from urllib2 import URLError, Request

"""
The threaded number retriever.

Retrieves numbers from random.org, can be controlled by sending string
arguments to the communication pipe passed as an argument 
(multiprocessing.Communication, one of the ends returned by Pipe()). 
The request argument should be a URL string or a urllib2.Request object.

Todo: allow multiple processes to be spawned.

"""
def get_numbers(request, pipe):
    numbers = []
    """Polled flag to allow/disallow number retrieval"""
    running = True
    
    """Run indefinitely, until a stop command is sent to the pipe"""
    while True:
        """Check for commands in the communication pipe"""
        if pipe.poll() is not None:
            msg = pipe.recv()
            
            if msg == "running":
                """Return the value of the running flag"""
                pipe.send(running)
            elif msg == "pause":
                """Toggle the running flag"""
                running = True if running is False else False
                pipe.send("Paused")
            elif msg == "stop":
                """
                Stop the process by breaking out of the infinite loop.
                Send back a response message followed by the list of
                numbers retrieved.
                
                Process.join() afterwards.
                """
                pipe.send("Stopped")
                pipe.send(numbers)
                break
            elif msg == "get":
                """Send back the current list of retrieved numbers"""
                pipe.send(numbers)
            else:
                pipe.send("Unknown command")

        if running:
            try:
                result = urllib2.urlopen(request)
            except URLError as reason:
                print "Error: " + reason
                break
        
            number = result.read().strip()
            if number not in numbers:
                numbers.append(number)

"""
A utility method to print a list of numbers

"""
def print_list(list):
    title = "%d numbers retrieved" % len(list)
    print title
    if len(list) > 0:
        print "-"*len(title)
        for i in range(0, len(list)):
            print "#%d\t%s" % (i+1, list[i])

if __name__ == "__main__":
    url = "http://www.random.org/integers/?num=1&min=1&max=100&col=1&base=10&format=plain&rnd=new"

    conn1, conn2 = Pipe()

    p = Process(target=get_numbers, args=(url, conn1))
    p.start()
    
    while True:
        command = raw_input("\nEnter command (status|get|pause|exit): ")
        if command == "status":
            conn2.send("running")
            print "Running" if conn2.recv() is True else "Stopped"
        elif command == "get":
            conn2.send("get")
            print_list(sorted(conn2.recv()))
        elif command == "exit":
            conn2.send("stop")
            print conn2.recv()
            print_list(sorted(conn2.recv()))
            
            p.join()
            break
        else:
            conn2.send(command)
            print conn2.recv()