## generate the descrition from the previous transactions using sqldb agent in langchain

import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts.few_shot import FewShotPromptTemplate
import pandas as pd
import re

#mykey = "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"


def query_llm_response(data):
    prompt = PromptTemplate(
        input_variables=["data"],
        template=""" Assume you are financial crime analyst with 20 years of experience. Given a list of financial transactions {data}, identify and explain potential instances of money laundering. Focus on the specific transactions that display characteristics commonly associated with money laundering practices. Your analysis should include:

Transaction Details: Provide the exact details of money laundering transactions, including timestamps, source account, destination account, amounts, and transaction types. Don't use outside data just use given for transactions.

Reasoning: Explain why each identified transaction is considered as money laundering indicators. Consider factors such as transfer amount from multiple sender to single receivers, single sender to multiple receiver accounts unusual patterns, large amounts, rapid transactions, multiple currencies, or suspicious account relationships.

Please provide detailed explanations for each flagged transaction, highlighting the specific attributes or patterns that indicate potential money laundering. Use clear and concise reasoning to support your identification of money laundering transactions. Provide sender accounts, receiver accounts, amount, currency, etc. Example:        * Multiple transactions continue:
        * Transaction ID 012386: 16003.44 Euros transferred via ACH from account 800F963A0 to account 800F07C90.
        * Transaction ID 01595: 8201.82 Euros transferred via ACH from account 800F963A0 to account 8014DDE40.
        * followed by additional transactions involving different currencies and accounts.
* 		September 6, 2022:
    * Transaction ID 022086: 18261.63 US Dollars transferred via ACH from account 800F963A0 to account 800CD0BE0.
The red flag here is the continuous movement of funds within a network of accounts. Funds are gathered into a central account (800F963A0) from various sources and then scattered or distributed across different accounts, often in different currencies, creating a complex web of transactions. This pattern of moving funds between multiple accounts in quick succession could be indicative of attempting to disguise the origin or destination of the funds, a typical characteristic of money laundering through "Gather-Scatter" schemes.

Display the transactions only which are money laundering. Note: Transaction id, sender id, receiver id , etc., should come from the given transaction data. don't come outside and reasoning also come based on the given examples and considered factors""",
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
        template=""" Given a list of financial transactions {data}, extract the list of transactions id of money laundering (role). output in list format (output) """,
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

def generate_sar_report1(data,transactionid):
    df1=list(data['transaction_id'])
    report=" "
    if transactionid in df1:
        data = data[data['transaction_id'] == transactionid]
        report = f"""FinCEN Form 109
        March, 2011 Previous editions will not be accepted after September 2011
        Suspicious Activity Report by Money Services Business

        Part I
        Subject Information
        *4 Individual’s last name or entity’s full name: {data['Name'].values[0]}
        *5 First name: {data['Name'].values[0]}
         6 Middle initial: NA
        *7 Address: NA
        *8 City: {data['city'].values[0]}
        *9 State: {data['city'].values[0]}
        *10 Zip Code: NA
        *11 Country Code (If not US): {data['city'].values[0]}
        *12 Government issued identification (if available): NA
        *13 SSN/ITIN (individual) or EIN (entity): NA
        *14 Date of birth: NA
         15 Telephone number: NA

        Part II
        Suspicious Activity Information
        *16 Date or date range of suspicious activity: {data['transaction_date'].values[0]}
        *17 Total amount involved in suspicious activity: {data['Total Amount'].values[0]}
        *18 Category of suspicious activity: Money Laundering
        *19 Financial services involved in the suspicious activity and character of the suspicious activity: NA
        Part III
        Narrative: {langchain_result}

        If mailing, send each completed SAR report to:
        Electronic Computing Center - Detroit
        Attn: SAR-MSB
        P.O. Box 33117
        Detroit, MI 48232-5980

        Catalog No. 34944N Rev. 3/01/11
        """
    else:
        print(f"Transaction ID {transactionid} not found in the dataset.")
    return report




# Streamlit app
st.title("Money Laundering Detection & SAR Report Generator")

# Load your data
df=pd.read_csv("/Users/centific/Downloads/Email Generator App - Source Code/MOCK_DATA.csv")
#df=df.drop(columns=['label','geographical_location','known_customer_locations','username'])
df=df.drop(columns=["label"])
#df=df[:50]
df['Total Amount']=df['transaction_amount']
df.rename(columns = {'geographical_location':'city', 'username':'Name','transaction_amount':'t_amount'}, inplace = True)
#data1=df.to_dict(orient='records')
st.write(df.head())

langchain_result = query_llm_response(df)
# Get LangChain response
if st.button("Process Transactions"):
    st.write("LangChain Response:")
    st.write(langchain_result)

extracted_ids = extract_transaction_ids(langchain_result)
#langchain_result1 = query_llm_response1(langchain_result)
if st.button("Extract money laundering transactionid"):
    st.write("LangChain Response:")
    st.write(extracted_ids)
    # Generate SAR Report
# Generate SAR report from the sample data
#generated_report = generate_sar_report1(sar_data)
#print(generated_report)
if st.button("Generate SAR Report"):
    sar_report1=[]
    for i in extracted_ids:
        sar_report = generate_sar_report1(df,i)
    #dataextractlist = extractfn(sar_report,df)
        st.write("Generated SAR Report:")
        sar_report1.append(sar_report)
        st.write(sar_report)
#tab1, tab2,tab3 = st.tabs(["Suscipicious Transactions", " Transaction Id", "SAR Report"])
#tab1.write(langchain_result)
#tab2.write(extracted_ids)
#tab3.write(sar_report1)
