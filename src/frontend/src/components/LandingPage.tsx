import React from 'react'
import { useNavigate } from 'react-router-dom'
import styled from 'styled-components'
import { NetflixButton } from '@/styles/GlobalStyles'

const LandingContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(
    rgba(0, 0, 0, 0.7),
    rgba(0, 0, 0, 0.7)
  ), linear-gradient(135deg, #141414 0%, #1a1a1a 100%);
  background-size: cover;
  background-position: center;
  color: white;
`

const Hero = styled.div`
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
`

const Logo = styled.h1`
  color: #e50914;
  font-size: 72px;
  margin-bottom: 20px;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
`

const Tagline = styled.h2`
  font-size: 32px;
  font-weight: 300;
  margin-bottom: 20px;
  max-width: 800px;
`

const Description = styled.p`
  font-size: 20px;
  color: #b3b3b3;
  margin-bottom: 40px;
  max-width: 700px;
  line-height: 1.6;
`

const CTAContainer = styled.div`
  display: flex;
  gap: 20px;
  margin-bottom: 60px;
  flex-wrap: wrap;
  justify-content: center;
`

const GetStartedButton = styled(NetflixButton)`
  padding: 18px 48px;
  font-size: 20px;
  font-weight: 600;
  border-radius: 4px;
`

const SignInButton = styled(NetflixButton)`
  padding: 18px 48px;
  font-size: 20px;
  font-weight: 600;
  background: transparent;
  border: 2px solid white;
  border-radius: 4px;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: #e50914;
  }
`

const FeaturesSection = styled.div`
  background: rgba(0, 0, 0, 0.6);
  padding: 80px 20px;
`

const FeaturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 40px;
  max-width: 1200px;
  margin: 0 auto;
`

const FeatureCard = styled.div`
  text-align: center;
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.08);
  }
`

const FeatureIcon = styled.div`
  font-size: 48px;
  margin-bottom: 20px;
`

const FeatureTitle = styled.h3`
  font-size: 24px;
  margin-bottom: 15px;
  color: #e50914;
`

const FeatureDescription = styled.p`
  font-size: 16px;
  color: #b3b3b3;
  line-height: 1.6;
`

const SectionTitle = styled.h2`
  text-align: center;
  font-size: 40px;
  margin-bottom: 60px;
  color: white;
`

export const LandingPage: React.FC = () => {
  const navigate = useNavigate()

  return (
    <LandingContainer>
      <Hero>
        <Logo>LangPlug</Logo>
        <Tagline>Learn German Through Your Favorite Shows</Tagline>
        <Description>
          Master German naturally by watching TV series you love. 
          Our AI-powered platform extracts vocabulary, creates personalized learning sessions, 
          and helps you learn in context - just like native speakers do.
        </Description>
        <CTAContainer>
          <GetStartedButton onClick={() => navigate('/register')}>
            Get Started Free
          </GetStartedButton>
          <SignInButton onClick={() => navigate('/login')}>
            Sign In
          </SignInButton>
        </CTAContainer>
      </Hero>

      <FeaturesSection>
        <SectionTitle>How It Works</SectionTitle>
        <FeaturesGrid>
          <FeatureCard>
            <FeatureIcon>📺</FeatureIcon>
            <FeatureTitle>Watch & Learn</FeatureTitle>
            <FeatureDescription>
              Upload episodes from your favorite German TV series. 
              Our AI automatically transcribes and translates the content.
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>🎯</FeatureIcon>
            <FeatureTitle>Smart Vocabulary</FeatureTitle>
            <FeatureDescription>
              AI identifies vocabulary at your level - A1 through B2. 
              Learn words that matter based on your current knowledge.
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>🎮</FeatureIcon>
            <FeatureTitle>Interactive Games</FeatureTitle>
            <FeatureDescription>
              Reinforce learning with engaging vocabulary games. 
              Practice with real sentences from the shows you watched.
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>📊</FeatureIcon>
            <FeatureTitle>Track Progress</FeatureTitle>
            <FeatureDescription>
              Monitor your vocabulary growth and learning streaks.
              See exactly how much you're improving over time.
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>🧠</FeatureIcon>
            <FeatureTitle>Context-Based</FeatureTitle>
            <FeatureDescription>
              Learn vocabulary in the context of real conversations. 
              Understand how words are actually used by native speakers.
            </FeatureDescription>
          </FeatureCard>

          <FeatureCard>
            <FeatureIcon>⚡</FeatureIcon>
            <FeatureTitle>Chunked Learning</FeatureTitle>
            <FeatureDescription>
              Break episodes into manageable 5-minute chunks. 
              Learn at your own pace without feeling overwhelmed.
            </FeatureDescription>
          </FeatureCard>
        </FeaturesGrid>
      </FeaturesSection>
    </LandingContainer>
  )
}
