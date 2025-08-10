from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random, json, os, threading, time
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
PORT = int(os.environ.get('PORT', 5000))

# Mini serveur Flask pour que Render « voie » le service
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Multiplier Rush bot is running 🎮", 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=PORT)

threading.Thread(target=run_flask, daemon=True).start()

# ------------------------------------------------------------------
# ———  Même logique de jeu que précédemment  ———
# ------------------------------------------------------------------
class MultiplierGame:
    def __init__(self):
        self.scores = {}
        self.multipliers = {}
    def load_scores(self):
        if os.path.exists('scores.json'):
            with open('scores.json', 'r') as f:
                self.scores = json.load(f)
    def save_scores(self):
        with open('scores.json', 'w') as f:
            json.dump(self.scores, f)

game = MultiplierGame()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🎯 JOUER", callback_data="play")],
        [InlineKeyboardButton("📊 SCORE", callback_data="score")],
        [InlineKeyboardButton("🏆 LEADERBOARD", callback_data="leaderboard")]
    ]
    await update.message.reply_text(
        f"🎮 *MULTIPLIER RUSH*\n\n"
        f"Bonjour {user.first_name}!\n\n"
        f"🎯 Objectif: Obtenir le score le plus élevé\n"
        f"💰 Points: 1-10 par clic\n"
        f"✨ Multiplicateurs: x2 (20%) ou x3 (10%)\n"
        f"🔥 Combo: +5 points toutes les 10 clics!\n\n"
        f"_Clique sur JOUER pour commencer!_",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_id = str(user.id)
    await query.answer()
    game.load_scores()

    if query.data == "play":
        base_points = random.randint(1, 10)
        multiplier, multiplier_text = 1, ""
        rand = random.random()
        if rand < 0.1:
            multiplier, multiplier_text = 3, "🎊 x3 MULTIPLIER! "
        elif rand < 0.3:
            multiplier, multiplier_text = 2, "🎉 x2 MULTIPLIER! "
        total_points = base_points * multiplier

        game.multipliers.setdefault(user_id, 0)
        game.multipliers[user_id] += 1
        combo_points = 5 if game.multipliers[user_id] % 10 == 0 else 0
        if combo_points:
            multiplier_text += f"\n🔥 COMBO +{combo_points}!"
        final_points = total_points + combo_points

        game.scores.setdefault(user_id, {"name": user.first_name, "score": 0})
        game.scores[user_id]["score"] += final_points
        game.save_scores()

        keyboard = [[
            InlineKeyboardButton("🎯 CLIQUER!", callback_data="play"),
            InlineKeyboardButton("📊 SCORE", callback_data="score")
        ]]
        await query.edit_message_text(
            f"{multiplier_text}\n💰 +{final_points} points!\n"
            f"📊 Total: {game.scores[user_id]['score']} points\n"
            f"🔥 Combo: {game.multipliers[user_id]} clics",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "score":
        score = game.scores.get(user_id, {}).get("score", 0)
        await query.answer(f"Ton score: {score} points", show_alert=True)

    elif query.data == "leaderboard":
        game.load_scores()
        sorted_scores = sorted(game.scores.items(), key=lambda x: x[1]["score"], reverse=True)[:10]
        leaderboard = "🏆 TOP 10:\n\n" + "\n".join(
            f"{i}. {data['name']}: {data['score']} pts"
            for i, (_, data) in enumerate(sorted_scores, 1)
        )
        keyboard = [[InlineKeyboardButton("🎯 JOUER", callback_data="play")]]
        await query.edit_message_text(leaderboard, reply_markup=InlineKeyboardMarkup(keyboard))

# Lancement du bot
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

if __name__ == "__main__":
    print("Bot démarré!")
    app.run_polling()
