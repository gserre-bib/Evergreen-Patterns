import os
import csv
import ollama
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
import generator
import data

# set the logging level
logging.basicConfig(level=logging.INFO)

# create a jinja2 environment
env = Environment(loader=FileSystemLoader('.'))

model_name='llama2:13b'
#model_name='qwen:14b'

for pattern in data.patterns:
  full_prompt = f"{data.pattern_prefix}\n{pattern['prompt']}\nPlease describe 4 graduals levels of maturity for this pattern, from absolute beginner to master of the practice."
  # replace the pattern_name in the prompt with the actual pattern name
  template = env.from_string(full_prompt)
  full_prompt = template.render(pattern)
  response_content, creation_date = generator.generate_text_ollama(model_name, full_prompt)
  logging.info(response_content)
