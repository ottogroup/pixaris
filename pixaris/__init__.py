# import os

# os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = (
#     "python"  # fix for aiplatform, it's currently using pre 3.20 version of protobuf and we using > 5.0
# )

"""Pixaris package setup."""

import logging

LOG_LEVEL = logging.INFO
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

