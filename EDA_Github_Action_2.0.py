#!/usr/bin/env python
# coding: utf-8

# ## Import libraries 
# 

# In[1]:


#Install all libraries requred
import pandas as pd #pandas
import seaborn as sns # Data Visualisation
import matplotlib.pyplot as plt # Data Visualisation
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter
import numpy as np 
from matplotlib.ticker import ScalarFormatter
# from telegram import Bot
# from telegram import InputFile
import telebot
import os 

import requests # To read the parque
import pyarrow.parquet as pq
from io import BytesIO


# ### Donations Facility

# In[2]:


donations_facility_url = 'https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/donations_facility.csv'
donations_facility = pd.read_csv(donations_facility_url)
donations_facility.head(3).T


# In[3]:


# Originally the column 'date' in object data type. Convert 'date' to datettime format
donations_facility['date'] = pd.to_datetime(donations_facility['date'])

donations_facility.info()


# ### Donations State

# In[4]:


donations_state_url = 'https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/donations_state.csv'
donations_state = pd.read_csv(donations_state_url) # extract data from url

donations_state.head().T


# In[5]:


# Convert 'date' columns Dtype to Datetime
donations_state['date'] = pd.to_datetime(donations_state['date'])

# Check Dtype of columns
donations_state.info()


# ## Trend Analysis without State MALAYSIA

# In[6]:


# Drop state = 'Malaysia'
donations_state = donations_state.drop(donations_state[donations_state['state'] == 'Malaysia'].index) 

# Groupby the total blood donation by State
donate_by_state = donations_state.groupby('state')['daily'].sum().reset_index() 

# Sort the state in ascending order
donate_by_state = donate_by_state.sort_values(by = 'daily', ascending= True) 
print(donate_by_state)


# #### Total Blood Donations by State from 2006 - 2024

# In[7]:


# Chart to show Daily vs state

# Set backend to Agg, to allow Matplotlib work in github actions(headless environment)
plt.switch_backend('Agg')

sns.set(style= "whitegrid")

# Bar plot using seaborn
plt.figure(figsize =(14,7)) # Size of the plot
bar_plot = sns.barplot(x = 'state', y = 'daily', data = donate_by_state, hue = 'state',palette = 'colorblind') # Colour, data for x & y axis, 

plt.title('Total Blood Donations by State from 2006 - 2024')
plt.xlabel('State') 
plt.ylabel('Total Blood Donations (000,000)')
plt.xticks(rotation = 45) # Angle of rotation for x-axis label

# Label value for each State
for index, value in enumerate(donate_by_state['daily']):
    plt.text(index, value + 0.1, f'{value:.0f}', ha = 'center', va = 'bottom', fontsize = 10)

#####
print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

# Save the as an image
yearlytrendstate = 'Blood_Donations_Yearly_Trend_In_Malaysia.png'
plt.savefig(yearlytrendstate, bbox_inches='tight')
plt.show()
plt.close()

##### Send Image to Telegram Bot######
bot_token = '6789524159:AAHIbYINLbnswT2iciqWCIQbt75uZsKSTTg'
chat_id = '-4112415710'  ##Group chat id which consist bot

# Initialize the Telegram bot
bot = telebot.TeleBot(bot_token)

# Send the image to Telegram
with open(yearlytrendstate, 'rb') as image:
    bot.send_photo(chat_id=chat_id, photo=image)


# Remove the saved image file in local, to save storage
os.remove(yearlytrendstate)



# #### Total Blood Donations trend from 2006 - 2024

# In[8]:


# Calculate sum of daily in year, without using groupby
trydf = donations_state.copy()

# Convert column 'date' to index, which necessary before can apply resample
trydf.set_index('date', inplace = True)

# Resample to year
yearly_donations_state_trydf = trydf.resample('Y').sum()

# Convert back index 'date' to column
yearly_donations_state_trydf = yearly_donations_state_trydf.rename_axis('date').reset_index() # Convert back index 'date' to columns

# Drop column name 'state'
yearly_donations_state_trydf = yearly_donations_state_trydf.drop('state', axis=1) 

# Set backend to Agg, to allow Matplotlib work in github actions(headless environment)
plt.switch_backend('Agg')

#########Yearly trend plot#####################
sns.set(style= "whitegrid")
plt.figure(figsize =(14,7)) # Size of the plot
sns.lineplot(x ='date', y ='daily', data =yearly_donations_state_trydf, color ='blue', label ='Number of blood donations')
plt.title('Yearly Blood Donation Trends in Malaysia') # Title of the plot/chart
plt.xlabel('Year')  # X-axis name
plt.ylabel('Total Blood Donations') # Y-axis name


# Display value of donations for each year in Million(M)
for index, value in enumerate(yearly_donations_state_trydf['daily']):
    plt.text(yearly_donations_state_trydf['date'].iloc[index], value + 0.1, f'{value / 1e6:.2f}M', ha='center', va='bottom', fontsize=11)


