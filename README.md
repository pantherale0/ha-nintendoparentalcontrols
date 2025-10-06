# Nintendo Switch Parental Controls

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
![Install Stats][stats]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]

_Integration to integrate with [ha-nintendoparentalcontrols][ha-nintendoparentalcontrols]._

## NOTICE

This integration will soon be available in Home Assistant core, therefore, this specific custom component will no longer receive updates.

**This integration will set up the following platforms.**

| Platform | Description                                       |
| -------- | ------------------------------------------------- |
| `sensor` | Read only states (such as current screen time)    |
| `switch` | Per app and device controls                       |
| `time`   | Control limit time and bonus time for current day |

## Supported features

- Sensor for used screen time
- Screen time sensor displays last 5 days of usage, including applications used and players.
- Switch to enable/disable the "Suspend Software" mode once the screentime limit has been reached.
- Switch to enable and disable alarms for the current day, Nintendo resets this back at midnight.
- Time platform to adjust the total amount of time allowed to play in the day, setting this to 0:00 and turning on "Suspend Software Limit" will effectively disable the device unless you enter the parental controls pin
- Optional switches to control the whitelist state of applications, this needs to be configured from the options menu.

## Installation

1. Add repository URL into HACS and install "Nintendo Switch Parental Controls"
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Nintendo Switch Parental Controls
1. You will be prompted for an access token, click the link provided in the description of the dialog (this is unique) and login to your Nintendo account.
1. After login, you will see a `Linking an External Account` screen. For the account you wish to link, right click on the red button `Select this person` and click `Copy Link`
1. #Optional# - If you inspect the link you should find the following format npf54789befxxxxxxxx://auth#session_token_code={redacted}&state={redacted}&session_state={redacted}
1. Close the `Nintendo Account` tab
1. Paste the previously copied value into the `Access token` field (the entire string you copied)
1. Click `Submit`
1. The configuration flow should then show some additional options, don't adjust the first box as this is the refresh token that will be used to refresh the access tokens in the background and is retrieved from Nintndo using the token you previously provided.
1. Click `Submit`

## Configuration is done in the UI

<!---->

You can configure applications to register entites for within the "CONFIGURE" menu after setting up the integration for the first time.

Enabling debugging will produce a lot of log entiries.

## Known issues

- New Nintendo Switch devices (or ones recently enrolled in Nintendo Parental Controls) don't usually provide enough data for the integration to function properly. If you see different errors and warnings such as `Unable to update daily summary for device Switch 1: A summary for the given date 2024-01-01 20:00:00 does not exist` this will resolve itself if left for a period of time once Nintendo has started to collect data from your Switch. See #55
- Duplicate application names in configuration menu - this is purely cosemtic, the underlying IDs are identical between different consoles.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

---

[ha-nintendoparentalcontrols]: https://github.com/pantherale0/ha-nintendoparentalcontrols
[commits-shield]: https://img.shields.io/github/commit-activity/y/pantherale0/ha-nintendoparentalcontrols.svg?style=for-the-badge
[commits]: https://github.com/pantherale0/ha-nintendoparentalcontrols/commits/main
[stats]: https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.nintendo_parental.total&style=for-the-badge
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-green.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/pantherale0/ha-nintendoparentalcontrols.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/pantherale0/ha-nintendoparentalcontrols.svg?style=for-the-badge
[releases]: https://github.com/pantherale0/ha-nintendoparentalcontrols/releases
