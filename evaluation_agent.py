import pandas as pd
import numpy as np
from typing import List, Dict, Union
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq.chat_models import ChatGroq
from pydantic import BaseModel, Field

rubric = """
Rubric for Scoring Reading Comprehension Answers:

1. Content Accuracy (0-5 points):
   0 - Completely incorrect or irrelevant
   1 - Mostly incorrect with minor relevant points
   2 - Partially correct, missing several key points
   3 - Mostly correct with some key points missing
   4 - Mostly correct with minor inaccuracies
   5 - Fully correct and comprehensive

2. Comprehension (0-5 points):
   0 - No understanding demonstrated
   1 - Minimal understanding of the passage
   2 - Limited understanding with major gaps
   3 - Good understanding with some gaps
   4 - Very good understanding with minor gaps
   5 - Excellent, thorough understanding of the passage

3. Clarity of Expression (0-5 points):
   0 - Incomprehensible or extremely unclear
   1 - Mostly unclear with significant issues
   2 - Somewhat clear but with notable issues
   3 - Mostly clear with minor issues
   4 - Clear and well-expressed with very minor issues
   5 - Exceptionally clear and well-articulated

4. Language Mechanics (0-5 points):
   0 - Numerous major errors in punctuation, grammar, and spelling
   1 - Many significant errors in punctuation, grammar, and spelling
   2 - Several noticeable errors in punctuation, grammar, and spelling
   3 - Some minor errors in punctuation, grammar, and spelling
   4 - Very few minor errors in punctuation, grammar, and spelling
   5 - Flawless or near-flawless punctuation, grammar, and spelling

Total possible score: 20 points
"""

class ScoringEvaluation(BaseModel):
    overall_accuracy: float = Field(description="Normalized accuracy of LLM scoring")
    bias_detection: Dict[str, float] = Field(description="Potential scoring biases")
    scoring_consistency: float = Field(description="Consistency of scoring across dimensions")

