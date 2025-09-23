/**
 * Dependency Injection Container
 * Manages service instances and provides them to components
 */

import { AuthClient, ProductionAuthClient, TestAuthClient } from '../clients/auth.client'
import { VideoRepository } from '../repositories/video.repository'
import { AuthRepository } from '../repositories/auth.repository'
import { ProfileRepository } from '../repositories/profile.repository'
import { VocabularyRepository } from '../repositories/vocabulary.repository'
import { HttpClient } from '../clients/http.client'

export interface DIContainer {
  // Clients
  authClient: AuthClient
  httpClient: HttpClient

  // Repositories
  auth: AuthRepository
  videos: VideoRepository
  profile: ProfileRepository
  vocabulary: VocabularyRepository
}

class DependencyContainer implements DIContainer {
  private static instance: DependencyContainer

  // Clients
  public authClient: AuthClient
  public httpClient: HttpClient

  // Repositories
  public auth: AuthRepository
  public videos: VideoRepository
  public profile: ProfileRepository
  public vocabulary: VocabularyRepository

  private constructor(isTestEnvironment: boolean = false) {
    // Initialize HTTP client
    this.httpClient = new HttpClient(
      process.env.REACT_APP_API_URL || 'http://localhost:8000'
    )

    // Initialize auth client based on environment
    this.authClient = isTestEnvironment
      ? new TestAuthClient()
      : new ProductionAuthClient(this.httpClient)

    // Initialize repositories
    this.auth = new AuthRepository(this.authClient)
    this.videos = new VideoRepository(this.httpClient)
    this.profile = new ProfileRepository(this.httpClient)
    this.vocabulary = new VocabularyRepository(this.httpClient)
  }

  public static getInstance(isTestEnvironment: boolean = false): DependencyContainer {
    if (!DependencyContainer.instance) {
      DependencyContainer.instance = new DependencyContainer(isTestEnvironment)
    }
    return DependencyContainer.instance
  }

  public static reset(): void {
    DependencyContainer.instance = null as any
  }
}

// Export singleton instance
export const container = DependencyContainer.getInstance(
  process.env.NODE_ENV === 'test'
)

// React Context for providing container to components
import React, { createContext, useContext } from 'react'

export const DIContext = createContext<DIContainer>(container)

export const useDI = () => {
  const context = useContext(DIContext)
  if (!context) {
    throw new Error('useDI must be used within DIProvider')
  }
  return context
}

export const DIProvider: React.FC<{
  children: React.ReactNode
  container?: DIContainer
}> = ({ children, container: customContainer }) => {
  return React.createElement(
    DIContext.Provider,
    { value: customContainer || container },
    children
  )
}