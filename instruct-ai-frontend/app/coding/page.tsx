// "use client";

// import { useState } from "react";
// import axios from "axios";
// import { Button } from "@/components/ui/button";
// import { Input } from "@/components/ui/input";
// import { Label } from "@/components/ui/label";
// import {
//   Select,
//   SelectContent,
//   SelectItem,
//   SelectTrigger,
//   SelectValue,
// } from "@/components/ui/select";
// import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
// import { Loader } from "lucide-react";

// interface CodingQuestion {
//   title: string;
//   difficulty: {
//     level: string;
//     explanation: string | null;
//   };
//   description: string;
//   function_signature: string;
//   test_cases: Array<{
//     input: Record<string, any>;
//     expected: any;
//   }>;
//   solution: string;
//   time_complexity: string;
//   space_complexity: string;
//   hints: string[] | null;
//   learning_points: string[];
// }

// export default function AssessmentPage() {
//   const [language, setLanguage] = useState("");
//   const [topic, setTopic] = useState("");
//   const [numQuestions, setNumQuestions] = useState(1);
//   const [loading, setLoading] = useState(false);
//   const [questions, setQuestions] = useState<CodingQuestion[]>([]);
//   const [isDarkMode, setIsDarkMode] = useState(false);

//   const generateQuestions = async () => {
//     setLoading(true);
//     try {
//       const response = await axios.post(
//         "http://localhost:8000/generate_coding_questions",
//         {
//           programming_language: language,
//           difficulty: "easy",
//           topic: topic,
//           num_questions: numQuestions,
//         }
//       );
//       setQuestions(response.data.questions);
//     } catch (error) {
//       console.error("Error generating questions:", error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const toggleTheme = () => {
//     setIsDarkMode(!isDarkMode);
//     document.documentElement.classList.toggle("dark");
//   };

//   return (
//     <div
//       className={`min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100`}
//     >
//       <main>
//         <Card className="max-w-2xl mx-auto">
//           <CardHeader>
//             <CardTitle>Generate Coding Questions</CardTitle>
//           </CardHeader>
//           <CardContent>
//             <form
//               onSubmit={(e) => {
//                 e.preventDefault();
//                 generateQuestions();
//               }}
//               className="space-y-4"
//             >
//               <div className="space-y-2">
//                 <Label htmlFor="language">Programming Language</Label>
//                 <Select value={language} onValueChange={setLanguage}>
//                   <SelectTrigger id="language">
//                     <SelectValue placeholder="Select a language" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     <SelectItem value="python">Python</SelectItem>
//                     <SelectItem value="javascript">JavaScript</SelectItem>
//                     <SelectItem value="java">Java</SelectItem>
//                     <SelectItem value="cpp">C++</SelectItem>
//                   </SelectContent>
//                 </Select>
//               </div>

//               <div className="space-y-2">
//                 <Label htmlFor="topic">Topic</Label>
//                 <Input
//                   id="topic"
//                   placeholder="Enter a coding topic (e.g., Arrays, Recursion, OOP)"
//                   value={topic}
//                   onChange={(e) => setTopic(e.target.value)}
//                 />
//               </div>

//               <div className="space-y-2">
//                 <Label htmlFor="num-questions">
//                   Number of Questions (max 5)
//                 </Label>
//                 <Input
//                   id="num-questions"
//                   type="number"
//                   min={1}
//                   max={5}
//                   value={numQuestions}
//                   onChange={(e) => setNumQuestions(parseInt(e.target.value))}
//                 />
//               </div>

//               <Button type="submit" className="w-full" disabled={loading}>
//                 {loading ? (
//                   <Loader className="mr-2 h-4 w-4 animate-spin" />
//                 ) : null}
//                 {loading ? "Generating..." : "Generate Questions"}
//               </Button>
//             </form>
//           </CardContent>
//         </Card>

