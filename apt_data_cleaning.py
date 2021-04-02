import pandas as pd
import numpy as np
import re

# Load the data
filepath = '/Users/ivylai/Desktop/Galvanize/apt_scraper/master_file0329.xlsx'
data = pd.read_excel(filepath)

# Drop the uneeded features
data = data.drop(columns = ['Unnamed: 0', 'Unnamed: 0.1', 'Unnamed: 0.1.1', 'Unnamed: 0.1.1.1', 'Student Features',
       'Cities', 'Neighborhoods', 'ZIP Codes', 'Beds', 'Property Style',
       'Amenity', 'Specialty', 'Price'])

# Standardize the 'city' feature
data['city'] = data['city'].str.title()

# Convert 'bed', 'bath', and 'walkscore' to numeric
data['n_bed'] = data['bed'].transform(lambda x: 0 if str(x) == 'Studio' else int(str(x)[0]))
data['n_bath'] = data['bath'].transform(lambda x: float(str(x).replace(" bath", "").replace("s", "")))
data['walkscore'] = data['walkscore'].apply(lambda x: int(x) if x != '-' else x)
avg = np.mean(data['walkscore'][data['walkscore'] != '-']) # replace the '-' value with the mean
data['walkscore'] = data['walkscore'].apply(lambda x: avg if x == '-' else x)

# Clean up the 'sq_ft' feature. In the case of sq_ft being a range instead of a number, take the average of the min and max.
data['sq_ft_range'] = 0
data['sq_ft_range'][data_3['sq_ft'].str.contains(' – ')] = 1 # Create a column to indicate that this is a range.

data['sq_ft'] = data['sq_ft'].replace(' sq ft',"", regex = True)
data['min_sq_ft'] = data['sq_ft']
data['max_sq_ft'] = data['sq_ft']
data['min_sq_ft'] = data['min_sq_ft'].transform(lambda x: re.search('(.+?) – ', x).group(1) if re.search('(.+?) – ', x) else x)
data['max_sq_ft'] = data['max_sq_ft'].transform(lambda x: re.split(r" – ", x)[1] if re.search('(.+?) – ', x) else x)
data['min_sq_ft'] = data['min_sq_ft'].replace('[\,]',"",regex=True).astype(int)
data['max_sq_ft'] = data['max_sq_ft'].replace('[\,]',"",regex=True).astype(int)
data['sq_ft_updated'] = data.loc[: , "min_sq_ft":"max_sq_ft"].mean(axis=1)
data = data[(1 < data.sq_ft_updated) & (data.sq_ft_updated < 9000)] # drop the extreme values

# Clean up the 'rent' feature. In the case of rent being a range instead of a number, take the average of the min and max.
data['rent_range'] = 0
data['rent_range'][data['rent'].str.contains(' – ')] = 1 # Create a column to indicate that this is a range.

data = data.drop(index = data[data['rent'].str.contains('Person')].index)
data = data.drop(index = data[data['rent'].str.contains('Call for Rent')].index)
data['min_rent'] = data['rent']
data['max_rent'] = data['rent']
data['min_rent'] = data['min_rent'].transform(lambda x: re.search('(.+?) – ', x).group(1) if re.search('(.+?) – ', x) else x)
data['max_rent'] = data['max_rent'].transform(lambda x: re.split(r" – ", x)[1] if re.search('(.+?) – ', x) else x)
data['min_rent'] = data['min_rent'].replace('[\$\,\.]',"",regex=True).astype(int)
data['max_rent'] = data['max_rent'].replace('[\$\,\.]',"",regex=True).astype(int)
data['rent_updated'] = data.loc[: , "min_rent":"max_rent"].mean(axis=1)
index_1 = data[(data['city'] == 'Encinitas') & (data['bed'] == '5 beds')].index
index_2 = data[(data['city'] == 'Carpinteria') & (data['bed'] == '3 beds')].index
index_3 = data[(data['city'] == 'Aptos') & (data['bed'] == '4 beds')].index
data = data.drop(index = [index_1[0], index_2[0], index_3[0]]) # drop the extreme values

# Create a numeric feature 'minimum_lease' from the 'Lease Length' feature
path = 'lease_info.xlsx'
pd.DataFrame(data['Lease Length'].unique()).to_excel(excel_writer = path) # manipulate the data and create mapping in Excel
minimum_lease = pd.read_excel(path) # read in the manipulated data
data = data.merge(minimum_lease, on = 'Lease Length')

