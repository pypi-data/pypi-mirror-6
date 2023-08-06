from logging import Handler, getLogger
from datetime import datetime, timedelta


def add_options(parser, env):
    
    parser.add_option('--close-pocket',
                      action='store_true',
                      dest='close_pocket',
                      help='')
    parser.add_option('--pocket-batch-size',
                      action='store',
                      dest='pocket_batch_size',
                      type=int,
                      default=200,
                      help='')
    parser.add_option('--pocket-write-frequency',
                      action='store',
                      dest='pocket_write_frequency',
                      type=float,
                      default=2.,
                      help='')

class TissueHandler(Handler):
    
    def __init__(self, tissue, options, noseconfig):
        
        Handler.__init__(self)
        self.tissue = tissue
        self.message_buffer_size = options.pocket_batch_size
        if options.pocket_write_frequency > 0:
            self.write_frequency = timedelta(options.pocket_write_frequency)
            self.next_write = datetime.now() + self.write_frequency
        else:
            self.next_write = self.write_frequency = None
        self.buffered_messsage_count = 0
        self.session = None
        self.session_objects = {}
        self.last_error = None
        getLogger().addHandler(self)
    
    @classmethod
    def enabled(cls, tissue, options, noseconfig):
        
        return not options.close_pocket
    
    def after_enter_case(self, case, description):
        
        last_session = self.session
        self.session, self.session_objects = self.tissue.make_session(False)
        if last_session:
            last_session.close()
    
    def emit(self, record):
        
        if self.session_objects:
            try:
                message = record.message
            except AttributeError:
                message = record.msg
            self.session_objects['case_execution'].log_messages.append(self.tissue.db_models['LogMessage'](message,
                                                                                                           record.levelname, 
                                                                                                           record.name))
            self.buffered_messsage_count += 1
            if ((self.next_write and datetime.now() >= self.next_write)
                or self.buffered_messsage_count >= self.message_buffer_size):
                self.flush()
    
    def flush(self):
        
        self.tissue.access_lock.acquire()
        self.session.commit()
        self.buffered_messsage_count = 0
        self.next_write += self.write_frequency
        self.tissue.access_lock.release()
    
    def peek_error(self, test, err):
        
        self.last_error = err
    
    def handle_skip(self, message):
        
        self.acquire()
        if self.session_objects:
            sep = self.last_error[1].message if hasattr(self.last_error[1], 'message') else self.last_error[1].msg
            if sep:
                _, error, capture = message.partition(sep)
            else:
                _, error, capture = message.partition('\n')
            error = message
            capture = capture.strip('\n')
            message = 'Test Skipped' + ((': %s' % error) if error else '')
            self.session_objects['case_execution'].log_messages.append(self.tissue.db_models['LogMessage'](message,
                                                                                                           'WARN', 
                                                                                                           'test.result'))
            self.buffered_messsage_count += 1
            if capture:
                self.session_objects['case_execution'].log_messages.append(self.tissue.db_models['LogMessage'](capture,
                                                                                                               'DEBUG', 
                                                                                                               'test.capture'))
                self.buffered_messsage_count += 1
        self.release()
    
    def handle_fail(self, message):
        
        self.acquire()
        if self.session_objects:
            sep = self.last_error[1].message if hasattr(self.last_error[1], 'message') else self.last_error[1].msg
            if sep:
                _, error, capture = message.partition(sep)
            else:
                _, error, capture = message.partition('\n')
            capture = capture.strip('\n')
            message = 'Test Failed' + ((': %s' % error) if error else '')
            self.session_objects['case_execution'].log_messages.append(self.tissue.db_models['LogMessage'](message,
                                                                                                           'CRITICAL', 
                                                                                                           'test.result'))
            self.buffered_messsage_count += 1
            if capture:
                self.session_objects['case_execution'].log_messages.append(self.tissue.db_models['LogMessage'](capture,
                                                                                                               'DEBUG', 
                                                                                                               'test.capture'))
                self.buffered_messsage_count += 1
        self.release()
    
    def handle_pass(self):
        
        self.acquire()
        if self.session_objects:
            self.session_objects['case_execution'].log_messages.append(self.tissue.db_models['LogMessage']('Test Passed',
                                                                                                           'INFO', 
                                                                                                           'test.result'))
            self.buffered_messsage_count += 1
        self.release()
    
    def after_exit_case(self, result):
        
        # TODO: Fix this bug... exit_case is not called for executions of default case,
        # so it may be possible to drop messages, or have them end up attached to the
        # wrong execution, because we rely on after_exit_case to do a flushing cleanup.
        self.flush()
    
    def exit_cycle(self):
        
        self.flush()