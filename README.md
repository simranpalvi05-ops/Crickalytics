<div align="center">



<h1>🏏 Crickalytics</h1>
<h3>ODI Cricket Analytics Dashboard</h3>

<p>An interactive dashboard to explore player, team, match and partnership insights from <b>4,700+ One Day International matches (1972–2023)</b>.</p>

<img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
<img src="https://img.shields.io/badge/Plotly-Charts-3F4F75?logo=plotly&logoColor=white" alt="Plotly">
<img src="https://img.shields.io/badge/Pandas-Data-150458?logo=pandas&logoColor=white" alt="Pandas">

<br><br>

<img src="https://github.com/user-attachments/assets/e7412625-8749-4bb1-ba82-efe80c378ed2" width="100%" alt="Crickalytics banner">

<br><br>

<a href="#-overview">Overview</a> •
<a href="#-features">Features</a> •
<a href="#-installation-and-setup">Installation</a> •
<a href="#-screenshots">Screenshots</a> •
<a href="#-author">Author</a>

</div>


## 📖 Overview

Cricket produces a huge amount of data, but raw scorecards are hard to read. **Crickalytics** cleans and combines ODI match data (batting, bowling, fall of wickets, partnerships and player details) and presents it through an interactive Streamlit dashboard.


**What you can explore**
- How a batter or bowler performs against different oppositions
- How teams compare across match phases (powerplay, middle overs, death overs)
- Which batting pairs have been the most productive
- Quick answers about ODI cricket through an AI chatbot

### 📊 Dashboard at a glance

| Matches analysed | Players found | Wickets recorded | Period covered |
|:---:|:---:|:---:|:---:|
| **4,739** | **2,820** | **61,386** | **1972 – 2023** |

---

## ✨ Features

<details open>
<summary><b>🤖 Chatbot</b></summary>

- AI cricket assistant for questions about ODI players, records and stats
- Chat history kept during the session, with a **Clear Chat** button
- Powered by an LLM endpoint through RapidAPI (key stored privately in `.env`)

</details>

<details>
<summary><b>🏠 Home</b></summary>

- Purpose of the dashboard and overview of the datasets
- Preview tables: Final Match Summary, Fall of Wickets, Player Info, Partnerships, Bowling Summary and Batting Summary

</details>

<details>
<summary><b>👤 Player Analysis</b></summary>

- **Bowler deep dive:** wickets against each opposition and economy-rate consistency (box plot)
- **Death-overs analysis** for bowlers
- **Batting performance:** runs progression (line chart) and boundary breakdown (pie chart)
- **Batting and dismissal:** wicket number at which the batter fell
- **Top 10 batting partners** for a selected batter

</details>

<details>
<summary><b>🌍 Team Analysis</b></summary>

- **Global wicket-takers map** (world choropleth)
- **Team comparison** across wickets and partnerships
- **Match-phase performance:** wickets and economy by phase of the innings
- **Detailed team phase analysis** with pie and bar charts
- **Head-to-head analysis** between two teams

</details>

<details>
<summary><b>📊 Match Analysis</b></summary>

- Fall of wickets and partnership progression for a selected match
- Partnership breakdown for each innings
- Bowler performance in the match

</details>

<details>
<summary><b>🤝 Partnership Analysis</b></summary>

- Top highest individual partnerships (choose how many to display)
- Most successful and most prolific batting pairs
- Partnership run-rate analysis (balls faced vs runs scored, filterable by team)

</details>

---

## 🛠 Tech Stack

| Area | Tools |
|------|-------|
| Language | Python |
| Data handling | Pandas, NumPy |
| Dashboard | Streamlit |
| Charts | Plotly Express, Plotly Graph Objects, Streamlit-ECharts |
| UI extras | Streamlit Option Menu, Streamlit Lottie |
| AI chatbot | RapidAPI (LLM endpoint), Requests |
| Configuration | python-dotenv |
| Exploration and cleaning | Jupyter Notebook, Matplotlib, Seaborn |

---

## 🔄 Project Workflow

