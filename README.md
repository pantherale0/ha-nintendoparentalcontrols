# Nintendo Switch Parental Controls

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]

_Integration to integrate with [ha-nintendoparentalcontrols][ha-nintendoparentalcontrols]._

**This integration will set up the following platforms.**

| Platform | Description                                    |
| -------- | ---------------------------------------------- |
| `sensor` | Read only states (such as current screen time) |
| `switch` | Per app and device controls                    |

## Supported features

- Sensor for used screen time
- Screen time sensor displays last 5 days of usage, including applications used and players.
- Switch to enable/disable the "Suspend Software" mode once the screentime limit has been reached.
- Switch to enable and disable alarms for the current day, Nintendo resets this back at midnight.
- Time platform to adjust the total amount of time allowed to play in the day, setting this to 0:00 and turning on "Suspend Software Limit" will effectively disable the device unless you enter the parental controls pin
- Optional switches to control the whitelist state of applications, this needs to be configured from the options menu.
<!-- - Raises issues if an error occures with the OAuth configuration (such as Nintendo changing the client IDs).
- Raises a configflow to handle reauthentication if the session token expires (usually around 2 years). -->

## Installation

1. Add repository URL into HACS and install "Nintendo Switch Parental Controls"
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Nintendo Switch Parental Controls"
1. HA will automatically navigate to a middleware site (see middleware.html in this repository) which will redirect you to Nintendo to login.
1. After login, you will see a `Linking an External Account` screen, for the account you wish to link, right click on the red button `Select this person` and click `Copy Link`
1. Close the `Nintendo Account` tab
1. Go back to the `Nintendo OAuth Redirection` tab
1. Paste the previously copied value into the `Response URL` text box (only text box on the page)
1. Click `Return back to Home Assistant`
1. The configuration flow should then show some additional options, don't adjust the first box as this is the session token that will be used to refresh the tokens in the background
1. Click `Submit`

<!-- ## Home Assistant Repairs

In version 2023.11.0 support for HA repairs was introduced as a way to inform you of errors relating to your configuration, the repairs will go away themselves once the error is resolved.

Currently two repair types are created, one for OAuth issues, and another for device sync issues.

### Error setting up {name}

If you see this error, you should verify your parental controls configuration in the app, a known tested configuration is as follows:
| Setting | Value |
| ------- | ----- |
| Restriction Level | Teen, Child, Young child |
| Bedtime Alarm | None |
| Play Time Limit | Any value from 15m to 6hr |
| Suspend Software | Enabled or Disabled |
| Set Days Individually | Off | -->

<!-- ### Mobile application has been updated

This happens if Nintendo has updated the mobile app significantly and the OAuth tokens that are hardcoded into pynintendoparental are out of date. If this happens please log an issue. -->

## Middleware notes

The middleware to return the OAuth response back to Home Assistant is a static html file that Home Assistant will register as an HTTP view.

The file contains no callbacks to any 3rd party services, all it does is open a new window in your browser taking you to the Nintendo login site. After _you_ provide the response URL into the text box, the button simply creates a required URL in the background and navigates your web browser back. Home Assistant is then responsible for closing the window.

## Deprecation notice

### Block Device Access

In version 2023.11.0 the "Block Device Access" switch has been deprecated and by default is disabled, functionality has been replaced by the time entity "Play Time Limit". You should update the value of the time entity to 0:00 to achieve the same result.

This has been implemented as the time platform allows for more granular control than what the previous switch allowed.

Full removal is planned for version 2024.1.0

## Configuration is done in the UI

<!---->

Currently only configuration of the update interval is supported.

Enabling debugging will produce a lot of log entiries.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

---

[ha-nintendoparentalcontrols]: https://github.com/pantherale0/ha-nintendoparentalcontrols
[commits-shield]: https://img.shields.io/github/commit-activity/y/pantherale0/ha-nintendoparentalcontrols.svg?style=for-the-badge
[commits]: https://github.com/pantherale0/ha-nintendoparentalcontrols/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/pantherale0/ha-nintendoparentalcontrols.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/pantherale0/ha-nintendoparentalcontrols.svg?style=for-the-badge
[releases]: https://github.com/pantherale0/ha-nintendoparentalcontrols/releases
