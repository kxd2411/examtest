import openai
from pywebio import start_server
from pywebio.output import put_table
from pywebio.input import input
import os

openai.api_key = os.getenv("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")

def openai_response(question):
    response = openai.Completion.create(
        engine="davinci",
        prompt=question,
        temperature=0.5,
        max_tokens=100,
        top_p=0.3,
        frequency_penalty=0.6,
        presence_penalty=0.0,
        stop=['']
    )
    return '{}'.format(response.choices[0].text[6:])

def main():
    while True:
        question = input('Ask something')
        put_table([
            ['Q:', question],
            ['A:', openai_response(question)]
        ])

if __name__ == "__main__":
    main()