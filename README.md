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
| `switch` | Device controls.                               |

## Supported features

- Sensor for used screen time
- Screen time sensor displays last 5 days of usage, including applications used and players.
- Switch to enable/disable the "Suspend Software" mode once the screentime limit has been reached.
- Switch to "lock"/"unlock" the device (providing "Suspend Software Limit" is turned on)
- Switch to enable and disable alarms for the current day, Nintendo resets this back at midnight.
- Raises issues if an error occures with the OAuth configuration (such as Nintendo changing the client IDs)
- Allows for reauthentication if the session token expires (usually around 2 years).

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `nintendo_parental`.
1. Download _all_ the files from the `custom_components/nintendo_parental/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
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

## Middleware notes

The middleware to return the OAuth response back to Home Assistant is a static html file that Home Assistant will register as an HTTP view.

The file contains no callbacks to any 3rd party services, all it does is open a new window in your browser taking you to the Nintendo login site. After _you_ provide the response URL into the text box, the button simply creates a required URL in the background and navigates your web browser back. Home Assistant is then responsible for closing the window.

## Configuration is done in the UI

<!---->

Currently only configuration of the update interval is supported.

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
