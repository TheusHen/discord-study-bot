# Discord Study Bot 📚

A Discord bot designed to help study groups track daily study habits, maintain streaks, and visualize progress through interactive calendars and ranking systems.

## Features 🌟

- **Daily Study Tracking**: Automatically prompts users to confirm their daily study sessions
- **Streak System**: Tracks consecutive study days for each member
- **Visual Calendar**: Generates monthly calendars showing who studied each day with user avatars
- **Ranking System**: Creates bar charts displaying study streaks for all members
- **Automated Reminders**: Sends hourly reminders to members who haven't confirmed their study sessions
- **Slash Commands**: Modern Discord slash command support for easy interaction

## How It Works 🔧

1. **Study Confirmation**: When members post messages in the designated study channel, the bot asks them to confirm if they studied that day
2. **Reaction System**: Users confirm their study sessions by reacting with ✅ to the bot's confirmation message
3. **Data Persistence**: All study data is stored in JSON format locally
4. **Visual Reports**: The bot generates daily reports with study calendars and ranking charts
5. **Reminder System**: Between 8 PM and 11 PM, the bot reminds members who haven't confirmed their daily study

## Setup Instructions 🚀

### Prerequisites

- Python 3.8 or higher
- Discord Developer Application and Bot Token
- Discord Server with appropriate permissions

### Installation

1. **Clone or download this project**
   ```bash
   git clone https://github.com/TheusHen/discord-study-bot.git
   cd discord-study-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   
   Create and edit `.env` and update the following variables:
   ```python
   TOKEN = "YOUR_BOT_TOKEN_HERE"          # Your Discord bot token
   STUDY_CHANNEL_ID = 1234567890          # ID of your study channel
   REMINDER_CHANNEL_ID = 1234567890       # ID of your reminder channel
   GUILD_ID = 1234567890                  # ID of your Discord server

   # Bot Settings
   TIMEZONE=America/Sao_Paulo             # Your timezone
   DATA_FILE=study_data.json              # Defalt .json
   ```

4. **Font Setup**
   
   Ensure the `Roboto-Regular.ttf` font file is in the `fonts/` directory for proper calendar rendering.

5. **Run the bot**
   ```bash
   python bot.py
   ```

## Configuration 📝

### Required Discord Permissions

The bot needs the following permissions:
- Read Messages
- Send Messages
- Add Reactions
- Attach Files
- Use Slash Commands

### Channel Setup

1. **Study Channel**: Where members post about their studies and receive confirmation prompts
2. **Reminder Channel**: Where the bot sends daily reports and reminders

### Time Zone

The bot is configured for `America/Sao_Paulo` timezone. To change it, modify the `TIMEZONE` variable in `bot.py` or `.env`:

```python
TIMEZONE = pytz.timezone("Your/Timezone")
```

## Commands 💬

### Slash Commands
- `/ranking` - Display the current study streak ranking
- `/calendar` - Show the monthly study calendar

### Text Commands
- `!ranking` - Display the current study streak ranking
- `!calendar` - Show the monthly study calendar

## File Structure 📁

```
discord-study-bot/
├── bot.py                    # Main bot file
├── requirements.txt          # Python dependencies
├── discloud.config          # Deployment configuration
├── fonts/
│   └── Roboto-Regular.ttf   # Font for calendar generation
└── utils/
    ├── calendar_img.py      # Calendar image generation
    └── graph.py             # Ranking graph generation
```

## Features in Detail 🔍

### Study Confirmation Flow

1. User posts a message in the study channel
2. Bot checks if user already confirmed study for today
3. If not confirmed, bot sends up to 3 confirmation requests (1 minute apart)
4. User reacts with ✅ to confirm their study session
5. Bot records the confirmation and updates user data

### Streak Calculation

- **Current Streak**: Consecutive days from today backwards
- **Max Streak**: Highest consecutive days in user's history
- Streaks reset if a day is missed

### Visual Elements

#### Study Calendar
- Monthly view with user avatars on study days
- Highlights current day
- Shows up to 5 avatars per day
- Rounded corners and shadow effects for modern appearance

#### Ranking Graph
- Bar chart showing streak lengths
- Sorted by highest streaks first
- Color-coded bars for easy reading

## Deployment 🚀

### Local Deployment
Simply run `python bot.py` after configuration.

### Cloud Deployment
The project includes a `discloud.config` file for deployment on DisCloud or similar platforms.

## Data Storage 💾

Study data is stored in `study_data.json` with the following structure:

```json
{
  "user_id": {
    "confirmations": {
      "2024-01-01": true,
      "2024-01-02": true
    },
    "avatar_url": "https://cdn.discordapp.com/avatars/...",
    "username": "UserName"
  }
}
```

## Customization 🎨

### Visual Styling

Modify colors and appearance in `utils/calendar_img.py`:

```python
BG_COLOR = "#f5f6fa"          # Background color
HEADER_BG = "#00aaff"         # Header background
TODAY_BG = "#ffe082"          # Today's date highlight
AVATAR_BORDER = "#00aaff"     # Avatar border color
```

### Reminder Times

Change reminder hours in `bot.py`:

```python
if 20 <= now.hour <= 23 and now.minute == 0:  # 8 PM to 11 PM
```

## Troubleshooting 🔧

### Common Issues

1. **Bot not responding**: Check token and permissions
2. **Calendar not generating**: Ensure Roboto font is in fonts/ directory
3. **Reminders not working**: Verify channel IDs and timezone settings
4. **Images not loading**: Check internet connection for avatar downloads

### Error Handling

The bot includes comprehensive error handling:
- Failed avatar downloads are skipped gracefully
- Missing fonts fall back to system defaults
- Network errors don't crash the bot

## Contributing 🤝

Feel free to fork this project and submit pull requests for improvements. Some ideas for enhancements:

- Multiple study subjects tracking
- Weekly/monthly statistics
- Integration with external calendar services
- Study goal setting and tracking
- Team challenges and competitions

## License 📄

This project was created for personal use in a Discord study group. Feel free to use and modify it for your own study groups!

---

**Created with ❤️ for productive study groups**
