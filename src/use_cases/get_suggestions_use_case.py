import pandas as pd
from use_cases.ports.ai_advisor import IAIAdvisor

class GetSuggestionsUseCase:
    def __init__(self, advisor: IAIAdvisor):
        self._advisor = advisor

    def execute(self, df: pd.DataFrame) -> str:
        return self._advisor.analyze_detractors(df)