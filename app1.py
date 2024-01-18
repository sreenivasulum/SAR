## generate the descrition from the previous transactions using sqldb agent in langchain

import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts.few_shot import FewShotPromptTemplate
import pandas as pd
import matplotlib.pyplot as plt
import re

#mykey = "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"


def query_llm_response(data):
    prompt = PromptTemplate(
        input_variables=["data"],
        template=""" using list of financial transactions {data}, identify and explain potential instances of money laundering. Your analysis should include:

Transaction Details: Provide the exact details of money laundering transactions, including transaction date, sender account, receiver account, amounts, and transaction types. Don't use outside data just use given for transactions.

Reasoning: Explain why each identified transaction is considered  money laundering indicators based on the Consider factors such as transfer amount from multiple sender accounts to single receiver account, single sender to multiple receiver accounts, large amounts, multiple currencies.

Please provide detailed explanations for each flagged transaction, highlighting the specific attributes or patterns that indicate potential money laundering. Use clear and concise reasoning to support your identification of money laundering transactions. should Provide sender accounts, receiver accounts, amount, currency, etc., based on given transactions 
Example: 
        * Transaction ID 012386: 16003.44 Euros transferred via ACH from  sender account 800F963A0 to receiver account 800F07C90.
        * Transaction ID 01595: 8201.82 Euros transferred via ACH from sender account 800F963A0 to  receiver account 8014DDE40.
    * Transaction ID 022086: 18261.63 US Dollars transferred via ACH from sender account 800F963A0 to receiver account 800CD0BE0.
The red flag here is the continuous movement of funds within a network of accounts. Funds are gathered into a central account (800F963A0) from various sources and then scattered or distributed across different accounts such as 800F07C90, 8014DDE40, 800CD0BE0, often in different currencies, creating a complex web of transactions. This pattern of moving funds between multiple accounts in quick succession could be indicative of attempting to disguise the origin or destination of the funds, a typical characteristic of money laundering through "Gather-Scatter" schemes.

Display the transactions only which are money laundering. Note: Transaction id, sender account id, receiver account id , etc., should come from the given transaction data. don't come outside and reasoning also come based on the given examples and considered factors""",
    )
    
    print(prompt.format(data=data))

    mykey = "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"
    llm = OpenAI(temperature=0.9,openai_api_key=mykey,model_name='gpt-3.5-turbo')
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Step 7: Run the LLMChain
    output = chain.run(data)
    return output

def query_llm_response1(data):
    prompt = PromptTemplate(
        input_variables=["data"],
        template=""" Using the provided list of financial transactions {data}, identify and explain potential instances of money laundering. Your analysis should strictly rely on the transactions provided.

Transaction Details: Identify money laundering transactions by must providing specific transaction details such as transaction date, sender account, receiver account, amounts, and transaction types. Extract transaction IDs, sender account IDs, receiver account IDs, amounts, and currencies exclusively from the given transaction data.

Reasoning: Examine the transactions for indicators of potential money laundering, considering factors like transfer amounts from multiple sender accounts to a single receiver account, single sender to multiple receiver accounts, large sums, and transactions involving multiple currencies.

Please provide detailed explanations for each flagged transaction, highlighting specific attributes or patterns indicating potential money laundering. Ensure that the details of the transactions, including transaction ID, sender account ID, receiver account ID, amounts, and currency, are derived solely from the provided transaction data.

Example:
800388YBN,800F963A0,448809.06,14/11/23,UK,USA,800F07C90,ghurtic0,Sayre,Rohlfing,Sayre Rohlfing,ACH,Australian dollar
974129BQ5,800F963A0,109298.1,15/11/23,UK,USA,8014DDE40,rremon1,Mano,Mapledorum,Mano Mapledorum,ACH,Australian dollar
308327ID1,800F963A0,796159.07,16/11/23,UK,UK,800CD0BE0,blanceley2,Roana,Gowry,Roana Gowry,ACH,Australian Dollar
For instance:
    * Transaction ID 800388YBN: 448809.06 Australian dollar transferred via ACH from sender account 800F963A0 to receiver account 800F07C90.
    * Transaction ID 974129BQ5: 109298.1 Australian dollar transferred via ACH from sender account 800F963A0 to receiver account 8014DDE40.
    * Transaction ID 308327ID1: 796159.07 Australian dollar transferred via ACH from sender account 800F963A0 to receiver account 800CD0BE0.

The identified red flag here is the continuous movement of funds within a network of accounts. Funds are gathered into a central account (e.g., 800F963A0) from various sources and then dispersed across different accounts (e.g., 800F07C90, 8014DDE40, 800CD0BE0), often in different currencies. This complex web of transactions, involving quick succession transfers between multiple accounts, might indicate an attempt to disguise the origin or destination of the funds. Such a pattern is typical of money laundering through "Gather-Scatter" schemes.

Display only the transactions identified as potential instances of money laundering, extracting transaction IDs, sender account IDs, receiver account IDs, etc., solely from the given transaction data. Ensure that the reasoning aligns with the examples provided and considers the specified factors.
don't use external transaction id, sender account id, receiver accountid. """,
    )
    
    print(prompt.format(data=data))

    mykey = "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"
    llm = OpenAI(temperature=0.9,openai_api_key=mykey,model_name='gpt-3.5-turbo')
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Step 7: Run the LLMChain
    output = chain.run(data)
    return output

def extract_transaction_ids(llm_response):
    transaction_ids = re.findall(r"Transaction ID: (\w+)", llm_response) + re.findall(r"Transaction ID (\w+)", llm_response)
    print("Extracted Transaction IDs:", transaction_ids)
    #print("Extracted Transaction IDs:", transaction_ids)
    return transaction_ids

