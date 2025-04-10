import logging
import coloredlogs
import sys

def init_logging():
    """Initialize logging with colors.
    
    This function configures the root logger with colored output.
    It should be called at the start of your application.
    """
    # Remove any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure coloredlogs
    coloredlogs.install(
        level='INFO',
        stream=sys.stdout,
        fmt='%(asctime)s %(name)s:%(lineno)d %(levelname)s %(message)s',
        level_styles={
            'info': {'color': 'green'},
            'warning': {'color': 'yellow'},
            'error': {'color': 'red'},
            'critical': {'color': 'red', 'bold': True},
        },
        field_styles={
            'asctime': {'color': 'cyan'},
            'name': {'color': 'blue'},
            'levelname': {'color': 'white', 'bold': True},
        }
    ) 