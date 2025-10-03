"""
Game Data Transfer Objects
API request/response models for game sessions
"""

from datetime import datetime

from pydantic import BaseModel, Field


class GameSessionDTO(BaseModel):
    """DTO for game session"""

    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User ID")
    game_type: str = Field(..., description="Game type (vocabulary, listening, comprehension)")
    difficulty: str = Field(default="intermediate", description="Difficulty level")
    video_id: str | None = Field(None, description="Associated video ID")
    started_at: datetime = Field(..., description="Session start time")
    completed_at: datetime | None = Field(None, description="Session completion time")
    status: str = Field(default="active", description="Session status (active, completed, paused)")
    score: int = Field(default=0, ge=0, description="Current score")
    max_score: int = Field(default=100, ge=0, description="Maximum possible score")
    questions_answered: int = Field(default=0, ge=0, description="Questions answered")
    correct_answers: int = Field(default=0, ge=0, description="Correct answers")
    current_question: int = Field(default=0, ge=0, description="Current question number")
    total_questions: int = Field(default=10, ge=1, le=50, description="Total questions")
    session_data: dict = Field(default_factory=dict, description="Session state data")


class StartGameRequest(BaseModel):
    """DTO for starting a game session"""

    game_type: str = Field(..., description="Game type (vocabulary, listening, comprehension)")
    difficulty: str = Field(default="intermediate", description="Difficulty (beginner, intermediate, advanced)")
    video_id: str | None = Field(None, description="Optional video context")
    total_questions: int = Field(default=10, ge=1, le=50, description="Number of questions")


class SubmitAnswerRequest(BaseModel):
    """DTO for submitting a game answer"""

    session_id: str = Field(..., description="Game session ID")
    question_id: str = Field(..., description="Question ID")
    question_type: str = Field(default="multiple_choice", description="Question type")
    user_answer: str = Field(..., description="User's answer")
    correct_answer: str | None = Field(None, description="Expected correct answer")
    points: int = Field(default=10, ge=0, description="Points for this question")


class AnswerResultDTO(BaseModel):
    """DTO for answer submission result"""

    is_correct: bool = Field(..., description="Whether answer was correct")
    points_earned: int = Field(..., ge=0, description="Points awarded")
    current_score: int = Field(..., ge=0, description="Updated total score")
    questions_remaining: int = Field(..., ge=0, description="Questions remaining")
    session_completed: bool = Field(..., description="Whether session is finished")
