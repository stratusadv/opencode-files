# Opencode Files
Our collection of Opencode files that can be shared with anyone around the whole world!

## Installation

Install Opencode from your shell with the following command

Terminal User Interface
```shell
winget install opencode
```

Graphical User Interface
```shell
winget install OpenCode
```

## Upgrade 

Make sure all instances of opencode are closed along with IDE's that use opencode

Terminal User Interface
```shell
winget upgrade opencode
```

Graphical User Interface
```shell
winget upgrade OpenCode
```

## Setup Files

Get your `opencode.json` config and place it in your `~\.config\opencode` directory.

Download Files

```shell
git init ~/.config/opencode/ && git -C ~/.config/opencode/ remote add origin https://github.com/stratusadv/opencode-files-public && git -C ~/.config/opencode/ fetch && git -C ~/.config/opencode/ reset --hard origin/main
```

## Update Files

Get the latest files from the repo

```shell
git -C ~/.config/opencode/ pull origin main
```

To update or change the files we suggest using your IDE or GIT Tooling.