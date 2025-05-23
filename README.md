
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

# TODO:
* Documentation for Config and Device json
* General documentation

# Disclaimer: 
* I'm an old programmer (Java, C/C++, and many scripting languages), but a rookie in Python
* I'm lazy

# Credits: 
Thanks to Deepseek for the teaching.
