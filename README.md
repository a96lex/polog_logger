### Polog logger

This is a helper script for adding logging to our repos. 

It is a wrapper around [polog](https://github.com/pomponchik/polog), which adds some extra functionality to the `logging` module, such as async logging.

## Installation

```
poetry add git+ssh://git@gitlab.com:unith-ai/polog_logger.git
```

## Usage

```py
from polog_logger import setup_logging

TEST_LOG_FILE = "testing.log"

class TestMetric(BaseModel):
    field1: str
    field2: int

setup_logging(logfile=TEST_LOG_FILE, pool_size=1, custom_log_model=TestMetric)

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
