# r/PhotoshopRequests Timed Flair Updater
Script to update post flairs on [r/PhotoshopRequests](https://www.reddit.com/r/PhotoshopRequests/), on a timed basis.

## Installation
- Install Python.
  - On a PC:
    - You can download it here https://www.python.org/downloads/ (Add to PATH during the installation).
  - Using Termux on a mobile device:
    - Run this command: ```pkg install python```
- Download this repo:
  - On a PC:
    - Click on 'Code' -> 'Download ZIP'.
  - On a mobile device:
    - Enable 'Desktop Mode' and follow the same instructions for the PC section.
- Unzip/Extract the ZIP file.
- Open your terminal (Command Prompt on Windows, Shell on Linux, Termux on mobile devices) and change your directory to that of the unzipped files. If using Termux, ensure to run ```termux-setup-storage``` to allow access to your device's storage.  
- Install the required packages:
  ```
  pip install -U praw
  ```
  
## Configuration
- Create a Reddit App (script) at https://www.reddit.com/prefs/apps/ and get your client_id and client_secret.  
- Edit the config.ini file with your details and save:
  ```
  [REDDIT]
  CLIENT_ID = your_client_id
  CLIENT_SECRET = your_client_secret
  PASSWORD = your_reddit_password
  USERNAME = your_reddit_username

  [VARS]
  SUBREDDIT = target_subreddit_name
  ```

## Running the script    
```
python main.py
```
