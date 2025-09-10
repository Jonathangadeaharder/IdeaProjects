import React from 'react';
import styled from 'styled-components';

export interface Language {
  code: string;
  name: string;
  flag: string;
}

interface LanguageSelectorProps {
  label: string;
  selectedLanguage: Language;
  languages: Language[];
  onSelect: (language: Language) => void;
  disabled?: boolean;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  label,
  selectedLanguage,
  languages,
  onSelect,
  disabled = false
}) => {
  return (
    <Container>
      <Label>{label}</Label>
      <LanguageOptions>
        {languages.map((lang) => (
          <LanguageOption
            key={lang.code}
            $selected={selectedLanguage.code === lang.code}
            $disabled={disabled}
            onClick={() => !disabled && onSelect(lang)}
            disabled={disabled}
          >
            <Flag>{lang.flag}</Flag>
            <LanguageCode $selected={selectedLanguage.code === lang.code}>
              {lang.code.toUpperCase()}
            </LanguageCode>
            <LanguageName $selected={selectedLanguage.code === lang.code}>
              {lang.name}
            </LanguageName>
          </LanguageOption>
        ))}
      </LanguageOptions>
    </Container>
  );
};

const Container = styled.div`
  margin: 12px 0;
`;

const Label = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
`;

const LanguageOptions = styled.div`
  display: flex;
  justify-content: space-between;
  gap: 8px;
`;

const LanguageOption = styled.button<{ $selected: boolean; $disabled: boolean }>`
  flex: 1;
  background-color: ${props => props.$selected ? '#e3f2fd' : '#f5f5f5'};
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 2px solid ${props => props.$selected ? '#2196F3' : 'transparent'};
  opacity: ${props => props.$disabled ? 0.5 : 1};
  cursor: ${props => props.$disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background-color: ${props => props.$selected ? '#e3f2fd' : '#e0e0e0'};
  }

  &:focus {
    outline: 2px solid #2196F3;
    outline-offset: 2px;
  }
`;

const Flag = styled.div`
  font-size: 32px;
  margin-bottom: 4px;
`;

const LanguageCode = styled.div<{ $selected: boolean }>`
  font-size: 14px;
  font-weight: bold;
  color: ${props => props.$selected ? '#2196F3' : '#666'};
  margin-bottom: 2px;
`;

const LanguageName = styled.div<{ $selected: boolean }>`
  font-size: 12px;
  color: ${props => props.$selected ? '#2196F3' : '#999'};
`;

export default LanguageSelector;