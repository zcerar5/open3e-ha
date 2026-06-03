# Open3e HomeAssistant Integration

Fork of the Open3e Home Assistant integration for the original Open3e MQTT listener.

This keeps the original device and entity categorisation, and adds room temperature and humidity sensors for:

- Open3e room-current DIDs `1886`, `1889`, `1892`, through `1943`
- ViCare/ZigBee current-value DIDs `2086`, `2089`, `2092`, through `2143`, and `2262`, `2265`, through `2319`

<img height="500" src="https://github.com/user-attachments/assets/02e14d18-757c-44f6-b413-0be74dcbb31a" /> <img height="500" src="https://github.com/user-attachments/assets/d7a38dbe-61e5-464e-a2fa-b4a120a3cfff" />

#### Supported Devices

- [x] Vitocal
- [x] Vitoair
- [x] Vitodens
- [x] Vitocharge

## Installation

**This integration needs the Open3e server in order to communicate with the devices. So make sure its installed and
running in listen mode.**

<details>
<summary>Open3e Server Installation Instructions</summary>

There are various ways to run the Open3e server that communicates with this integration.

1. Install Open3e.
2. Make sure your Open3e server runs in listen mode and is connected to MQTT.
3. Proceed with installing this integration via the button below.
</details>

### MQTT topics

This fork is paired with the classic `Open3e` add-on from `zcerar5/ha-addons`, not the separate `Open3e Develop` Web UI add-on.

Use these matching defaults:

| Open3e add-on option | Open3e HA setup field | Value |
| --- | --- | --- |
| `Server_Topic` | `Open3e MQTT topic` | `open3e` |
| `Listen_Topic` | `Open3e MQTT command topic` | `open3e/cmnd` |

The integration already uses these values by default. Only change them if you also changed the matching topics in the Open3e add-on.


[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=zcerar5&repository=open3e-ha&category=integration)

## Features

- Connects to Open3e via MQTT
- Automatic device discovery and entity setup
- Integrates sensors, climate controls, automations, etc.
- Automatic data refreshing
- Varies data refreshing interval based on integration and enabled entities
- Room-current temperature and humidity sensors from DIDs `1886` to `1943`
- ViCare/ZigBee room-device temperature and humidity sensors from DIDs `2086` to `2319`
- German & English language support