# Save the Blood Type Trend as an image
yearlytrend = 'Blood_Donations_Yearly_Trend_In_Malaysia.png'
plt.savefig(yearlytrend, bbox_inches='tight')
plt.show()
plt.close()


# Send the image to Telegram
# with open(yearlytrend, 'rb') as image:
#     bot.send_photo(chat_id=chat_id, photo=InputFile(image))
with open(yearlytrendstate, 'rb') as image:
    bot.send_photo(chat_id=chat_id, photo=image)

# Remove the saved image file in local, to save storage
os.remove(yearlytrend)


# ### Yearly trend line for each blood type

# In[9]:


# Plotting the blood donation trend

# Set backend to Agg, to allow Matplotlib work in github actions(headless environment)
plt.switch_backend('Agg')

# Plot size
plt.figure(figsize =(20, 10)) # Size of the plot

# Plot each blood type as a separate line
plt.plot(yearly_donations_state_trydf['date'], yearly_donations_state_trydf['blood_a'], label ='Blood Type A', marker ='o')
plt.plot(yearly_donations_state_trydf['date'], yearly_donations_state_trydf['blood_b'], label ='Blood Type B', marker ='o')
plt.plot(yearly_donations_state_trydf['date'], yearly_donations_state_trydf['blood_o'], label ='Blood Type O', marker ='o')
plt.plot(yearly_donations_state_trydf['date'], yearly_donations_state_trydf['blood_ab'], label ='Blood Type AB', marker ='o')



# Customize the plot
plt.title('Blood Donation Yearly Trend by Blood Type') # Title of the plot
plt.xlabel('Year') # X-axis title
plt.ylabel('Total Blood Donations') # Y-axis title
plt.legend()
plt.grid(True)

# Save the Blood Type Trend as an image
bloodtype = 'Blood_Type_Yearly_Trend.png'
plt.savefig(bloodtype, bbox_inches='tight')
plt.show()
plt.close()

# Send the image to Telegram
# with open(bloodtype, 'rb') as image:
#     bot.send_photo(chat_id=chat_id, photo=InputFile(image))
with open(bloodtype, 'rb') as image:
    bot.send_photo(chat_id=chat_id, photo=image)

# Remove the saved image file in local, to save storage
os.remove(bloodtype)





# In[10]:


# # Group by date and sum daily donations
# daily_donations_state_sum = donations_state.groupby('date')['daily'].sum().reset_index()

# # Set column date as index
# daily_donations_state_sum.set_index('date', inplace = True)

# # Resample to yearly frequency 
# yearly_donations_state = daily_donations_state_sum.resample('Y').sum()
# yearly_donations_state = yearly_donations_state.rename_axis('date').reset_index() # Convert back index 'date' to columns

# # Resample to monthly frequency
# quarter_donations_state = daily_donations_state_sum.resample('Q').sum()
# quarter_donations_state = quarter_donations_state.rename_axis('date').reset_index() # Convert back index 'date' to columns


# yearly_donations_state.head(10)


# In[11]:


# # Yearly trend plot
# sns.set(style= "whitegrid")
# plt.figure(figsize =(14,7)) # Size of the plot
# sns.lineplot(x ='date', y ='daily', data =yearly_donations_state, color ='blue', label ='Number of donations')
# plt.title('Blood Donations Yearly Trend')
# plt.xlabel('Year') 
# plt.ylabel('Total Blood Donations (000,000)')


# # Display value of daonations for each year
# for index, value in enumerate(yearly_donations_state['daily']):
#     plt.text(yearly_donations_state['date'].iloc[index], value + 0.1, f'{value / 1e6:.2f}M', ha='center', va='bottom', fontsize=11)


# ### Newdonors_facility

# In[12]:


newdonors_facility_url = 'https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/newdonors_facility.csv'
newdonors_facility = pd.read_csv(newdonors_facility_url)

# Convert Dtype 'date' column to Datetime
newdonors_facility['date'] = pd.to_datetime(newdonors_facility['date'])

newdonors_facility.head(10)


# In[13]:


newdonors_facility['hospital'].nunique()


# In[14]:


# Check data type
newdonors_facility.info()


# ### Newdonors_state

# In[15]:


newdonors_state_url = 'https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/newdonors_state.csv'
newdonors_state = pd.read_csv(newdonors_state_url)
newdonors_state.head(10)


# In[16]:


# Convert Dtype 'date' column to Datetime
newdonors_state['date'] = pd.to_datetime(newdonors_state['date'])

# Check Dtype of columns
newdonors_state.info()


# In[17]:


# Filter column 'state' to include Malaysia only
newdonors_state_malaysia = newdonors_state[ newdonors_state['state'] == 'Malaysia']
newdonors_state_malaysia.head()