1. **Data acquisition:** ODI data collected as CSV files from Kaggle and ESPNcricinfo StatsGuru
2. **Data cleaning (Pandas):** handled missing values and duplicates, fixed data types, converted dates, standardised player and team names
3. **Exploratory data analysis:** summary statistics, grouping and aggregation by player, team, venue and match phase
4. **Visualisation:** interactive Plotly charts for every analysis
5. **Dashboard:** multi-tab Streamlit app with filters, caching and a chatbot

---

## 📁 Project Structure

```
Crickalytics/
│
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── .gitignore                    # Keeps .env and cache files out of GitHub
│
├── bowling_clean.csv             # Cleaned bowling data
├── fow_clean.csv                 # Cleaned fall-of-wickets data
├── partnership_clean.csv         # Cleaned partnership data
├── player_info_clean.csv         # Player details
├── player_batting_summary.csv    # Batting summary per player
├── Final_match_summary.csv       # Match-level summary
└── ODI_Match_Data.csv            # Match data used for batting analysis
```

> `.env` (your private API key) is **not** stored in the repository.

---

## 📂 Datasets

| File | What it contains |
|------|------------------|
| `bowling_clean.csv` | Bowling figures (wickets, economy, opposition, match phase) |
| `fow_clean.csv` | Fall-of-wickets records |
| `partnership_clean.csv` | Batting partnerships (players, runs, balls) |
| `player_info_clean.csv` | Player names and details |
| `player_batting_summary.csv` | Aggregated batting statistics |
| `Final_match_summary.csv` | Match-level results |
| `ODI_Match_Data.csv` | Detailed ODI match data |

**Data sources:** open cricket datasets from [Kaggle](https://www.kaggle.com) and [ESPNcricinfo StatsGuru](https://stats.espncricinfo.com), cleaned and processed with Pandas. The data belongs to its original sources and is used here for learning and analysis.

---

## ⚙️ Installation and Setup

**Prerequisites:** Python 3.9+, pip, Git

**1. Clone the repository**
```bash
git clone https://github.com/simranpalvi05-ops/Crickalytics.git
cd Crickalytics
```

**2. (Recommended) Create a virtual environment**
```bash
python -m venv venv
```
Activate it:
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

**3. Install the dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the app**
```bash
streamlit run app.py
```
The dashboard opens in your browser, usually at `http://localhost:8501`.

---

## 🔑 Chatbot Setup (Optional)

The dashboard works fully without the chatbot. To enable the **Chatbot** tab:

1. Get an API key from [RapidAPI](https://rapidapi.com/) for the LLM endpoint used in the app.
2. In the project folder, create a file named `.env`.
3. Add this line:
   ```
   RAPIDAPI_KEY=your_api_key_here
   ```
4. Restart the app.

If the key is missing, the Chatbot tab shows a setup message and every other tab still works.

⚠️ **Never upload your `.env` file to GitHub.** It is already listed in `.gitignore`.

---

## 📸 Screenshots

### 🤖 Chatbot
Ask questions about ODI players and records.

<img width="800" alt="Chatbot" src="https://github.com/user-attachments/assets/807c84f4-cc15-4fea-ae2b-2eda4066d01b" />


### 🏠 Home
Dataset overview and dashboard purpose.


<img width="800" alt="Chatbot" src="https://github.com/user-attachments/assets/f0722cdf-4fe2-4807-9fc6-1db53c088386" />

## 🚧 Limitations

- Data is static (CSV files), so it does not update after new matches
- The analysis is descriptive; no machine learning prediction models are included
- The chatbot answers from a general LLM, not directly from the dashboard datasets

---

## 🚀 Future Improvements

- Live data through a cricket API and auto-updating dashboards
- Match outcome and player performance prediction using machine learning
- Ground the chatbot in the dashboard datasets
- Add T20 and Test formats for cross-format comparison
- Deploy online with Streamlit Community Cloud

---

## 👩‍💻 Author

**Simran**
BTech IT Student | Data Science and Machine Learning enthusiast

🔗 [LinkedIn](https://www.linkedin.com/in/simran-78a04032b/) • 💻 [GitHub](https://github.com/simranpalvi05-ops)

---

<div align="center">⭐ If you found this project useful, consider giving the repo a star!</div>
