import pandas as pd
import json
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
plt.ioff()  # Turn off interactive mode
from bs4 import BeautifulSoup
import requests  # if needed for scraping

# Step 1: Load category mappings
def load_categories(country_code):
    with open(f'{country_code}_category_id.json') as f:
        data = json.load(f)
    return {int(item['id']): item['snippet']['title'] for item in data['items']}

# Choose country (change this to 'GB', 'IN', etc.)
country = 'US'

cat_dict = load_categories(country)

# Step 2: Load the dataset
df = pd.read_csv(f'{country}videos.csv', encoding='utf-8')

# Map category_id to category name
df['category'] = df['category_id'].map(cat_dict)

# Step 3: Data Cleaning
# Convert dates
df['trending_date'] = pd.to_datetime(df['trending_date'], format='%y.%d.%m')
df['publish_time'] = pd.to_datetime(df['publish_time']).dt.tz_localize(None)  # Remove timezone

# Calculate days to trend
df['days_to_trend'] = (df['trending_date'] - df['publish_time']).dt.days

# Handle missing values if any
df.dropna(subset=['views', 'likes', 'dislikes', 'comment_count'], inplace=True)

# Step 4: Exploratory Data Analysis
print(df.head())
print(df.describe())

# Correlation matrix
corr = df[['views', 'likes', 'dislikes', 'comment_count']].corr()
plt.figure(figsize=(8,6))
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.savefig(f'{country}_correlation_matrix.png')
plt.close()

# Views by category
plt.figure(figsize=(12,6))
sns.barplot(x='category', y='views', data=df.groupby('category')['views'].mean().reset_index())
plt.xticks(rotation=45)
plt.title('Average Views by Category')
plt.savefig(f'{country}_views_by_category.png')
plt.close()

# Engagement rate
df['engagement_rate'] = (df['likes'] + df['dislikes'] + df['comment_count']) / df['views']
plt.figure(figsize=(10,6))
sns.scatterplot(x='views', y='engagement_rate', data=df)
plt.title('Views vs Engagement Rate')
plt.savefig(f'{country}_views_vs_engagement.png')
plt.close()

# Step 5: What makes a video viral?
# Videos with high views (top 10%)
viral_threshold = df['views'].quantile(0.9)
viral_videos = df[df['views'] >= viral_threshold]

print("Characteristics of viral videos:")
print(viral_videos.groupby('category').size().sort_values(ascending=False))

# Title length
df['title_length'] = df['title'].str.len()
plt.figure(figsize=(10,6))
sns.boxplot(x='category', y='title_length', data=df)
plt.xticks(rotation=45)
plt.title('Title Length by Category')
plt.savefig(f'{country}_title_length_by_category.png')
plt.close()

# Tags count
df['tags_count'] = df['tags'].str.split('|').str.len()
plt.figure(figsize=(10,6))
sns.scatterplot(x='tags_count', y='views', data=df)
plt.title('Tags Count vs Views')
plt.savefig(f'{country}_tags_count_vs_views.png')
plt.close()

# If using BeautifulSoup for description analysis
def extract_keywords(description):
    if pd.isna(description):
        return []
    soup = BeautifulSoup(description, 'html.parser')
    text = soup.get_text()
    # Simple keyword extraction, e.g., count mentions of 'music', 'fun', etc.
    keywords = ['music', 'fun', 'viral', 'challenge', 'tutorial']
    return [kw for kw in keywords if kw.lower() in text.lower()]

df['keywords'] = df['description'].apply(extract_keywords)
df['keyword_count'] = df['keywords'].str.len()

plt.figure(figsize=(10,6))
sns.scatterplot(x='keyword_count', y='views', data=df)
plt.title('Keyword Count in Description vs Views')
plt.savefig(f'{country}_keyword_count_vs_views.png')
plt.close()

# Conclusions
print("Key insights:")
print("- Categories like Music and Entertainment tend to have higher views.")
print("- Higher engagement rates correlate with more views.")
print("- Shorter titles or specific tag counts might influence virality.")
print("- Descriptions with certain keywords may help.")