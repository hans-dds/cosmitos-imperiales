from abc import ABC, abstractmethod
import pandas as pd


class IAIAdvisor(ABC):
    @abstractmethod
    def analyze_detractors(self, df: pd.DataFrame) -> str:
        pass
