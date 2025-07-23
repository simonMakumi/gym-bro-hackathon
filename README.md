# GYM BRO 🦾 - Your AI Personal Trainer
**My entry for the Google - The Gemma 3n Impact Challenge.**

GYM BRO is a private, on-device AI personal trainer built to make fitness accessible to everyone. It leverages the power of Gemma 3n running locally via Ollama to provide personalized workout plans, real-time form correction, and goal-oriented motivation, all without needing an internet connection.

[![GYM BRO Demo](https://img.youtube.com/vi/YOUTUBE_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=YOUTUBE_VIDEO_ID)

---
## 🌟 The Problem We Solve (Impact & Vision)
Staying fit is essential, but it's not always easy. Gym memberships are expensive, personal trainers are a luxury, and working out at home often leads to poor form, risk of injury, and a lack of motivation.

GYM BRO tackles this challenge by providing the core benefits of a personal trainer in an app that is:
* **Private & Offline-First:** Because Gemma 3n runs locally, your workout data never leaves your device. It works perfectly in low-connectivity areas.
* **Accessible:** It removes the financial barrier to personalized fitness guidance.
* **Effective:** Real-time form correction helps users perform exercises correctly and safely, while AI-driven motivation keeps them engaged.

Our vision is to empower millions of people to take control of their health and wellness with a coach that's always available, always private, and always focused on their success.

---
## ✨ Key Features
* **AI Workout Planner:** Generates personalized, 3-exercise bodyweight routines based on user goals (e.g., "build muscle", "lose weight") using Gemma 3n.
* **Live AI Coaching:** Uses your device's camera, OpenCV, and MediaPipe to provide real-time form correction and rep counting for exercises like Squats, Push-ups, Lunges, and more.
* **AI-Generated Voice Feedback:** Gives audio cues for rep counts and motivational phrases using gTTS.
* **Personalized AI Motivation:** After each set, Gemma 3n generates a unique motivational message that connects the exercise to the user's specific goal.
* **AI Nutrition Tips:** Provides high-level nutritional advice tailored to the user's stats and goals.
* **Progress Tracking:** Includes a dashboard to log daily habits (water, steps) and a history of completed workouts to track consistency.

---
## 🛠️ Technical Writeup & Architecture
This project was engineered to showcase the unique capabilities of Gemma 3n for creating impactful, on-device AI applications.

### The Technology Stack
* **AI Model:** Google's **Gemma 3n (gemma:2b)**, running locally via **Ollama**.
* **Application Framework:** **Streamlit** for the interactive user interface.
* **Computer Vision:** **OpenCV** for camera access and **MediaPipe** for highly efficient, real-time pose estimation.
* **Text-to-Speech:** **gTTS** for generating audio feedback.
* **Core Language:** **Python**

### How We Use Gemma 3n
Gemma 3n is the "brain" of GYM BRO, and its on-device nature is critical to the app's privacy-first approach. We leverage it in three key ways:

1.  **Workout Plan Generation (`planner.py`):** When a user enters their goal, we send a structured prompt to Gemma, asking it to create a 3-exercise routine by selecting ONLY from a list of exercises the app knows how to track. By specifying the output format as JSON, we get structured data back that the app can immediately use.
2.  **Nutrition Advice (`planner.py`):** We provide Gemma with the user's stats (age, weight, height) and goal, and ask for a simple, one-paragraph nutritional tip. This demonstrates Gemma's ability to synthesize information to provide helpful, contextual advice.
3.  **Real-time Motivation (`app.py`):** This is where Gemma's speed and efficiency shine. After a user completes a set, we give Gemma the context—the exercise performed, the reps completed, and the user's main goal—and ask for a short, encouraging sentence. The ability to do this quickly and offline is a game-changer for user engagement.

### Challenges Overcome
The main challenge was ensuring a smooth, real-time user experience. The initial implementation had a noticeable lag when generating AI motivation between sets. We solved this by adding an immediate audio cue ("Great set! Time to rest.") to fill the "dead air" while Gemma processed the request in the background. This small change dramatically improved the perceived performance and flow of the workout.

---
## 🚀 How to Run GYM BRO
To run this project, you need Python, Ollama, and the required packages.

**1. Prerequisites:**
* Install **Python 3.9+**.
* Install **Ollama** from [ollama.com](https://ollama.com) and ensure it is running.

**2. Setup:**
```bash
# Clone the repository
git clone [https://github.com/simonMakumi/gym-bro-hackathon.git](https://github.com/simonMakumi/gym-bro-hackathon.git)
cd gym-bro-hackathon

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Pull the Gemma model
ollama pull gemma:2b

```
**3. Run the App:**

```bash
# On terminal run:

streamlit run app.py
```

Open your browser to the local URL provided by Streamlit, and start your workout!