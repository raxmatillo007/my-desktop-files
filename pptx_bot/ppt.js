const pptxgen = require('pptxgenjs');
const fs = require('fs');

async function createPptx(slides, outputPath) {
  if (!Array.isArray(slides) || slides.length === 0) {
    throw new Error('Slides must be a non-empty array.');
  }

  const pres = new pptxgen();

  pres.layout = 'LAYOUT_WIDE';

  for (const slide of slides) {
    const s = pres.addSlide();

    s.addText(slide.title, {
      x: 0.5,
      y: 0.3,
      w: 9,
      h: 1.1,
      fontSize: 42,
      bold: true,
      color: '003366',
      align: 'left',
      margin: 0.2,
    });

    const bulletText = slide.bullets.map((b) => `• ${b}`).join('\n');

    s.addText(bulletText, {
      x: 0.6,
      y: 1.6,
      w: 8.4,
      h: 4.5,
      fontSize: 20,
      color: '333333',
      align: 'left',
      bullet: false,
      lineSpacing: 26,
    });

    s.background = { color: 'FFFFFF' };

    s.addShape(pptxgen.shapes.rect, {
      x: 0.4,
      y: 0.2,
      w: 9.2,
      h: 5.5,
      line: { color: 'CCCCCC', width: 1 },
      fill: { color: 'F9FBFF' },
    });
  }

  // Clean up existing file if any
  try {
    if (fs.existsSync(outputPath)) {
      fs.unlinkSync(outputPath);
    }
  } catch (err) {
    // ignore
  }

  await pres.writeFile({ fileName: outputPath });
  return outputPath;
}

module.exports = {
  createPptx,
};