//         {questions.length > 0 && (
//           <div className="mt-8 space-y-6">
//             <h3 className="text-2xl font-bold mb-4">
//               Generated Coding Questions
//             </h3>
//             {questions.map((question, index) => (
//               <Card key={index}>
//                 <CardHeader>
//                   <CardTitle>{question.title}</CardTitle>
//                 </CardHeader>
//                 <CardContent className="space-y-2">
//                   <p>
//                     <strong>Difficulty:</strong> {question.difficulty.level}
//                   </p>
//                   <p>
//                     <strong>Description:</strong> {question.description}
//                   </p>
//                   <div>
//                     <strong>Function Signature:</strong>
//                     <pre className="bg-gray-100 dark:bg-gray-800 p-2 rounded mt-1 overflow-x-auto">
//                       {question.function_signature}
//                     </pre>
//                   </div>
//                   <div>
//                     <strong>Test Cases:</strong>
//                     <ul className="list-disc pl-5 mt-1">
//                       {question.test_cases.map((testCase, i) => (
//                         <li key={i}>
//                           Input: {JSON.stringify(testCase.input)}, Expected:{" "}
//                           {JSON.stringify(testCase.expected)}
//                         </li>
//                       ))}
//                     </ul>
//                   </div>
//                   <p>
//                     <strong>Time Complexity:</strong> {question.time_complexity}
//                   </p>
//                   <p>
//                     <strong>Space Complexity:</strong>{" "}
//                     {question.space_complexity}
//                   </p>
//                   {question.hints && (
//                     <div>
//                       <strong>Hints:</strong>
//                       <ul className="list-disc pl-5 mt-1">
//                         {question.hints.map((hint, i) => (
//                           <li key={i}>{hint}</li>
//                         ))}
//                       </ul>
//                     </div>
//                   )}
//                   <div>
//                     <strong>Learning Points:</strong>
//                     <ul className="list-disc pl-5 mt-1">
//                       {question.learning_points.map((point, i) => (
//                         <li key={i}>{point}</li>
//                       ))}
//                     </ul>
//                   </div>
//                 </CardContent>
//               </Card>
//             ))}
//           </div>
//         )}
//       </main>
//     </div>
//   );
// }

"use client";

import { useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Loader } from "lucide-react";

interface CodingQuestion {
  title: string;
  difficulty: {
    level: string;
    explanation: string | null;
  };
  description: string;
  function_signature: string;
  test_cases: Array<{
    input: Record<string, any>;
    expected: any;
  }>;
  solution: string;
  time_complexity: string;
  space_complexity: string;
  hints: string[] | null;
  learning_points: string[];
}

interface TestResult {
  passed: boolean;
  input: Record<string, any>;
  expected: any;
  actual: any;
  error?: string;
}

interface EvaluationResponse {
  passed: boolean;
  test_results: TestResult[];
  feedback: string;
  score: number;
  difficulty_appropriate: boolean;
  time_complexity_analysis?: string;
  space_complexity_analysis?: string;
  code_quality_feedback?: string;
  improvement_suggestions?: string[];
}

