from common.logging import logger

import pickle


DATA_FILENAME = "DATA.pickle"


class KeyValueStore:
    def __init__(self):
        self.data = {}

    def save_data_to_stable_storage(self):
        with open(DATA_FILENAME, "wb") as file:
            pickle.dump(self.data, file)
        logger.info(f"KV Store data is successfully written to a stable storage")

    def load_data_from_stable_storage(self):
        try:
            with open(DATA_FILENAME, "rb") as file:
                self.data = pickle.load(file)
            logger.info(f"KV Store data is successfully loaded from a stable storage")
        except Exception as err:
            logger.info(f"Nothing is loaded from a stable storage. Why: {str(err)}")


KV_STORE = KeyValueStore()
