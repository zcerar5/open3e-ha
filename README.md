# Open3e Home Assistant Integration

Fork of the Open3e Home Assistant integration adapted for the Open3e Develop Web UI add-on.

The integration keeps the curated base entity set from the original HACS integration and adds Open3e develop room-current values for per-room temperature and humidity.

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=zcerar5&repository=open3e-ha&category=integration)

Add this repository to HACS as a custom integration repository:

```text
https://github.com/zcerar5/open3e-ha
```

## Open3e Develop Web UI Mode

Use this mode with the Open3e Develop add-on from:

```text
https://github.com/zcerar5/ha-addons
```

Default setup values:

| Field | Value |
| --- | --- |
| Connection mode | Open3e Web UI add-on |
| Open3e MQTT topic | `open3e_develop` |
| Open3e MQTT command topic | `open3e_develop/cmnd` |
| MQTT discovery prefix | `homeassistant` |

The integration reads retained MQTT discovery records published by the Web UI add-on, but only creates entities from a curated list:

- the original Open3e HACS feature set
- room-current values from Open3e develop DIDs `1886`, `1889`, `1892`, through `1943`
- room-current subfields `ActualTemp` and `ActualHumidity`

## Classic Listener Mode

Classic mode is still available for an Open3e server running with the MQTT listener command topic, such as `open3e/cmnd`.

## Notes

The Web UI add-on must have relevant datapoints selected and must publish Home Assistant MQTT discovery at least once so this integration can learn the correct MQTT state topics.
