# Commands
A list of all the commands in Beacon as of the latest version. A format section is included **only** for commands that include Parameters.

In command formats:
- Angle brackets <> denote a **required** parameter.
- Square brackets [] denote an **optional** parameter.

## Utility
These are miscellaneous commands to help with using the bot.
### `/about`
#### Usage
Shows basic information about the bot, including the version.

### `/cmds`
#### Usage
Lists all commands in the bot without any description.

## Server
These commands are all to do with getting the status of a Minecraft server.
### `/getserverinfo`
#### Format
```
/getserverinfo <host>
```
#### Parameters
- Host: The server domain or IP address. Shows a list of hosts as defined in the server hosts list.
#### Usage
A one-off message to find the status of a Minecraft server. 

### `/watchserver`
#### Format
```
/watchserver <host> [interval]
```
#### Parameters
- Host: The server domain or IP address. Shows a list of hosts as defined in the server hosts list.
- Interval: How often the message should update in minutes. Default of 5 if not set otherwise. Value cannot be less than 2.
#### Usage
Sends a message in the channel it is run in that displays server status (similar to `/getserverinfo`) and updates every few minutes, depending on the time in minutes set in `[interval]`.

### `/unwatch`
#### Format
```
/unwatch <message_id>
```
#### Parameters
- Message ID -  The message ID of the watch message you wish to unwatch. This can be obtained by enabling [Discord developer mode](https://docs.discord.com/developers/activities/building-an-activity#step-0-enable-developer-mode), right clicking on the message and copying the message ID.
#### Usage
Stops a message sent by `/watchserver` updating. 

## Hosts
These are commands to modify the server's host list. Each Discord server has a list of hosts, meaning when server commands are run, the list is shown as a suggestion of what host to use.
### `/addhost`
#### Format
```
/addhost <shorthand> <host>
```
#### Parameters
- Shorthand - The name the server should be referred to as.
- Host - The server domain or IP address.
#### Usage
Adds a host to the server's hosts list.

### `/removehost`
#### Format
```
/removehost <shorthand>
```
#### Parameters
- Shorthand - The name of the server that should be removed as defined in the hosts list. The list appears on this command when you are selecting a host to be removed.
#### Usage
Removes a host from the server's hosts list.

### `/listhosts`
#### Usage
Displays all hosts on the server's hosts list.

## Issues
This section will soon be merged with Utility.

### `/issue`
#### Usage
If an end user wants to report an issue with the bot, they can do so by running the `/issue` command, and filling the form in the modal that appears. In this modal, they must fill in:

- Title - The issue title
- Description - Details of the issue, for example, what happened, what they were doing when it happened, how to reproduce the issue, etc.

Once the form has been submitted, it automatically creates an issue on the GitHub repository, and gives the user a link to do this. The issue is created by the [Beacon Issues Bot](https://github.com/beaconissuesbot), a GitHub account with the sole purpose of creating issues from this command.
#### Rate Limits
In order to combat spam that may arise from this command, users are limited to two issues per 30 minutes from the command. If they have more than 2 issues, they are welcome to make them directly on the GitHub repository.