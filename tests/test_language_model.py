import sys, os
from typing import Dict
import torch
from transformers import BatchEncoding
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
import syncode.common as common
from syncode.language_model import HuggingFaceModel
from syncode.parsers.grammars.grammar import Grammar
from transformers.generation.utils import GenerationMode
from transformers.generation.configuration_utils import  PretrainedConfig
from transformers.generation.utils import GenerationMixin
from transformers.modeling_outputs import CausalLMOutputWithPast
import unittest


class TestModel(GenerationMixin):
    def __init__(self) -> None:
        self.device = 'cpu'
        self.config = PretrainedConfig()
    
    def __call__(self, input_ids: torch.Tensor, attention_mask: torch.Tensor, kv_cache=None) -> CausalLMOutputWithPast:
        output_logits = torch.randn(1, 1, 20)
        return CausalLMOutputWithPast(
            logits=output_logits
            )
    
    def generate(self, input_ids: torch.Tensor, max_new_tokens=10, **kwargs):
        random_ids = torch.randint(0, 20, (input_ids.size(0), max_new_tokens))
        return torch.cat([input_ids, random_ids], dim=1)
    
    def _get_generation_mode(self, a, b) -> GenerationMode:
        return GenerationMode.GREEDY_SEARCH

class TestTokenizer:
    def __init__(self) -> None:
        vocab = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '-', '*', '/', '(', ')', ' ', '\n', '\t', '=']
        self.vocab = vocab
        self.eos_token_id = ''

    def __call__(self, input_batch: list[str], return_tensors="pt") -> BatchEncoding:
        # This works since we have single character tokens
        # return torch.tensor([[self.vocab.index(c) for c in input] for input in input_batch])
        return BatchEncoding({
                'input_ids': torch.tensor([[self.vocab.index(c) for c in input] for input in input_batch]),
                'attention_mask': torch.ones(len(input_batch), len(input_batch[0]))
             })
    
    def decode(self, token_ids, skip_special_tokens=False):
        return ''.join([self.vocab[i] for i in token_ids])
    
    def get_vocab(self) -> Dict[str, int]:
        return {v: i for i, v in enumerate(self.vocab)}

class TestHuggingFaceModel(unittest.TestCase):
    def test_generate_batch_completion_grammar(self):
        torch.manual_seed(0)
        model = TestModel()
        tokenizer = TestTokenizer()
        logger = common.EmptyLogger()
        lm = HuggingFaceModel(model, Grammar('calc'), logger, tokenizer, mode='original', max_new_tokens=15, device='cpu')
        prompt = "113 + 235 + 17"
        output = lm.generate_batch_completion_grammar(prompt, 1)
        self.assertEqual(len(output[0]), 15, "The output length does not match the expected value.")
    
    def test_generate_batch_completion_grammar2(self):
        torch.manual_seed(0)
        model = TestModel()
        tokenizer = TestTokenizer()
        logger = common.EmptyLogger()
        lm = HuggingFaceModel(model, Grammar('calc'), logger, tokenizer, mode='original', max_new_tokens=15, device='cpu')
        prompt = "113 + 235 + 17"
        output = lm.generate_batch_completion_grammar(prompt, 2)
        print(output)
        self.assertEqual(len(output[0]), 15, "The output length does not match the expected value.")
        self.assertEqual(len(output[1]), 15, "The output length does not match the expected value.")
