<p align="center">
    <img src="logo.png"/>
</p>

<h3 align="center">
    <p>Conversational search and workflows for all</p>
</h3>

-------------------------------------------------------------------------------------------------------------------------------------------------------

txtchat is a framework for building conversational search and workflows.

![demo](https://raw.githubusercontent.com/neuml/txtchat/master/demo.gif)

A set of intelligent agents are available to integrate with messaging platforms. These agents or personas are associated with an automated account and respond to messages with AI-powered responses. Workflows can use large language models (LLMs), small models or both.

txtchat is built with Python 3.7+ and [txtai](https://github.com/neuml/txtai).

## Installation

The easiest way to install is via pip and PyPI

    pip install txtchat

You can also install txtchat directly from GitHub. Using a Python Virtual Environment is recommended.

    pip install git+https://github.com/neuml/txtchat

Python 3.7+ is supported

See [this link](https://github.com/neuml/txtai#installation) to help resolve environment-specific install issues.

## Messaging platforms

txtchat is designed to and will support a number of messaging platforms. Currently, [Rocket.Chat](https://github.com/RocketChat/Rocket.Chat) is the only supported platform given it's ability to be installed in a local environment along with being MIT-licensed. The easiest way to start a local Rocket.Chat instance is with Docker Compose. See these [instructions](https://docs.rocket.chat/deploy/prepare-for-your-deployment/rapid-deployment-methods/docker-and-docker-compose) for more.

Extending txtchat to additional platforms only needs a new Agent subclass for that platform.

## Personas

The [txtchat-persona](https://hf.co/neuml/txtchat-personas) repository has a list of standard persona workflows. A persona is a combination of a chat agent and workflow that determines the type of responses. Each agent is tied to an account in the messaging platform. Persona workflows are messaging-platform agnostic.

- [Wikitalk](https://hf.co/neuml/txtchat-personas/blob/main/wikitalk.yml): Conversational search with Wikipedia
- [Summary](https://hf.co/neuml/txtchat-personas/blob/main/summary.yml): Reads input URLs and summarizes the text
- [Mr. French](https://hf.co/neuml/txtchat-personas/blob/main/mrfrench.yml): Translates input text into French

The following shows how to start a txtchat persona.

```
# Set to server URL, this is default when running local
export URL=ws://localhost:3000/websocket
export USERNAME=<Rocket Chat User>
export PASSWORD=<Rocket Chat User Password>

# YAML is loaded from Hugging Face Hub, can also reference local path
python -m txtchat.agent wikitalk.yml
```

Want to add a new persona? Simply submit a PR on the Hugging Face Hub repository.

## Wikitalk

The following is a [list of YouTube videos](https://www.youtube.com/watch?v=ROyess8dLoA&list=PLaqn_lxC5d0C_HPe53GPk7jBH3xhBcgu-) that show how txtchat works. These videos run a series of queries with the Wikitalk persona. Wikitalk is a combination of a Wikipedia embeddings index and a LLM prompt to answer questions.

Every answer shows an associated reference with where the data came from. Wikitalk will say "I don't have data on that" when it doesn't have an answer.

### History

Conversation with Wikitalk about history.

[![History](https://img.youtube.com/vi/ROyess8dLoA/maxresdefault.jpg)](https://youtube.com/watch?v=ROyess8dLoA)

### Sports

Talk about sports.

[![Sports](https://img.youtube.com/vi/LXRB-iruKSc/maxresdefault.jpg)](https://youtube.com/watch?v=LXRB-iruKSc)

### Culture

Arts and culture questions.

[![Culture](https://img.youtube.com/vi/OkObkNhJIgk/maxresdefault.jpg)](https://youtube.com/watch?v=OkObkNhJIgk)

### Science

Let's quiz Wikitalk on science.

[![Science](https://img.youtube.com/vi/-rsYDsZc9Wo/maxresdefault.jpg)](https://youtube.com/watch?v=-rsYDsZc9Wo)

## Summary

Not all workflows need a LLM. There are plenty of great small models available to perform a specific task. The Summary persona simply reads the input URL and summarizes the text.

[![Summary](https://img.youtube.com/vi/PBJm9aDqkn0/maxresdefault.jpg)](https://youtube.com/watch?v=PBJm9aDqkn0)

## Mr. French

Like the summary persona, Mr. French is a simple persona that translates input text to French.

[![French](https://img.youtube.com/vi/4x8pOIm4rbo/maxresdefault.jpg)](https://youtube.com/watch?v=4x8pOIm4rbo)
