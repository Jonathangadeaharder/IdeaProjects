/**
 * Subtitle Synchronization Service
 * Handles word-level timestamp generation and subtitle-video synchronization
 */

export interface WordTimestamp {
  word: string
  start: number
  end: number
  confidence: number
}

export interface SubtitleSegment {
  id: string
  text: string
  start: number
  end: number
  words: WordTimestamp[]
}

export class SubtitleSyncService {
  /**
   * Generate word-level timestamps from segment data.
   * Whisper provides segment-level timestamps, so we interpolate word positions
   * based on equal distribution within the segment duration.
   *
   * This is a simplified approach. For production, consider using forced alignment
   * tools like Montreal Forced Aligner or wav2vec2-based alignment.
   */
  generateWordTimestamps(segment: SubtitleSegment): WordTimestamp[] {
    // Clean and tokenize the text
    const words = this.tokenizeWords(segment.text)

    if (words.length === 0) {
      return []
    }

    const segmentDuration = segment.end - segment.start
    const avgWordDuration = segmentDuration / words.length

    return words.map((word, index) => ({
      word,
      start: segment.start + index * avgWordDuration,
      end: segment.start + (index + 1) * avgWordDuration,
      confidence: 1.0,
    }))
  }

  /**
   * Tokenize text into words, preserving German characters.
   * Filters out pure punctuation tokens.
   */
  private tokenizeWords(text: string): string[] {
    // Match words (including German special characters) and contractions
    const wordRegex = /\b[\w'äöüÄÖÜß]+\b/g
    const matches = text.match(wordRegex) || []

    return matches.filter(word => word.trim().length > 0)
  }

  /**
   * Find the active word at a specific timestamp.
   */
  getActiveWordAtTime(segments: SubtitleSegment[], currentTime: number): WordTimestamp | null {
    for (const segment of segments) {
      // Check if currentTime is within segment bounds
      if (currentTime >= segment.start && currentTime <= segment.end) {
        // Ensure words are generated for this segment
        if (!segment.words || segment.words.length === 0) {
          segment.words = this.generateWordTimestamps(segment)
        }

        // Find the active word within this segment
        for (const word of segment.words) {
          if (currentTime >= word.start && currentTime <= word.end) {
            return word
          }
        }
      }
    }

    return null
  }

  /**
   * Get all words within a time range (for bulk highlighting).
   */
  getWordsInRange(
    segments: SubtitleSegment[],
    startTime: number,
    endTime: number
  ): WordTimestamp[] {
    const words: WordTimestamp[] = []

    for (const segment of segments) {
      // Check if segment overlaps with the time range
      if (segment.start <= endTime && segment.end >= startTime) {
        // Ensure words are generated
        if (!segment.words || segment.words.length === 0) {
          segment.words = this.generateWordTimestamps(segment)
        }

        // Collect words within range
        for (const word of segment.words) {
          if (word.start <= endTime && word.end >= startTime) {
            words.push(word)
          }
        }
      }
    }

    return words
  }

  /**
   * Find the segment containing a specific timestamp.
   */
  getActiveSegmentAtTime(segments: SubtitleSegment[], currentTime: number): SubtitleSegment | null {
    for (const segment of segments) {
      if (currentTime >= segment.start && currentTime <= segment.end) {
        return segment
      }
    }

    return null
  }

  /**
   * Get the next segment after the current time.
   */
  getNextSegment(segments: SubtitleSegment[], currentTime: number): SubtitleSegment | null {
    for (const segment of segments) {
      if (segment.start > currentTime) {
        return segment
      }
    }

    return null
  }

  /**
   * Get the previous segment before the current time.
   */
  getPreviousSegment(segments: SubtitleSegment[], currentTime: number): SubtitleSegment | null {
    let previous: SubtitleSegment | null = null

    for (const segment of segments) {
      if (segment.end < currentTime) {
        previous = segment
      } else {
        break
      }
    }

    return previous
  }

  /**
   * Convert SRT subtitle data to SubtitleSegment format.
   */
  parseSRT(srtContent: string): SubtitleSegment[] {
    const segments: SubtitleSegment[] = []
    const blocks = srtContent.trim().split(/\n\s*\n/)

    for (const block of blocks) {
      const lines = block.split('\n')

      if (lines.length < 3) continue

      const timeLine = lines[1]
      const textLines = lines.slice(2)

      // Parse timestamps: 00:00:01,234 --> 00:00:04,567
      const timeMatch = timeLine.match(/(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})/)

      if (!timeMatch) continue

      const [_, startH, startM, startS, startMs, endH, endM, endS, endMs] = timeMatch

      const start =
        parseInt(startH) * 3600 +
        parseInt(startM) * 60 +
        parseInt(startS) +
        parseInt(startMs) / 1000

      const end =
        parseInt(endH) * 3600 + parseInt(endM) * 60 + parseInt(endS) + parseInt(endMs) / 1000

      const text = textLines.join(' ').trim()

      const segment: SubtitleSegment = {
        id: `segment-${start}-${end}`,
        text,
        start,
        end,
        words: [],
      }

      // Generate word timestamps immediately
      segment.words = this.generateWordTimestamps(segment)

      segments.push(segment)
    }

    return segments
  }
}

// Singleton instance
export const subtitleSyncService = new SubtitleSyncService()
