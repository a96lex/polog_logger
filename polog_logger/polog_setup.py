import json
import logging

from pydantic import BaseModel, validate_model, ValidationError
from polog import config, file_writer
from polog.core.log_item import LogItem


def customLogFormat(data: LogItem):
    """Formats a log to our liking.

    In this implementation we are just logging the message (which is what we
    input in the logging.log call), and a couple other fields.
    We can add any other field from `data.keys()`

    Note: the source code of the polog module is in russian.

    Arguments:
        data -- the log object

    Returns:
        a string, which will be logged to the handler
    """
    values = data.get("message")
    process = data.get("process")
    level = logging.getLevelName(data.get("level"))
    return f"{process} - {level} - {values}\n"


def performanceLogFilter(LogModel: BaseModel) -> bool:
    """Checks wether a log message conforms to the PerformanceMetrics class

    Arguments:
        record -- a log message

    Returns:
        a boolean value
    """

    def inner_filter(record: LogItem):
        try:
            raw_log = json.loads(dict(record).get("message"))
            validate_model(LogModel, raw_log)
            print("true")
            return True
        except (ValueError, ValidationError, Exception):
            return False

    return inner_filter


def setup_logging(
    logfile: str = None, CustomLogModel: BaseModel = None, pool_size: int = 0
) -> None:
    """Sets up logging using the polog module on top of stdlib logging.

    It will create two handlers:
        - console handler. Has no filters Will output everything with
          severity > 20 (logging.INFO).
        - file handler. Will output only logs that conform to the
         `CustomLogModel` class. This class should be a Pydantic model that
          inherits from `BaseModel`.

    Logging a dict that conforms to the class schema will get it logged to both
    the console and file. Example:

    ```
    TEST_LOG_FILE = "testing.log"

    class TestMetric(BaseModel):
        field1: str
        field2: int

    setup_logging(logfile=TEST_LOG_FILE, CustomLogModel=TestMetric, pool_size=1)

    # Will only appear on console stream
    logging.info("Normal log. Will only appear in console")

    # Will appear in file too!
    logging.info(
        json.dumps(
            {
                "field1": "Custom log",
                "field2": "Will appear both in file and in console",
            }
        )
    )
    ```

    Keyword Arguments:
        pool_size -- Size of thread pool. 0 means sync logging (default: {0})
    """
    # Set basic config for logging module
    logging.basicConfig(level=logging.INFO)

    # stdout handler. Can log to a file instead if we modify the file writer
    config.add_handlers(file_writer(formatter=customLogFormat))

    # file handler. We add here the filter to only save performance metrics
    config.add_handlers(
        file_writer(
            logfile,
            filter=performanceLogFilter(LogModel=CustomLogModel),
            formatter=customLogFormat,
        )
    )

    # initialize the thread pool if needed
    config.set(pool_size=pool_size)


if __name__ == "__main__":
    TEST_LOG_FILE = "testing.log"

    class TestMetric(BaseModel):
        field1: str
        field2: int

    setup_logging(logfile=TEST_LOG_FILE, CustomLogModel=TestMetric, pool_size=1)

    # Will only appear on console stream
    logging.info("Normal log. Will only appear in console")

    # Will appear in file too!
    logging.info(
        json.dumps(
            {
                "field1": "Custom log",
                "field2": "Will appear both in file and in console",
            }
        )
    )

