from functools import wraps

from mock import patch
from splunk_logger import SplunkLogger


class SplunkLoggerContextDecorator(object):
    '''
    This is a util that should be used by our users when writing their
    unittests. It allows you to get SplunkLogger working without any
    credentials, which is useful for running in continuous integration.
    
    
    from splunk_logger.unittest_utils import mock_splunk
    from splunk_logger import SplunkLogger
    
    with mock_splunk:
        SplunkLogger() # without any credentials
    
    @mock_splunk
    def sample():
        SplunkLogger() # without any credentials
    
    '''
    def __enter__(self):
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def __call__(self, func):
        
        @wraps(func)
        def wrapper(*args, **kwds):
            with self:
                with patch.object(SplunkLogger, '_set_auth') as mock_auth,\
                patch.object(SplunkLogger, '_send_to_splunk') as mock_send:
                    print 'a' * 35
                    return func(*args, **kwds)
            
        return wrapper
    
mock_splunk = SplunkLoggerContextDecorator()