def generate_sar_report(data):
    prompt = PromptTemplate(
        input_variables=["data"],
        template=""" using the given infomation don't use outside information create a SAR sucpicious activity report 
        {data}
Report should have 4 section as:
Part1 as Subject Information. Display subject information as bold and large. Under this section 5 rows should be there each are separated by line and first row contains subject types which contain
attributes such as (a).sender, (b). receiver, (c)a & b. (d). None. should be display these four attributes in check box format. In the second row contains Name, first name and last should be display as attributes with the names of given data else put NA. The third row contains address attributes display attribute  with the values of given data else put NA. Similarly, fourth row city name filled with given data else use NA and fifth row contains aadhar card, driving licences and others with check box display and fill based on the given data else use not aviable. All the 5 rows attribute  values filled with given data. All the rows are separated by line with one sentence gap should be displayed |Part2 Suspicious Activity Information|Part3 Previous Transactions |Part4

part1,part2,part3 should be describes using given data and all parts titles are displayed with large size. 

part4 should following below guidelines
guidelines:
Explanation/description of suspicious activity(ies). 

It is note that if the data is not available for the attribute just put Not available.
  """,
    )
    
    print(prompt.format(data=data))

    mykey = "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"
    llm = OpenAI(temperature=0.9,openai_api_key=mykey,model_name='gpt-3.5-turbo')
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Step 7: Run the LLMChain
    output = chain.run(data)
    return output

def generate_sar_report1(fullnames,firstnames,lastnames,cities,dates,amounts):
    report=" "

    report = f"""FinCEN Form 109
    March, 2011 Previous editions will not be accepted after September 2011
    Suspicious Activity Report by Money Services Business

    Part I
    Subject Information
    *4 Individual’s last name or entity’s full name: {fullnames}
    *5 First name: {firstnames}
     6 Middle initial: NA
    *7 Address: NA
    *8 City: {cities}
    *9 State: {cities}
    *10 Zip Code: NA
    *11 Country Code (If not US): {cities}
    *12 Government issued identification (if available): NA
    *13 SSN/ITIN (individual) or EIN (entity): NA
    *14 Date of birth: NA
    15 Telephone number: NA

    Part II
    Suspicious Activity Information
    *16 Date or date range of suspicious activity: {dates}
    *17 Total amount involved in suspicious activity: {amounts}
    *18 Category of suspicious activity: Money Laundering
    *19 Financial services involved in the suspicious activity and character of the suspicious activity: NA
       
    Part III
    Narrative: {langchain_result}
    """
    return report




# Streamlit app
st.title("SAR Report Generator for Money Laundering")

# Load your data
df=pd.read_csv("/Users/centific/Downloads/Email Generator App - Source Code/MOCK_DATA.csv")
#df=df.drop(columns=['label','geographical_location','known_customer_locations','username'])
df1=df
df=df.drop(columns=["label"])
#df=df[:50]

# Select a column for the pie chart (e.g., 'geographical_location')
selected_column = st.selectbox("Select a column for the pie chart:", df1.columns)

# Create a pie chart
fig, ax = plt.subplots()
df1[selected_column].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=plt.cm.Paired.colors)
ax.set_aspect('equal')  # Equal aspect ratio ensures that the pie is drawn as a circle.

# Display the pie chart using Streamlit
st.pyplot(fig)

df['Total Amount']=df['transaction_amount']
df.rename(columns = {'geographical_location':'city', 'username':'Name','transaction_amount':'t_amount'}, inplace = True)
#data1=df.to_dict(orient='records')
st.write(df.head())

langchain_result = query_llm_response1(df)
# Get LangChain response
if st.button("Process Transactions"):
    st.write("Response:")
    st.write(langchain_result)

extracted_ids = extract_transaction_ids(langchain_result)
#langchain_result1 = query_llm_response1(langchain_result)
full_names = []
first_names=[]
last_names=[]
cities = []
dates = []
amounts = []

# Iterate through each transaction ID and extract corresponding attribute values
for transaction_id in extracted_ids:
    # Filter the data for a specific transaction ID
    if transaction_id in list(df['transaction_id']):
       data_for_id = df[df['transaction_id'] == transaction_id]
       full_names.extend(data_for_id['full_name'].values.tolist())
       first_names.extend(data_for_id['first_name'].values.tolist())
       last_names.extend(data_for_id['last_name'].values.tolist())
       cities.extend(data_for_id['city'].values.tolist())
       dates.extend(data_for_id['transaction_date'].values.tolist())
       amounts.extend(data_for_id['Total Amount'].values.tolist())
    else:
        #df.loc[row_number, columns_of_interest]
        full_names.extend(df.loc[transaction_id, ['full_name']])
        first_names.extend(df.loc[transaction_id, ['first_name']])
        last_names.extend(df.loc[transaction_id, ['last_name']])
        cities.extend(df.loc[transaction_id, ['city']])
        dates.extend(df.loc[transaction_id, ['transaction_date']])
        amounts.extend(df.loc[transaction_id, ['Total Amount']])


#if st.button("Extract money laundering transactionid"):
    #st.write("LangChain Response:")
    #st.write(extracted_ids)
 
sar_report = generate_sar_report1(full_names,first_names,last_names,cities,dates,amounts)
#if st.button("Generate SAR Report"):
   
    #sar_report = generate_sar_report1(names,cities,dates,amounts)
    #dataextractlist = extractfn(sar_report,df)
    #st.write("Generated SAR Report:")
    #sar_report1.append(sar_report)
    #st.write(sar_report)
tab1, tab2,tab3 = st.tabs(["Suscipicious Transactions", " Transaction Id", "SAR Report"])
tab1.write(langchain_result)
tab2.write(extracted_ids)
tab3.write(sar_report)
