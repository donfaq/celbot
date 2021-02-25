import logging
import pathlib

import markovify

from bot.engine.database import DatabaseWrapper


class MarkovifyWrapper:
    def __init__(self, models_folder: pathlib.Path, db: DatabaseWrapper = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__models_folder = models_folder
        self.__max_size = 200
        self.db = db
        self.__saved_model = self.__load_saved_model()

    def __load_saved_model(self):
        models = []
        for model_path in self.__models_folder.glob("*.json"):
            self.logger.info("Reading model from file '%s'", model_path)
            with open(model_path, mode='r') as model_file:
                model_raw_json = model_file.read()
                models.append(markovify.Text.from_json(model_raw_json))
        return markovify.combine(models=models, weights=[1] * len(models))

    def __model_from_db(self):
        self.logger.info("Selecting all texts from DB")
        texts = self.db.select_all_texts()
        return markovify.Text(
            input_text=". ".join(map(lambda x: x[0], texts)),
            retain_original=False
        )

    def __get_current_model(self):
        model = self.__saved_model
        if self.db:
            model = markovify.combine(models=[model, self.__model_from_db()], weights=[1, 1.5])
        return model.compile()

    def generate(self, predicate=None):
        message = None
        model = self.__get_current_model()
        if model:
            try:
                if predicate:
                    self.logger.debug("Generating message with predicate token: {}".format(predicate))
                    message = model.make_sentence_with_start(predicate, strict=False)
                    if not message:
                        raise KeyError
                    if len(message) > self.__max_size * 2:
                        raise KeyError
            except (KeyError, markovify.text.ParamError):
                self.logger.debug("No such token in corpus: {}".format(predicate))
            if not message:
                self.logger.debug("Generating short message")
                message = model.make_short_sentence(self.__max_size)
        message = "I have nothing to say yet" if not message else message
        return message
