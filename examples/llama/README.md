# Talk with LLaMA

This example shows how an instruction-following LLaMA model can be loaded with txtchat. Run the following steps to get started.

![demo](https://raw.githubusercontent.com/neuml/txtchat/master/images/llama.png)

## Install

Install the following required dependencies. As of March 2023, running LLaMA through Hugging Face Transformers requires the latest development release.

```
pip install txtchat git+https://github.com/huggingface/transformers.git peft sentencepiece
```

This example also requires an instance of [Rocket.Chat](https://github.com/RocketChat/Rocket.Chat) running locally. The easiest way to start a local Rocket.Chat instance is with Docker Compose. See these [instructions](https://docs.rocket.chat/deploy/prepare-for-your-deployment/rapid-deployment-methods/docker-and-docker-compose) for more.

## Download example pipeline

```
wget https://raw.githubusercontent.com/neuml/txtchat/master/examples/llama/llama.py
```

## Start the persona

```
# Set to server URL, this is default when running local
export AGENT_URL=ws://localhost:3000/websocket
export AGENT_USERNAME=<Rocket Chat User>
export AGENT_PASSWORD=<Rocket Chat User Password>

# YAML is loaded from Hugging Face Hub, can also reference local path
python -m txtchat.agent llama.yml
```

This workflow uses a base 7B parameter LLaMA model with a PEFT-LoRA fine-tuned model (Alpaca-LoRA). 

# Modify configuration

Running the steps above uses default configuration found in the [txtchat-persona](https://hf.co/neuml/txtchat-personas) repository. This configuration can be modified and run locally. The default configuration is shown below.

```yaml
# LLaMA model inference with a txtai workflow
workflow:
  chat:
    tasks:
      - task: template
        template: |-
          Below is an instruction that describes a task. Write a response that appropriately completes the request.
          ### Instruction:
          {text}
          ### Response:
        action: llama.Llama
```

## Further reading

The following great projects below have made this example possible. Read more on LLaMA and Alpaca at the links below.

It's important to note that LLaMA models and derivatives are licensed under a *non-commercial license*.

- [Introducing LLaMA: A foundational, 65-billion-parameter large language model](https://ai.facebook.com/blog/large-language-model-llama-meta-ai/)
- [Stanford Alpaca: An Instruction-following LLaMA Model](https://github.com/tatsu-lab/stanford_alpaca)
- [Alpaca-LoRA: Low-Rank LLaMA Instruct-Tuning](https://github.com/tloen/alpaca-lora) 
