
const { generateFonts } = require('fantasticon');

// Use forward slashes natively avoiding fast-glob windows bug
const absoluteInput = process.cwd().replace(/\\\\/g, '/') + '/svgs'; 
const absoluteOutput = process.cwd().replace(/\\\\/g, '/') + '/output_font';

generateFonts({
    inputDir: absoluteInput,
    outputDir: absoluteOutput,
    fontTypes: ['ttf'],
    assetTypes: ['css', 'html'],
    name: 'TamilHandwritten',
    fontHeight: 1000,
    normalize: true,
    codepoints: {}
}).then(results => {
    console.log('Font generated successfully');
}).catch(err => {
    console.error('Error generating font:', err);
    process.exit(1);
});
    