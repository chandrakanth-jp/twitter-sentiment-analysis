# twitter-sentiment-analysis
Twitter sentiment analysis application using Kafka, Hugging Face, MongoDB Atlas, Streamlit, containerized with Docker.

## Pipeline
![Architecture](/images/streampipeline.png)

## Streamlit dashboard
![Streamlit dashboard](/images/streamlit_dashboard.PNG)

## Components
The main components of this project include:
- Tweepy library
- Hugging Face Transformers library (we use the RoBERTa model, a transformer based pre-trained network, finetuned for sentiment analysis)
- MongoDB Atlas
- Streamlit
- Docker

## Prerequisites
- MongoDB Atlas account and connection string https://www.mongodb.com/cloud/atlas/register
- Twitter API key https://developer.twitter.com/en/docs/twitter-api
- Docker 

## Installation
1. Clone the repo
```
git clone https://github.com/chandrakanth-jp/twitter-stream-analysis.git
```
2. Configure .env files in 'consumer' and 'streamlit' with MongoDB connection string and Twitter API key and token.

4. Build the docker images and start the containers using the docker compose command
```
docker-compose up
```
