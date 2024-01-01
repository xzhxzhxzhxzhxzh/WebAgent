# CogVLM/CogAgent Web Agent

This is an application of CogVLM/CogAgent and Puppeteer, aiming to demonstrate the feasibility of a web AI agent with the help of vision-language model. User can chat with the web AI agent, then, the agent will do task planning and interact with webpages like a human to complete user's tasks.

## Demonstration

In this demonstration I show how to use the web agent to buy a MacBook on Amazon.
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/2prbGdOzB0Q/0.jpg)](https://www.youtube.com/watch?v=2prbGdOzB0Q)

## Getting started

Install Puppeteer:
```shell
$ npm install puppeteer
$ npm install puppeteer-extra-plugin-stealth
$ npm install puppeteer-extra
```

Prepare python environment:
```shell
$ pip install -r requirements.txt
```

Go through the code for loading model in `api.py`, update it according to your available GPUs. You can follow the instruction here: https://huggingface.co/THUDM/cogvlm-chat-hf

By default, the initial webpage is set to https://www.amazon.com/ at `chat_loop.py` line 222. You can change it to your interested webpage.

Start the CogVLM/CogAgent API:
```shell
$ python api.py
```

Start the chat loop:
```shell
$ python chat_loop.py
```

## Examples

You can ask stuff like this, for example:

- Can you guide me to "buy a MacBook Pro M3"?
- Can you guide me through steps to "go to the product page of the first listed product"?
- Can you guide me through steps to "select 1TB capacity"?
- Can you guide me through steps to "select Apple M3 Max Chip"?

## Reference

This project was inspired by:

- https://github.com/THUDM/CogVLM
- https://github.com/unconv/gpt4v-browsing

Thanks for their contribution!