
# Functionalities
## It's just a supervision GUI for my home network, in python.
* It can ping
* It can test HTTP
* it can runs SSH ans check patterns
* SSH can be configured for obsolete ciphers (as my NAS is old)
* It produce voice message when there are failures or when back to normal
* GUI propose the list of device that are down
* GUI propose to show the logs, which contain the history of up and down devices
* icon is changed depending on the state of the supervision
* some devices are declared "important". 
 * if only "non important" devices are down, the icon is yellow warning. 
 * if any important device is down, the icon is red alert.

## It's just a tool for my home. I could for example:
* supervise with ping/http my routers, my box, my NAS, my camera, my wifi printer
* check if my openwrt routers have wifi 2.4GHz and 5GHz both up
* check if my (old) NAS, and one of my OpenWRT router have mounted their disks
* check if IPV6 connectivity is OK, as much as IPV4, pinging/getting google services, my box...
* check if my company VPN site is up

## Internationalization :
* you can change the voice language 
* you can change the voice messages
* you can change the log message
* you can change the GUI labels

# Configuration
## Config.json
This json file determines 
* Global settings, 
* Internalionalization settings
* Default value for some Device parameters

an example is in /samples/config-french.json with localization as French.

### Global settings :
* `log_file` : the log file to writ to (set `nul:` for no log file)
* `devices_file` : path of the devices.json to load
* `devices_file_out` : path to write loaded devices into (for debug. set empty or `nul:` to prevent this)

### Speech parameterization and internationalization
* `speech_speed` : speed of vocalization (standard is 200, I prefer 150)
* `speech_volume` : speech volume (as a flow, max is 1.0)
* `speech_voice` : speech language
* `speech_text_all_is_reachable` : message when all is reachable
* `speech_text_unreachable` : message after the list of unreachable devices

### Log internationalization
* `log_message_reconnected` : text when a devices is reconnected
* `log_message_unreachable_for` : text on how long the devices was disconnected
* `log_message_reachable` : text when a devices is connected
* `log_message_unreachable` : text when a devices is disconnected without past connection

### GUI internationalization
* `gui_title` : windows title
* `gui_heading_status` : windows title
* `gui_heading_downtime` : windows title
* `gui_button_show_logs` : windows title
* `gui_button_hide_logs` : windows title
* `gui_message_status_alert` : windows title
* `gui_message_status_warn` : windows title
* `gui_message_status_ok` : windows title
* `gui_title` : windows title
* `gui_title` : windows title

### Default values for Device
* `interval` : interval between devices tests. 
* `accelerate` : factor to reduce interval. Usually changed at Device level
* `failed_accelerate` : factor to reduce interval even more when device is down.
* `ssh_decelerate` : factor to increase interval, for SSH test that often are more heavy.
* `ssh_failed_accelerate` : factor to decrease interval, for SSH test on down devices (to cancel ssh_decelerate maybe).
* `ping_count` : number of ping to send (one reply will be enough)
* `ping_timeout` : delay to wait for the ping reply, and between pings
* `http_retry` : number of tries for HTTP request
* `http_timeout` : maximum time for HTTP requests
* `ssh_retry` : number of tries for SSH request
* `ssh_timeout` : maximum time for HTTP requests
* `ssh_key_file` : SSH key file to use
* `ssh_key_password` : SSH key password
* `ssh_obsolete` : flag to prevent modern cryptographic algorithms, to work with old SSH servers


### Overloading via command line arguments
you can overload the values of any config parameter with a command line flag. 
Just put the `--` prefix, then add the name of the field, changing `_` into `-`, then `=` and then the value

For example:
```
pyNetWatch --devices-file=mydevices.json --speech-volume=0.2
```

## Devices.json

This json file, configured in config.json, contains  an array of Device description with many properties.
an example is in /samples/devices.json 
### General properties
* `name` : name of the device, for GUI, log and speech
* `is_important` : flag to tell that this devices is important

### changing interval
* `interval` : interval between devices tests. Prefer to keep it by defat from Config, and change accelerate/decelerate values.
* `accelerate` : factor to reduce interval. 
* `failed_accelerate` : factor to reduce interval even more when device is down.
* `ssh_decelerate` : factor to increase interval, for SSH test that often are more heavy.
* `ssh_failed_accelerate` : factor to decrease interval, for SSH test on down devices (to cancel ssh_decelerate maybe).

### Ping
* `ip` : IP address or DNS name to ping
* `ping_count` : number of ping to send (one reply will be enough)
* `ping_timeout` : delay to wait for the ping reply, and between pings

### HTTP/S
* `url` : HTTP/HTTPS URL to test (NB: SSL/TLS certificate is not checked)
* `http_retry` : number of tries for HTTP request
* `http_timeout` : maximum time for HTTP requests

### SSH
* `ssh_host` : SSH host
* `ssh_user` : SSH user
* `ssh_user_password` : SSH user password (optional)
* `ssh_command` : SSH Command
* `ssh_pattern_required` : array of string with regex patterns that are all required
* `ssh_pattern_forbiden` : array of string with regex patterns that are each forbidden
* `ssh_retry` : 
* `ssh_retry` : number of tries for SSH request
* `ssh_timeout` : maximum time for HTTP requests
* `ssh_key_file` : SSH key file to use
* `ssh_key_password` : SSH key password
* `ssh_obsolete` : flag to prevent modern cryptographic algorithms, to work with old SSH servers


