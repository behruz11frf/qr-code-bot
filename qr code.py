import logging
import qrcode
import os
from uuid import uuid4
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


TOKEN = "your bot token"

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


class QrCode(StatesGroup):
    text = State()


# Command to start the bot and display initial message with QR code generation button
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_generate = types.KeyboardButton("Generate QrCode")
    button_help = types.KeyboardButton("Help")
    keyboard.add(button_generate)
    keyboard.add(button_help)

    await message.answer(f"Hello {message.from_user.first_name}!")
    await message.answer("Send me text to generate a <b>QrCode</b> or use the buttons below:", reply_markup=keyboard)


# Handler to generate QR code when user sends text
@dp.message_handler(lambda message: message.text == "Generate QrCode")
async def prompt_for_text(message: types.Message):
    await message.answer("Send me text for <b>QrCode</b>")
    await QrCode.text.set()


@dp.message_handler(state=QrCode.text, content_types=types.ContentTypes.TEXT)
async def generate_qrcode(message: types.Message, state: FSMContext):
    text = str(message.text)
    qr_code = generate_qr_code(text)
    
    img_path = f"qrcode_{uuid4()}.png"
    qr_code.save(img_path)
    
    with open(img_path, "rb") as img_file:
        await message.answer_photo(photo=img_file, caption="Here is your QR code:")
    
    os.remove(img_path)
    await state.finish()


# Command to display help information
@dp.message_handler(lambda message: message.text == "Help")
async def help_command(message: types.Message):
    help_text = "Here are the available commands:\n"
    help_text += "/start - Start the bot\n"
    help_text += "/help - Show this help message\n"
    help_text += "Simply send text to generate a QR code!"
    await message.answer(help_text)


# Function to generate QR code
def generate_qr_code(text: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
