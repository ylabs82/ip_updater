# IP Updater

This Python program is designed to automatically update the IP address of a
domain hosted on OVH. It uses the OVH API to perform the update operation. The
program is designed to be run periodically, checking for changes in the public
IP address and updating the OVH DNS record when a change is detected.

The program also includes error handling and logging capabilities. In case of
any issues during the IP update process, such as connection errors or HTTP
errors, the program logs the error details to the system log. Additionally, it
sends notifications about the operation status via Telegram.

The IP Updater program is designed to be flexible and can work with multiple IP
update service providers, not just OVH. This is possible because the program
uses a URL-based approach for updating the IP address.

In the `hosts.data` configuration file, each host object includes an `updater`
property. This property should be set to the URL of the IP update service
provided by the host's DNS provider. The program will replace `<HOST_NAME>` and
`<NEW_IP>` placeholders in this URL with the actual hostname and the new IP
address.

This means that as long as your DNS provider offers a URL-based IP update
service, you can use this program to automatically update your IP address. This
includes providers like No-IP and others, in addition to OVH.

Remember to check the documentation of your DNS provider to find the correct
URL and any necessary authentication details (username and password) for their
IP update service. These details should be included in the `hosts.data` file
for each host that you want the program to manage.

## Features

- Automatic IP address detection
- OVH API integration for DNS record update
- Error handling and logging
- Telegram notifications

## Configuration files

The IP Updater program uses two configuration files: `ip_updater.conf` and
`hosts.data`. Both files must be located in the `/etc/ip_updater` directory.

The `ip_updater.conf` file contains the configuration for the Telegram
notifications, including the Telegram bot token and the ID of the chat where
the notifications will be sent.

The `hosts.data` file contains an array of objects, each representing a host
that the IP Updater program will manage. It includes information such as
whether the host's IP should be updated even if it has not changed, the name of
the host, the URL of the updater service, and the credentials for
authenticating with the updater service.

Please refer to the subsequent sections for detailed information on how to
configure these files.

### ip_updater.conf File

The `ip_updater.conf` file is a JSON file that contains the configuration for
the Telegram notifications. It has two properties:

- `telegram_token`: This is the token for the Telegram bot that will be used to
send notifications. You can obtain this token by creating a new bot through the
BotFather in Telegram.
- `telegram_chat_id`: This is the ID of the chat where the notifications will
be sent. This can be a user ID, group ID, or channel ID depending on where you
want to receive the notifications.

Here is an example of what the `ip_updater.conf` file might look like:

```json
{
    "telegram_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
    "telegram_chat_id": "-1234567890123"
}
```

In this example, `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` is the Telegram
bot token and `-1234567890123` is the ID of the chat where the notifications
will be sent.

### hosts.data File

The `hosts.data` file is a JSON file that contains an array of objects. Each
object represents a host that the IP Updater program will manage. The
properties of each object are as follows:

- `always_update`: A boolean value that indicates whether the host's IP should
be updated even if it has not changed.
- `host_name`: The name of the host whose IP address you want to update.
- `updater`: The URL of the updater service that will be used to update the IP
address of the host. The program will replace `<HOST_NAME>` and `<NEW_IP>`
placeholders in the URL with the actual hostname and the new IP address.
- `username`: The username for authenticating with the updater service.
- `password`: The password for authenticating with the updater service.

Here is an example of what the `hosts.data` file might look like:

```json
[
    {
        "always_update": true,
        "host_name": "mywebsite.com",
        "updater": "https://www.updater.com/update?hostname=<HOST_NAME>&myip=<NEW_IP>",
        "username": "myusername",
        "password": "mypassword"
    },
    {
        "always_update": false,
        "host_name": "myotherwebsite.com",
        "updater": "https://www.otherupdater.com/update?hostname=<HOST_NAME>&myip=<NEW_IP>",
        "username": "myotherusername",
        "password": "myotherpassword"
    }
]
```

In this example, there are two hosts. The first host, `mywebsite.com`, will
always have its IP updated, even if it has not changed. The second host,
`myotherwebsite.com`, will only have its IP updated if it has changed.

Sure, here's a draft for the License section of your README file:

## License

This project is licensed under the MIT License. 

```
The MIT License (MIT)
Copyright (c) 2024 Yago Mouriño Mendaña

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the “Software”), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
