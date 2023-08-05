# Gists.cli


> I'm a Developer who uses VI and the like. iPad and iPhone apps are great, but when I really need a Gist i'm at the command line. 

An easy to use CLI to manage *your* GitHub Gists. Create, edit, append, view, search and download. 

- Github - https://github.com/khilnani/gists.cli 
- Python Package - https://pypi.python.org/pypi/gists.cli

# For the Casual User

## Installation

- Install the Python package manager PIP (http://www.pip-installer.org/)
  - Run `sudo easy_install pip`
- Once PIP is installed, 
  - Run `sudo pip install gists.cli`
  - Run `sudo pip install gists.cli --upgrade` if upgrading.

## Authentication


- By default the application will attempt to use Basic Auth to authenticate i.e. will prompt for username/password each time it is run.
- If the file `~/.git-credentials` is available, it will use the first OAuth token entry. 
- If the file  `~/.gists` with a Github OAuth token is found, it will be given preference over the above two mechanisms.
- Run `./gists token|t` to avoid the username/password prompt and to use an OAuth Token other than `~/.git-credentials`. Saves to `~/.gists`.

## Usage


*All the commands below are interactive and will prompt for user input (eg. public/private, descriptions) and confirmations (eg. directory creation).*

**List all your Gists**

- `./gists`

**View a Gist**

- `./gists ID` - View Gist with ID on the console.
- `./gists ID PATH` - Download Gist files with ID to PATH. Will prompt for confirmation.


**Create a Gist**

We'll prompt for stuff like Gist type (public/private), Description and Gist Content as needed.

- `./gists new` or `./gists create`
- `./gists FILE` - Create a Gist using the contents of FILE
- `./gists "Content"` - Create a Gist using the string "Content"

To avoid the Public/private Gist type prompt -

> Bool should be `true` for Public, `false` for Private

- `./gists Bool FILE`
- `./gists Bool "Content"`



# For The Advanced User


## Usage


*All the commands below are interactive and will prompt for user input.*
*To suppress interactivity, simple include the word 'suppress', 'silent' or 's'. See the 'Tips' section for more info.*

**List all your Gists**

- `./gists` - list your Gists.

**View a Gist**

- `./gists ID` - view Gist with ID on the console.
- `./gists ID PATH` - download Gist files with ID to PATH. Will prompt for confirmation.

**Setup OAuth token**

- `./gists token|t` - setup to use OAuth Token other than `~/.git-credentials`. Saves to `~/.gists`.

**Create a Gist**

> - FILE - is a file path, relative or absolute.
> - Bool - True for Public, False for Private. Supports True, False, 1, 0, Yes, No, y, n. Case-insensitive
> - Description and Content - Text content within quotes


Without specifying a command (eg. create, new), the application will trying to figure it out. However, this supports fewer combinations of arguments.

- `./gists FILE`
- `./gists "Content"`
- `./gists Bool FILE`
- `./gists Bool "Content"`
- `./gists "Description" FILE`
- `./gists "Description" "Content"`
- `./gists Bool "Description" FILE`
- `./gists Bool "Description" "Content"`


If you like to type, or be specific (will prompt for stuff like Gist type, Description and Gist Content etc as needed).

- `./gists new|n|create|c`
- `./gists new|n|create|c FILE`
- `./gists new|n|create|c "Content"`
- `./gists new|n|create|c Bool FILE`
- `./gists new|n|create|c Bool "Content"`
- `./gists new|n|create|c "Description" FILE`
- `./gists new|n|create|c "Description" "Content"`
- `./gists new|n|create|c Bool "Description" FILE`
- `./gists new|n|create|c Bool "Description" "Content"`


# For the Developer

## Installation

If you would like to contribute changes to the code base

- Get the code
  - Fork and `git clone` the fork, or ...
  - `git clone https://github.com/khilnani/gists.cli.git`, or ...
  - Download the latest Tag Archive from https://github.com/khilnani/gists.cli  
    - *Downloading the Archive is not recommended, since it won't be easy to merge code back*.
- Install dependencies by running `./setup.sh`. 
  - This installs PIP (if not already installed) and then installs the dependencies.
- Run the installer as below. If you get any error run with `sudo ...`
  - `./install.py` with no arguments will install to `/usr/local/bin`.
  - `./install.py INSTALL_PATH` will install to a specific directory.
  
## Tips

- Add `debug|d` at the end of any execution to view low level details. eg. `./gists debug`. *NOTE - This will reveal your OAuth ID but not your Basic Auth password.*
- Add `supress|silent|s` at the end of any execution to supress any prompts of confirmations if you like to live dangerously. 
  - eg. `./gists create FILE supress debug`. 

# In Development

- `./gists update|u ID [PARAMS]` - Update a Gist. Content sent via Console, Clipboard or File.
- `./gists delete|del|d ID` - Delete a Gist.
- `./gists append|a ID [PARAMS]` - Append to a Gist. Content sent via Console, Clipboard or File.
- `./gists backup|b [DIR]` - Backup all Gists in the user's account.
- `./gists search|query|q QUERY` - Search Gists.
- `./gists star` - List starred Gists

# Issues and Roadmap

- Take a look at https://github.com/khilnani/gists.cli/issues to view Issues and Milestones.


