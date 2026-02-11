<p align="center">
    <img src="https://raw.githubusercontent.com/neuml/txtchat/master/logo.png"/>
</p>

<p align="center">
    <b>Local chat assistants with AI superpowers</b>
</p>

-------------------------------------------------------------------------------------------------------------------------------------------------------

txtchat helps you build your own local chat assistants with AI superpowers.

![demo](https://raw.githubusercontent.com/neuml/txtchat/master/demo.gif)

The advent of large language models (LLMs) has pushed us to reimagine how we work. We can now do much more than just manually searching for answers, processing each result and then executing our tasks. `Agents` are like ⚡superpowered⚡ versions of ourselves that can find information, digest it and make decisions exponentially faster than ever before.

txtchat adds a set of intelligent agents that are available to integrate with messaging platforms. These agents or personas are associated with an automated account and respond to messages with AI-powered responses. Workflows can use large language models (LLMs), small models or both.

txtchat is built with Python 3.10+ and [txtai](https://github.com/neuml/txtai).

## Installation

The easiest way to install is via pip and PyPI

    pip install txtchat

You can also install txtchat directly from GitHub. Using a Python Virtual Environment is recommended.

    pip install git+https://github.com/neuml/txtchat

Python 3.10+ is supported

See [this link](https://github.com/neuml/txtai#installation) to help resolve environment-specific install issues.

## Messaging platforms

txtchat is designed to support any messaging platform. The following platforms currently have providers, select a quickstart link for the platform of your choice to get started with a local install.

- [Rocket.Chat](https://github.com/RocketChat/Rocket.Chat) ([Quickstart](https://docs.rocket.chat/v1/docs/deploy-with-docker-docker-compose#step-1-install-docker-and-docker-compose))
- [Mattermost](https://github.com/mattermost/mattermost) ([Quickstart](https://docs.mattermost.com/deployment-guide/server/deploy-containers.html#itab--Docker--2_1-trial-mattermost-using-docker-preview))

Extending txtchat to additional platforms only needs a new Chat subclass for that platform.

## Architecture

![architecture](https://raw.githubusercontent.com/neuml/txtchat/master/images/architecture.png#gh-light-mode-only)
![architecture](https://raw.githubusercontent.com/neuml/txtchat/master/images/architecture-dark.png#gh-dark-mode-only)

A persona is a combination of a chat agent and workflow that determines the type of responses. Each agent is tied to an account in the messaging platform. Persona workflows are messaging-platform agnostic. The [txtchat-persona](https://hf.co/neuml/txtchat-personas) repository has a list of standard persona workflows.

- [Agent](https://hf.co/neuml/txtchat-personas/blob/main/agent.yml): Agent with connections to the web
- [Wikitalk](https://hf.co/neuml/txtchat-personas/blob/main/wikitalk.yml): Retrieval Augmented Generation (RAG) with Wikipedia
- [Summary](https://hf.co/neuml/txtchat-personas/blob/main/summary.yml): Reads input URLs and summarizes the text
- [Mr. French](https://hf.co/neuml/txtchat-personas/blob/main/mrfrench.yml): Translates input text into French

The following command shows how to start a txtchat persona with Rocket.Chat.

```
# Set to server URL, this is the default when running local
export AGENT_URL=http://localhost:3000
export AGENT_USERNAME=<Rocket Chat User>
export AGENT_PASSWORD=<Rocket Chat User Password>

# YAML is loaded from Hugging Face Hub, can also reference local path
python -m txtchat.agent agent.yml
```

or with Mattermost.

```
# Set to server URL, this is the default when running local
export AGENT_URL=http://localhost:3000 
export AGENT_TOKEN=<Account Token>
export AGENT_PROVIDER=mattermost

python -m txtchat.agent agent.yml
```

Want to add a new persona? Simply create a [txtai app](https://neuml.github.io/txtai/api/configuration) and save it to a YAML file.

## Examples

The following is a [list of YouTube videos](https://www.youtube.com/watch?v=ROyess8dLoA&list=PLaqn_lxC5d0C_HPe53GPk7jBH3xhBcgu-) that shows how txtchat works. These videos run a series of queries with the Wikitalk persona. Wikitalk is a combination of a [Wikipedia embeddings index](https://huggingface.co/NeuML/txtai-wikipedia) and a LLM prompt to answer questions.

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

### Summary

Not all workflows need a LLM. There are plenty of great small models available to perform a specific task. The Summary persona simply reads the input URL and summarizes the text.

[![Summary](https://img.youtube.com/vi/PBJm9aDqkn0/maxresdefault.jpg)](https://youtube.com/watch?v=PBJm9aDqkn0)

### Mr. French

Like the summary persona, Mr. French is a simple persona that translates input text to French.

[![French](https://img.youtube.com/vi/4x8pOIm4rbo/maxresdefault.jpg)](https://youtube.com/watch?v=4x8pOIm4rbo)

## Connect your own data

Want to connect txtchat to your own data? All that you need to do is create a txtai workflow. Let's run through an example of building a Hacker News indexing workflow and a txtchat persona.

First, we'll define the indexing workflow and build the index. This is done with a workflow for convenience. Alternatively it could be a Python program that builds an embeddings index from your dataset. There are over [50 example notebooks](https://neuml.github.io/txtai/examples/) covering a wide range of ways to get data into txtai. There are also example workflows that can be downloaded from in this [Hugging Face Space](https://huggingface.co/spaces/NeuML/txtai).

```yaml
path: /tmp/hn
embeddings:
  path: sentence-transformers/all-MiniLM-L6-v2
  content: true
tabular:
  idcolumn: url
  textcolumns:
  - title
workflow:
  index:
    tasks:
    - batch: false
      extract:
      - hits
      method: get
      params:
        tags: null
      task: service
      url: https://hn.algolia.com/api/v1/search?hitsPerPage=50
    - action: tabular
    - action: index
writable: true
```

This workflow parses the Hacker News front page feed and builds an embeddings index at the path `/tmp/hn`. 

Run the workflow with the following.

```python
from txtai.app import Application

app = Application("index.yml")
list(app.workflow("index", ["front_page"]))
```

Now we'll define the chat workflow and run it as an agent.

```yaml
path: /tmp/hn
writable: false

rag:
  path: Qwen/Qwen3-14B-AWQ
  output: flatten
  system: You are a friendly assistant. You answer questions from users.
  template: |
    Answer the following question using only the context below. Only include information
    specifically discussed.

    question: {question}
    context: {context}

workflow:
  search:
    tasks:
      - rag
```

```
python -m txtchat.agent query.yml
```

Let's talk to Hacker News!

![hn](https://raw.githubusercontent.com/neuml/txtchat/master/images/custom.png)

As you can see, Hacker News is a highly opinionated data source!

Getting answers is nice but being able to have answers with where they came from is nicer. Let's build a workflow that adds a reference link to each answer.

```yaml
path: /tmp/hn
writable: false

rag:
  path: Qwen/Qwen3-14B-AWQ
  output: reference
  system: You are a friendly assistant. You answer questions from users.
  template: |
    Answer the following question using only the context below. Only include information
    specifically discussed.

    question: {question}
    context: {context}

workflow:
  search:
    tasks:
      - rag
      - task: template
        template: "{answer}\nReference: {reference}"
```

![hn-reference](https://raw.githubusercontent.com/neuml/txtchat/master/images/custom-reference.png)

## Further Reading

- [Introducing txtchat — Retrieval Augmented Generation (RAG) powered search](https://medium.com/neuml/introducing-txtchat-next-generation-conversational-search-and-workflows-for-all-97557009fb53)
