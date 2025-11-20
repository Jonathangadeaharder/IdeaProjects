/**
 * Interactive Subtitle Component
 * Displays subtitles with hover-based word translation
 * Implements known/unknown word highlighting
 */
import React, { useMemo } from 'react'
import { useSubtitleHover } from '../hooks/useSubtitleHover'
import './InteractiveSubtitle.css'

interface InteractiveSubtitleProps {
  text: string
  language?: string
  knownWords?: Set<string>
  showTranslation?: boolean
  className?: string
}

interface WordToken {
  text: string
  isWord: boolean
  index: number
}

const InteractiveSubtitle: React.FC<InteractiveSubtitleProps> = ({
  text,
  language = 'de',
  knownWords = new Set(),
  showTranslation = true,
  className = '',
}) => {
  const { hoveredWord, translationData, isLoading, onWordHover, onWordLeave, tooltipPosition } =
    useSubtitleHover(language)

  // Tokenize text into words and punctuation
  const tokens = useMemo((): WordToken[] => {
    const regex = /(\b[\w'äöüÄÖÜß]+\b|[^\w\s])/g
    const matches = text.match(regex) || []

    return matches.map((match, index) => ({
      text: match,
      isWord: /[\wäöüÄÖÜß]/.test(match),
      index,
    }))
  }, [text])

  const renderToken = (token: WordToken) => {
    if (!token.isWord) {
      return (
        <span key={token.index} className="subtitle-punctuation">
          {token.text}
        </span>
      )
    }

    const normalizedWord = token.text.toLowerCase()
    const isKnown = knownWords.has(normalizedWord)
    const isHovered = hoveredWord?.toLowerCase() === normalizedWord

    return (
      <span
        key={token.index}
        className={`subtitle-word ${isKnown ? 'known' : 'unknown'} ${isHovered ? 'hovered' : ''}`}
        onMouseEnter={e => onWordHover(token.text, e)}
        onMouseLeave={onWordLeave}
        data-word={token.text}
      >
        {token.text}
      </span>
    )
  }

  return (
    <div className={`interactive-subtitle ${className}`}>
      <div className="subtitle-text">{tokens.map(renderToken)}</div>

      {showTranslation && tooltipPosition && (hoveredWord || isLoading) && (
        <div
          className="translation-tooltip"
          style={{
            left: `${tooltipPosition.x}px`,
            top: `${tooltipPosition.y + 20}px`,
          }}
        >
          {isLoading ? (
            <div className="tooltip-loading">Loading...</div>
          ) : translationData ? (
            <div className="tooltip-content">
              <div className="tooltip-word">{translationData.word}</div>
              <div className="tooltip-translation">{translationData.translation}</div>
              {translationData.level && (
                <div className="tooltip-level">Level: {translationData.level}</div>
              )}
              {translationData.partOfSpeech && (
                <div className="tooltip-pos">{translationData.partOfSpeech}</div>
              )}
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}

export default InteractiveSubtitle
