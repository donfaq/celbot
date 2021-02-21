from celery import Task
from celery.utils.log import get_task_logger
from rusyll import rusyll

logger = get_task_logger(__name__)


class GreetingTask(Task):
    name = "greet"

    def run(self, name):
        logger.info("Replying with greet to %s message", name)
        return f"Hello, {name}"


class HaikuDetector(Task):
    name = "haiku_detector"

    def run(self, text):
        return self.get_haiku(text)

    def get_haiku(self, text):
        max_syllables = (5, 7, 5)
        n_syllables = rusyll.token_to_syllables(text)

        if len(n_syllables) == 17:
            haiku = [[], [], []]
            words = text.split()

            row_num = 0
            for word in words:
                haiku[row_num].append(word)
                syllables_count = len(rusyll.token_to_syllables(' '.join(haiku[row_num])))
                if syllables_count == max_syllables[row_num]:
                    row_num += 1
                    continue
                if syllables_count > max_syllables[row_num]:
                    return None
            return '\n'.join(map(lambda line: ' '.join(line), haiku))
        return None