export default function CodingAssessment() {
  const [language, setLanguage] = useState("");
  const [topic, setTopic] = useState("");
  const [numQuestions, setNumQuestions] = useState(1);
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState<CodingQuestion[]>([]);
  const [userCode, setUserCode] = useState("");
  const [evaluationResult, setEvaluationResult] =
    useState<EvaluationResponse | null>(null);
  const [evaluating, setEvaluating] = useState(false);

  const generateQuestions = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:8000/generate_coding_questions",
        {
          programming_language: language,
          difficulty: "easy",
          topic: topic,
          num_questions: numQuestions,
        }
      );
      setQuestions(response.data.questions);
    } catch (error) {
      console.error("Error generating questions:", error);
    } finally {
      setLoading(false);
    }
  };

  const evaluateAnswer = async () => {
    if (questions.length === 0) return;

    setEvaluating(true);
    try {
      const response = await axios.post(
        "http://localhost:8000/evaluate_coding_answer",
        {
          question: questions[0],
          user_code: userCode,
          programming_language: language,
        }
      );
      setEvaluationResult(response.data);
    } catch (error) {
      console.error("Error evaluating answer:", error);
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="min-h-screen text-gray-900 dark:text-gray-100 p-8">
      <main className="max-w-4xl mx-auto space-y-8">
        <Card>
          <CardHeader>
            <CardTitle>Generate Coding Questions</CardTitle>
          </CardHeader>
          <CardContent>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                generateQuestions();
              }}
              className="space-y-4"
            >
              <div className="space-y-2">
                <Label htmlFor="language">Programming Language</Label>
                <Select value={language} onValueChange={setLanguage}>
                  <SelectTrigger id="language">
                    <SelectValue placeholder="Select a language" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="python">Python</SelectItem>
                    <SelectItem value="javascript">JavaScript</SelectItem>
                    <SelectItem value="java">Java</SelectItem>
                    <SelectItem value="cpp">C++</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="topic">Topic</Label>
                <Input
                  id="topic"
                  placeholder="Enter a coding topic (e.g., Arrays, Recursion, OOP)"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="num-questions">
                  Number of Questions (max 5)
                </Label>
                <Input
                  id="num-questions"
                  type="number"
                  min={1}
                  max={5}
                  value={numQuestions}
                  onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                />
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <Loader className="mr-2 h-4 w-4 animate-spin" />
                ) : null}
                {loading ? "Generating..." : "Generate Questions"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {questions.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>{questions[0].title}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p>
                <strong>Difficulty:</strong> {questions[0].difficulty.level}
              </p>
              <p>
                <strong>Description:</strong> {questions[0].description}
              </p>
              <div>
                <strong>Function Signature:</strong>
                <pre className="bg-gray-100 dark:bg-gray-800 p-2 rounded mt-1 overflow-x-auto">
                  {questions[0].function_signature}
                </pre>
              </div>
              <div>
                <Label htmlFor="user-code">Your Solution</Label>
                <Textarea
                  id="user-code"
                  placeholder="Enter your code here..."
                  value={userCode}
                  onChange={(e) => setUserCode(e.target.value)}
                  className="font-mono h-64"
                />
              </div>
              <Button onClick={evaluateAnswer} disabled={evaluating}>
                {evaluating ? (
                  <Loader className="mr-2 h-4 w-4 animate-spin" />
                ) : null}
                {evaluating ? "Evaluating..." : "Submit and Evaluate"}
              </Button>
            </CardContent>
          </Card>
        )}

        {evaluationResult && (
          <Card>
            <CardHeader>
              <CardTitle>Evaluation Result</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p>
                <strong>Passed:</strong>{" "}
                {evaluationResult.passed ? "Yes" : "No"}
              </p>
              <p>
                <strong>Score:</strong> {evaluationResult.score}
              </p>
              <p>
                <strong>Feedback:</strong> {evaluationResult.feedback}
              </p>
              <div>
                <strong>Test Results:</strong>
                <ul className="list-disc pl-5 mt-1">
                  {evaluationResult.test_results.map((result, index) => (
                    <li
                      key={index}
                      className={
                        result.passed ? "text-green-600" : "text-red-600"
                      }
                    >
                      Test {index + 1}: {result.passed ? "Passed" : "Failed"}
                      {!result.passed && (
                        <ul className="list-disc pl-5 mt-1">
                          <li>Input: {JSON.stringify(result.input)}</li>
                          <li>Expected: {JSON.stringify(result.expected)}</li>
                          <li>Actual: {JSON.stringify(result.actual)}</li>
                          {result.error && <li>Error: {result.error}</li>}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
              {evaluationResult.time_complexity_analysis && (
                <p>
                  <strong>Time Complexity Analysis:</strong>{" "}
                  {evaluationResult.time_complexity_analysis}
                </p>
              )}
              {evaluationResult.space_complexity_analysis && (
                <p>
                  <strong>Space Complexity Analysis:</strong>{" "}
                  {evaluationResult.space_complexity_analysis}
                </p>
              )}
              {evaluationResult.code_quality_feedback && (
                <p>
                  <strong>Code Quality Feedback:</strong>{" "}
                  {evaluationResult.code_quality_feedback}
                </p>
              )}
              {evaluationResult.improvement_suggestions && (
                <div>
                  <strong>Improvement Suggestions:</strong>
                  <ul className="list-disc pl-5 mt-1">
                    {evaluationResult.improvement_suggestions.map(
                      (suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      )
                    )}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