class LLMScoringEvaluator:
    def __init__(self, model_name="llama3-8b-8192"):
        self.llm = ChatGroq(model_name="llama3-8b-8192", api_key="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", temperature=0.7)
        
    def create_ground_truth_prompt(self):
        return PromptTemplate(
            input_variables=["context", "question", "user_answer", "rubric"],
            template="""You are an experienced, highly analytical reading comprehension expert with 20 years of academic assessment experience. 
- Your goal is to provide precise, objective, and nuanced scoring
- Approach each answer with academic rigor
- Avoid subjective bias
- Provide clear, evidence-based justification for each score

Rubric: {rubric}

Context: {context}
Question: {question}
User Answer: {user_answer}

Systematic Evaluation Protocol:
1. Read the entire answer carefully
2. Cross-reference with context and question
3. Score each dimension independently
4. Provide concrete, specific reasoning

Scoring Requirements:
- Be extremely precise in score allocation
- Use the full 0-5 point range
- Highlight both strengths and weaknesses
- Explain scoring rationale with academic precision

Detailed Scoring Format:
Content Accuracy: X/5 
- Precise score explanation
- Specific evidence mapping to context
- Clear reasoning for point allocation

Comprehension: Y/5
- Depth of understanding assessment
- Specific textual evidence
- Analytical breakdown of comprehension level

Clarity of Expression: Z/5
- Technical assessment of communication
- Language structure analysis
- Specific examples of clarity/obscurity

Language Mechanics: W/5
- Grammatical precision evaluation
- Specific error identification
- Systematic mechanical assessment

Final Note: Your evaluation is a scholarly, objective assessment of the answer's academic merit."""
    )

    def parse_llm_scores(self, llm_response: str) -> List[int]:
        """Parse LLM-generated scores from response text."""
        dimensions = ['Content Accuracy', 'Comprehension', 'Clarity of Expression', 'Language Mechanics']
        scores = []
        
        for dim in dimensions:
            try:
                # More robust score extraction
                score_line = [line for line in llm_response.split('\n') if dim in line][0]
                score = int(score_line.split(':')[1].split('/')[0].strip())
                scores.append(score)
            except (IndexError, ValueError):
                # Fallback to median score if parsing fails
                scores.append(3)
        
        return scores

    def calculate_scoring_metrics(self, ground_truth_scores: List[int], predicted_scores: List[int]) -> ScoringEvaluation:
        """Calculate comprehensive scoring metrics."""
        deviations = [abs(gt - pred) for gt, pred in zip(ground_truth_scores, predicted_scores)]
        
        overall_accuracy = 1 - (np.mean(deviations) / 5)
        
        bias_detection = {
            'content_bias': abs(ground_truth_scores[0] - predicted_scores[0]) / 5,
            'comprehension_bias': abs(ground_truth_scores[1] - predicted_scores[1]) / 5,
            'clarity_bias': abs(ground_truth_scores[2] - predicted_scores[2]) / 5,
            'mechanics_bias': abs(ground_truth_scores[3] - predicted_scores[3]) / 5
        }
        
        scoring_consistency = 1 - (np.std(deviations) / 5)
        
        return ScoringEvaluation(
            overall_accuracy=max(0, overall_accuracy),
            bias_detection=bias_detection,
            scoring_consistency=max(0, scoring_consistency)
        )

    def evaluate_scoring_capability(self, data: pd.DataFrame) -> pd.DataFrame:
        evaluation_results = []
        
        for index, row in data.iterrows():
            # Create ground truth scoring prompt
            prompt = self.create_ground_truth_prompt()
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            try:
                # Generate ground truth scores via LLM
                llm_ground_truth_response = chain.run(
                    context=row['context'],
                    question=row['question'],
                    user_answer=row['sample_user_answer'],
                    rubric=rubric
                )
                
                # Parse ground truth scores
                ground_truth_scores = self.parse_llm_scores(llm_ground_truth_response)
                
                # Extract predicted scores from CSV
                predicted_scores = [
                    row['content_accuracy'], 
                    row['comprehension_score'], 
                    row['clarity_score'], 
                    row['language_mechanics_score']
                ]
                
                # Calculate scoring metrics
                scoring_metrics = self.calculate_scoring_metrics(ground_truth_scores, predicted_scores)
                
                # Collect results
                evaluation_results.append({
                    'passage_id': row['passage_id'],
                    'ground_truth_scores': ground_truth_scores,
                    'predicted_scores': predicted_scores,
                    'overall_accuracy': scoring_metrics.overall_accuracy,
                    'content_bias': scoring_metrics.bias_detection['content_bias'],
                    'comprehension_bias': scoring_metrics.bias_detection['comprehension_bias'],
                    'clarity_bias': scoring_metrics.bias_detection['clarity_bias'],
                    'mechanics_bias': scoring_metrics.bias_detection['mechanics_bias'],
                    'scoring_consistency': scoring_metrics.scoring_consistency,
                    'llm_ground_truth_response': llm_ground_truth_response
                })
                
            except Exception as e:
                print(f"Error processing sample {index + 1}: {e}")
                evaluation_results.append({
                    'passage_id': row['passage_id'],
                    'error': str(e)
                })
        
        return pd.DataFrame(evaluation_results)

def main():
    # Load dataset
    try:
        data = pd.read_csv('reading_comprehension_testset.csv')
    except FileNotFoundError:
        print("Error: Dataset file 'reading_comprehension_testset.csv' not found.")
        return
    
    # Initialize evaluator
    evaluator = LLMScoringEvaluator()
    
    # Evaluate LLM scoring capabilities
    results = evaluator.evaluate_scoring_capability(data)
    
    # Save results
    results.to_csv('llm_ground_truth_scoring_analysis.csv', index=False)
    
    print("\n--- Evaluation Complete ---")
    print(f"Total Samples Processed: {len(results)}")

if __name__ == "__main__":
    main()