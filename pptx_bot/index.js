require('dotenv').config();
const path = require('path');
const fs = require('fs');
const TelegramBot = require('node-telegram-bot-api');
const { OpenAI } = require('openai');
const { generatePresentation } = require('./ai');
const { createPptx } = require('./ppt');

const telegramToken = process.env.TELEGRAM_BOT_TOKEN;
const openAiApiKey = process.env.OPENAI_API_KEY;

if (!telegramToken) {
  throw new Error('TELEGRAM_BOT_TOKEN is not set in environment variables.');
}
if (!openAiApiKey) {
  throw new Error('OPENAI_API_KEY is not set in environment variables.');
}

const bot = new TelegramBot(telegramToken, { polling: true });
const openai = new OpenAI({ apiKey: openAiApiKey });

bot.onText(/\/start/, async (msg) => {
  try {
    await bot.sendMessage(
      msg.chat.id,
      'Welcome! Send me a presentation topic (e.g., "Business presentation"), and I will generate a 6-8 slide PPTX for you.'
    );
  } catch (err) {
    console.error('Failed to respond to /start', err);
  }
});

bot.on('message', async (msg) => {
  const chatId = msg.chat.id;
  const text = (msg.text || '').trim();

  if (!text || text.startsWith('/')) {
    return;
  }

  try {
    await bot.sendChatAction(chatId, 'typing');
    const waiting = await bot.sendMessage(chatId, '📌 Generating your presentation, please wait...');

    const slides = await generatePresentation(text, openai);

    if (!slides || slides.length === 0) {
      throw new Error('No slides generated from AI response.');
    }

    const safeTopic = text.replace(/[^a-zA-Z0-9-_ ]/g, '').substring(0, 32).replace(/ +/g, '_');
    const outputFileName = `presentation_${Date.now()}_${safeTopic || 'topic'}.pptx`;
    const outputPath = path.join(__dirname, outputFileName);

    await createPptx(slides, outputPath);

    await bot.sendDocument(chatId, outputPath, {
      caption: `✅ Your generated presentation on "${text}" is ready!`,
    });

    if (fs.existsSync(outputPath)) {
      fs.unlinkSync(outputPath);
    }

    await bot.deleteMessage(chatId, waiting.message_id);

  } catch (err) {
    console.error('Error generating presentation:', err);
    await bot.sendMessage(
      chatId,
      '⚠️ Something went wrong while generating your presentation. Please try again later.'
    );
  }
});

bot.on('polling_error', (error) => {
  console.error('Polling error:', error);
});
