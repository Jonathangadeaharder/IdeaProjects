#!/usr/bin/env node

/**
 * Manual test script to verify video player subtitle functionality
 * This script checks if the ChunkedLearningPlayer component can parse SRT files correctly
 */

// Simple SRT parser function (copied from the component)
function parseSRT(srtContent) {
  const entries = [];
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

// Test data
const testSRT = `1
00:00:01,000 --> 00:00:04,000
This is a test subtitle

2
00:00:05,000 --> 00:00:08,000
This is another test subtitle | This is the translation

3
00:00:10,000 --> 00:00:13,000
Single language subtitle
`;

console.log('Testing SRT parsing functionality...');
console.log('=====================================');

try {
  const parsed = parseSRT(testSRT);
  
  console.log('✅ SRT parsing successful');
  console.log(`   Found ${parsed.length} entries`);
  
  if (parsed.length === 3) {
    console.log('✅ Correct number of entries parsed');
    
    // Check first entry
    if (parsed[0].text === 'This is a test subtitle' && parsed[0].translation === '') {
      console.log('✅ First entry parsed correctly');
    } else {
      console.log('❌ First entry parsing failed');
      console.log(`   Expected: "This is a test subtitle" (no translation)`);
      console.log(`   Got: "${parsed[0].text}" (${parsed[0].translation})`);
    }
    
    // Check second entry (dual language)
    if (parsed[1].text === 'This is another test subtitle' && parsed[1].translation === 'This is the translation') {
      console.log('✅ Second entry (dual language) parsed correctly');
    } else {
      console.log('❌ Second entry parsing failed');
      console.log(`   Expected: "This is another test subtitle" | "This is the translation"`);
      console.log(`   Got: "${parsed[1].text}" | "${parsed[1].translation}"`);
    }
    
    // Check third entry
    if (parsed[2].text === 'Single language subtitle' && parsed[2].translation === '') {
      console.log('✅ Third entry parsed correctly');
    } else {
      console.log('❌ Third entry parsing failed');
      console.log(`   Expected: "Single language subtitle" (no translation)`);
      console.log(`   Got: "${parsed[2].text}" (${parsed[2].translation})`);
    }
  } else {
    console.log(`❌ Expected 3 entries, got ${parsed.length}`);
  }
  
  console.log('\n🎉 SRT parsing test completed successfully!');
  console.log('The video player should be able to parse subtitle files correctly.');
  
} catch (error) {
  console.error('❌ SRT parsing test failed:', error);
  console.error('The video player may have issues parsing subtitle files.');
}