# In[18]:


# Set column date as index(need to do this before resample can be done)
newdonors_state_malaysia.set_index('date', inplace = True)


# In[19]:


# Resample date to yearly
newdonors_state_malaysia = newdonors_state_malaysia.resample('Y').sum()
newdonors_state_malaysia = newdonors_state_malaysia.rename_axis('date').reset_index() # Convert back index 'date' to columns

# Drop column 'state'
newdonors_state_malaysia = newdonors_state_malaysia.drop('state', axis=1) 




# In[20]:


# Convert value inside columns age to %(percentage)
age_group_columns = ['17-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', 'other']
df_percentage = [newdonors_state_malaysia[age_group_columns].div(newdonors_state_malaysia['total'], axis = 0)*100] # Take the value exist inside column age and divide with 'Total' , then multiply with 100. To get the percentage

# Convert the list to pandas dataframe
df_percentage = pd.concat(df_percentage)

# Round off to 2 decimal places of %(percentage)
df_percentage = df_percentage.round(2)

# Add column 'date' to the df_percentage
df_percentage = pd.concat([newdonors_state_malaysia['date'].dt.year, df_percentage], axis = 1)

# Rename column 'date' to 'year'

df_percentage.rename(columns = {'date':'Year'}, inplace = True) 

df_percentage


# In[21]:


# Set 'Year' column as index
df_percentage.set_index('Year', inplace = True)


# ## Heatmap Age range

# In[22]:


# Heatmap

# Set backend to Agg, to allow Matplotlib work in github actions(headless environment)
plt.switch_backend('Agg')

plt.figure(figsize=(10, 8)) # Plot size
sns.heatmap(df_percentage, cmap='Greens', annot=True, fmt=".1f", linewidths=.1)
plt.title('2006-2024\nTotal Blood Donations of Malaysia by Age Range (%)\n') # Plot title

# Move X-axis to the top
plt.gca().xaxis.tick_top()

# 6789524159:AAHIbYINLbnswT2iciqWCIQbt75uZsKSTTg


# Save the heatmap as an image
image_filename = 'heatmap.png'
plt.savefig(image_filename, bbox_inches='tight')
plt.close()

# Send the image to Telegram
# with open(image_filename, 'rb') as image:
#     bot.send_photo(chat_id=chat_id, photo=InputFile(image))
with open(image_filename, 'rb') as image:
    bot.send_photo(chat_id=chat_id, photo=image)

# Remove the saved image file in local, to save storage
os.remove(image_filename)


# ### Granular / Parque file

# In[23]:


donor_url = "https://dub.sh/ds-data-granular"

# Download the Parquet file
response = requests.get(donor_url)
parquet_data = BytesIO(response.content)

# Read the Parquet file into a pandas DataFrame
table = pq.read_table(parquet_data)
donor_df = table.to_pandas()

# Convert dtype column 'visit_date' to datetime
donor_df['visit_date'] = pd.to_datetime(donor_df['visit_date'])

donor_df.head(7)




# In[24]:


# Check time difference between consecutive visits for each donor
aa = donor_df.copy()
aa.sort_values(['donor_id','visit_date'], inplace= True)
aa['Day_Between_Visit'] = aa.groupby('donor_id')['visit_date'].diff().dt.days

aa.head()


# In[25]:


# Check number of donor that donate more than 1 time
returning_donors = aa[aa['Day_Between_Visit'].notnull()]

returning_donors['donor_id'].nunique()



# In[26]:


average_time_between_visits = aa['Day_Between_Visit'].mean()
average_time_between_visits


# In[27]:


# Distribution

# Set backend to Agg, to allow Matplotlib work in github actions(headless environment)
plt.switch_backend('Agg')

plt.figure(figsize= (10,6))
histogram =sns.histplot(data= returning_donors, x='Day_Between_Visit', bins=20, kde= True, color='red')
plt.title("Distribution of Day Between Visits")
plt.xlabel('Days between Visits')
plt.ylabel('Frequency of Observations')

# Set x-axis limits from 0 -1000 only
plt.xlim(0, 1000)

# Save the Blood Type Trend as an image
distribution_image = 'Distribution_of_day_between_visits.png'
plt.savefig(distribution_image, bbox_inches='tight')
plt.show()
plt.close()


# Send the image to Telegram
# with open(distribution_image, 'rb') as image:
#     bot.send_photo(chat_id=chat_id, photo=InputFile(image))
with open(distribution_image, 'rb') as image:
    bot.send_photo(chat_id=chat_id, photo=image)

# Remove the saved image file in local, to save storage
os.remove(distribution_image)


# ### Donor  Facility

# In[28]:


# donors_facility  = 'https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/newdonors_facility.csv'
# donors_facility = pd.read_csv(donors_facility)
# donors_facility.head()


