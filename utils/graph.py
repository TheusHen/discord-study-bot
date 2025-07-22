import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz

def get_streak(confirmations):
    streak = 0
    max_streak = 0
    tz = pytz.timezone("America/Sao_Paulo")
    today = datetime.now(tz).date()
    d = today
    while True:
        if confirmations.get(d.strftime("%Y-%m-%d")):
            streak += 1
            d -= timedelta(days=1)
        else:
            break
    streak = 0
    max_streak = 0
    for date_str in sorted(confirmations.keys()):
        if confirmations[date_str]:
            if streak == 0:
                streak = 1
            else:
                last_date = datetime.strptime(date_str, "%Y-%m-%d").date() - timedelta(days=1)
                if confirmations.get(last_date.strftime("%Y-%m-%d")):
                    streak += 1
                else:
                    streak = 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak

def create_streak_graph(study_data):
    streaks = []
    names = []
    for user_id, data in study_data.items():
        streak = get_streak(data["confirmations"])
        streaks.append(streak)
        names.append(data.get("username", user_id))
    streaks, names = zip(*sorted(zip(streaks, names), reverse=True))

    plt.figure(figsize=(8,6))
    plt.bar(names, streaks, color="#4CAF50")
    plt.title("Consecutive Study Days (Streak)")
    plt.xlabel("User")
    plt.ylabel("Consecutive Days")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    path = "streak_graph.png"
    plt.savefig(path)
    plt.close()
    return path