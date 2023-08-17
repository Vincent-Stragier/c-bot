# Interactive agent for visually impaired and blind individuals (based on Llama2)

This project uses a tier application to run the Large Language Model and accesses it using an API.
The current tier application is based on Oobabooga's text generation webui. In the future support for Petals, or OpenAI API will be added.

## Installation

You first need to setup the tier application server. Then you can install this server application on a different or on the same machine.

### Installation of the tier application

Here Oobabooga's application is installed on an Ubuntu server equipped with 2 RTX 3090.

For reference, I'm using the [one click installer](https://github.com/oobabooga/text-generation-webui#one-click-installers) with a script to set up the API and a Ngrok tunnel. I installed Ngrok via pip (`python -m pip install pyngrok`).

```bash
#!/usr/bin/env bash

trap_with_arg() { # from https://stackoverflow.com/a/2183063/804678
  local func="$1"; shift
  for sig in "$@"; do
    trap "$func $sig" "$sig"
  done
}

stop() {
  trap - SIGINT EXIT
  printf '\n%s\n' "received $1, killing child processes"
  kill -s SIGINT 0
}

trap_with_arg 'stop' EXIT SIGINT SIGTERM SIGHUP

export OOBABOOGA_FLAGS="--extension api --loader exllama_hf --model  TheBloke_Llama-2-13B-chat-GPTQ --verbose --listen --chat --max_seq_len 4096 --compress_pos_emb 1"

bash /path/to/oobabooga_linux/start_linux.sh &
# Wait for the application to start
sleep 30s

# Start the reverse proxy
# --basic-auth 'api_token:your_custom_token'  is optional, it allows using basic access authentication
# The username is 'api_token' and the password is 'your_custom_token'
ngrok http --domain=my-ngrok-domain.ngrok-free.app 5000 --basic-auth 'api_token:your_custom_token' &
while true; do read; done

```

Then I use `screen` to launch the script in the detached mode:

```bash
# api is the session name, -dm is to start the session in detached mode.
screen -dm -S api bash ~/start_api.sh
```

I can check if the `screen` session is running with:

```bash
screen -ls
```

And I can kill the session using:

```bash
screen -X -S api kill
```

But, I'm still battling with the API on the client-side, trying to generate a working prompt…

### Installation of this application

Note that you might need to install espeak on your computer. You can install this application using pip (and git) via the following command:

```bash
python3 -m pip install --force-reinstall git+https://github.com/Vincent-Stragier/c-bot.git
```

#### Configuration

To simplify the configuration, multiple settings can be changed using a YAML file. Then you can start the application using the following command:

```bash
python3 -m seeingllama2 -c /path/to/config.yaml
```

##### config.yaml

```yaml
---
flask:
  # Use the debug functionality of Flask
  debug: true
  # Listen on port 80
  port: 80
  # Listen from any interface.
  # You can use "127.0.0.1" when using a reverse proxy.
  host: "0.0.0.0"
  # You can configure Flask to use an SSL certificate.
  # To generate this certificate, you need an hostname, and
  # a service like Letsencrypt to register your domain.
#   ssl_keyfile: "/etc/letsencrypt/live/example.com/fullchain.pem"
#   ssl_certfile: "/etc/letsencrypt/live/example.com/privkey.pem"

# Here you can change some details of the application
html_index:
  title: C-Bot
  chat_title: Your chat
  chat_number_of_messages: 0 message
  chat_send_button_value: Send
  chat_input_placeholder: Write your message here
  footer_text: >-
    © 2023 - C-Bot, handmade by Vincent Stragier,
    University of Mons and les Amis des Aveugles, Ghlin

js_app:
  bot_name: C-Bot
  username: Vini

interface:
  locale: en_US.UTF-8

# Here are the pyttsx4 settings
voice:
  id: 2
  # In word per minute
  rate: 200
  # A float between 0 and 1.
  volume: 1.0

llm_api:
  # The API to use
  name: oobabooga
  # The URL of the API (or its IP address)
  url: "my-ngrok-domain.ngrok-free.app"
  port: 443

  path: "/api/v1/generate"
  http_basic_auth:
    username: api_token
    password: your_custom_token
```
