# MSTSearch

![Workflow](https://img.shields.io/github/workflow/status/PStarH/MSTSearch/CI)
![License](https://img.shields.io/github/license/PStarH/MSTSearch)
![Stars](https://img.shields.io/github/stars/PStarH/MSTSearch?style=social)

MSTSearch is a comprehensive search aggregation platform that crawls multiple search engines, processes and ranks the results based on various metrics, and leverages AI to provide insightful summaries and answers to user queries. Built with a Python backend and a Vue.js frontend, MSTSearch offers a seamless and efficient search experience.

## 📖 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Installation](#installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Usage](#usage)
- [Future Plans](#future-plans)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## ✨ Features

- **Multi-Engine Crawling:** Scrapes search results from Baidu, Sohu, and other search engines.
- **Result Processing:** Cleans and normalizes search results for consistency.
- **Scoring Mechanisms:** Utilizes BM25, TF-IDF, and Word2Vec for ranking search results.
- **AI-Powered Summarization:** Uses AI models to summarize and answer user questions based on search data.
- **Responsive Frontend:** Built with Vue.js, offering a user-friendly interface for searching and viewing results.
- **Settings Management:** Allows users to add or remove search engines dynamically.
- **Caching & Rate Limiting:** Ensures efficient performance and protects against abuse.

## 🛠 Tech Stack

### Backend

- **Python 3.8+**
- **Flask:** Web framework for API endpoints.
- **Selenium:** Automates browser interactions for crawling.
- **BeautifulSoup:** Parses HTML content.
- **Gensim:** Implements Word2Vec for semantic analysis.
- **Scikit-learn:** Provides TF-IDF vectorizer and cosine similarity metrics.
- **Rank BM25:** Implements BM25 ranking algorithm.
- **Concurrent Futures:** Handles parallel processing.
- **Flask-Limiter:** Implements rate limiting.
- **Flask-Caching:** Caches responses for improved performance.

### Frontend

- **Vue.js 3:** JavaScript framework for building user interfaces.
- **Vuex:** State management pattern + library for Vue.js.
- **Tailwind CSS:** Utility-first CSS framework for styling.
- **Axios:** HTTP client for API requests.

### Others

- **ChromeDriver:** Automates Chrome browser for scraping.
- **Webdriver Manager:** Manages browser driver binaries.

## 🏗 Architecture

MSTSearch follows a client-server architecture where the frontend communicates with the backend via RESTful APIs. The backend handles search crawling, result processing, scoring, and AI-driven summarization. The frontend provides an intuitive interface for users to perform searches, view results, and interact with AI summaries.

## 🚀 Installation

### Backend Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/MSTSearch.git
   cd MSTSearch/backend
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup ChromeDriver**

   The backend uses Selenium for crawling, which requires ChromeDriver.

   - **Automatic Installation:**
     
     Ensure `webdriver_manager` is included in `requirements.txt`. The `BaiduCrawler.py` and `SohuCrawler.py` scripts handle driver installation automatically.

   - **Manual Installation:**
     
     Download ChromeDriver from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads) and place it in the `./driver` directory.

5. **Configuration**

   - **Environment Variables:**
     
     Create a `.env` file in the `backend` directory and add necessary environment variables like API keys.

     ```env
     AI_API_KEY=your_api_key_here
     ```

6. **Run the Backend Server**

   ```bash
   python app.py
   ```

   The backend server will start on `http://127.0.0.1:5000`.

### Frontend Setup

1. **Navigate to Frontend Directory**

   ```bash
   cd ../frontend
   ```

2. **Install Dependencies**

   ```bash
   npm install
   ```

3. **Run the Frontend Server**

   ```bash
   npm run serve
   ```

   The frontend application will start on `http://localhost:8080`.

## 🎯 Usage

1. **Access the Application**

   Open your browser and navigate to `http://localhost:8080`.

2. **Perform a Search**

   - Enter your search query in the search bar.
   - Click the **Search** button.
   - View aggregated and ranked search results from multiple search engines.

3. **View Summary**

   - After performing a search, input a question related to the search results.
   - The AI will provide a summarized answer based on the top-ranked results.

4. **Manage Search Engines**

   - Navigate to the **Settings** page.
   - Add or remove search engines by providing their URLs.
   - The system dynamically adjusts to include the specified search engines in future searches.

## 🚀 Future Plans

MSTSearch is continually evolving to enhance user experience and functionality. Upcoming features include:

- **Cookie Management:**
  
  - **Purpose:** To maintain session states and handle authentication where necessary.
  - **Benefits:** Improved crawling efficiency, reduced likelihood of being blocked by search engines, and enhanced ability to access personalized or restricted content.
  - **Implementation:** Integrate cookie handling mechanisms within the crawlers to store and reuse cookies during crawling sessions.

- **History-Based Sorting:**
  
  - **Purpose:** To personalize search result rankings based on user interaction history.
  - **Benefits:** Provides users with more relevant and tailored search results, enhancing the overall search experience.
  - **Implementation:** 
    - **Data Collection:** Track and store user interactions, such as clicked links and time spent on result pages.
    - **Algorithm Development:** Develop algorithms that analyze historical data to influence the ranking of current search results.
    - **Integration:** Modify the ranking system to incorporate history-based metrics alongside existing scoring mechanisms like BM25 and TF-IDF.

- **Enhanced AI Summarization:**
  
  - **Purpose:** To provide more accurate and context-aware summaries and answers.
  - **Benefits:** Offers users clearer and more concise information derived from aggregated search results.
  - **Implementation:** Explore and integrate advanced AI models and fine-tune existing models for better performance.

- **User Authentication and Profiles:**
  
  - **Purpose:** To allow users to create accounts and manage their preferences.
  - **Benefits:** Enables personalized experiences, such as saving search history and customizing settings.
  - **Implementation:** Implement authentication systems and profile management features in both backend and frontend.

- **Mobile Optimization:**
  
  - **Purpose:** To ensure seamless access and usability on mobile devices.
  - **Benefits:** Expands accessibility and provides users with flexibility to use MSTSearch on the go.
  - **Implementation:** Optimize the frontend design for responsive layouts and improve performance on mobile platforms.

- **API Enhancements:**
  
  - **Purpose:** To provide more robust and flexible API endpoints for integration with other services.
  - **Benefits:** Facilitates broader usage scenarios and allows third-party integrations.
  - **Implementation:** Develop additional API endpoints and comprehensive documentation for developers.

## 📂 Project Structure

MSTSearch/
├── backend/
│ ├── app.py
│ ├── BaiduCrawler.py
│ ├── SohuCrawler.py
│ ├── crawler.py
│ ├── sort.py
│ ├── summarize.py
│ ├── process_result.py
│ ├── requirements.txt
│ └── driver/
├── frontend/
│ ├── src/
│ │ ├── views/
│ │ │ ├── SearchPage.vue
│ │ │ └── ResultPage.vue
│ │ ├── store/
│ │ │ └── index.ts
│ │ └── components/
│ ├── public/
│ ├── package.json
│ └── tailwind.config.js
├── README.md
└── LICENSE


- **backend/**: Contains all backend-related code, including crawlers, sorting mechanisms, and AI summarization.
- **frontend/**: Contains the Vue.js frontend application.
- **driver/**: Stores browser driver binaries like ChromeDriver.
- **requirements.txt**: Lists Python dependencies.
- **package.json**: Lists frontend dependencies.

## 🗺 Future Plans

We are committed to continuously enhancing MSTSearch to provide a more personalized and efficient search experience. Our upcoming features include:

### 🍪 Cookie Management

- **Advanced Session Handling:** Implement cookie management to maintain user sessions across different browsing activities.
- **Personalized Search Results:** Utilize stored cookies to tailor search results based on user preferences and past interactions.
- **Enhanced Privacy Controls:** Allow users to manage cookie settings, ensuring their privacy is respected while still offering personalized experiences.

### 📜 History-Based Sorting

- **Search History Integration:** Incorporate user search history to prioritize and rank search results that align with previously expressed interests.
- **Dynamic Ranking Algorithms:** Develop algorithms that adapt the ranking of search results based on the evolution of user behavior over time.
- **User Feedback Loops:** Enable users to provide feedback on search results, allowing the system to learn and improve its sorting mechanisms continuously.

### 🔄 Continuous Improvements

- **Scalability Enhancements:** Optimize the backend to handle larger volumes of search queries and results more efficiently.
- **UI/UX Refinements:** Continuously improve the frontend interface based on user feedback to ensure an intuitive and seamless experience.
- **Integration of Additional AI Models:** Expand the range of AI models supported for more diverse and accurate summarizations and answers.

These features aim to make MSTSearch not only a powerful search aggregation tool but also a personalized assistant that evolves with your needs.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add some feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

## 📜 License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software as per the license terms.

## 📫 Contact

For any inquiries or feedback, please contact s22360.pan@stu.scie.com/cn.

---

Made with ❤️ by [Your Name](https://github.com/PStarH)