# Create a binary feature 'allow_pet' (1 = Yes, 0 = No) from the 'Pet Policy' feature
path = 'pet_info.xlsx'
pd.DataFrame(data['Pet Policy'].unique()).to_excel(excel_writer = path) # manipulate the data and create mapping in Excel
allow_pets = pd.read_excel(path) # read in the manipulated data
data = data.merge(allow_pets, on = 'Pet Policy')

# Create a binary feature 'onsite_parking' (1 = Yes, 0 = No) from the 'Parking' feature
path = 'parking_info.xlsx'
pd.DataFrame(data['Parking'].unique()).to_excel(excel_writer = path) # manipulate the data and create mapping in Excel
parking_info = pd.read_excel(path) # read in the manipulated data
data = data.merge(parking_info, on = 'Parking')

# Create binary features 'pool' and 'fitness_center' (1 = Yes, 0 = No) from the 'Fitness & Recreation' feature
data['pool'] = data['Fitness & Recreation'].apply(lambda x: 1 if 'Pool' in str(x) else 0)
data['fitness_center'] = data['Fitness & Recreation'].apply(lambda x: 1 if 'Fitness Center' in str(x) else 0)

# Create a binary feature 'elevator' (1 = Yes, 0 = No) from the 'Interior' feature
data['elevator'] = data['Interior'].apply(lambda x: 1 if 'Elevator' in str(x) else 0)

# Create a numeric feature 'kitchen_features' from the 'Kitchen' feature
data['kitchen_features'] = data['Kitchen'].apply(lambda x: str(x).count('•'))

# Create a binary feature 'security_system' from the 'Security' feature
data['security_system'] = 1
data['security_system'][data['Security'].isnull()] = 0

# Create binary features 'washer_dryer', 'internet', air_conditioning' (1 = Yes, 0 = No) from the 'Unique Features' and 'Features' feature
data['washer_dryer'] = data['Unique Features']
data['washer_dryer'] = data['Features'].apply(lambda x: 1 if 'washer/dryer' in str(x).lower() else 0)
data['washer_dryer'] = data['washer_dryer'].apply(lambda x: 1 if 'washer/dryer' in str(x).lower() else x)
data['internet'] = data['Unique Features']
data['internet'] = data['Features'].apply(lambda x: 1 if ('internet' or 'wifi' or 'wi-fi') in str(x).lower() else 0)
data['internet'] = data['internet'].apply(lambda x: 1 if ('internet' or 'wifi' or 'wi-fi') in str(x).lower() else x)
data['air_conditioning'] = data['Unique Features']
data['air_conditioning'] = data['Features'].apply(lambda x: 1 if 'air conditioning' in str(x).lower() else 0)
data['air_conditioning'] = data['air_conditioning'].apply(lambda x: 1 if 'air conditioning' in str(x).lower() else x)

# Create a binary feature 'furnished' (1 = Yes, 0 = No) from the 'Property Information' and 'Living Space' feature
data['furnished'] = data['Property Information']
data['furnished'] = data['Living Space'].apply(lambda x: 1 if 'furnished' in str(x).lower() else 0)
data['furnished'] = data['furnished'].apply(lambda x: 1 if 'furnished' in str(x).lower() else x)

# Reorder and export the cleaned data
clean_data = data[['url', 'property_name', 'city', 'rent_updated', 'n_bath','n_bath',
       'sq_ft_updated', 'walkscore', 'allow_pet', 'minimum_lease',  'onsite_parking', 
        'pool', 'fitness_center', 'elevator', 'kitchen_features','security_system', 
        'washer_dryer', 'internet', 'air_conditioning', 'furnished']]
clean_data.to_csv('clean_apt_data.csv')

# Reorder and export the cleaned data with exact rent and sqrt (i.e. not a range)
clean_data_exact = data[['url', 'property_name', 'city', 'rent_updated', 'n_bed','n_bath',
       'sq_ft_updated', 'walkscore', 'allow_pet', 'minimum_lease', 'onsite_parking', 
        'pool', 'fitness_center', 'elevator', 'kitchen_features',
       'security_system', 'washer_dryer', 'internet', 'air_conditioning',
       'furnished', 'rent_range', 'sq_ft_range']][(data['rent_range'] == 0) & (data['sq_ft_range'] == 0)]
clean_data_exact.to_csv('clean_apt_data_norange.csv')



