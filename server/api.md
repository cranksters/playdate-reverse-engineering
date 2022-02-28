This is the API that is used by the Playdate console for things like fetching game updates, scoreboards, player details, etc. It is available under `https://play.date/api/v2`. All API endpoints require [auth headers](#auth-headers).

This list of endpoints was obtained by decompiling the Playdate Simulator app. Some haven't actually been seen in use, so they are only partially documented and there may be mistakes.

## Endpoints

| Method | Path |
|:-|:-|
| `POST` | [`/auth_echo/`](#post-auth_echo) |
| `GET`  | [`/player/`](#get-player) |
| `GET`  | [`/player/:playerId/`](#get-playerplayerid) |
| `POST` | `/player/avatar/` |
| `GET`  | `/games/scheduled/` |
| `GET`  | `/games/testing/` |
| `GET`  | `/games/user/` |
| `GET`  | `/games/purchased/` |
| `GET`  | `/games/system/` |
| `GET`  | `/games/:bundleId/latest_build/` |
| `GET`  | `/games/:bundleId/boards/` |
| `GET`  | `/games/:bundleId/boards/:unknown/` |
| `POST` | `/games/:bundleId/boards/:unknown/` |
| `GET`  | `/device/settings/` |
| `POST` | [`/device/register/:serialNumber/`]((#get-deviceregisterserialnumber)) |
| `GET`  | [`/device/register/:serialNumber/complete`](#get-deviceregisterserialnumbercomplete) |
| `GET`  | [`/firmware/`](#get-firmware) |

### POST /auth_echo

Seems to just return whatever JSON body is sent to it.

### GET /player

Returns the player profile for the user that owns the current access token.

### GET /player/:playerId

Same as `/player`, but gets the player profile for another user, given their [Player ID](#player-id).

### GET /device/register/:serialNumber/

If the device hasn't already been registered, returns a JSON containing its serial number and pin.

This endpoint requires an extra header:

| Header | Value |
|:-|:-|
| `Idempotency-Key` | Random 16-character string. Allowed chars are `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`. |

### GET /device/register/:serialNumber/complete

Returns a JSON with the device's registered status, access token, and serial number. Access token will only be available on the first request to this endpoint after registering the device.

### GET /firmware

Returns information about the latest available firmware version, including a URL to download it. For whatever reason, the latest available firmware for the Simulator is `0.10.2`, so I might not have everything correct here.

## Auth Headers

All routes require a basic authorization token sent via a HTTP header. If you have a developer account on [play.date](//play.date), you can generate an access token by going to `https://play.date/players/account/` and clicking 'register simulator'. It looks as though you're allowed to register up to 5 simulators at one time.

| Header | Value |
|:-|:-|
| `Authorization` | `Token ` followed by your authorization token |

## Player ID

Player IDs seem to use the `DCE 1.1, ISO/IEC 11578:1996` variant of UUID v4, with dashes separating each section, e.g `XXXXXXXX-XXXX-4XXX-8XXX-XXXXXXXXXXXX`.