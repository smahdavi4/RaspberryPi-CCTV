# RaspberryPi CCTV

This repository contains the code to a project to turn a raspberrypi into a security camera.

## Features

* Setup a security camera using a raspberry pi + a pi camera.
* Get notified of any suspicious motion change using a simple telegram interface.
* Configure Pi to have schedules for capturing images (e.g., activate/deactivate when needed).

## Requirements

* Raspberry Pi board (version 3 or newer) with a Raspbian OS installed.
* Raspberry Pi camera (e.g., OVA5647) connected to the raspberry pi.
* Python >= 3.8
* A private server with a valid IP to store images (optional)

## Quick Start

This project has two parts: 1) Raspberry pi 2) Server. The first part is the raspberrypi client, which is run on the
raspberrypi board and uses a telegram bot as an interface to interact with user. The second part is a server which
stores images captured by the Pi camera. Follow the following steps to setup the security system:

1) Create a [telegram bot](https://core.telegram.org/bots) and save its token.
2) Run the server code on your server using the following command:

```shell
python3 server/server.py --bot-token <BOT_TOKEN> --save-dir <SAVE_DIR>
```

where `<BOT_TOKEN>` is the token you obtained from telegram and `<SAVE_DIR>` is the directory to save images sent by the
raspberry pi.

3) Run the raspberry pi code on your pi using the following command:

```shell
python3 raspberry/main.py --bot-token <BOT_TOKEN> --server-addr <SERVER_ADDR>
```

where `<BOT_TOKEN>` is the telegram bot token and `SERVER_ADDR` is the address of the server on which you ran step two.

4) Subscribe to the bot using your telegram and control the security camera using the bot interface. You will also be
   notified of any suspicious events.  
