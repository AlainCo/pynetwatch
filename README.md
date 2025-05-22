# It's just a supervision GUI for my home network, in python.
* It can ping
* It can test HTTP
* it can runs SSH ans check patterns
* SSH can be configured for obsolete ciphers (as my NAS is old)
* It produce voice message when there are failures or when back to normal
* GUI propose the list of device that are down
* GUI propose to show the logs, which contain the history of up and down devices
* icon is changed depending on the state of the supervision

# It's just a tool for my home. I could for example:
* supervise with ping/http my routers, my box, my NAS, my camera, my wifi printer
* check if my openwrt routers have wifi 2.4GHz and 5GHz both up
* check if my (old) NAS, and one of my OpenWRT router have mounted their disks
* check if IPV6 connectivity is OK, as much as IPV4, pinging/getting google services, my box...
* check if my company VPN site is up

# TODO:
* vocal message and GUI are in French (Just add field in Config)
* reading json into Device, and also setting default values from Config, could be made more automatic
* I should add samples for Config and Device json
* I should make a documentation for for Config and Device json at least 

# Disclaimer: 
* I'm an old programmer (Java, C/C++, and many scripting languages), but a rookie in Python
* I'm lazy

# Credits: 
Thanks to Deepseek for the teaching.
