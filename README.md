# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders usually combine many signals, such as what similar users liked, what features a song has, and what someone seems to want in the current moment. My simulation focuses on the content-based part of that idea: it compares the attributes of each song to a user's taste profile and gives higher scores to songs that are closer to the user's preferred vibe. In this version, I will prioritize transparent and explainable recommendations over complexity, so the system is designed to reward strong matches in genre, mood, and a few numeric audio features rather than trying to learn from large-scale user behavior.

This music recommender uses a point-based scoring algorithm to match songs to user preferences. The system loads songs from a CSV file, scores each song individually against the user's profile, ranks them by score, and returns the top recommendations.

### Algorithm Recipe

The recommendation system assigns points based on the following rules, designed for balance between genre (most important), mood, and energy:

1. **Genre Match (+2.0 points)**: If the song's genre exactly matches the user's favorite genre, add +2.0 points.
2. **Mood Match (+1.0 points)**: If the song's mood exactly matches the user's favorite mood, add +1.0 points.
3. **Energy Similarity (0.0 to +1.0 points)**: Calculate similarity as `1.0 - abs(song.energy - user.target_energy)`, then add that value as points (capped at 1.0).
4. **Acoustic Preference Bonus (+0.5 points)**: If the user likes acoustic music and the song's acousticness is >= 0.7, add +0.5 points.

**Total Score**: Sum of all points (range: 0.0 to 4.5). Songs are ranked by score descending, with ties broken by energy similarity.

**Potential Biases**: This system might over-prioritize genre matches, potentially ignoring great songs that strongly match the user's mood or energy but differ in genre. It also relies on exact string matches for genre and mood, which could miss nuanced similarities (e.g., "indie" vs. "alternative").

`Song` features used in this simulation:

- `title`
- `artist`
- `genre`
- `mood`
- `energy`
- `tempo_bpm`
- `valence`
- `danceability`
- `acousticness`

`UserProfile` features used in this simulation:

- preferred `genre`
- preferred `mood`
- preferred `energy`
- preferred `tempo_bpm`
- preferred `valence`
- preferred `danceability`
- preferred `acousticness`

### Example Output

The screenshot below shows the recommender loading the dataset and printing the top song recommendations with their scores and explanation strings.

![Terminal output showing top song recommendations](./images/recommender-output.png)

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:

- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:

- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:

- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"
```
