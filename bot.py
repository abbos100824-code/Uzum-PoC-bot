import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import google.generativeai as genai

# --- Tokenlar va Sozlamalar ---
TOKEN = os.getenv("BOT_TOKEN", "BU_YERGA_TOKEN_QOYING")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    ai_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    ai_model = None

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- FSM Holatlari ---
class SellerFlow(StatesGroup):
    waiting_for_product = State()

class BuyerFlow(StatesGroup):
    waiting_for_query = State()


# --- Tugmalar (Interfeys) ---

def main_role_cards() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🏦 1. Bank Assistent (Escrow & To'lov)", callback_data="role_bank")],
        [InlineKeyboardButton(text="🏪 2. Sotuvchi Assistent (AI Kartochka)", callback_data="role_seller")],
        [InlineKeyboardButton(text="🛍 3. Xaridor Assistent (Uzum Qidiruv)", callback_data="role_buyer")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_to_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Asosiy menyuga qaytish", callback_data="back_to_main")]]
    )

def bank_menu_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🔒 Escrow depozit holati", callback_data="bank_escrow_check")],
        [InlineKeyboardButton(text="⚡️ Kliring & To'lov shlyuzi", callback_data="bank_gateway_status")],
        [InlineKeyboardButton(text="🔙 Asosiy menyuga qaytish", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def seller_menu_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="📝 AI bilan yangi kartochka tuzish", callback_data="seller_create_card")],
        [InlineKeyboardButton(text="🏷 Teglar va SEO tahlili", callback_data="seller_seo_tips")],
        [InlineKeyboardButton(text="🔙 Asosiy menyuga qaytish", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def buyer_menu_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🔍 Mahsulot qidirish (Uzum Market)", callback_data="buyer_search_start")],
        [InlineKeyboardButton(text="🔥 Ommabop toifalar", callback_data="buyer_popular_categories")],
        [InlineKeyboardButton(text="🔙 Asosiy menyuga qaytish", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# --- Buyruqlar menyusi ---

async def setup_commands(bot_instance: Bot):
    commands = [
        BotCommand(command="start", description="Asosiy menyu va rollar"),
        BotCommand(command="bank", description="Bank & Escrow assistenti"),
        BotCommand(command="sotuvchi", description="Sotuvchi kabineti va kartochkalar"),
        BotCommand(command="xaridor", description="Uzum Market qidiruv assistenti"),
    ]
    await bot_instance.set_my_commands(commands)


# --- Asosiy Menyu ---

async def show_main_menu(target: types.Message | types.CallbackQuery, is_callback: bool = False):
    caption = (
        "👋 **Uzum PoC Ko'p Modulli AI Tizimiga xush kelibsiz!**\n\n"
        "O'zingizga kerakli bo'lim kartochkasini tanlang:\n\n"
        "💳 **Bank Assistent:** To'lovlar xavfsizligi va Escrow deponentlash nazorati.\n"
        "📦 **Sotuvchi Assistent:** Gemini AI yordamida tovar kartochkasini professional formatlash.\n"
        "🔍 **Xaridor Assistent:** Uzum Market katalogidan tovar qidirish tizimi."
    )
    if is_callback:
        await target.message.edit_text(caption, reply_markup=main_role_cards(), parse_mode="Markdown")
        await target.answer()
    else:
        await target.answer(caption, reply_markup=main_role_cards(), parse_mode="Markdown")


# --- START va Navigatsiya ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await show_main_menu(message)

@dp.callback_query(F.data == "back_to_main")
async def cb_back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await show_main_menu(callback, is_callback=True)


# --- 1-KARTA: BANK ASSISTENT ---

@dp.message(Command("bank"))
@dp.callback_query(F.data == "role_bank")
async def show_bank_card(event: types.Message | types.CallbackQuery):
    card_text = (
        "🏦 **BANK & ESCROW ASSISTENTI KARTASI**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "• **Funksiya:** Tranzaksiyalar xavfsizligi va mablag' kliringi\n"
        "• **Escrow moduli:** Xaridor to'lagan pul buyurtma qabul qilingunicha bankda muzlatiladi\n"
        "• **Tranzaksiya komissiyasi:** 0% (PoC shartnoma doirasida)\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Kerakli amaliyotni tanlang:"
    )
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(card_text, reply_markup=bank_menu_kb(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(card_text, reply_markup=bank_menu_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "bank_escrow_check")
async def cb_bank_escrow(callback: types.CallbackQuery):
    text = (
        "🔒 **Deponentlangan mablag'lar (Escrow Audit):**\n\n"
        "• Bloklangan summa: `240,000 UZS`\n"
        "• Faol tranzaksiyalar soni: `1 ta` (Buyurtma #UZ-4819)\n"
        "• Holati: *Yetkazib berish jarayonida (Muzlatilgan)*\n\n"
        "Xaridor tovar holatini tasdiqlagach, summa sotuvchining hisobiga o'tkaziladi."
    )
    await callback.message.edit_text(text, reply_markup=bank_menu_kb(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "bank_gateway_status")
async def cb_bank_gateway(callback: types.CallbackQuery):
    text = (
        "⚡️ **To'lov Shlyuzi Holati (Payment Gateway):**\n\n"
        "• Uzum Pay API: **ONLINE** (Kechikish: 42ms)\n"
        "• Humo / Uzcard protokoli: **FAOL**\n"
        "• Xavfsizlik darajasi: 3D-Secure 2.0 faollashtirilgan."
    )
    await callback.message.edit_text(text, reply_markup=bank_menu_kb(), parse_mode="Markdown")
    await callback.answer()


# --- 2-KARTA: SOTUVCHI ASSISTENT (GEMINI AI INTEGRATSIYASI) ---

@dp.message(Command("sotuvchi"))
@dp.callback_query(F.data == "role_seller")
async def show_seller_card(event: types.Message | types.CallbackQuery):
    card_text = (
        "🏪 **SOTUVCHI (MERCHANT) ASSISTENTI KARTASI**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "• **Vazifa:** Gemini AI yordamida Uzum Market uchun professional kartochka tayyorlash\n"
        "• **Imkoniyat:** Xususiyatlarni tartiblash, jozibador sarlavha va SEO kalit so'zlar\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Kerakli bo'limni tanlang:"
    )
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(card_text, reply_markup=seller_menu_kb(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(card_text, reply_markup=seller_menu_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "seller_create_card")
async def cb_seller_create(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(SellerFlow.waiting_for_product)
    text = (
        "📝 **Mahsulot ma'lumotlarini kiriting:**\n\n"
        "Tovar nomi, taxminiy narxi va asosiy xususiyatini erkin shaklda yozing.\n"
        "*(Masalan: 'Simsiz naushnik M10, 85000 so'm, shovqinni bosuvchi, qora rang')*"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="Markdown")
    await callback.answer()

@dp.message(SellerFlow.waiting_for_product)
async def process_seller_product(message: types.Message, state: FSMContext):
    user_input = message.text
    await state.clear()

    wait_msg = await message.answer("🤖 Gemini AI kartochkani shakllantirmoqda...")

    if ai_model:
        prompt = (
            f"Foydalanuvchi Uzum Market sotuvchisi. U quyidagi tovar ma'lumotini kiritdi:\n'{user_input}'\n\n"
            "Ushbu tovar uchun Uzum Market standarti bo'yicha tayyor kartochka yaratib ber:\n"
            "1. Jozibador rasmiy sarlavha\n"
            "2. Asosiy 3-4 ta afzalligi (bullet point bilan)\n"
            "3. Qisqa va sotuvchan tavsif\n"
            "4. 5 ta SEO qidiruv teglari (#bilan)\n"
            "Javobni aniq o'zbek tilida va Telegram Markdown formatiga moslab qaytar."
        )
        try:
            response = ai_model.generate_content(prompt)
            result_text = response.text
        except Exception as e:
            result_text = f"Xatolik yuz berdi: {str(e)}"
    else:
        result_text = "⚠️ Gemini API kaliti ulanmagan. Render muhit sozlamalarini (Environment) tekshiring."

    await wait_msg.delete()
    await message.answer(result_text, reply_markup=seller_menu_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "seller_seo_tips")
async def cb_seller_seo(callback: types.CallbackQuery):
    text = (
        "📈 **Uzum Marketda Tovarni TOPga chiqarish qoidalari:**\n\n"
        "1. **Sarlavha formulasi:** Tovar turi + Brend + Model + Asosiy xususiyat.\n"
        "2. **Infografika:** Birinchi rasmda aniq mahsulot va asosiy 3 ta ustunlik bo'lishi lozim.\n"
        "3. **Tezkor qoldiq:** Ombordagi qoldiq soni 0 ga tushib qolmasligini nazorat qiling."
    )
    await callback.message.edit_text(text, reply_markup=seller_menu_kb(), parse_mode="Markdown")
    await callback.answer()


# --- 3-KARTA: XARIDOR ASSISTENT ---

@dp.message(Command("xaridor"))
@dp.callback_query(F.data == "role_buyer")
async def show_buyer_card(event: types.Message | types.CallbackQuery):
    card_text = (
        "🛍 **XARIDOR ASSISTENTI KARTASI**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "• **Vazifa:** Uzum Market bo'yicha tovar qidirish va narxlarni solishtirish\n"
        "• **Afzalligi:** Qidiruv so'rovi bo'yicha mahsulot havolasini taqdim etish\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Bo'limni tanlang:"
    )
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(card_text, reply_markup=buyer_menu_kb(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(card_text, reply_markup=buyer_menu_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "buyer_search_start")
async def cb_buyer_search_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BuyerFlow.waiting_for_query)
    text = (
        "🔍 **Qanday mahsulot qidiryapsiz?**\n\n"
        "Nomini yozib yuboring (masalan: *iPhone 15*, *mexanik klaviatura*):"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="Markdown")
    await callback.answer()

@dp.message(BuyerFlow.waiting_for_query)
async def process_buyer_query(message: types.Message, state: FSMContext):
    query = message.text.strip()
    await state.clear()

    encoded_query = query.replace(" ", "%20")
    uzum_search_url = f"https://uzum.uz/uz/search?query={encoded_query}"

    result_card = (
        f"🎯 **'{query}' bo'yicha qidiruv natijasi:**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📦 **Mavjud takliflar:** Do'konlarda topildi\n"
        "🚚 **Yetkazib berish:** Ertaga 1 kunda topshirish punktiga (PVZ)\n"
        "🔒 **To'lov:** Tovarni olgandan so'ng yoki Uzum Nasiya orqali bo'lib to'lash\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    action_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Uzum Marketda ko'rish", url=uzum_search_url)],
            [InlineKeyboardButton(text="🔍 Boshqa tovar qidirish", callback_data="buyer_search_start")],
            [InlineKeyboardButton(text="🔙 Asosiy menyuga qaytish", callback_data="back_to_main")]
        ]
    )

    await message.answer(result_card, reply_markup=action_kb, parse_mode="Markdown")

@dp.callback_query(F.data == "buyer_popular_categories")
async def cb_buyer_categories(callback: types.CallbackQuery):
    text = (
        "🔥 **Uzum Marketdagi ommabop bo'limlar:**\n\n"
        "1. 📱 Smartfonlar va gadjetlar\n"
        "2. 👟 Poyabzallar va kiyim-kechak\n"
        "3. 🏠 Maishiy texnika va uy-ro'zg'or buyumlari\n"
        "4. 🧴 Go'zallik va parvarish"
    )
    await callback.message.edit_text(text, reply_markup=buyer_menu_kb(), parse_mode="Markdown")
    await callback.answer()


# --- Dasturni ishga tushirish ---

async def main():
    await setup_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
