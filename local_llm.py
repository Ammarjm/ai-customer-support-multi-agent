import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)


MODEL_NAME = "google/flan-t5-base"


# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)


# Load model
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME
)


# Use GPU if available
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

model.to(device)


def generate_text(
    prompt,
    max_new_tokens=150
):
    """
    Generate text using the shared FLAN-T5 model.
    """

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False
        )

    answer = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    return answer.strip()