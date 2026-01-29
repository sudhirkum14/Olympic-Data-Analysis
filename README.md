# 🏅 Olympics Data Analysis Dashboard

An interactive Streamlit web application for analyzing historical Olympic Games data spanning over 120 years. Explore medal statistics, athlete performance, gender participation trends, and fascinating Olympic records.

## Data Source

The application uses two datasets:
- **athlete_events.csv**: Contains historical records of athletes, their participation, and medal achievements
- **noc_regions.csv**: Maps NOC (National Olympic Committee) codes to country names and regions

## Data Processing

The application includes comprehensive data preprocessing:
- Merging athlete data with regional/country information
- Removing duplicate records
- Handling missing values (imputing age, height, and weight with mean values)
- One-hot encoding medal types (Gold, Silver, Bronze)
- Deduplication of team events to avoid double-counting medals

## Navigation

Use the sidebar menu to switch between different analysis sections:
1. **Medal Tally** - Global medal distribution by year
2. **Overall Analysis** - Historical Olympic statistics
3. **Country Analysis** - Host advantage and sport-specific performance
4. **Country-wise Analysis** - Individual country medal trends
5. **India Special Focus** - Dedicated analysis for India's Olympic performance
6. **Olympic Records & Fun Facts** - Record-breaking athletes
7. **Athlete-wise Analysis** - Top performers by sport
8. **Gender Analysis** - Gender participation and medal statistics
9. **Athlete Physical Stats** - Physical attributes of medal winners


## Author Notes

This project provides a comprehensive analysis of Olympic Games data, enabling users to uncover patterns, trends, and records from over a century of Olympic history.

---

**Built with** ❤️ using Streamlit, Pandas, and Plotly
# Olympic-Data-Analysis
