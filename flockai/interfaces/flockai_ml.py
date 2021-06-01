import abc


class FlockAIClassifier(abc.ABC):
    def __init__(self):
        self.model = None

    @abc.abstractmethod
    def _load_model(self):
        raise NotImplementedError

    @abc.abstractmethod
    def predict(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_model_input(self):
        raise NotImplementedError