# Building
* first create a virtual environnement with `create-venv.bat`
* to install the dependencies use `install_requirements.bat` simply installing `requirements.txt` with `pip`, while using the venv
* to package, use `build.bat` script to package the program with `pyinstall` you can use also the `pynetwatch.spec`

# Usage

The first work is to create the config JSON file, and then the device JSON file.

## create config.json file
The filename for the config file is by default: `pynetwatch-config.json` in the current folder, but you can set it via a parameter `--config-file=folder\myconfigfilename.json`
Get inspired by the samples in `samples`and use the documentation above.

in the JSON config file you first need to define the name of the "device_file", or else it will be assumed to be `devices.json`
```json
{
	"devices_file": "perso/devices.json"
}
```
The others fields are set by default to reasonable values, for English language, but you will have to adjust them for your needs...

## create devices.json
The filename of the devices.json file is defined in the config file, or else it will be assumed to be `devices.json`.
Get inspired by the samples in `samples`and use the documentation above.

It is a simple list of JSON objects, abd the fields are documented above. values set in the config file are used as default values in device object.

Here are some common use case I've tested at home:
### testing with ping
```json
[
    {
        "name": "My Box",
        "ip": "192.168.0.254",
        "is_important": true,
        "accelerate":3,
        "ping_count":5
    }
]
```
I ask to ping My Box, at most 5 times, with default timeout (1 second, set in the config.json), givens it's address (it can be a DNS alias).
With `accelerate`I ask to ping it 3 times more frequently that the base frequency set by `interval` in the config. I do that because I have no fear to spam by own devices. For a public machine, I may do the opposite, set `accelerate` to 0.1 to prefent annoying the public server.

### testing with HTTP
```json
[
    {
        "name": "My Server",
        "url":"http://192.168.0.253/favicon.ico",
        "is_important": true,
        "accelerate":2
    }
]
```
I ask to test my HTTP server. I use the default `http_timeout` set to 3 in my config.json, but I may change it for a slow server.

### testing with IPV6
```json
[
    {
        "name": "IP V6 Box",
        "url":"https://[2a01:abc:def:1234::1]:12345/favicon.ico",
        "is_important": false,
        "accelerate":3,
        "ping_count":10
    },
]
```

```json
[
    {
        "name": "IP V6 Box",
        "ip": "[2a01:abc:def:1234::1]",
        "is_important": false,
        "accelerate":3,
        "ping_count":10
    },
]
```
no problem using IPV6 adresses for ping or HTTP

### testing public services, like google 

```
[
    {
        "name": "IP V6",
        "ip": "ipv6.google.com",
        "is_important": false,
        "accelerate":0.2,
        "failed_accelerate":10,
        "ping_count":10
    },
    {
        "name": "IP V4",
        "url":"http://ipv4.google.com/favicon.ico",
        "is_important": true,
        "accelerate":0.5
    }
]
```
It's easy to test Internet connectivity, in IPV4 and IPV6. Note that I reduce the frequency of test not to annoy google servers.

### checking that OpenWRT router's WiFi radio are both UP

```
[
    {
        "name": "WiFi Openwrt",
        "ssh_host": "192.168.0.249",
        "ssh_user":"root",
        "ssh_command":" ubus call network.wireless status | jsonfilter -e '@[@.up=true].config.hwmode'",
        "ssh_pattern_required":["11g","11a"],
        "is_important": false
    }
]
```
Here I use  SSH command to check is my 2 Wifi radio interfaces are up.
I use the default values from config.json:
```
    "ssh_key_file":"C:\\Users\\me`\mysshkey.ppk",
    "ssh_key_password":"mypassword",
    "ssh_retry":2,
    "ssh_timeout":10,
    "ssh_decelerate":10.0,
    "ssh_failed_accelerate":10.0,
    "ssh_obsolete":false

``` 
By defaul, the polling via SSH command is set to be 10 times less frequent than normal, because it's annoying for my routers, and that I don't need to be quickly informed. 
However when a SSH test is failed, I accelerate to normal interval, to knwo quickly when it is back up.
Note also that SSH ciphers are set to normal (not `ssh_obsolete`)

### checking mounted volumes on an old NAS
```
[
    {
        "name": "Sharecenter Disk",
        "ssh_host": "192.168.0.245",
        "ssh_user":"root",
        "ssh_command":"mount",
        "ssh_obsolete":true,
        "ssh_pattern_required":["/dev/sda2","/dev/sdb2","/dev/sda4","/dev/sdb4"],
        "is_important": false
    }
]
```

Here I check that the disk of my old NAS are well mounted. I have activated `ssh_obsolete` so the ciphers are old and recognized by this old NAS.

## launch pyNetWatch
Then you have to launch `pyNetWatch.exe` generated in `dist\pyNetWatch.exe`
You can add parameters as explained above, to overload the values in the config file, or by default. 
The name of parameters is simply the name of the json fields, replacing `_` by `--`with the usual `--`prefix, and the `=` separator with the value afterward.
In `run-pynetwatch.bat`there is a sample launcher with those banal parameters :

```
pyNetWatch.exe --config-file=%~dp0perso\config.json  --config-create=true --log-file=%~dp0perso\pynetwatch.log
```
The idea is to change the pathname of the config file to force creation of the config file if missing and set the path of the log file...

# TODO:
* Find Todo

# Disclaimer: 
* I'm an old programmer (Java, C/C++, and many scripting languages), but a rookie in Python
* I'm lazy
* Tell me if something can be improved (easily)
* Don't hesitate to share use case.

# Credits: 
Thanks to Deepseek for the teaching.
