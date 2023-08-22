from enum import Enum


class GPTModel:
    def __init__(self, name: str, max_tokens: int, price_per_thousand_token) -> None:
        self.name = name
        self.max_tokens = max_tokens
        self.price_per_token = price_per_thousand_token / 1000

    def calculate_price(self, tokens: int) -> float:
        return tokens * self.price_per_token


gpt_3_5_turbo = GPTModel('gpt-3.5-turbo', 4000, 0.0015)
gpt_3_5_turbo_16k = GPTModel('gpt-3.5-turbo-16k', 16000, 0.003)
gpt_4 = GPTModel('gpt-4', 8000, 0.03)
gpt_4_32k = GPTModel('gpt-4-32k', 32000, 0.06)


class EnumGPTModel(Enum):
    gpt_3_5_turbo = 'gpt-3.5-turbo'
    gpt_3_5_turbo_16k = 'gpt-3.5-turbo-16k'
    gpt_4 = 'gpt-4'
    gpt_4_32k = 'gpt-4-32k'


def get_gpt_model(name: EnumGPTModel) -> GPTModel:
    match name:
        case EnumGPTModel.gpt_3_5_turbo:
            return gpt_3_5_turbo
        case EnumGPTModel.gpt_3_5_turbo_16k:
            return gpt_3_5_turbo_16k
        case EnumGPTModel.gpt_4:
            return gpt_4
        case EnumGPTModel.gpt_4_32k:
            return gpt_4_32k
    raise ValueError(f'Unknown model {name}')
