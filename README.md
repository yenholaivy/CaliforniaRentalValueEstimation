# California Rental Value Estimation

## Overview
According to 2019 Census American Community Survey (ACS) data, 45% of households in California were renters. As a renter myself, I am curious to know how the rental prices differ based on different apartments features (e.g. location, size). My goal is to build a model to predict rental values in California.

#### Data Collection
My data was scraped and parsed from apartments.com using BeautifulSoup, organized into a Pandas dataframe, and saved locally as a csv file. For details, see [apt_scraper.py](https://github.com/yenholaivy/CaliforniaRentalValueEstimation/blob/main/apt_scraper.py).

#### Data Cleaning
The final dataframe contains apartment listings from over 150 cities, 4,000 properties and 15,000 apartment listings. 

For data cleaning, I extracted and converted most features to binary features (e.g. Washer/Dryer) with 1 = Yes and 0 = No. I also converted numeric features specificed as a range to its average value (e.g. Rental Price). For details, see [apt_data_cleaning.py](https://github.com/yenholaivy/CaliforniaRentalValueEstimation/blob/main/apt_data_cleaning.py).

#### Features

|  Feature Name | Feature Type |
| ----- | ---- | 
| Rental Price | Numeric | 
| Number of Beds | Numeric | 
| Number of Baths | Numeric | 
| SQ-FT | Numeric | 
| City | Categorical | 
| Walkscore | Numeric | 
| Onsite Parking | Binary | 
| WiFi | Binary | 
| Washer/Dryer | Binary | 
| Minimum Lease Length | Numeric | 
| Number of Kitchen Features | Numeric | 
| Air Conditioning | Binary | 
| Elevator | Binary | 
| Pool | Binary | 
| Fitness Center | Binary | 
| Allow Pets | Binary | 
| Security System | Binary | 
| Furnished | Binary | 

## Data Analysis
For details, see [apt_analysis.ipynb](https://github.com/yenholaivy/CaliforniaRentalValueEstimation/blob/main/apt_analysis.ipynb).
As briefly mentioned in the Data Cleaning section, some of the numeric features were given as a range. In fact, half of the rental price were listed as a range (e.g. $1,200 - 1,500) instead of an exact number (e.g. $1,350). In order to make predictions, I converted all prices with ranges to their average value. For example: if the price is listed as $1,000 to $1,200, the price will be converted to $1,100. To validate this approach, I will be running the same model on both the whole dataset (with the range converted) and the dataset with only single values where I dropped all listings with a price range.

#### Rental Price Distribution
Looking at the rental price distributions, we can see that the shapes are quite similar between the whole dataset and the dataset with only single values. They are both right skewed, with the mean price around $3,100.

![alt text](https://github.com/yenholaivy/CaliforniaRentalValueEstimation/blob/main/img/rental_price_dist.png)

#### Cities
Even though there are more than 150 cities in the dataset, about 40% came from 5 cities. Below you can see that the top three cities are the same between the whole dataset and the dataset with only single values. Los Angeles, San Diego and San Francisco. So, instead of using all 150 cities, I converted these three cities to dummy variables and incorporate them in my prediction model.

![alt text](https://github.com/yenholaivy/CaliforniaRentalValueEstimation/blob/main/img/top5cities_all.png)
![alt text](https://github.com/yenholaivy/CaliforniaRentalValueEstimation/blob/main/img/top5cities_sv.png)

## Modeling
For my prediction model, I've tried linear regression, ridge regression, decision tree, random forest and gradient boosting. My baseline is to predict the mean price, and I evaluated each created model using the Root Mean Square Error (RMSE). For details, see [California_Rental_Price_Estimator.ipynb](https://github.com/yenholaivy/CaliforniaRentalValueEstimation/blob/main/California_Rental_Price_Estimator.ipynb).

#### Result
The results showed that random forest gave us the best prediction. For the training data, we were able to decrease the error from almost 1900 to 1100, which is about 42%. As for the data with only single value, results showed that the scores are much higher. One possible explanation for this is that the sample size is much smaller and so there might be more variance in the data. 

|  | Baseline | Linear Regression | Ridge Regression | Decision Tree | Random Forest | Gradient Boosting | 
| --- | --- | --- | --- |--- |--- |--- |
| All Data (Train) | 1872 | 1430 | 1433 | 1440 | 1096 | 1116 |
| All Data (Test) | 1786 | 1436 | 1436 | 1381 | 1012 |1017 |
| Data - Single Values (Test) | 2104 | 1569 | 1570 | 1530 | 1215 |1251|

## Conclusion & Next Steps
I was able to successfully created a prediction model that reduces RMSE by 42% compared to the baseline. However, there was inconclusive evidence to support the approach of averaging the prices. As of next steps, I will collect more data for longer period of time.

