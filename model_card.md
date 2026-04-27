# Model Card: MusixxMatch 1.0

## Model Name
MusixxMatch 1.0

## Goal / Task
MusixxMatch recommends songs from a structured catalog based on a listener profile. It is designed to match user preferences across genre, mood, energy, acoustic preference, popularity, era, mood tags, vocal presence, and replay value. The system also provides explanations, confidence scores, warnings, and self-critique notes to make its output easier to interpret and evaluate.

## Model Type
MusixxMatch is an explainable, rules-based recommendation system rather than a generative model or a fine-tuned neural network. It combines:
- profile-based scoring
- diversity-aware reranking
- confidence estimation
- warning generation
- a self-critique review loop

## Data Used
The dataset contains 25 songs in [data/songs.csv](/c:/Users/saifs/ai110-applied-ai-system-final-project/data/songs.csv:1). Each song includes structured fields such as:
- `title`
- `artist`
- `genre`
- `mood`
- `energy`
- `tempo_bpm`
- `valence`
- `danceability`
- `acousticness`
- `popularity_0_100`
- `release_decade`
- `mood_tags`
- `instrumentalness`
- `vocal_presence`
- `replay_value`

The catalog is intentionally small and classroom-friendly, which makes the system easier to inspect but also limits its realism and coverage.

## How the System Works
1. User preferences are validated and normalized.
2. Missing preference details are partly inferred from known genre and mood patterns.
3. Each song is scored against the listener profile using interpretable weighted rules.
4. A diversity reranker reduces repetition from the same artist or genre.
5. Confidence is estimated from the score strength relative to the active scoring mode.
6. Warnings are added for weak or indirect matches.
7. A self-critique loop reviews the full list and can attach critique notes or adjust the ordering.

## Intended Use
MusixxMatch is intended for classroom learning, experimentation, and portfolio demonstration. It is useful for showing how an applied AI system can combine recommendation logic with guardrails, evaluation, logging, and post-hoc critique.

## Out-of-Scope Use
This system is not intended for production music platforms, commercial recommendation pipelines, or any high-stakes setting. It should not be treated as a complete or fair representation of real musical taste, and it does not use large-scale user behavior or cultural context.

## Strengths
- Transparent scoring logic makes the recommendations explainable.
- Reliability features such as confidence scoring and warnings make weak cases easier to detect.
- Logging and evaluation support reproducibility and traceability.
- The self-critique loop adds an agentic second pass over the recommendation list.
- The Streamlit app makes the system accessible to non-technical users.

## Limitations and Biases
- The catalog is small, so recommendation quality is constrained by limited coverage.
- The system depends heavily on exact genre and mood labels, which can oversimplify music taste.
- Hand-designed weights reflect my assumptions about what matters most, which introduces design bias.
- The recommender does not use lyrics, language, listening history, or collaborative filtering signals.
- Some recommendation lists may look plausible even when they rely mainly on soft feature similarity rather than direct preference matches.

## Evaluation
MusixxMatch was evaluated using:
- automated unit tests
- recommendation logging
- confidence scoring
- warnings for weak matches
- a dedicated evaluation harness over 8 predefined listener profiles

Current evaluation summary:
- profiles evaluated: `8`
- average confidence: `0.58`
- average low-confidence rate: `0.28`
- average warning rate: `0.75`
- average genre diversity: `0.88`
- average exact-match rate: `0.53`
- strongest profile: `Perfect Match with Acoustic`
- weakest profile: `Conflicting High-Energy Moody`

These results show that the system works best for clear preferences that are well represented in the catalog and struggles more when the profile is internally conflicting or only weakly supported by the available songs.

## Risk Mitigations
To reduce misuse or overconfidence, the system includes:
- input validation and guardrails
- confidence scoring
- low-confidence warnings
- critique notes for weak or repetitive lists
- JSONL session logging
- clear documentation of limitations

## Future Improvements
- add softer matching between related genres and moods
- expand the song catalog
- include richer preference signals such as tempo preferences or learned embeddings
- improve the critique loop to reason about more nuanced recommendation failures

## Personal Reflection
The most important lesson from building MusixxMatch was that reliability features can change the meaning of a recommendation system just as much as the ranking logic itself. Explanations, warnings, confidence scores, and evaluation made the final system much more trustworthy and much more aligned with responsible AI design.
