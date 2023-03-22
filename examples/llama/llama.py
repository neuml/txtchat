"""
Llama module
"""

import torch

from peft import PeftModel

from transformers import LlamaTokenizer, LlamaForCausalLM
from transformers import pipeline

from txtai.pipeline import Pipeline


class Llama(Pipeline):
    """
    Runs a LLaMA model with a txtai pipeline.
    """

    def __init__(self, base="decapoda-research/llama-7b-hf", lora="tloen/alpaca-lora-7b"):
        """
        Creates a new LLaMA pipeline.

        Args:
            base: base model path
            lora: lora fine-tuned model path
        """

        # Load base model
        model = LlamaForCausalLM.from_pretrained(
            base,
            load_in_8bit=False,
            torch_dtype=torch.float16,
            device_map="auto",
        )

        # Base tokenizer
        tokenizer = LlamaTokenizer.from_pretrained(base)

        # Load PEFT-LoRA fine-tuned model
        model = PeftModel.from_pretrained(model, lora, torch_dtype=torch.float16)

        # Load as half precision
        model.half()
        model.eval()

        # Create text generation pipeline
        self.pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)

    def __call__(self, texts, temperature=0.1, topp=0.75, topk=40, numbeams=1, maxtokens=128):
        """
        Generates answers from a list of text instructions.

        Args:
            texts: list of instructions
            temperature: optional generation temperature parameter
            topp: optional generation top_p parameter
            topk: optional generation top_k parameter
            maxtokens: optional generation max_tokens parameter
        """

        # Generate answers
        answers = self.pipeline(texts, temperature=temperature, top_p=topp, top_k=topk, num_beams=numbeams, max_new_tokens=maxtokens)

        # Extract answer text and return
        return [x[0]["generated_text"].split("### Response:\n")[1] for x in answers]
