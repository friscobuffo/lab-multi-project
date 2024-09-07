import multiprocessing

def receive():
    # Code for receiving process goes here
    pass

def transmit():
    # Code for transmitting process goes here
    pass

if __name__ == "__main__":
    receive_process = multiprocessing.Process(target=receive)
    receive_process.start()

    transmit_process = multiprocessing.Process(target=transmit)
    transmit_process.start()

    transmit_process.join()
    receive_process.join()