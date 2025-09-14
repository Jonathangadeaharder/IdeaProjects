/**
 * Test utility to verify SRT parsing functionality
 */

// Sample SRT content for testing
const sampleSRT = `1
00:00:01,000 --> 00:00:04,000
This is a test subtitle

2
00:00:05,000 --> 00:00:08,000
This is another test subtitle | This is the translation

3
00:00:10,000 --> 00:00:13,000
Single language subtitle
`;

function parseSRT(srtContent: string) {
  const entries: any[] = [];
  const blocks = srtContent.trim().split(/\n\s*\n/);
  
  for (const block of blocks) {
    const lines = block.split('\n');
    if (lines.length >= 3) {
      const timeMatch = lines[1].match(/(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})/);
      if (timeMatch) {
        const start = parseInt(timeMatch[1]) * 3600 + parseInt(timeMatch[2]) * 60 + parseInt(timeMatch[3]) + parseInt(timeMatch[4]) / 1000;
        const end = parseInt(timeMatch[5]) * 3600 + parseInt(timeMatch[6]) * 60 + parseInt(timeMatch[7]) + parseInt(timeMatch[8]) / 1000;
        
        // Join remaining lines as subtitle text
        const textLines = lines.slice(2);
        let originalText = '';
        let translation = '';
        
        // Check if this is a dual-language subtitle (original | translation)
        if (textLines.length > 0 && textLines[0].includes('|')) {
          const parts = textLines[0].split('|');
          originalText = parts[0].trim();
          translation = parts[1]?.trim() || '';
        } else {
          originalText = textLines.join(' ');
        }
        
        entries.push({ start, end, text: originalText, translation });
      }
    }
  }
  
  return entries;
}

// Test the parsing function
console.log('Testing SRT parsing...');
const parsed = parseSRT(sampleSRT);
console.log('Parsed entries:', parsed);

if (parsed.length === 3) {
  console.log('✅ SRT parsing test passed');
  console.log(`   Found ${parsed.length} entries`);
  console.log(`   First entry: ${parsed[0].text}`);
  console.log(`   Second entry has translation: ${!!parsed[1].translation}`);
  console.log(`   Third entry: ${parsed[2].text}`);
} else {
  console.log('❌ SRT parsing test failed');
}

export { parseSRT };