# To control logging level for various modules used in the application:
import logging

logger = logging.getLogger('transformers')
logger.disabled = False
logger.setLevel(logging.CRITICAL)
import re
import os
import transformers

# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

device = 'cpu'


def SimplifyText(txt):
    WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))

    input_ids = tokenizer(
        [WHITESPACE_HANDLER(txt)],
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=512
    )["input_ids"].to(device)

    output_ids = model.generate(
        input_ids=input_ids,
        max_length=512,
        no_repeat_ngram_size=2,
        num_beams=4
    )[0].to(device)

    summary = tokenizer.decode(
        output_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )
    return summary


def module_path(pth):
    print(os.path.abspath(pth))
    return os.path.abspath(pth)


# device = "cuda" if torch.cuda.is_available() else "cpu"

model = transformers.T5ForConditionalGeneration.from_pretrained("model/")
tokenizer = transformers.T5Tokenizer.from_pretrained(module_path('tokenizer/'))
