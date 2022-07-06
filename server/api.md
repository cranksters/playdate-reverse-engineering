This is the API that is used by the Playdate console for things like fetching game updates, scoreboards, player details, etc. It is available under `https://play.date/api/v2`. All API endpoints require [auth headers](#auth-headers).

This list of endpoints was obtained by decompiling the Playdate Simulator app. Some haven't actually been seen in use, so they are only partially documented and there may be mistakes.

## Endpoints

| Method | Path |
|:-|:-|
| `POST` | [`/auth_echo/`](#post-auth_echo) |
| `GET`  | [`/player/`](#get-player) |
| `GET`  | [`/player/:playerId/`](#get-playerplayerid) |
| `POST` | `/player/avatar/` |
| `GET`  | [`/games/scheduled/`](#get-gamesscheduled) |
| `GET`  | [`/games/user/`](#get-gamesuser) |
| `GET`  | `/games/testing/` |
| `GET`  | `/games/purchased/` |
| `GET`  | `/games/system/` |
| `GET`  | `/games/:bundleId/latest_build/` |
| `GET`  | `/games/:bundleId/boards/` |
| `GET`  | `/games/:bundleId/boards/:boardId/` |
| `POST` | `/games/:bundleId/boards/:boardId/` |
| `GET`  | `/device/settings/` |

### POST /auth_echo

Seems to just return whatever JSON body is sent to it.

### GET /player

Returns the player profile for the user that owns the current access token.

### GET /player/:playerId

Same as `/player`, but gets the player profile for another user, given their [Player ID](#player-id).

### GET /games/scheduled/

Returns an array of [Schedule](#Schedule) entries for any seasons that you have access to.

### GET /games/user/

Returns an array of [Game](#Game) entries for games that you have [sideloaded](https://help.play.date/games/sideloading/).

### GET /device/register/:serialNumber/

If the device hasn't already been registered, returns a JSON containing its serial number and pin.

This endpoint requires an extra header:

| Header | Value |
|:-|:-|
| `Idempotency-Key` | Random 16-character string. Allowed chars are `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`. |

### GET /device/register/:serialNumber/complete

Returns a JSON with the device's registered status, access token, and serial number. Access token will only be available on the first request to this endpoint after registering the device.

## Schemas

### Schedule

| Key | Type | Detail |
|:----|:------|:------|
| `name` | string | Schedule name (Season One is `Season-001`) |
| `start_date` | string | Schedule start datetime, formatted as `E MMM d HH:mm:ss yyyy zzz` (e.g. `Mon Apr 18 00:00:00 2022 PDT`) |
| `start_date_timestamp` | number | Schedule start as a UNIX timestamp |
| `next_release_timestamp` | number | Time of next scheduled release as a UNIX timestamp |
| `ended` | boolean | |
| `games` | array | Array of released [Game](#Game) entries |

### Game 

| Key | Type | Detail |
|:----|:------|:------|
| `name` | string | Game name, will be displayed to the user |
| `bundle_id` | string | Reverse-domain formatted bundle ID (e.g `com.jaames.playnote`) |
| `short_description` | string | Few games currently have this (only seen on Flipper Lifter and Boogie Loops so far), often `null` |
| `studio` | string | Game's publisher/developer |
| `has_newer_build` | boolean | |
| `latest_build` | [Build](#Build) | |

### Build

| Key | Type | Detail |
|:----|:------|:------|
| `url` | string | Web URL for the build's .zip file |
| `is_beta` | boolean | |
| `version` | string | Human-friendly version string, taken from the game's pdxinfo file |
| `build_number` | number | Incremental build number from the game's pdxinfo |
| `filesize` | number | .zip file size, in bytes |
| `upzipped_filesize` | number | size of the .zip contents after decompression, in bytes |

## Auth Headers

All routes require a basic authorization token sent via a HTTP header. If you have a developer account on [play.date](//play.date), you can generate an access token by going to `https://play.date/players/account/` and clicking 'register simulator'. It looks as though you're allowed to register up to 5 simulators at one time.

| Header | Value |
|:-|:-|
| `Authorization` | `Token ` followed by your authorization token |

## Player ID

Player IDs seem to use the `DCE 1.1, ISO/IEC 11578:1996` variant of UUID v4, with dashes separating each section, e.g `XXXXXXXX-XXXX-4XXX-8XXX-XXXXXXXXXXXX`.
