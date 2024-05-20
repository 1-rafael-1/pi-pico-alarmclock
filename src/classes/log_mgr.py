import uos
import utime

class LogManager:
    def __init__(self, state_mgr):
        self.state_mgr = state_mgr
        self.verbose = True
        self.log = False
        self.max_log_length = 100
        self.log_file = 'log.txt'
        self.clean_log = False

    def set_verbose(self, verbose):
        self.verbose = verbose

    def set_log(self, log):
        self.log = log

    def get_verbose(self):
        return self.verbose
    
    def get_log(self):
        return self.log
    
    def set_max_log_length(self, max_log_size):
        self.max_log_length = max_log_size

    def get_max_log_length(self):
        return self.max_log_length
    
    def set_log_file(self, log_file):
        self.log_file = log_file

    def get_log_file(self):
        return self.log_file
    
    def set_clean_log(self, clean_log):
        self.clean_log = clean_log

    def get_clean_log(self):
        return self.clean_log

    def initialize(self):
        # Check if the log file exists
        if self.log_file in uos.listdir():
            # If clean_log is True, delete the file
            if self.clean_log:
                uos.remove(self.log_file)
                # Create the log file
                with open(self.log_file, 'w') as f:
                    pass
        else:
            # If the file doesn't exist, create it
            with open(self.log_file, 'w') as f:
                pass
    
    def emit(self, message, source_class):
        # Get the current time as a tuple
        now = utime.localtime()
        # Format the time as a string
        timestamp = '{}-{:02d}-{:02d}-{:02d}-{:02d}-{:02d}'.format(now[0], now[1], now[2], now[3], now[4], now[5])
        # Create the log entry
        log_entry = '{}: {}: {}'.format(timestamp, source_class, message)
        # If verbose is True, print the log entry
        if self.verbose:
            print(log_entry)
        # If log is True, append the log entry to the file
        if self.log:
            with open(self.log_file, 'a') as f:
                f.write(log_entry + '\n')
            # Check the log size and remove the oldest message if necessary
            self.check_log_size()

    def check_log_size(self):
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
        if len(lines) > self.max_log_length:
            with open(self.log_file, 'w') as f:
                for line in lines[-self.max_log_length:]:
                    f.write(line)

    def deinit(self):
        pass

## Mocks ##
class MockStateManager:
    def __init__(self):
        pass

    def log_emit(self, message, source_class):
        pass

## Test ##
def log_manager_emits_messages():
    #[GIVEN]: A LogManager instance, set up to print but not log
    state_mgr = MockStateManager()
    log_mgr = LogManager(state_mgr)
    log_mgr.set_verbose(True)
    log_mgr.set_log(False)
    log_mgr.set_max_log_length(5)
    log_mgr.set_log_file('test_log.txt')
    log_mgr.set_clean_log(True)
    log_mgr.initialize()
    #[WHEN]: We emit a message
    log_mgr.emit('Test message', 'TestClass')
    #[THEN]: The message is printed
    # The output is the message
    #[TEARDOWN]: Clean up the log file
    uos.remove('test_log.txt')

def log_manager_logs_messages():
    #[GIVEN]: A LogManager instance, set up to log but not print
    state_mgr = MockStateManager()
    log_mgr = LogManager(state_mgr)
    log_mgr.set_verbose(False)
    log_mgr.set_log(True)
    log_mgr.set_max_log_length(5)
    log_mgr.set_log_file('test_log.txt')
    log_mgr.set_clean_log(True)
    log_mgr.initialize()
    #[WHEN]: We emit a message
    log_mgr.emit('Test message', 'TestClass')
    #[THEN]: The message is logged
    # The log file contains the message
    print('load the log file and print() its contents')
    with open('test_log.txt', 'r') as f:
        print(f.read())    
    #[TEARDOWN]: Clean up the log file
    uos.remove('test_log.txt')

def log_manager_limits_log_size():
    #[GIVEN]: A LogManager instance, set up to log but not print
    state_mgr = MockStateManager()
    log_mgr = LogManager(state_mgr)
    log_mgr.set_verbose(False)
    log_mgr.set_log(True)
    log_mgr.set_max_log_length(5)
    log_mgr.set_log_file('test_log.txt')
    log_mgr.initialize()
    #[WHEN]: We emit more messages than the log can hold
    for i in range(10):
        log_mgr.emit('Test message {}'.format(i), 'TestClass')
    #[THEN]: The log contains only the most recent messages
    # The log file contains the last 5 messages
    print('load the log file and print() its contents')
    with open('test_log.txt', 'r') as f:
        print(f.read())    
    #[TEARDOWN]: Clean up the log file
    uos.remove('test_log.txt')