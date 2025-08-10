from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
import json
import os

TOKEN = os.environ.get('BOT_TOKEN')

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
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎮 *MULTIPLIER RUSH*\n\n"
        f"Bonjour {user.first_name}!\n\n"
        f"🎯 Objectif: Obtenir le score le plus élevé\n"
        f"💰 Points: 1-10 par clic\n"
        f"✨ Multiplicateurs: x2 (20%) ou x3 (10%)\n"
        f"🔥 Combo: +5 points toutes les 10 clics!\n\n"
        f"_Clique sur JOUER pour commencer!_",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_id = str(user.id)
    
    await query.answer()
    
    game.load_scores()
    
    if query.data == "play":
        base_points = random.randint(1, 10)
        
        multiplier = 1
        multiplier_text = ""
        
        rand = random.random()
        if rand < 0.1:
            multiplier = 3
            multiplier_text = "🎊 x3 MULTIPLIER! "
        elif rand < 0.3:
            multiplier = 2
            multiplier_text = "🎉 x2 MULTIPLIER! "
        
        total_points = base_points * multiplier
        
        if user_id not in game.multipliers:
            game.multipliers[user_id] = 0
        game.multipliers[user_id] += 1
        
        combo_points = 0
        if game.multipliers[user_id] % 10 == 0:
            combo_points = 5
            multiplier_text += f"\n🔥 COMBO +{combo_points}!"
        
        final_points = total_points + combo_points
        
        if user_id not in game.scores:
            game.scores[user_id] = {"name": user.first_name, "score": 0}
        game.scores[user_id]["score"] += final_points
        
        game.save_scores()
        
        keyboard = [[
            InlineKeyboardButton("🎯 CLIQUER!", callback_data="play"),
            InlineKeyboardButton("📊 SCORE", callback_data="score")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"{multiplier_text}\n"
            f"💰 +{final_points} points!\n"
            f"📊 Total: {game.scores[user_id]['score']} points\n"
            f"🔥 Combo: {game.multipliers[user_id]} clics"
        )
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data
