# Flemmarr

<img width="30%" src="logo.svg" alt="Flemmarr"></img>

> **flemmard (*noun or adj.*):** lazy, slacker, idler in French 🇫🇷
(cf. [Wiktionary](https://en.wiktionary.org/wiki/flemmard))

**Flemmarr** is a simple Python script that parses a configuration written in YAML and can apply it to any of the **-arr apps (Sonarr, Radarr, Lidarr, Readarr, Prowlarr)** using their API.

## Installation

The easiest way to use it is to run it using **Docker** alongside your other -arr applications.

```docker
docker run pierremesure/flemmarr:latest -v ./config/flemmarr:config
```

You can also just add it to your **docker-compose.yml**

```yaml
version: "3"
services:
  flemmarr:
    container_name: flemmarr
    image: pierremesure/flemmarr
    volumes:
      - "./config/flemmarr:/config"
```

Check out the example [docker-compose.yml](docker-compose.yml) with flemmarr alongside all other -arr apps.

## Configuration

To configure your apps, simply put a file called **config.yml** in the **config** folder.

For each app, you need to provide the address and the port under the **server** key.

Regarding the actual configuration, both keys and values need to be the ones used by the apps to communicate with their user interface through the API.

For instance, in order to change the app's language to French, a call would be made to `/config/ui` with a payload containing `uiLanguage: 2`. To add a new root folder, the call would go to `/rootfolder` and send the folder's name, path and some more metadata.

These two examples are displayed below:

```yaml
lidarr:
  server:
    address: localhost
    port: 8686
  config:
    ui:
      uiLanguage: 2 # 1 = English, 2 = French, 3 = Spanish...
  rootfolder:
    - name: Music
      path: !ENV ${ROOTFOLDER_PATH}
      defaultTags: []
      defaultQualityProfileId: 1
      defaultMetadataProfileId: 1
```

Check out the example [config.yml](config/flemmarr/config.yml) with more settings for various apps, or [example_backup.yml](config/flemmarr/example_backup.yml) for all supported settings. Use environment variables where needed by using the `!ENV ${ENV_VAR}` syntax. They can be added in an untracked `.env` file.

**NB:** Unfortunately, I found the APIs for all -arr tools to be of poor quality. Oftentimes, some fields are needed for no reason, default values are not the same as the ones applied by the GUI.

If you cannot find how to change a specific part of the configuration in this file, you will have to find out by yourself how it should look like. You can for instance:

- browse the API docs of the app ([Sonarr](https://github.com/Sonarr/Sonarr/wiki/API), [Radarr](https://radarr.video/docs/api/), [Lidarr](https://lidarr.audio/docs/api/), [Readarr](https://readarr.com/docs/api/), [Prowlarr](http://prowlarr.com/docs/api/))
- use your browser inspector to identify which call is sent by the GUI
- use a REST client such as [Insomnia](https://insomnia.rest) to tinker your payload and see exactly which values work and don't
- ask for help here by creating an issue.

Once you've found the solution, please add it to the example config file so others can benefit from your knowledge.

## Backup
A backup of the current configuration will be created automatically and stored in `/config/config_backup.yml`. If you only want
to create a backup and do not apply a config, simply do not provide a `/config/config.yml` file.


## Contributing

I created Flemmarr because I was shocked when I couldn't find a way to write configuration as code for any of the -arr applications. I hope it is useful to more.

I do not actually use any of the -arr apps in my daily life, I was just helping a friend to install them. So I don't plan on spending too much time on maintaining or improving the project. Feel free to submit your issues and your suggestions though! And feel free to have a look at the (very simple) code and documentation and try to make them better.

### Some ideas I have

- [ ] document more of the configuration's possible values, required fields
- [ ] make the service idempotent (not easy considering how the APIs are designed)
- [ ] make it possible to declare a common config for several apps to avoid redundancy in the file (maybe with group configs)
- [ ] add automated testing
- [ ] repackage the Python script as an Ansible package (if there is demand)

## Credits

Cute cartoon vector created by [catalyststuff](https://www.freepik.com/free-vector/cute-sloth-yoga-cartoon-icon-illustration_11167789.htm) - [freepik.com](https://www.freepik.com)
