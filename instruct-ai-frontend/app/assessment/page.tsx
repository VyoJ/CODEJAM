"use client";

import { useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader } from "lucide-react";

interface Question {
  type: "MCQ" | "Subjective";
  question: string;
  options?: string[];
  model_answer: string;
}

interface Evaluation {
  grade: string;
  feedback: string;
}

export default function AssessmentPage() {
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [questionType, setQuestionType] = useState<"MCQ" | "Subjective">("MCQ");
  const [numQuestions, setNumQuestions] = useState(1);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState("");
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [isAnswerSubmitted, setIsAnswerSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const generateQuestions = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:8000/generate_questions",
        {
          topic: subject + " " + topic,
          question_type: questionType,
          num_questions: numQuestions,
        }
      );
      setQuestions(response.data.questions);
      setCurrentQuestionIndex(0);
      setUserAnswer("");
      setEvaluation(null);
      setIsAnswerSubmitted(false);
    } catch (error) {
      console.error("Error generating questions:", error);
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!userAnswer.trim()) {
      return;
    }

    setLoading(true);
    try {
      const currentQuestion = questions[currentQuestionIndex];
      console.log("currentQuestion", currentQuestion);
      const response = await axios.post(
        "http://localhost:8000/evaluate_answer",
        {
          question: currentQuestion.question,
          user_answer: userAnswer,
          model_answer: currentQuestion.model_answer,
        }
      );
      setEvaluation(response.data);
      setIsAnswerSubmitted(true);
    } catch (error) {
      console.error("Error submitting answer:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setUserAnswer("");
      setEvaluation(null);
      setIsAnswerSubmitted(false);
    }
  };

  return (
    <div className="py-12 px-4">
      <h1 className="text-4xl font-bold mb-8 text-center text-black dark:text-white">
        Instruct AI Assessment
      </h1>
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl">Generate Questions</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="subject">Subject</Label>
              <Select onValueChange={setSubject}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a subject" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="software engineering">
                    Software Engineering
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="topic">Topic</Label>
              <Input
                id="topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Enter a topic"
              />
            </div>
            <div className="space-y-2">
              <Label>Question Type</Label>
              <RadioGroup
                defaultValue="MCQ"
                onValueChange={(value) =>
                  setQuestionType(value as "MCQ" | "Subjective")
                }
                className="flex space-x-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="MCQ" id="mcq" />
                  <Label htmlFor="mcq">Multiple Choice</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="Subjective" id="subjective" />
                  <Label htmlFor="subjective">Subjective</Label>
                </div>
              </RadioGroup>
            </div>
            <div className="space-y-2">
              <Label htmlFor="numQuestions">Number of Questions (max 5)</Label>
              <Input
                id="numQuestions"
                type="number"
                min="1"
                max="5"
                value={numQuestions}
                onChange={(e) => setNumQuestions(parseInt(e.target.value, 10))}
              />
            </div>
            <Button
              type="button"
              onClick={generateQuestions}
              disabled={loading}
            >
              {loading ? (
                <Loader className="animate-spin h-5 w-5" />
              ) : (
                "Generate Questions"
              )}
            </Button>
          </form>
        </CardContent>
        {questions.length > 0 && (
          <CardContent className="pt-6">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">
                Question {currentQuestionIndex + 1} of {questions.length}
              </h3>
              <p className="mt-1 p-4 rounded-md">
                {questions[currentQuestionIndex].question}
              </p>
              <div className="space-y-2">
                <Label htmlFor="answer">Your Answer</Label>
                {questions[currentQuestionIndex].type === "MCQ" ? (
                  <RadioGroup
                    onValueChange={setUserAnswer}
                    className="space-y-2"
                  >
                    {questions[currentQuestionIndex].options?.map(
                      (option, index) => (
                        <div
                          key={index}
                          className="flex items-center space-x-2"
                        >
                          <RadioGroupItem
                            value={option}
                            id={`option-${index}`}
                          />
                          <Label htmlFor={`option-${index}`}>{option}</Label>
                        </div>
                      )
                    )}
                  </RadioGroup>
                ) : (
                  <Textarea
                    id="answer"
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    placeholder="Enter your answer"
                  />
                )}
              </div>
              <Button
                type="button"
                onClick={submitAnswer}
                disabled={loading || !userAnswer.trim()}
              >
                {loading ? (
                  <Loader className="animate-spin h-5 w-5" />
                ) : (
                  "Submit Answer"
                )}
              </Button>
              {isAnswerSubmitted &&
                currentQuestionIndex < questions.length - 1 && (
                  <Button
                    type="button"
                    onClick={handleNextQuestion}
                    className="ml-4"
                  >
                    Next Question
                  </Button>
                )}
            </div>
          </CardContent>
        )}
        {evaluation && (
          <CardFooter className="flex-col items-start">
            <h3 className="text-lg font-semibold my-2">Evaluation</h3>
            <p>Grade: {evaluation.grade}</p>
            <p>Feedback: {evaluation.feedback}</p>
          </CardFooter>
        )}
      </Card>
    </div>
  );
}
