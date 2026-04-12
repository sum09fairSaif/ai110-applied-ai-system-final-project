# Model Card: VibeMatch 1.0

## Model Name

VibeMatch 1.0

---

## Goal / Task

This recommender suggests songs from a small catalog based on a user's taste profile. It tries to find songs that match the user's favorite genre, favorite mood, and target energy level. It also gives a small bonus to acoustic songs for users who like acoustic music.

---

## Data Used

The dataset has 25 songs in `data/songs.csv`. Each song includes `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness`. The data covers many genres and moods, but it is still very small. It does not include lyrics, language, culture, listening history, or real user feedback.

---

## Algorithm Summary

The system gives points to each song based on how well it matches the user profile. A song gets points for matching the user's genre and mood. It also gets a similarity score for how close its energy is to the user's target energy. If the user likes acoustic music, songs with high acousticness get a small extra bonus. After that, the songs are sorted from highest score to lowest score.

---

## Observed Behavior / Biases

One pattern I noticed is that energy has a strong effect because every song receives an energy score. Genre and mood only help when there is an exact text match, so users with broader or more mixed tastes may not be represented well. This can create an "energy bubble" where songs with similar energy keep rising even if they are not the best musical fit. I also noticed that `Gym Hero` often ranked highly because its energy was close to several user profiles.

---

## Evaluation Process

I tested the recommender with eight user profiles, including High-Energy Pop, Chill Lofi, Deep Intense Rock, and some edge cases. I ran the CLI and compared the top results to my own musical intuition. I also changed the scoring weights to see how sensitive the rankings were. One surprising result was that `Gym Hero` showed up for several profiles that did not clearly want intense pop, which showed me that energy was sometimes doing too much work.

---

## Intended Use and Non-Intended Use

This system is meant for classroom learning and simple experimentation. It is useful for showing how a content-based recommender can turn user preferences into ranked song suggestions. It is not meant for real users, music streaming platforms, or high-stakes decisions. It should not be treated as a complete or fair model of real musical taste.

---

## Ideas for Improvement

- Add more user preference fields, such as tempo, valence, or danceability.
- Use softer matching for related genres and moods instead of exact text matches only.
- Improve diversity so the top recommendations are not all from one narrow vibe.

---

## Personal Reflection

My biggest learning moment was seeing how a very simple scoring rule could still produce results that felt surprisingly believable. It showed me that recommendations do not need to be very complex before users start feeling like the system "understands" them. AI tools helped me move faster when I was writing, testing ideas, and explaining my design, but I still had to double-check the scoring logic, file changes, and README details to make sure they matched what the code actually did. I was also surprised that a song like `Gym Hero` could keep showing up for different profiles, which taught me how even a small weight choice can create bias or repetition. If I kept extending this project, I would try adding more features, softer category matching, and a diversity rule so the recommendations feel less repetitive.
