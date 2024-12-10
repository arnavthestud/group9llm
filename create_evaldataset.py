import pandas as pd
import csv

def add_passages_to_csv(existing_csv_path, new_passages):

    existing_df = pd.read_csv(existing_csv_path)
    

    new_df = pd.DataFrame(new_passages)
    

    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    

    combined_df.to_csv(existing_csv_path, index=False)
    
    print(f"Added {len(new_passages)} new passages to {existing_csv_path}")


new_passages = [
    {
        "passage_id": "global_citizenship",
        "difficulty_level": "hard",
        "context": "The notion of a 'global citizen' has gained widespread acceptance in recent years, but its implications for national identity and cultural heritage are still debated. In his latest book, philosopher Kwame Anthony Appiah argues that the concept of a global citizen is not only a desirable goal, but also a necessary one for the preservation of humanity's shared cultural heritage. According to Appiah, the increasing interconnectedness of the world's cultures has created a sense of shared humanity, which can only be sustained through a cosmopolitan understanding of citizenship. However, others have criticized Appiah's views, citing the importance of preserving national traditions and cultural differences.",
        "question": "What is the author's stance on the relationship between national identity and cultural heritage in the context of global citizenship?",
        "correct_answer": "The author argues that the concept of global citizenship is not only a desirable goal, but also a necessary one for the preservation of humanity's shared cultural heritage, suggesting a tension between national identity and cultural heritage.",
        "explanation": "The author's stance is inferred through the passage, which presents Appiah's argument that global citizenship is necessary for the preservation of shared cultural heritage. The author does not explicitly state a stance, but the presentation of Appiah's views and the critique of those views implies that the author is sympathetic to the idea of global citizenship as a means of preserving shared cultural heritage, while acknowledging the potential tension with national identity and cultural heritage.",
        "sample_user_answer": "Kwame Anthony Appiah argues that the concept of a global citizen is not only a desirable goal, but also a necessary one for the preservation of humanity's shared cultural heritage.",
        "content_accuracy": 4,
        "comprehension_score": 3,
        "clarity_score": 4,
        "language_mechanics_score": 5,
        "total_score": 16,
        "overall_feedback": "The user demonstrates a good understanding of the passage and is able to accurately summarize Appiah's views on global citizenship and cultural heritage."
    },
    {
        "passage_id": "tokyo_tourism",
        "difficulty_level": "medium",
        "context": "The city of Tokyo is famous for its vibrant nightlife, delicious food, and ancient temples. However, the city is also known for its crowded streets and high cost of living. Many tourists visit Tokyo every year, but the city's residents are constantly struggling to find affordable housing and decent working conditions. In recent years, the city has taken steps to address these issues, including building new apartment complexes and implementing policies to support small businesses.",
        "question": "What might be the main reason why the city's residents are struggling to find affordable housing and decent working conditions, despite the city's efforts to address these issues?",
        "correct_answer": "The main reason might be the high demand for housing and jobs in the city, driven by its popularity among tourists and the growing number of new businesses and developments.",
        "explanation": "The correct answer requires the reader to think critically about the passage and make an inference. The passage mentions that the city is famous for its nightlife, food, and temples, which attracts many tourists. It also mentions that the city is building new apartment complexes and implementing policies to support small businesses. However, it also mentions that the residents are struggling to find affordable housing and decent working conditions. The reader can infer that the high demand for housing and jobs in the city, driven by its popularity among tourists and the growing number of new businesses and developments, might be the main reason for the residents' struggles.",
        "sample_user_answer": "Reason y resident struggle are expensive house",
        "content_accuracy": 1,
        "comprehension_score": 1,
        "clarity_score": 2,
        "language_mechanics_score": 3,
        "total_score": 7,
        "overall_feedback": "The user demonstrates limited understanding of the passage and provides a brief, incomplete answer that lacks detail and accuracy."
    },
    {
        "passage_id": "ravenswood_arts",
        "difficulty_level": "medium",
        "context": "The small town of Ravenswood was known for its vibrant arts scene. Every year, the town hosted a prestigious art festival, attracting visitors from all over the world. The festival was organized by the Ravenswood Arts Council, a non-profit organization that relied heavily on donations and sponsorships to fund its activities. Despite its financial struggles, the council had managed to maintain a strong reputation for its high-quality exhibitions and performances. However, this year's festival was facing its biggest challenge yet. The council's main sponsor, a local business tycoon, had announced that he would no longer be providing financial support, citing concerns over the festival's financial transparency.",
        "question": "What can be inferred about the relationship between the Ravenswood Arts Council and the local business tycoon, based on the information provided?",
        "correct_answer": "The business tycoon and the council were previously in a close and dependent relationship, but the tycoon's decision to withdraw sponsorship suggests that the relationship has become strained or even adversarial.",
        "explanation": "The passage implies that the business tycoon was a significant supporter of the festival, and his withdrawal of sponsorship is a significant blow to the council's finances. The fact that the tycoon cites concerns over the council's financial transparency as the reason for his decision suggests that there may be some underlying tension or conflict between the two parties. This inference is supported by the fact that the council, despite its financial struggles, had managed to maintain a strong reputation for its high-quality exhibitions and performances, implying that it may have been relying too heavily on the tycoon's support.",
        "sample_user_answer": "bizness man did not wants to pay for festival. so festival would not happen",
        "content_accuracy": 1,
        "comprehension_score": 1,
        "clarity_score": 2,
        "language_mechanics_score": 3,
        "total_score": 7,
        "overall_feedback": "The user's answer demonstrates a weak understanding of the passage and fails to accurately infer the relationship between the business tycoon and the Ravenswood Arts Council."
    },
    {
        "passage_id": "cherry_blossom_festival",
        "difficulty_level": "medium",
        "context": "The city of Tokyo is known for its vibrant atmosphere and rich cultural heritage. Every year, millions of tourists visit the city to experience its unique blend of traditional and modern attractions. One of the most popular festivals in Tokyo is the Cherry Blossom Festival, which takes place in late March. During this time, the city's parks and gardens are filled with thousands of blooming cherry blossom trees, creating a stunning display of pink and white flowers. Visitors can enjoy traditional Japanese food, drinks, and music while taking in the breathtaking views.",
        "question": "What might be a possible reason why the Cherry Blossom Festival in Tokyo is so popular among tourists, despite being held in late March, which is considered a relatively chilly month in Japan?",
        "correct_answer": "The festival is popular because of the unique combination of the blooming cherry blossom trees and the traditional Japanese culture and food, which create a unique and festive atmosphere.",
        "explanation": "The correct answer is that the festival is popular because of the unique combination of the blooming cherry blossom trees and the traditional Japanese culture and food, which create a unique and festive atmosphere. The passage suggests that the festival attracts millions of tourists every year, and the reason is not just the beauty of the cherry blossom trees, but also the opportunity to experience traditional Japanese culture and food. The passage mentions that visitors can enjoy 'traditional Japanese food, drinks, and music' during the festival, which implies that the festival offers a unique cultural experience that tourists are eager to take part in.",
        "sample_user_answer": "Cherry Blosom festival is popular even tho it is cold cos of lfowers and food and music",
        "content_accuracy": 2,
        "comprehension_score": 2,
        "clarity_score": 1,
        "language_mechanics_score": 1,
        "total_score": 6,
        "overall_feedback": "The user demonstrates limited understanding of the passage and struggles with expressing themselves clearly and accurately."
    }
]

# Path to your CSV file
csv_file_path = 'reading_comprehension_testset.csv'

# Add the new passages
add_passages_to_csv(csv_file_path, new_passages)