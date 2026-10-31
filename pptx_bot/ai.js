const OpenAI = require('openai');

function normalizeSlides(data) {
  if (!Array.isArray(data)) {
    throw new Error('AI response is not a slide array.');
  }

  return data
    .slice(0, 8)
    .map((slide, index) => {
      if (!slide || typeof slide !== 'object') {
        throw new Error(`Invalid slide object at position ${index + 1}`);
      }

      const title = (slide.title || slide.Title || '').toString().trim();
      const bullets = (slide.bullets || slide.points || slide.bulletPoints || slide.bulletsPoints);

      if (!title) {
        throw new Error(`Slide ${index + 1} missing title`);
      }

      if (!Array.isArray(bullets) || bullets.length < 3) {
        throw new Error(`Slide ${index + 1} bullets not valid (must be 3-5 items).`);
      }

      const cleanedBullets = bullets
        .slice(0, 5)
        .map((bullet) => bullet.toString().trim())
        .filter(Boolean);

      if (cleanedBullets.length < 3) {
        throw new Error(`Slide ${index + 1} must have at least 3 non-empty bullets.`);
      }

      return { title, bullets: cleanedBullets };
    });
}

async function generatePresentation(topic, openaiClient) {
  if (!topic || !topic.trim()) {
    throw new Error('Topic is required.');
  }

  const prompt = `You are a professional presentation writer. Create 6-8 slides for the topic: "${topic.trim()}". Provide the exact output in JSON with this format:\n[\n  {\n    \"title\": \"Slide 1 title\",\n    \"bullets\": [\"bullet1\",\"bullet2\",\"bullet3\"]\n  }, ...\n]\nEach slide: title and 3-5 bullets. Do not add any extra text outside JSON.`;

  const completion = await openaiClient.responses.create({
    model: 'gpt-4.1',
    input: prompt,
    max_tokens: 850,
    temperature: 0.75,
  });

  let content = ''; 

  if (completion.output && completion.output[0] && completion.output[0].content) {
    const parts = completion.output[0].content;
    for (const part of parts) {
      if (part.type === 'output_text' && part.text) {
        content += part.text;
      }
    }
  }

  if (!content) {
    throw new Error('Empty AI completion content.');
  }

  // Find JSON inside content if text has wrappers
  let jsonStr = content.trim();

  const firstBrace = jsonStr.indexOf('[');
  const lastBrace = jsonStr.lastIndexOf(']');
  if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
    jsonStr = jsonStr.slice(firstBrace, lastBrace + 1);
  }

  let slides;
  try {
    slides = JSON.parse(jsonStr);
  } catch (parseErr) {
    throw new Error(`Failed to parse AI JSON response: ${parseErr.message} - raw: ${content}`);
  }

  return normalizeSlides(slides);
}

module.exports = {
  generatePresentation,
};
